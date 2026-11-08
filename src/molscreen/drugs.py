"""Loop 2 per-drug sensitivity models on hotspot mutations (cell lines, not patients).

Rules: docs/evaluation-loop2.md, "Per-drug models". Usage:

    python -m molscreen.drugs [--drugs BRD-K... BRD-K...]

Writes results/loop2_models.json, results/loop2_models.md and models/loop2/<broad_id>.joblib. A run on some drugs
updates their entries and keeps the others already in the JSON. `predict_drugs` is what the app calls.
"""

import argparse
import json
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
MIN_LINES, PER_TARGET, TEST_FRAC, SEED = 300, 3, 0.2, 0
SENSITIVE_PERCENTILE, UNDERPOWERED, N_BOOT = 10, 5, 1000
LR_PARAMS = {"C": 1.0, "class_weight": "balanced", "max_iter": 1000}  # sklearn's default penalty is L2
RF_PARAMS = {"n_estimators": 300, "class_weight": "balanced", "random_state": 0, "n_jobs": -1}
# Amendment 2026-11-04 (Prakhar, FIX round 1): logistic regression ships whatever the switch rule says; the switch
# rule is still computed and reported. See docs/evaluation-loop2.md, Changes.
SHIPPED = "logreg"
# Earlier runs, from their committed results/loop2_models.json. Medians and beat-1-NN over drugs that are not
# underpowered (all of them in both runs); weak = CI lower bound <= 0.5, over all drugs.
EARLIER_RUNS = [
    {   # first run: the 60 oncology-list matches with the most lines; random forest shipped by the switch rule
        "label": "First run", "commit": "5b7d361", "drugs": 60, "underpowered": 0, "rf_wins": 32,
        "powered_drugs": 60, "shipped": "rf",
        "median_roc_auc": {"majority": 0.5, "nn1": 0.5072, "logreg": 0.5492, "rf": 0.5623},
        "beat_nn1": {"logreg": 40, "rf": 40}, "weak": {"logreg": 51, "rf": 53}, "model_bytes": 73143794,
    },
    {   # FIX round 1: up to 3 per oncology gene (first-listed gene); logistic regression ships by amendment
        "label": "FIX round 1", "commit": "71dc695", "drugs": 86, "underpowered": 0, "rf_wins": 40,
        "powered_drugs": 86, "shipped": "logreg",
        "median_roc_auc": {"majority": 0.5, "nn1": 0.5181, "logreg": 0.5452, "rf": 0.5402},
        "beat_nn1": {"logreg": 55, "rf": 54}, "weak": {"logreg": 65, "rf": 73}, "model_bytes": 675367,
    },
]
# Reporting text for results/loop2_models.md (Prakhar, 2026-11-04: keep all selective picks and disclose them).
KNOWN_LIMITS = (
    "Some selective picks come from PRISM's target annotations, not from any oncology judgement: antibiotics "
    "(norfloxacin, sparfloxacin and trovafloxacin under TOP2A), the fungicide thiram (JAK2), anthelmintics "
    "(fenbendazole and parbendazole under TUBB) and natural products (oridonin under BCL2, nobiletin under MAP2K1, "
    "parthenolide under HDAC1). They are kept, and the app shows them like any other drug; the nearest cell lines "
    "and their measured sensitivities remain the main evidence. Vemurafenib is absent because PRISM lists it with "
    "two targets (BRAF, RAF1), so it is not selective, and it is 4th by screened lines for BRAF, after the 3 kept."
)
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


def _candidates(derived: Path) -> pd.DataFrame:
    """Compounds naming a gene in `target` with >= 300 lines in the hotspot matrix, with their line count."""
    hot, _, sens, cpd = _tables(derived)
    n = sens[sens["ModelID"].isin(hot.index)].groupby("compound").size()
    c = cpd.assign(n_lines=n.reindex(cpd.index).fillna(0).astype(int)).rename_axis("compound").reset_index()
    has_gene = c["target"].fillna("").str.split(r",\s*").map(lambda t: any(t))
    return c[has_gene & (c["n_lines"] >= MIN_LINES)]


def oncology_genes(target) -> list[str]:
    """The oncology-list genes that `target` names, in list order."""
    tokens = set(str(target).split(", ")) if isinstance(target, str) else set()
    return [g for g in ONCOLOGY if g in tokens]


def oncology_gene(target) -> str | None:
    """The first gene of the oncology list (in list order) that `target` names, or None."""
    return next(iter(oncology_genes(target)), None)


def pick_per_target(c: pd.DataFrame) -> pd.DataFrame:
    """Up to 3 compounds per oncology gene. Compounds are taken most screened first (ties by Broad ID); each goes,
    once, to the oncology gene its `target` names that has the fewest compounds so far (ties by list order), and is
    skipped when that gene already has 3 (amended 2026-11-04, FIX round 2; was: the first-listed gene)."""
    count, rows = dict.fromkeys(ONCOLOGY, 0), []
    for r in c.sort_values(["n_lines", "compound"], ascending=[False, True]).to_dict("records"):
        genes = oncology_genes(r["target"])
        if not genes:
            continue
        g = min(genes, key=lambda x: (count[x], ONCOLOGY.index(x)))
        if count[g] < PER_TARGET:
            count[g] += 1
            rows.append(r | {"oncology_gene": g, "first_gene": genes[0]})
    return pd.DataFrame(rows, columns=[*c.columns, "oncology_gene", "first_gene"])


def pick_selective(c: pd.DataFrame) -> pd.DataFrame:
    """Selective drugs: `target` names exactly one gene and that gene is on the oncology list (FIX round 2)."""
    tokens = c["target"].fillna("").str.split(r",\s*").map(lambda t: [x for x in t if x])
    one = tokens.map(lambda t: len(t) == 1 and t[0] in ONCOLOGY)
    return c[one].assign(oncology_gene=tokens[one].str[0], first_gene=tokens[one].str[0])


def pick_drug_set(c: pd.DataFrame) -> pd.DataFrame:
    """3 per oncology gene, plus every selective drug not already in; each compound once. Sorted by gene."""
    per_gene = pick_per_target(c).assign(rule="3 per gene")
    selective = pick_selective(c)
    selective = selective[~selective["compound"].isin(per_gene["compound"])].assign(rule="selective")
    out = pd.concat([per_gene, selective], ignore_index=True)
    out = out.assign(order=out["oncology_gene"].map(ONCOLOGY.index), r=out["rule"].ne("3 per gene"))
    out = out.sort_values(["order", "r", "n_lines", "compound"], ascending=[True, True, False, True])
    return out.drop(columns=["order", "r"]).reset_index(drop=True)


def select_compounds(derived: Path = DERIVED) -> pd.DataFrame:
    """The drug set (amended 2026-11-04, FIX rounds 1 and 2): a gene in `target`, >= 300 hotspot lines; up to 3
    per oncology gene, plus every selective drug (one target gene, on the oncology list)."""
    c = pick_drug_set(_candidates(derived))
    return c[["compound", "name", "target", "moa", "smiles", "n_lines", "oncology_gene", "first_gene", "rule"]]


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
    g, s, k, sel, st = res["drugs"], res["split"], res["shipped_model"], res["selection"], res["summary"]
    runs, med = res["earlier_runs"], st["median_roc_auc"]
    first = runs[0]
    rows = [
        [cell(r["name"]), b, cell(r["target"]), f"{r['oncology_gene']} ({r['rule']})", r["n_train"], r["n_test"], r["sensitive_test"],
         f3(r["majority"]["roc_auc"]), f3(r["nn1"]["roc_auc"]), ci(r["logreg"]), ci(r["rf"]),
         f"{f3(r[k]['pr_auc'])} vs {f3(r['test_prevalence'])}", f3(r[k]["balanced_acc"]),
         "; ".join(x for x in ["weak" if weak(r[k]) else "",
                               f"underpowered ({r['sensitive_test']})" if r["underpowered"] else ""] if x)]
        for b, r in g.items()
    ]

    this = {**st, "commit": "this run", "label": "FIX round 2", "rf_wins": res["rf_wins"],
            "powered_drugs": res["powered_drugs"], "shipped": k}
    added = sel["selective_added"]

    def change(label, key):
        return f"| {label} | " + " | ".join(str(key(x)) for x in [*runs, this]) + " |"

    lines = [
        "# Loop 2 per-drug sensitivity models: held-out results", "",
        "Built by `python -m molscreen.drugs`; every number is in `results/loop2_models.json`. Protocol:",
        "`docs/evaluation-loop2.md` (\"Per-drug models\" and its dated Changes). **Cell lines, not patients.**",
        "Research and learning tool, not medical advice. Features: the 0/1 hotspot vector (542 genes). Label: sensitive",
        "when `auc` is below the 10th percentile of the drug's `auc` over its training lines.", "",
        ("**How the app uses this.** The nearest cell lines and their measured sensitivities are the main evidence in "
         "loop 2; model ranks are shown second and greyed when `weak` (95% CI lower bound <= 0.5); the probabilities "
         "are not calibrated and must be shown as ranks, never as percentages."), "",
        "## Drug set", "",
        (f"{sel['candidates']:,} compounds name a gene in `target` and have >= {MIN_LINES} lines in the hotspot "
         f"matrix. Two rules pick from them (each compound counts once). **3 per gene:** compounds are taken most "
         f"screened first (ties by Broad ID); each goes to the oncology-list gene its `target` names that has the "
         f"fewest compounds so far (ties by list order), while that gene has fewer than {sel['per_target']}. "
         f"{sel['reassigned']} of the {sel['by_rule'].get('3 per gene', 0)} compounds picked this way went to a gene "
         f"other than the first one they name in list order (the FIX round 1 assignment). **Selective:** every other "
         f"candidate whose `target` names exactly one gene, on the oncology list: {len(added)} added. "
         f"{sel['genes_with_compounds']} genes have at least one compound, giving **{sel['selected']} compounds**. "
         "The \"Gene\" column is the gene and rule a compound was picked under."), "",
        "Selective drugs added: " + (", ".join(
            f"{cell(a['name'])} ({cell(a['target'])}, {a['n_lines']} lines)" for a in added) or "none") + ".", "",
        "## Split (leave-lineage-out, one split for every drug)", "",
        (f"{s['n_lines']} cell lines in {s['n_lineages']} lineages. Train: {s['n_train_lines']} lines in "
         f"{len(s['train_lineages'])} lineages. Test: {s['n_test_lines']} lines in {len(s['test_lineages'])} lineages "
         f"({', '.join(f'{x} {n}' for x, n in s['test_lineages'].items())})."), "",
        "## Results", "",
        (f"ROC-AUC with its 95% CI: bootstrap over the test lines ({N_BOOT} resamples, seed 0). PR-AUC (sensitive "
         f"class, next to its test prevalence = a random ranking's PR-AUC) and balanced accuracy at 0.5 are for the "
         f"shipped model ({NAMES[k]}). \"Weak\": the shipped model's CI lower bound is <= 0.5. \"Underpowered\": "
         f"fewer than {UNDERPOWERED} sensitive test lines."), "",
        ("| Drug | Broad ID | Target | Gene | n train | n test | Sensitive in test | Majority | 1-NN | "
         "Logistic (95% CI) | RF (95% CI) | PR-AUC vs prevalence | Bal. acc. | Note |"),
        "|" + "---|" * 14,
        *["| " + " | ".join(str(c) for c in r) + " |" for r in rows],
        "",
        (f"**Which model ships:** the pre-registered switch rule, re-applied for the record, gives the random forest the "
         f"higher held-out ROC-AUC on {res['rf_wins']} of {res['powered_drugs']} drugs that are not underpowered (it "
         f"needs more than half), so the rule alone would ship the "
         f"{NAMES[res['switch_rule_model']]}. **By the 2026-11-04 amendment, {NAMES[k]} ships for every drug**: the "
         f"first run's random-forest win (32 of 60) was a tie-sized margin, and the hosted app's size matters (the "
         f"first run's 60 random forests took {first['model_bytes']:,} bytes). Random-forest results stay in every table. "
         f"Underpowered drugs: {st['underpowered']} of {st['drugs']}."),
        "",
        "## What this says", "",
        (f"Over the {st['powered']} drugs that are not underpowered: median held-out ROC-AUC {f3(med['logreg'])} "
         f"(logistic), {f3(med['rf'])} (random forest), {f3(med['nn1'])} (1-NN). Logistic regression beats 1-NN on "
         f"{st['beat_nn1']['logreg']} drugs; the random forest beats 1-NN on {st['beat_nn1']['rf']}. "
         f"{st['below_half']} of those {st['powered']} are below 0.5, and the highest is {f3(st['max_roc_auc'])} "
         f"({st['max_drug']}). Counting every drug instead, including the underpowered ones, {st['weak'][k]} of "
         f"{st['drugs']} shipped models are weak, meaning the 95% CI lower bound is at or below 0.5 so the model is "
         f"not shown to beat chance. Hotspot mutations alone explain little of how a cell line "
         "responds to most of these drugs; the models are a weak signal next to the measured responses of the nearest "
         "cell lines, not a prediction for a person."),
        "",
        "## Known limits", "",
        KNOWN_LIMITS, "",
        "## What changed between runs", "",
        ("First run = commit 5b7d361 (the 60 oncology-list matches with the most lines; random forest shipped by "
         "the switch rule). FIX round 1 = commit 71dc695 (up to 3 per oncology gene, first-listed gene; logistic "
         "regression ships by amendment). FIX round 2 = this run (3 per gene with the fewest-so-far assignment, plus "
         "selective drugs). Same split, seed and model parameters. Medians and beat-1-NN are over drugs that are not "
         "underpowered; weak counts all drugs."), "",
        "| | " + " | ".join(f"{x['label']} ({x['commit']})" for x in [*runs, this]) + " |",
        "|---|" + "---|" * (len(runs) + 1),
        change("Drugs", lambda x: x["drugs"]),
        change("Underpowered", lambda x: x["underpowered"]),
        *[change(f"Median ROC-AUC, {NAMES[m]}", lambda x, m=m: f3(x["median_roc_auc"][m])) for m in KINDS],
        *[change(f"Beats 1-NN, {NAMES[m]}", lambda x, m=m: x["beat_nn1"][m]) for m in ("logreg", "rf")],
        *[change(f"Weak, {NAMES[m]}", lambda x, m=m: x["weak"][m]) for m in ("logreg", "rf")],
        change("Switch rule: RF wins", lambda x: f"{x['rf_wins']} of {x['powered_drugs']}"),
        change("Shipped", lambda x: NAMES[x["shipped"]]),
        change("Model bytes", lambda x: f"{x['model_bytes']:,}"),
        "",
        (f"Models: `models/loop2/<broad_id>.joblib` (git-ignored), {NAMES[k]} fit on the training lines, "
         f"{st['model_bytes']:,} bytes in total."),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def weak(m: dict) -> bool:
    """Weak = the lower end of the held-out ROC-AUC 95% CI is at or below 0.5 (or there is no CI).

    Not shown to beat chance, which is not the same as shown not to. Counting instead the models whose CI
    *contains* 0.5 gives 166, not 171, which is why the wording here is exact.
    """
    return m["roc_auc_ci95"] is None or m["roc_auc_ci95"][0] <= 0.5


def summarise(res: dict, models_dir: Path) -> dict:
    g, k = res["drugs"], res["shipped_model"]
    powered = {b: r for b, r in g.items() if not r["underpowered"] and r[k]["roc_auc"] is not None}
    best = max(powered, key=lambda b: powered[b][k]["roc_auc"]) if powered else None
    med = {m: float(np.median([r[m]["roc_auc"] for r in powered.values()])) if powered else None for m in KINDS}
    return {
        "drugs": len(g), "powered": len(powered), "underpowered": len(g) - len(powered),
        "median_roc_auc": med,
        "beat_nn1": {m: sum(r[m]["roc_auc"] > r["nn1"]["roc_auc"] for r in powered.values()) for m in ("logreg", "rf")},
        "weak": {m: sum(weak(r[m]) for r in g.values()) for m in ("logreg", "rf")},
        "below_half": sum(r[k]["roc_auc"] < 0.5 for r in powered.values()),
        "max_roc_auc": powered[best][k]["roc_auc"] if best else None,
        "max_drug": g[best]["name"] if best else None,
        "model_bytes": sum(f.stat().st_size for f in models_dir.glob("*.joblib")),
    }


def train_all(
    compounds: list[str] | None = None, derived: Path = DERIVED, results: Path = RESULTS, models_dir: Path = MODELS
) -> dict:
    """Evaluate and save the given drugs (default: the selected set), update the JSON and the Markdown."""
    sel = select_compounds(derived)
    cpd = _tables(derived)[3]
    path = results / "loop2_models.json"
    res = json.loads(path.read_text()) if path.exists() else {"drugs": {}}
    if full := compounds is None:
        res["drugs"] = {}  # a full run replaces the drug set
    compounds = compounds or sel["compound"].tolist()
    gene_of = sel.set_index("compound")[["oncology_gene", "rule"]].to_dict("index")
    fitted = {}
    for b in compounds:
        out, fitted[b], d = evaluate(b, derived)
        info = cpd.loc[b]
        res["drugs"][b] = {
            "name": info["name"], "target": info["target"], "smiles": info["smiles"],
            **gene_of.get(b, {"oncology_gene": oncology_gene(info["target"]), "rule": "requested"}), **out,
        }
        fitted[b]["data"] = d
        print(f"{b} {info['name']}: n_test={out['n_test']} sens={out['sensitive_test']} "
              f"logreg={f3(out['logreg']['roc_auc'])} rf={f3(out['rf']['roc_auc'])}")

    by_rule, wins, powered = switch_rule(res["drugs"])
    shipped = SHIPPED
    train, test = lineage_split(str(derived))
    lin = cell_lines(derived)
    cands = _candidates(derived)
    res.update(
        protocol="docs/evaluation-loop2.md", lr_params=LR_PARAMS, rf_params=RF_PARAMS, n_boot=N_BOOT,
        sensitive_percentile=SENSITIVE_PERCENTILE, underpowered_below=UNDERPOWERED, oncology_list=ONCOLOGY,
        shipped_model=shipped, switch_rule_model=by_rule, rf_wins=wins, powered_drugs=powered,
        shipped_by="amendment 2026-11-04: logistic regression ships; the switch rule is reported, not applied",
        earlier_runs=EARLIER_RUNS,
        selection={
            "candidates": len(cands), "per_target": PER_TARGET, "selected": len(sel),
            "genes_with_compounds": int(sel["oncology_gene"].nunique()),
            "by_rule": sel["rule"].value_counts().to_dict(),
            "reassigned": int(((sel["rule"] == "3 per gene") & (sel["oncology_gene"] != sel["first_gene"])).sum()),
            "selective_added": sel.loc[sel["rule"] == "selective", ["compound", "name", "target", "n_lines"]]
            .to_dict("records"),
            "per_gene": sel.groupby("oncology_gene", sort=False)["compound"].apply(list).to_dict(),
        },
        split={
            "test_frac": TEST_FRAC, "seed": SEED, "n_lines": len(lin), "n_lineages": int(lin.nunique()),
            "n_train_lines": len(train), "n_test_lines": len(test),
            "train_lineages": lin[lin.index.isin(train)].value_counts().to_dict(),
            "test_lineages": lin[lin.index.isin(test)].value_counts().to_dict(),
        },
    )
    models_dir.mkdir(parents=True, exist_ok=True)
    if full:  # drop model files of drugs no longer in the set (generated files, git-ignored)
        for f in models_dir.glob("*.joblib"):
            if f.stem not in res["drugs"]:
                f.unlink()
    for b in compounds:
        r, d = res["drugs"][b], fitted[b]["data"]
        joblib.dump({
            "compound": b, "name": r["name"], "target": r["target"], "smiles": r["smiles"], "kind": shipped,
            "model": fitted[b][shipped], "genes": d["genes"],
            "train_genes": sorted(np.array(d["genes"])[d["X_tr"].any(axis=0)]),
            "threshold_auc": r["threshold_auc"], "roc_auc": r[shipped]["roc_auc"],
            "roc_auc_ci95": r[shipped]["roc_auc_ci95"], "underpowered": r["underpowered"],
            "n_sensitive_test": r["sensitive_test"],
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
    """Rank every shipped drug model for a cell line with these hotspot genes (rank 1 = highest P(sensitive)).

    `p_sensitive` is not calibrated: show the rank, never a percentage. `weak` = the lower end of the model's
    held-out ROC-AUC 95% CI is at or below 0.5 (show it greyed). A model abstains (is left out) when no listed
    gene is mutated in any of its
    training lines; an empty list means every model abstained and the app must show no prediction. The nearest
    cell lines and their measured sensitivities are the main evidence. Cell lines, not patients.
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
            "roc_auc": m["roc_auc"], "roc_auc_ci95": m["roc_auc_ci95"], "n_sensitive_test": m["n_sensitive_test"],
            "weak": weak(m), "underpowered": m["underpowered"],
        })
    out.sort(key=lambda r: (-r["p_sensitive"], r["name"]))
    return [{"rank": i, **r} for i, r in enumerate(out, 1)]


def main() -> None:
    ap = argparse.ArgumentParser(description="Train loop-2 per-drug sensitivity models.")
    ap.add_argument("--drugs", nargs="+", help="Broad IDs (BRD-K...); default: the selected drug set")
    res = train_all(ap.parse_args().drugs)
    s = res["summary"]
    m = s["median_roc_auc"]
    print(f"{s['drugs']} drugs; switch rule: rf won ROC-AUC on {res['rf_wins']} of {res['powered_drugs']} "
          f"(rule says {res['switch_rule_model']}); shipped={res['shipped_model']} by amendment; median ROC-AUC "
          f"logreg {f3(m['logreg'])} rf {f3(m['rf'])} 1-NN {f3(m['nn1'])}; weak {s['weak'][res['shipped_model']]}; "
          f"underpowered {s['underpowered']}; models {s['model_bytes']:,} bytes")


if __name__ == "__main__":
    main()
