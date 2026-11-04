"""Loop 2 per-drug sensitivity models on hotspot mutations (cell lines, not patients).

Rules: docs/evaluation-loop2.md, "Per-drug models". Usage:

    python -m molscreen.drugs [--drugs BRD-K... BRD-K...]

Writes results/loop2_models.json, results/loop2_models.md and models/loop2/<broad_id>.joblib. A run on some drugs
updates their entries and keeps the others already in the JSON. `predict_drugs` is what the app calls.
"""

import argparse
import json
import re
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score

from molscreen import depmap
from molscreen.split import group_split

DERIVED = depmap.RAW / "derived"
RESULTS = Path("results")
MODELS = Path("models/loop2")
# Fixed in docs/evaluation-loop2.md before any model was trained.
ONCOLOGY = [
    "EGFR", "BRAF", "ERBB2", "CDK4", "CDK6", "ALK", "ABL1", "PARP1", "BCL2", "MAP2K1", "MAP2K2", "MTOR", "PIK3CA",
    "KIT", "FLT3", "BTK", "JAK1", "JAK2", "AURKA", "AURKB", "PLK1", "TOP1", "TOP2A", "TUBB", "HDAC1", "PSMB5", "MDM2",
    "BCL2L1", "KDR", "MET", "RET", "FGFR1",
]
MIN_LINES, MAX_DRUGS, TEST_FRAC, SEED = 300, 60, 0.2, 0
SENSITIVE_PERCENTILE, UNDERPOWERED, N_BOOT = 10, 5, 1000
LR_PARAMS = {"C": 1.0, "class_weight": "balanced", "max_iter": 1000}  # sklearn's default penalty is L2
RF_PARAMS = {"n_estimators": 300, "class_weight": "balanced", "random_state": 0, "n_jobs": -1}
KINDS = ("majority", "nn1", "logreg", "rf")
NAMES = {"majority": "majority", "nn1": "1-NN", "logreg": "logistic regression", "rf": "random forest"}


def _tables(derived: Path):
    return depmap._load(str(derived))


def cell_lines(derived: Path = DERIVED) -> pd.Series:
    """Lineage of every line in PRISM, the hotspot matrix and Model.csv (with a lineage), sorted by ModelID."""
    hot, models, sens, _ = _tables(derived)
    ids = sorted(set(sens["ModelID"]) & set(hot.index))
    return models["OncotreeLineage"].reindex(ids).dropna()


@lru_cache(maxsize=4)
def lineage_split(derived: str = str(DERIVED)) -> tuple[frozenset, frozenset]:
    """(train ModelIDs, test ModelIDs): one leave-lineage-out split shared by every drug."""
    lin = cell_lines(Path(derived))
    tr, te = group_split(lin.tolist(), TEST_FRAC, SEED)
    return frozenset(lin.index[tr]), frozenset(lin.index[te])


def _candidates(derived: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Compounds naming a gene in `target` with >= 300 hotspot lines, and whether each matches the oncology list."""
    hot, _, sens, cpd = _tables(derived)
    n = sens[sens["ModelID"].isin(hot.index)].groupby("compound").size()
    c = cpd.assign(n_lines=n.reindex(cpd.index).fillna(0).astype(int)).rename_axis("compound").reset_index()
    tokens = c["target"].fillna("").str.split(r",\s*").map(lambda t: {x for x in t if x})
    keep = tokens.map(bool) & (c["n_lines"] >= MIN_LINES)
    c, tokens = c[keep], tokens[keep]
    word = re.compile(r"\b(" + "|".join(ONCOLOGY) + r")\b")
    onco = tokens.map(lambda t: bool(t & set(ONCOLOGY))) | c["moa"].fillna("").map(lambda m: bool(word.search(m)))
    return c, onco


def select_compounds(derived: Path = DERIVED) -> pd.DataFrame:
    """The drug set: a gene in `target`, >= 300 hotspot lines; if more than 60, oncology-list matches only;
    then the 60 with the most lines (ties by Broad ID)."""
    c, onco = _candidates(derived)
    if len(c) > MAX_DRUGS:
        c = c[onco]
    c = c.sort_values(["n_lines", "compound"], ascending=[False, True]).head(MAX_DRUGS)
    return c[["compound", "name", "target", "moa", "smiles", "n_lines"]].reset_index(drop=True)


def build_xy(compound: str, derived: Path = DERIVED) -> dict:
    """Features, labels and `auc` for one drug on the shared split. Threshold from training lines only."""
    hot, _, sens, _ = _tables(derived)
    train, test = lineage_split(str(derived))
    auc = sens[sens["compound"] == compound].set_index("ModelID")["auc"]
    out = {"genes": list(hot.columns)}
    for side, ids in (("tr", train), ("te", test)):
        ids = sorted(set(auc.index) & ids)
        out[f"ids_{side}"], out[f"auc_{side}"] = ids, auc[ids].to_numpy()
        out[f"X_{side}"] = hot.loc[ids].to_numpy(dtype=np.uint8)
    out["threshold"] = float(np.percentile(out["auc_tr"], SENSITIVE_PERCENTILE))
    out["y_tr"] = (out["auc_tr"] < out["threshold"]).astype(int)
    out["y_te"] = (out["auc_te"] < out["threshold"]).astype(int)
    return out


def jaccard_nn(query: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Index of the most Jaccard-similar `ref` row for each `query` row (first one on ties; empty pairs score 0)."""
    q, r = query.astype(np.float32), ref.astype(np.float32)
    inter = q @ r.T
    union = q.sum(1)[:, None] + r.sum(1)[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0).argmax(1)


def metrics(y: np.ndarray, score: np.ndarray, pred: np.ndarray, seed: int = SEED) -> dict:
    """ROC-AUC with bootstrap 95% CI, sensitive-class PR-AUC, balanced accuracy. None where y has one class."""
    if len(np.unique(y)) < 2:
        return {"roc_auc": None, "roc_auc_ci95": None, "pr_auc": None, "balanced_acc": None}
    rng, boot = np.random.default_rng(seed), []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) == 2:
            boot.append(roc_auc_score(y[i], score[i]))
    return {
        "roc_auc": float(roc_auc_score(y, score)),
        "roc_auc_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "pr_auc": float(average_precision_score(y, score)),
        "balanced_acc": float(balanced_accuracy_score(y, pred)),
    }


def fit(kind: str, X: np.ndarray, y: np.ndarray):
    model = LogisticRegression(**LR_PARAMS) if kind == "logreg" else RandomForestClassifier(**RF_PARAMS)
    return model.fit(X, y)


def evaluate(compound: str, derived: Path = DERIVED) -> tuple[dict, dict, dict]:
    """Held-out results for one drug, the fitted models and the data they were fit on."""
    d = build_xy(compound, derived)
    y_tr, y_te = d["y_tr"], d["y_te"]
    out = {
        "n_train": len(y_tr), "n_test": len(y_te), "threshold_auc": d["threshold"],
        "sensitive_train": int(y_tr.sum()), "sensitive_test": int(y_te.sum()),
        "test_prevalence": float(y_te.mean()) if len(y_te) else None,
    }
    out["underpowered"] = out["sensitive_test"] < UNDERPOWERED
    majority = int(y_tr.mean() >= 0.5)
    out["majority"] = metrics(y_te, np.full(len(y_te), float(majority)), np.full(len(y_te), majority))
    nn = jaccard_nn(d["X_te"], d["X_tr"])
    out["nn1"] = metrics(y_te, 1 - d["auc_tr"][nn], y_tr[nn])
    fitted = {}
    for kind in ("logreg", "rf"):
        # n_jobs=1 at predict: a parallel forest sums tree votes in thread order (last-digit noise)
        m = fit(kind, d["X_tr"], y_tr)
        fitted[kind] = m.set_params(n_jobs=1) if kind == "rf" else m
        p = m.predict_proba(d["X_te"])[:, 1]
        out[kind] = metrics(y_te, p, (p >= 0.5).astype(int))
    return out, fitted, d


def switch_rule(drugs: dict) -> tuple[str, int, int]:
    """Logistic regression ships unless RF has the higher ROC-AUC on more than half of the powered drugs."""
    powered = [r for r in drugs.values() if not r["underpowered"] and r["rf"]["roc_auc"] is not None]
    wins = sum(r["rf"]["roc_auc"] > r["logreg"]["roc_auc"] for r in powered)
    return ("rf" if wins > len(powered) / 2 else "logreg"), wins, len(powered)


def f3(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def ci(m: dict) -> str:
    return "n/a" if m["roc_auc"] is None else "{:.3f} ({:.3f} to {:.3f})".format(m["roc_auc"], *m["roc_auc_ci95"])


def cell(v) -> str:
    return "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v).replace("|", "/")


def write_md(res: dict, path: Path) -> None:
    g, s, k = res["drugs"], res["split"], res["shipped_model"]
    sel = res["selection"]
    rows = [
        [cell(r["name"]), b, cell(r["target"]), r["n_train"], r["n_test"], r["sensitive_test"],
         f3(r["majority"]["roc_auc"]), f3(r["nn1"]["roc_auc"]), f3(r["logreg"]["roc_auc"]), f3(r["rf"]["roc_auc"]),
         ci(r[k]), f"{f3(r[k]['pr_auc'])} vs {f3(r['test_prevalence'])}", f3(r[k]["balanced_acc"]),
         f"underpowered ({r['sensitive_test']})" if r["underpowered"] else ""]
        for b, r in g.items()
    ]
    st = res["summary"]
    lines = [
        "# Loop 2 per-drug sensitivity models: held-out results", "",
        "Built by `python -m molscreen.drugs`; every number is in `results/loop2_models.json`. Protocol:",
        "`docs/evaluation-loop2.md` (\"Per-drug models\"). **Cell lines, not patients.** Research and learning tool,",
        "not medical advice. Features: the 0/1 hotspot vector (542 genes). Label: sensitive when `auc` is below the",
        "10th percentile of the drug's `auc` over its training lines.", "",
        "## Drug set", "",
        f"{sel['candidates']:,} compounds name a gene in `target` and have >= {MIN_LINES} lines in the hotspot matrix;",
        f"{sel['oncology_matches']:,} of them match the oncology target list; the {sel['selected']} with the most lines",
        "are kept (ties by Broad ID). The table lists every trained drug with its name, Broad ID and PRISM target.", "",
        "## Split (leave-lineage-out, one split for every drug)", "",
        (f"{s['n_lines']} cell lines in {s['n_lineages']} lineages. Train: {s['n_train_lines']} lines in "
        f"{len(s['train_lineages'])} lineages. Test: {s['n_test_lines']} lines in {len(s['test_lineages'])} lineages "
        f"({', '.join(f'{x} {n}' for x, n in s['test_lineages'].items())})."), "",
        "## Results", "",
        (f"ROC-AUC 95% CI: bootstrap over the test lines ({N_BOOT} resamples, seed 0), shown for the shipped model "
        f"({NAMES[k]}). PR-AUC is for the sensitive class, next to its test prevalence (a random ranking's PR-AUC)."),
        f"Balanced accuracy at 0.5. \"Underpowered\": fewer than {UNDERPOWERED} sensitive test lines.", "",
        ("| Drug | Broad ID | Target | n train | n test | Sensitive in test | Majority | 1-NN | Logistic | RF | "
        f"{NAMES[k]} ROC-AUC (95% CI) | PR-AUC vs prevalence | Bal. acc. | Note |"),
        "|" + "---|" * 14,
        *["| " + " | ".join(str(c) for c in r) + " |" for r in rows],
        "",
        (f"**Switch rule:** the random forest had the higher held-out ROC-AUC on {res['rf_wins']} of "
         f"{res['powered_drugs']} drugs that are not underpowered (it needed more than half), so **{NAMES[k]}** "
         f"ships for every drug. Underpowered drugs: {st['underpowered']} of {len(g)}. The models are close: "
         f"median ROC-AUC {f3(st['median_logreg'])} (logistic) vs {f3(st['median_rf'])} (random forest)."),
        "",
        "## What this says", "",
        (f"Of the {st['powered']} drugs that are not underpowered, the shipped model ({NAMES[k]}) has a higher "
         f"held-out ROC-AUC than the 1-NN baseline on {st['beat_nn1']} (1-NN median {f3(st['median_nn1'])}), and its 95% CI includes 0.5 on "
         f"{st['ci_includes_half']} (no better than chance at this test size); {st['below_half']} are below 0.5. Its median ROC-AUC is "
         f"{f3(st['median_roc_auc'])} over those drugs ({f3(st['median_roc_auc_all'])} over all {len(g)}); the "
         f"highest is {f3(st['max_roc_auc'])} ({st['max_drug']}). Hotspot mutations alone explain little of how "
         "a cell line responds to most of these drugs; the models are shown as a weak, honest signal next to the "
         "measured responses of the nearest cell lines, not as a prediction for a person."),
        "",
        (f"Models: `models/loop2/<broad_id>.joblib` (git-ignored), {NAMES[k]} fit on the training lines, "
         f"{st['model_bytes']:,} bytes in total."),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def summarise(res: dict, models_dir: Path) -> dict:
    g, k = res["drugs"], res["shipped_model"]
    powered = {b: r for b, r in g.items() if not r["underpowered"] and r[k]["roc_auc"] is not None}
    aucs = [r[k]["roc_auc"] for r in powered.values()]
    every = [r[k]["roc_auc"] for r in g.values() if r[k]["roc_auc"] is not None]
    best = max(powered, key=lambda b: powered[b][k]["roc_auc"]) if powered else None
    return {
        "powered": len(powered), "underpowered": len(g) - len(powered),
        "beat_nn1": sum(r[k]["roc_auc"] > r["nn1"]["roc_auc"] for r in powered.values()),
        "below_half": sum(r[k]["roc_auc"] < 0.5 for r in powered.values()),
        "ci_includes_half": sum(r[k]["roc_auc_ci95"][0] <= 0.5 <= r[k]["roc_auc_ci95"][1] for r in powered.values()),
        "median_roc_auc": float(np.median(aucs)) if aucs else None,
        "median_logreg": float(np.median([r["logreg"]["roc_auc"] for r in powered.values()])) if powered else None,
        "median_rf": float(np.median([r["rf"]["roc_auc"] for r in powered.values()])) if powered else None,
        "median_nn1": float(np.median([r["nn1"]["roc_auc"] for r in powered.values()])) if powered else None,
        "median_roc_auc_all": float(np.median(every)) if every else None,
        "max_roc_auc": powered[best][k]["roc_auc"] if best else None,
        "max_drug": g[best]["name"] if best else None,
        "model_bytes": sum(f.stat().st_size for f in models_dir.glob("*.joblib")),
    }


def train_all(
    compounds: list[str] | None = None, derived: Path = DERIVED, results: Path = RESULTS, models_dir: Path = MODELS
) -> dict:
    """Evaluate and save the given drugs (default: the selected set), update the JSON and the Markdown."""
    sel = select_compounds(derived)
    compounds = compounds or sel["compound"].tolist()
    cpd = _tables(derived)[3]
    path = results / "loop2_models.json"
    res = json.loads(path.read_text()) if path.exists() else {"drugs": {}}
    fitted = {}
    for b in compounds:
        out, fitted[b], d = evaluate(b, derived)
        info = cpd.loc[b]
        res["drugs"][b] = {"name": info["name"], "target": info["target"], "smiles": info["smiles"], **out}
        fitted[b]["data"] = d
        print(f"{b} {info['name']}: n_test={out['n_test']} sens={out['sensitive_test']} "
              f"logreg={f3(out['logreg']['roc_auc'])} rf={f3(out['rf']['roc_auc'])}")

    shipped, wins, powered = switch_rule(res["drugs"])
    train, test = lineage_split(str(derived))
    lin = cell_lines(derived)
    cands, onco = _candidates(derived)
    res.update(
        protocol="docs/evaluation-loop2.md", lr_params=LR_PARAMS, rf_params=RF_PARAMS, n_boot=N_BOOT,
        sensitive_percentile=SENSITIVE_PERCENTILE, underpowered_below=UNDERPOWERED, oncology_list=ONCOLOGY,
        shipped_model=shipped, rf_wins=wins, powered_drugs=powered,
        selection={
            "candidates": len(cands), "oncology_matches": int(onco.sum()),
            "selected": len(sel), "compounds": sel["compound"].tolist(),
        },
        split={
            "test_frac": TEST_FRAC, "seed": SEED, "n_lines": len(lin), "n_lineages": int(lin.nunique()),
            "n_train_lines": len(train), "n_test_lines": len(test),
            "train_lineages": lin[lin.index.isin(train)].value_counts().to_dict(),
            "test_lineages": lin[lin.index.isin(test)].value_counts().to_dict(),
        },
    )
    # ponytail: only this run's drugs are re-saved; if the switch rule flips, re-run all drugs.
    models_dir.mkdir(parents=True, exist_ok=True)
    for b in compounds:
        r, d = res["drugs"][b], fitted[b]["data"]
        joblib.dump({
            "compound": b, "name": r["name"], "target": r["target"], "smiles": r["smiles"], "kind": shipped,
            "model": fitted[b][shipped], "genes": d["genes"],
            "train_genes": sorted(np.array(d["genes"])[d["X_tr"].any(axis=0)]),
            "threshold_auc": r["threshold_auc"], "roc_auc": r[shipped]["roc_auc"],
            "roc_auc_ci95": r[shipped]["roc_auc_ci95"], "underpowered": r["underpowered"],
        }, models_dir / f"{b}.joblib", compress=3)
        r["model_file"] = {"path": f"{models_dir.as_posix()}/{b}.joblib", "kind": shipped,
                           "bytes": (models_dir / f"{b}.joblib").stat().st_size}
    res["summary"] = summarise(res, models_dir)
    results.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    write_md(res, results / "loop2_models.md")
    _load_models.cache_clear()
    return res


@lru_cache(maxsize=4)
def _load_models(models_dir: str) -> list[dict]:
    return [joblib.load(f) for f in sorted(Path(models_dir).glob("*.joblib"))]


def predict_drugs(genes: list[str], models_dir: Path = MODELS) -> list[dict]:
    """P(sensitive) from every shipped drug model for a cell line with these hotspot genes, highest first.

    A model abstains (is left out) when no listed gene is mutated in any of its training lines; an empty list
    means every model abstained and the app must show no prediction. Cell lines, not patients.
    """
    query = {g.strip().upper() for g in genes}
    out = []
    for m in _load_models(str(models_dir)):
        if not query & set(m["train_genes"]):
            continue
        x = np.isin(m["genes"], list(query)).astype(np.uint8)[None, :]
        out.append({
            "compound": m["compound"], "name": m["name"], "target": m["target"], "smiles": m["smiles"],
            "p_sensitive": float(m["model"].predict_proba(x)[0, 1]), "model": m["kind"],
            "roc_auc": m["roc_auc"], "roc_auc_ci95": m["roc_auc_ci95"], "underpowered": m["underpowered"],
        })
    return sorted(out, key=lambda r: (-r["p_sensitive"], r["name"]))


def main() -> None:
    ap = argparse.ArgumentParser(description="Train loop-2 per-drug sensitivity models.")
    ap.add_argument("--drugs", nargs="+", help="Broad IDs (BRD-K...); default: the selected drug set")
    res = train_all(ap.parse_args().drugs)
    s = res["summary"]
    print(f"shipped={res['shipped_model']} (rf won ROC-AUC on {res['rf_wins']} of {res['powered_drugs']}); "
          f"median ROC-AUC {f3(s['median_roc_auc'])}; beat 1-NN {s['beat_nn1']} of {s['powered']}; "
          f"underpowered {s['underpowered']}; models {s['model_bytes']:,} bytes")


if __name__ == "__main__":
    main()
