"""Train and evaluate the per-target activity models exactly as docs/evaluation.md says.

Usage: uv run python -m molscreen.train [--genes CDK6 EGFR]
Writes results/activity_models.json, results/activity_models.md, results/datasets.md and models/<GENE>.joblib.
A run on some genes updates their entries and keeps the others already in the JSON.
"""

import argparse
import json

import joblib
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score

from molscreen.chem import morgan_fp, murcko_scaffold, scaffold_split
from molscreen.data import PULLS, ROOT, build_dataset

RESULTS = ROOT / "results"
MODELS = ROOT / "models"
RADIUS, N_BITS = 2, 2048
ABSTAIN_PERCENTILE = 5
# Fixed before seeing any result; not tuned (no inner split was used).
LGBM_PARAMS = {
    "n_estimators": 500, "learning_rate": 0.05, "num_leaves": 31, "min_child_samples": 10, "subsample": 0.8,
    "subsample_freq": 1, "colsample_bytree": 0.5, "random_state": 0, "deterministic": True, "force_col_wise": True,
    "n_jobs": 4, "verbose": -1,
}
RF_PARAMS = {"n_estimators": 500, "random_state": 0, "n_jobs": -1}


def fingerprints(smiles: list[str]) -> np.ndarray:
    return np.stack([morgan_fp(s, RADIUS, N_BITS) for s in smiles])


def max_tanimoto(query: np.ndarray, ref: np.ndarray, leave_one_out: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """For each query row: the max Tanimoto to `ref` and the index of that neighbour.
    With `leave_one_out`, `query` is `ref` and each row skips itself."""
    r = ref.astype(np.float32)
    r_bits = r.sum(1)
    best, arg = np.empty(len(query), np.float32), np.empty(len(query), np.int64)
    for start in range(0, len(query), 1000):  # chunks keep the similarity matrix small
        q = query[start:start + 1000].astype(np.float32)
        inter = q @ r.T
        union = q.sum(1)[:, None] + r_bits[None, :] - inter
        sim = np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)
        if leave_one_out:
            sim[np.arange(len(q)), np.arange(start, start + len(q))] = -1.0
        arg[start:start + len(q)] = sim.argmax(1)
        best[start:start + len(q)] = sim.max(1)
    return best, arg


def abstain_cutoff(train_fps: np.ndarray) -> float:
    """5th percentile of the train-set leave-one-out max Tanimoto."""
    loo, _ = max_tanimoto(train_fps, train_fps, leave_one_out=True)
    return float(np.percentile(loo, ABSTAIN_PERCENTILE))


def metrics(y: np.ndarray, score: np.ndarray, pred: np.ndarray) -> dict:
    """ROC-AUC, PR-AUC (average precision) and balanced accuracy; AUCs are None if `y` has one class."""
    two = len(np.unique(y)) == 2
    return {
        "roc_auc": float(roc_auc_score(y, score)) if two else None,
        "pr_auc": float(average_precision_score(y, score)) if two else None,
        "balanced_acc": float(balanced_accuracy_score(y, pred)) if two else None,
    }


def fit(kind: str, X: np.ndarray, y: np.ndarray):
    model = LGBMClassifier(**LGBM_PARAMS) if kind == "lgbm" else RandomForestClassifier(**RF_PARAMS)
    return model.fit(X, y)


def split(ds):
    train, test = scaffold_split(ds["smiles"].tolist(), test_frac=0.2, seed=0)
    return ds.iloc[train].reset_index(drop=True), ds.iloc[test].reset_index(drop=True)


def run_gene(gene: str, pulled_rows: int):
    """Held-out results for one target, plus the train split and its fingerprints (for the saved model)."""
    ds = build_dataset(gene)
    tr, te = split(ds)
    X_tr, X_te = fingerprints(tr["smiles"].tolist()), fingerprints(te["smiles"].tolist())
    y_tr, y_te = tr["active"].to_numpy(), te["active"].to_numpy()
    if len(np.unique(y_tr)) < 2:
        raise ValueError(f"{gene}: train set has one class only")

    out = {
        "dataset": {
            "rows_pulled": pulled_rows, "rows_kept": int(ds["n_rows"].sum()), "molecules": len(ds),
            "actives": int(ds["active"].sum()), "active_frac": float(ds["active"].mean()),
            "scaffolds": len({murcko_scaffold(s) for s in ds["smiles"]}),
        },
        "n_train": len(tr), "n_test": len(te), "test_active_frac": float(y_te.mean()),
    }
    majority = int(y_tr.mean() >= 0.5)
    out["majority"] = metrics(y_te, np.full(len(te), float(majority)), np.full(len(te), majority))
    sim, nn = max_tanimoto(X_te, X_tr)
    out["nn1"] = metrics(y_te, tr["pchembl"].to_numpy()[nn], y_tr[nn])

    cutoff = abstain_cutoff(X_tr)
    kept = sim >= cutoff
    out["abstain"] = {"cutoff": cutoff, "n_test_abstain": int((~kept).sum()), "n_test_kept": int(kept.sum())}
    for kind in ("rf", "lgbm"):
        p = fit(kind, X_tr, y_tr).predict_proba(X_te)[:, 1]
        out[kind] = metrics(y_te, p, (p >= 0.5).astype(int))
        out[kind]["roc_auc_kept"] = metrics(y_te[kept], p[kept], (p[kept] >= 0.5).astype(int))["roc_auc"]
    return out, tr, X_tr


def switch_rule(genes: dict) -> tuple[str, int]:
    """LightGBM ships unless RF has the higher held-out PR-AUC on at least 6 targets."""
    rf_wins = sum(
        1 for r in genes.values()
        if None not in (r["rf"]["pr_auc"], r["lgbm"]["pr_auc"]) and r["rf"]["pr_auc"] > r["lgbm"]["pr_auc"]
    )
    return ("rf" if rf_wins >= 6 else "lgbm"), rf_wins


def save_model(gene: str, kind: str, release: str, res: dict, tr, X_tr: np.ndarray) -> int:
    path = MODELS / f"{gene}.joblib"
    MODELS.mkdir(exist_ok=True)
    joblib.dump({
        "gene": gene, "target_chembl_id": res["target_chembl_id"], "release": release, "kind": kind,
        "model": fit(kind, X_tr, tr["active"].to_numpy()),
        "radius": RADIUS, "n_bits": N_BITS, "train_fps_packed": np.packbits(X_tr, axis=1),
        "train": tr[["molecule_chembl_id", "smiles", "pchembl", "active"]],
        "abstain_cutoff": res["abstain"]["cutoff"], "metrics": res,
    }, path, compress=3)
    return path.stat().st_size


def f3(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def write_markdown(results: dict) -> None:
    g, rel = results["genes"], results["release"]
    names = {"lgbm": "LightGBM", "rf": "random forest"}
    ds_lines = [
        "# Activity datasets (loop 1)", "",
        f"From `uv run python -m molscreen.train` on ChEMBL pulls ({rel}). Numbers are in",
        "`results/activity_models.json` under `genes.<GENE>.dataset`. Rules: `docs/evaluation.md`.", "",
        "| Gene | Rows pulled | Rows kept | Unique molecules | Actives | Active fraction | Train | Test | Scaffolds |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for gene, r in g.items():
        d = r["dataset"]
        ds_lines.append(
            f"| {gene} | {d['rows_pulled']} | {d['rows_kept']} | {d['molecules']} | {d['actives']} | "
            f"{d['active_frac']:.3f} | {r['n_train']} | {r['n_test']} | {d['scaffolds']} |"
        )
    (RESULTS / "datasets.md").write_text("\n".join(ds_lines) + "\n", encoding="utf-8")

    shipped, rf_wins = results["shipped_model"], results["rf_pr_auc_wins"]
    pairs = ("majority", "nn1", "rf", "lgbm")
    lines = [
        "# Activity models (loop 1): held-out results", "",
        f"Scaffold-split held-out test sets, ChEMBL release {rel}, protocol `docs/evaluation.md`.",
        "All numbers come from `results/activity_models.json`, written by `uv run python -m molscreen.train`.",
        "Morgan fingerprints (radius 2, 2048 bits). Model parameters are fixed in `src/molscreen/train.py`;",
        "nothing was tuned, so no inner split was used. Each cell pair is ROC-AUC / PR-AUC on the held-out set.",
        "Test active frac is also the PR-AUC of a random ranking. Held-out abstain counts held-out molecules whose",
        "max Tanimoto to train is below the cut-off; AUC kept is the shipped model's ROC-AUC on the others.", "",
        ("| Gene | n train | n test | Test active frac | Majority | 1-NN | Random forest | LightGBM "
         "| Abstain cut-off | Held-out abstain | AUC kept | Shipped |"),
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for gene, r in g.items():
        a = r["abstain"]
        cells = [f"{f3(r[k]['roc_auc'])} / {f3(r[k]['pr_auc'])}" for k in pairs]
        lines.append(
            f"| {gene} | {r['n_train']} | {r['n_test']} | {r['test_active_frac']:.3f} | {' | '.join(cells)} "
            f"| {a['cutoff']:.3f} | {a['n_test_abstain']} of {r['n_test']} | {f3(r[shipped]['roc_auc_kept'])} "
            f"| {names[shipped]} |"
        )
    lines += [
        "",
        f"Switch rule: the random forest had the higher held-out PR-AUC on {rf_wins} of {len(g)} targets",
        f"(it needed at least 6), so **{names[shipped]}** ships for every target.",
        "",
        "## Credits",
        "",
        "Bioactivity data: ChEMBL.",
        f"ChEMBL data is from http://www.ebi.ac.uk/chembl - the version of ChEMBL is {rel.lower()}.",
        "Licensed under CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/); any ChEMBL-derived data",
        "published from this project is shared under the same licence. Mendez D, Gaulton A, Bento AP, et al.",
        "ChEMBL: towards direct deposition of bioassay data. Nucleic Acids Res. 2019;47(D1):D930-D940.",
        "doi:10.1093/nar/gky1075",
    ]
    (RESULTS / "activity_models.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    info = json.loads((PULLS / "PULL_INFO.json").read_text())
    ap = argparse.ArgumentParser(description="Train loop-1 activity models.")
    ap.add_argument("--genes", nargs="+", default=list(info["targets"]))
    genes = ap.parse_args().genes

    path = RESULTS / "activity_models.json"
    results = json.loads(path.read_text()) if path.exists() else {"genes": {}}
    trains = {}
    for gene in genes:
        t = info["targets"][gene]
        out, tr, X_tr = run_gene(gene, t["rows"])
        trains[gene] = (tr, X_tr)
        results["genes"][gene] = {"target_chembl_id": t["target_chembl_id"], **out}
        r = results["genes"][gene]
        print(f"{gene}: n_test={r['n_test']} PR-AUC lgbm={f3(r['lgbm']['pr_auc'])} rf={f3(r['rf']['pr_auc'])}")

    shipped, rf_wins = switch_rule(results["genes"])
    results.update(release=info["release"], protocol="docs/evaluation.md", lgbm_params=LGBM_PARAMS,
                   rf_params=RF_PARAMS, shipped_model=shipped, rf_pr_auc_wins=rf_wins)
    # ponytail: only this run's genes are re-saved; if the switch rule flips, re-run all genes.
    for gene in genes:
        r = results["genes"][gene]
        size = save_model(gene, shipped, info["release"], r, *trains[gene])
        r["model_file"] = {"path": f"models/{gene}.joblib", "kind": shipped, "bytes": size}
        print(f"saved models/{gene}.joblib ({shipped}, {size} bytes)")

    RESULTS.mkdir(exist_ok=True)
    path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    write_markdown(results)
    print(f"shipped={shipped} (rf won PR-AUC on {rf_wins} of {len(results['genes'])}); wrote {path}")


if __name__ == "__main__":
    main()
