"""Train and evaluate the per-target activity models exactly as docs/evaluation.md says.

Usage: uv run python -m molscreen.train [--genes CDK6 EGFR]
Writes results/activity_models.json, results/activity_models.md, results/datasets.md, data/datasets/<GENE>.csv
and models/<GENE>.joblib. A run on some genes updates their entries and keeps the others already in the JSON.
"""

import argparse
import json

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from rdkit import Chem
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score

from molscreen.chem import morgan_fp, murcko_scaffold, scaffold_split
from molscreen.data import PULLS, ROOT, aggregate, filter_activities, save_dataset

RESULTS = ROOT / "results"
MODELS = ROOT / "models"
RADIUS, N_BITS = 2, 2048
ABSTAIN_PERCENTILE = 5
UNDERPOWERED_INACTIVES = 50  # reporting only: a test set with fewer inactives is flagged "underpowered"
N_BOOT = 1000
# Fixed before seeing any result and not tuned (no inner split was used). They were first committed with the
# results (4c71e50), not with the protocol (1cc2650); see docs/evaluation.md.
LGBM_PARAMS = {
    "n_estimators": 500, "learning_rate": 0.05, "num_leaves": 31, "min_child_samples": 10, "subsample": 0.8,
    "subsample_freq": 1, "colsample_bytree": 0.5, "random_state": 0, "deterministic": True, "force_col_wise": True,
    "n_jobs": 4, "verbose": -1,
}
RF_PARAMS = {"n_estimators": 500, "random_state": 0, "n_jobs": -1}
# First run, before the 2026-11-04 amendment (git 4c71e50, results/activity_models.json):
# gene -> (molecules, random forest ROC-AUC, LightGBM ROC-AUC).
FIRST_RUN = {
    "EGFR": (11023, 0.8766, 0.8503), "BRAF": (5381, 0.8703, 0.8764), "ERBB2": (2560, 0.8805, 0.8696),
    "CDK4": (1404, 0.8862, 0.8789), "CDK6": (821, 0.9015, 0.7704), "ALK": (2476, 0.9076, 0.8915),
    "ABL1": (3038, 0.8554, 0.8367), "PARP1": (4510, 0.9, 0.8976), "BCL2": (3142, 0.9619, 0.9634),
}
NAMES = {"lgbm": "LightGBM", "rf": "random forest", "nn1": "1-NN", "majority": "majority"}
KINDS = ("majority", "nn1", "rf", "lgbm")


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
    """ROC-AUC, PR-AUC with active and with inactive as the positive class, balanced accuracy.
    All None if `y` has one class."""
    two = len(np.unique(y)) == 2
    return {
        "roc_auc": float(roc_auc_score(y, score)) if two else None,
        "pr_auc": float(average_precision_score(y, score)) if two else None,
        "pr_auc_inactive": float(average_precision_score(1 - y, -score)) if two else None,
        "balanced_acc": float(balanced_accuracy_score(y, pred)) if two else None,
    }


def roc_auc_ci(y: np.ndarray, score: np.ndarray, n: int = N_BOOT, seed: int = 0) -> list[float]:
    """Bootstrap 95% interval of ROC-AUC over `n` resamples of the test set (one-class resamples skipped)."""
    rng = np.random.default_rng(seed)
    aucs = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) == 2:
            aucs.append(roc_auc_score(y[i], score[i]))
    return [float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))]


def fit(kind: str, X: np.ndarray, y: np.ndarray):
    model = LGBMClassifier(**LGBM_PARAMS) if kind == "lgbm" else RandomForestClassifier(**RF_PARAMS)
    return model.fit(X, y)


def split(ds):
    train, test = scaffold_split(ds["smiles"].tolist(), test_frac=0.2, seed=0)
    return ds.iloc[train].reset_index(drop=True), ds.iloc[test].reset_index(drop=True)


def dataset_stats(acts: pd.DataFrame, rows: pd.DataFrame, ds: pd.DataFrame) -> dict:
    # rows that pass every other rule but come from an assay declaring a protein variant
    mutant = len(filter_activities(acts.assign(assay_variant_mutation=None))) - len(rows)
    flat = ds["smiles"].map(lambda s: Chem.MolToSmiles(Chem.MolFromSmiles(s), isomericSmiles=False))
    return {
        "rows_pulled": len(acts), "rows_mutant_dropped": mutant, "rows_kept": len(rows),
        "chembl_ids": int(rows["molecule_chembl_id"].nunique()), "molecules": len(ds),
        "ids_collapsed": int(rows["molecule_chembl_id"].nunique() - len(ds)),
        "actives": int(ds["active"].sum()), "active_frac": float(ds["active"].mean()),
        "scaffolds": len({murcko_scaffold(s) for s in ds["smiles"]}),
        "rows_by_type": {t: int((rows["standard_type"] == t).sum()) for t in ("IC50", "Ki", "EC50")},
        "rows_functional": int((rows["assay_type"] == "F").sum()),
        "molecules_stereo_siblings": int(flat.duplicated(keep=False).sum()),
    }


def run_gene(gene: str):
    """Held-out results for one target, plus the train split and its fingerprints (for the saved model)."""
    acts = pd.read_csv(PULLS / f"{gene}.csv")
    rows = filter_activities(acts)
    ds = aggregate(rows)
    save_dataset(gene, ds)
    tr, te = split(ds)
    X_tr, X_te = fingerprints(tr["smiles"].tolist()), fingerprints(te["smiles"].tolist())
    y_tr, y_te = tr["active"].to_numpy(), te["active"].to_numpy()
    if len(np.unique(y_tr)) < 2:
        raise ValueError(f"{gene}: train set has one class only")

    out = {
        "dataset": dataset_stats(acts, rows, ds),
        "n_train": len(tr), "n_test": len(te), "test_active_frac": float(y_te.mean()),
        "test_inactives": int((y_te == 0).sum()),
    }
    majority = int(y_tr.mean() >= 0.5)
    out["majority"] = metrics(y_te, np.full(len(te), float(majority)), np.full(len(te), majority))
    sim, nn = max_tanimoto(X_te, X_tr)
    out["nn1"] = metrics(y_te, tr["pchembl"].to_numpy()[nn], y_tr[nn])

    cutoff = abstain_cutoff(X_tr)
    kept = sim >= cutoff
    out["abstain"] = {"cutoff": cutoff, "n_test_abstain": int((~kept).sum()), "n_test_kept": int(kept.sum())}
    for kind in ("rf", "lgbm"):
        # n_jobs=1 at predict: a parallel forest sums tree votes in thread order, which moves PR-AUC at 1e-8
        p = fit(kind, X_tr, y_tr).set_params(n_jobs=1).predict_proba(X_te)[:, 1]
        out[kind] = metrics(y_te, p, (p >= 0.5).astype(int))
        out[kind]["roc_auc_kept"] = metrics(y_te[kept], p[kept], (p[kept] >= 0.5).astype(int))["roc_auc"]
        out[kind]["roc_auc_ci95"] = roc_auc_ci(y_te, p)
    return out, tr, X_tr


def switch_rule(genes: dict) -> tuple[str, int]:
    """LightGBM ships unless RF has the higher held-out PR-AUC (active class) on at least 6 targets."""
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
        "train": tr[["smiles", "molecule_chembl_ids", "pchembl", "active"]],
        "abstain_cutoff": res["abstain"]["cutoff"], "metrics": res,
    }, path, compress=3)
    return path.stat().st_size


def f3(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%"


def table(header: list[str], rows: list[list]) -> list[str]:
    head = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return head + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]


def write_datasets_md(results: dict) -> None:
    g = results["genes"]
    lines = [
        "# Activity datasets (loop 1)", "",
        f"From `uv run python -m molscreen.train` on ChEMBL pulls ({results['release']}). Numbers are in",
        "`results/activity_models.json` under `genes.<GENE>.dataset`. Rules: `docs/evaluation.md` and its",
        "2026-11-04 amendment. Mutant rows dropped = rows that pass every other rule but whose assay declares a",
        "protein variant (`assay_variant_mutation`). IDs collapsed = ChEMBL IDs in the kept rows minus parent molecules",
        "(salts stripped to the largest fragment, stereo kept).", "",
        *table(
            ["Gene", "Rows pulled", "Mutant rows dropped", "Rows kept", "ChEMBL IDs", "Parent molecules",
             "IDs collapsed", "Actives", "Active fraction", "Train", "Test", "Scaffolds"],
            [[gene, d["rows_pulled"], d["rows_mutant_dropped"], d["rows_kept"], d["chembl_ids"], d["molecules"],
              d["ids_collapsed"], d["actives"], f"{d['active_frac']:.3f}", r["n_train"], r["n_test"],
              d["scaffolds"]] for gene, r in g.items() for d in [r["dataset"]]],
        ),
    ]
    (RESULTS / "datasets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_models_md(results: dict) -> None:
    g, rel, low = results["genes"], results["release"], results["underpowered_inactives"]
    shipped, rf_wins = results["shipped_model"], results["rf_pr_auc_wins"]
    sname = NAMES[shipped]
    fr = [r["test_active_frac"] for r in g.values()]

    def note(r):
        return f"underpowered: {r['test_inactives']} test inactives" if r["test_inactives"] < low else ""

    def margin(r):
        return r["rf"]["pr_auc"] - r["lgbm"]["pr_auc"]

    def ci(r):
        return "{:.3f} to {:.3f}".format(*r[shipped]["roc_auc_ci95"])

    def per_model(metric):
        return [[gene, *(f3(r[k][metric]) for k in KINDS), note(r)] for gene, r in g.items()]

    lines = [
        "# Activity models (loop 1): held-out results", "",
        f"Scaffold-split held-out test sets, ChEMBL release {rel}, protocol `docs/evaluation.md` with its",
        "2026-11-04 amendments (wild-type assays only, salts stripped to the parent; extra reporting).",
        "All numbers come from `results/activity_models.json`, written by `uv run python -m molscreen.train`.",
        "Morgan fingerprints (radius 2, 2048 bits). Model parameters are fixed in `src/molscreen/train.py`; nothing",
        "was tuned, so no inner split was used. Every metric below is on the held-out test set.",
        f"**Shipped model: {sname}.** \"Underpowered\" marks a target with fewer than {low} inactive molecules",
        "in its test set: its AUCs can move a lot with a few molecules.", "",
        "## Headline: shipped model against the baselines", "",
        f"ROC-AUC 95% CI: bootstrap over the test set ({results['n_boot']} resamples, seed 0). The random value of",
        "inactive-class PR-AUC is the test inactive fraction. Balanced accuracy uses a 0.5 threshold (1-NN: its",
        "neighbour's label). Active-class PR-AUC comes last because a random ranking already scores the test",
        f"active fraction there ({min(fr):.2f} to {max(fr):.2f} here), so high values are expected.", "",
        *table(
            ["Gene", "n train", "n test", "Test inactives", f"ROC-AUC {sname} (95% CI)", "ROC-AUC 1-NN",
             f"Inactive PR-AUC {sname}", "Inactive PR-AUC random", f"Bal. acc. {sname}", "Bal. acc. 1-NN",
             f"Active PR-AUC {sname}", "Active PR-AUC random", "Note"],
            [[gene, r["n_train"], r["n_test"], r["test_inactives"], f"{f3(r[shipped]['roc_auc'])} ({ci(r)})",
              f3(r["nn1"]["roc_auc"]), f3(r[shipped]["pr_auc_inactive"]), f"{1 - r['test_active_frac']:.3f}",
              f3(r[shipped]["balanced_acc"]), f3(r["nn1"]["balanced_acc"]), f3(r[shipped]["pr_auc"]),
              f"{r['test_active_frac']:.3f}", note(r)] for gene, r in g.items()],
        ),
        "", "## All models", "", "### ROC-AUC", "",
        *table(["Gene", "Majority", "1-NN", "Random forest", "LightGBM", "Note"], per_model("roc_auc")),
        "", "### PR-AUC, inactive as the positive class", "",
        *table(["Gene", "Random", "Majority", "1-NN", "Random forest", "LightGBM", "Note"],
               [[gene, f"{1 - r['test_active_frac']:.3f}", *row[1:]]
                for (gene, r), row in zip(g.items(), per_model("pr_auc_inactive"))]),
        "", "### Balanced accuracy at 0.5", "",
        *table(["Gene", "Majority", "1-NN", "Random forest", "LightGBM", "Note"], per_model("balanced_acc")),
    ]
    def vs_nn(metric: str, label: str) -> str:
        below = [(gene, r) for gene, r in g.items() if r["rf"][metric] < r["nn1"][metric]]
        detail = ", ".join(f"{gene} {r['rf'][metric]:.3f} vs {r['nn1'][metric]:.3f}" for gene, r in below)
        return f"- {label}: below 1-NN on {len(below)} of {len(g)} targets" + (f" ({detail})." if below else ".")

    lines += [
        "", "### Random forest against 1-NN, per metric", "",
        vs_nn("roc_auc", "ROC-AUC"),
        vs_nn("pr_auc_inactive", "PR-AUC, inactive class"),
        vs_nn("balanced_acc", "Balanced accuracy at 0.5"),
        vs_nn("pr_auc", "PR-AUC, active class"),
        "",
        "### PR-AUC, active as the positive class (the switch rule's metric)", "",
        "A random ranking scores the test active fraction here.", "",
        *table(["Gene", "Random", "Majority", "1-NN", "Random forest", "LightGBM", "RF - LightGBM", "Note"],
               [[gene, f"{r['test_active_frac']:.3f}", *row[1:-1], f"{margin(r):+.4f}", row[-1]]
                for (gene, r), row in zip(g.items(), per_model("pr_auc"))]),
        "",
        (f"Switch rule (re-applied after the amendment): the random forest had the higher active-class PR-AUC on "
        f"{rf_wins} of {len(g)} targets (it needs at least 6), so **{sname}** ships for every target. In the "
        "first run (4c71e50) the count was 7 of 9, also the random forest."),
    ]
    for gene, r in g.items():
        if r["test_inactives"] < low:
            lines.append(f"{gene} is underpowered: its RF-vs-LightGBM PR-AUC margin ({margin(r):+.4f}) rests on "
                         f"{r['test_inactives']} test inactives.")

    ab = {gene: r["abstain"]["n_test_abstain"] / r["n_test"] for gene, r in g.items()}
    lo, hi = min(ab, key=ab.get), max(ab, key=ab.get)
    lines += [
        "", "## Abstain", "",
        "Held-out abstain = held-out molecules whose max Tanimoto to train is below the cut-off. AUC kept = the",
        "shipped model's ROC-AUC on the other, non-abstained molecules (the ones closer to train).", "",
        *table(["Gene", "Abstain cut-off", "Held-out abstain", f"ROC-AUC {sname}, all", "AUC kept"],
               [[gene, f"{r['abstain']['cutoff']:.3f}", f"{r['abstain']['n_test_abstain']} of {r['n_test']}",
                 f3(r[shipped]["roc_auc"]), f3(r[shipped]["roc_auc_kept"])] for gene, r in g.items()]),
        "", "## What changed from the first run", "",
        "Before = commit 4c71e50 (all assays incl. mutant, one molecule per ChEMBL ID). After = this run",
        "(wild-type assays only, salts stripped to the parent). ROC-AUC on each run's own held-out set; the",
        "held-out sets differ: the split is recomputed on the new molecule list, and scaffold groups of equal size",
        "can land on the other side, so even a target with the same molecules (CDK6, BCL2) gets a new test set.", "",
        *table(["Gene", "Molecules before", "Molecules after", "RF ROC-AUC before", "RF ROC-AUC after",
                "LightGBM ROC-AUC before", "LightGBM ROC-AUC after"],
               [[gene, b[0], r["dataset"]["molecules"], f"{b[1]:.3f}", f3(r["rf"]["roc_auc"]), f"{b[2]:.3f}",
                 f3(r["lgbm"]["roc_auc"])] for gene, r in g.items() for b in [FIRST_RUN[gene]]]),
    ]

    d = {gene: r["dataset"] for gene, r in g.items()}
    kept = sum(x["rows_kept"] for x in d.values())
    types = {t: sum(x["rows_by_type"][t] for x in d.values()) for t in ("IC50", "Ki", "EC50")}
    act = [x["active_frac"] for x in d.values()]
    rises = sum(r[shipped]["roc_auc_kept"] > r[shipped]["roc_auc"] for r in g.values())
    lines += [
        "", "## Known limits", "",
        f"- **Measurement types and assay types are pooled.** Of the {kept} kept rows: "
        + ", ".join(f"{t} {pct(n, kept)}" for t, n in types.items()) + ". Functional (F) assays, the rest binding (B): "
        + ", ".join(f"{gene} {pct(x['rows_functional'], x['rows_kept'])}" for gene, x in d.items()) + " of kept rows.",
        "- **Wild type only, as far as ChEMBL says.** Rows from assays declaring a variant were dropped ("
        + ", ".join(f"{gene} {pct(x['rows_mutant_dropped'], x['rows_kept'] + x['rows_mutant_dropped'])}"
                    for gene, x in d.items())
        + " of the rows that pass every other rule). An assay on a mutant protein that does not declare it is still in (inferred risk).",
        (f"- **The abstain rule holds back {100 * ab[lo]:.0f}% ({lo}) to {100 * ab[hi]:.0f}% ({hi}) of held-out "
        "molecules**: a scaffold split makes held-out molecules unlike train by design."),
        "- **Stereoisomers stay separate training points, and charged salt forms are not neutralised.** Parent "
        "molecules that share a structure once stereo is removed: "
        + ", ".join(f"{gene} {x['molecules_stereo_siblings']} of {x['molecules']}" for gene, x in d.items()) + ".",
        (f"- **The active rate ({100 * min(act):.0f}% to {100 * max(act):.0f}% of molecules) reflects what gets "
        "published** (mostly optimised series), not a screening library, so these numbers do not predict real hit "
        "rates."),
        (f"- **AUC kept is measured on the non-abstained subset, closer to train and usually easier**; it is above the all-molecule ROC-AUC on "
        f"{rises} of {len(g)} targets. Quote the all-molecule ROC-AUC as the headline."),
        "", "## Credits", "",
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
        out, tr, X_tr = run_gene(gene)
        trains[gene] = (tr, X_tr)
        results["genes"][gene] = r = {"target_chembl_id": info["targets"][gene]["target_chembl_id"], **out}
        print(f"{gene}: n_test={r['n_test']} PR-AUC lgbm={f3(r['lgbm']['pr_auc'])} rf={f3(r['rf']['pr_auc'])}")

    shipped, rf_wins = switch_rule(results["genes"])
    results.update(
        release=info["release"], protocol="docs/evaluation.md", lgbm_params=LGBM_PARAMS, rf_params=RF_PARAMS,
        shipped_model=shipped, rf_pr_auc_wins=rf_wins, n_boot=N_BOOT, underpowered_inactives=UNDERPOWERED_INACTIVES,
        first_run={"commit": "4c71e50", "molecules_rf_roc_auc_lgbm_roc_auc": FIRST_RUN},
    )
    # ponytail: only this run's genes are re-saved; if the switch rule flips, re-run all genes.
    for gene in genes:
        r = results["genes"][gene]
        size = save_model(gene, shipped, info["release"], r, *trains[gene])
        r["model_file"] = {"path": f"models/{gene}.joblib", "kind": shipped, "bytes": size}
        print(f"saved models/{gene}.joblib ({shipped}, {size} bytes)")

    RESULTS.mkdir(exist_ok=True)
    path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    write_datasets_md(results)
    write_models_md(results)
    print(f"shipped={shipped} (rf won PR-AUC on {rf_wins} of {len(results['genes'])}); wrote {path}")


if __name__ == "__main__":
    main()
