"""Loop 3: safety flags on the 12 Tox21 assays, exactly as docs/evaluation-loop3.md says.

Usage: uv run python -m molscreen.tox [--tasks NR-AR SR-p53] [--split-seeds 0 1 2 3 4]
Reads data/tox21/tox21.csv.gz (scripts/pull_tox21.py). Writes data/tox21/dataset.csv, results/tox21_models.json,
results/tox21_models.md and, on a run over all 12 tasks, models/tox21.joblib (one file, all 12 shipped models).
A run on some tasks updates their entries and keeps the others already in the JSON.
"""

import argparse
import json
from functools import cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from molscreen.chem import morgan_fp
from molscreen.data import ROOT, parent_smiles
from molscreen.predict import tanimoto_to_train
from molscreen.train import (
    MODELS,
    N_BITS,
    N_BOOT,
    RADIUS,
    RESULTS,
    abstain_cutoff,
    f3,
    fingerprints,
    max_tanimoto,
    metrics,
    roc_auc_ci,
    split,
    table,
)

TOX = ROOT / "data" / "tox21"
RAW = TOX / "tox21.csv.gz"
DATASET = TOX / "dataset.csv"
MODEL_PATH = MODELS / "tox21.joblib"
TASKS = ["NR-AR", "NR-AR-LBD", "NR-AhR", "NR-Aromatase", "NR-ER", "NR-ER-LBD", "NR-PPAR-gamma", "SR-ARE",
         "SR-ATAD5", "SR-HSE", "SR-MMP", "SR-p53"]
# Fixed in docs/evaluation-loop3.md, committed with the protocol before any training. Not tuned.
LR_PARAMS = {"C": 1.0, "class_weight": "balanced", "max_iter": 2000}
RF_PARAMS = {"n_estimators": 500, "class_weight": "balanced", "random_state": 0, "n_jobs": -1}
UNDERPOWERED_ACTIVES = 20
NAMES = {"lr": "logistic regression", "rf": "random forest", "nn1": "1-NN", "majority": "majority"}
KINDS = ("majority", "nn1", "lr", "rf")
FLAG_WORDING = ("A flag means the molecule resembles compounds that were active in that assay; it is not a toxicity "
                "verdict.")
# PubChem AIDs from https://tripod.nih.gov/tox21/challenge/data.jsp; one-line summaries of the PubChem assay
# titles and descriptions (https://pubchem.ncbi.nlm.nih.gov/bioassay/<AID>), read 2026-11-04.
ASSAYS = {
    "NR-AR": (743040, "switches on the androgen receptor (full-length, MDA breast cancer cell line)"),
    "NR-AR-LBD": (743053, "switches on the androgen receptor ligand-binding domain (HEK293 reporter cells)"),
    "NR-AhR": (743122, "switches on the aryl hydrocarbon receptor (responds to dioxin-like chemicals)"),
    "NR-Aromatase": (743139, "blocks aromatase, the enzyme that turns androgens into estrogens (MCF-7 aro ERE cells)"),
    "NR-ER": (743079, "switches on estrogen receptor alpha (full-length, BG1 ovarian cell line)"),
    "NR-ER-LBD": (743077, "switches on the estrogen receptor alpha ligand-binding domain (HEK293 reporter cells)"),
    "NR-PPAR-gamma": (743140, "switches on PPAR-gamma, a receptor that controls fat and sugar metabolism"),
    "SR-ARE": (743219, "switches on the antioxidant response element (an oxidative-stress signal)"),
    "SR-ATAD5": (720516, "raises ATAD5, a sign of DNA damage (genotoxicity; human embryonic kidney cells)"),
    "SR-HSE": (743228, "switches on the heat shock response (a protein-damage stress signal)"),
    "SR-MMP": (720637, "disrupts the mitochondrial membrane potential (mitochondria losing their charge)"),
    "SR-p53": (720552, "switches on p53 signalling (the cell's DNA-damage alarm)"),
}


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Parent molecules (salts stripped), one row each; per task the max label over its tested rows (NaN = untested)."""
    parent = raw["smiles"].map(parent_smiles)
    ok = parent.notna()
    rows = raw[ok].assign(smiles=parent[ok])
    g = rows.groupby("smiles", sort=True)
    ds = g[TASKS].max().reset_index()  # max skips NaN: any active call wins; all-blank stays blank
    ds.insert(1, "mol_ids", g["mol_id"].agg(lambda s: ";".join(sorted(s))).to_numpy())
    stats = {
        "rows": len(raw), "rows_unparseable": int((~ok).sum()),
        "rows_salt_stripped": int(raw.loc[ok, "smiles"].str.contains(".", regex=False).sum()),
        "molecules": len(ds), "rows_collapsed": int(ok.sum() - len(ds)),
        "conflicting_cells": int((g[TASKS].nunique() > 1).to_numpy().sum()),
        "tasks": {t: {"tested": int(ds[t].notna().sum()), "actives": int((ds[t] == 1).sum()),
                      "active_frac": float(ds[t].mean())} for t in TASKS},
    }
    return ds, stats


def build_dataset(raw: Path = RAW, out: Path = DATASET) -> tuple[pd.DataFrame, dict]:
    ds, stats = clean(pd.read_csv(raw))
    ds.to_csv(out, index=False)
    return ds, stats


def make(kind: str):
    return LogisticRegression(**LR_PARAMS) if kind == "lr" else RandomForestClassifier(**RF_PARAMS)


def evaluate(ds: pd.DataFrame, tasks: list[str], seed: int = 0, kinds: tuple = ("lr", "rf")):
    """One shared scaffold split; per task, train and test on the molecules tested in it.
    Returns (per-task results, fitted models, train table, train fingerprints, split info)."""
    tr, te = split(ds, seed)
    X_tr, X_te = fingerprints(tr["smiles"].tolist()), fingerprints(te["smiles"].tolist())
    cutoff = abstain_cutoff(X_tr)
    kept_all = max_tanimoto(X_te, X_tr)[0] >= cutoff
    info = {"n_train": len(tr), "n_test": len(te), "abstain_cutoff": cutoff,
            "n_test_abstain": int((~kept_all).sum())}
    results, fitted = {}, {}
    for task in tasks:
        a, b = tr[task].notna().to_numpy(), te[task].notna().to_numpy()
        Xa, ya, Xb, yb = X_tr[a], tr.loc[a, task].astype(int).to_numpy(), X_te[b], te.loc[b, task].astype(int).to_numpy()
        kept = kept_all[b]
        r = {"n_train": len(ya), "n_test": len(yb), "train_actives": int(ya.sum()), "test_actives": int(yb.sum()),
             "test_active_frac": float(yb.mean()), "n_test_abstain": int((~kept).sum())}
        majority = int(ya.mean() >= 0.5)
        r["majority"] = metrics(yb, np.full(len(yb), float(majority)), np.full(len(yb), majority))
        _, nn = max_tanimoto(Xb, Xa)
        r["nn1"] = metrics(yb, ya[nn].astype(float), ya[nn])
        fitted[task] = {}
        for kind in kinds:
            m = make(kind).fit(Xa, ya)
            if kind == "rf":
                m.set_params(n_jobs=1)  # a parallel forest sums votes in thread order (moves PR-AUC at 1e-8)
            p = m.predict_proba(Xb)[:, 1]
            r[kind] = metrics(yb, p, (p >= 0.5).astype(int))
            r[kind]["roc_auc_kept"] = metrics(yb[kept], p[kept], (p[kept] >= 0.5).astype(int))["roc_auc"]
            r[kind]["roc_auc_ci95"] = roc_auc_ci(yb, p) if r[kind]["roc_auc"] is not None else None
            fitted[task][kind] = m
        results[task] = r
    return results, fitted, tr, X_tr, info


def switch_rule(tasks: dict) -> tuple[str, int]:
    """The random forest ships unless logistic regression has the higher held-out ROC-AUC on more than 6 tasks."""
    lr_wins = sum(1 for r in tasks.values()
                  if None not in (r["lr"]["roc_auc"], r["rf"]["roc_auc"]) and r["lr"]["roc_auc"] > r["rf"]["roc_auc"])
    return ("lr" if lr_wins > 6 else "rf"), lr_wins


def save_bundle(path: Path, kind: str, fitted: dict, tr: pd.DataFrame, X_tr: np.ndarray, info: dict,
                results: dict) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "kind": kind, "tasks": list(fitted), "models": {t: m[kind] for t, m in fitted.items()},
        "radius": RADIUS, "n_bits": N_BITS, "train_fps_packed": np.packbits(X_tr, axis=1),
        "train": tr[["smiles", "mol_ids", *TASKS]], "abstain_cutoff": info["abstain_cutoff"], "metrics": results,
    }, path, compress=3)
    return path.stat().st_size


@cache
def load_bundle(path: Path = MODEL_PATH) -> dict:
    return joblib.load(path)


def predict_tox(smiles_list: list[str], path: Path = MODEL_PATH) -> list[dict]:
    """App contract. One dict per input: parent SMILES or `error`, max Tanimoto to train, abstain flag, and per assay
    the probability of active and `flag` (probability >= 0.5). Probabilities are given even when `abstain` is True;
    the caller decides what to show. A bad SMILES never stops the batch."""
    b = load_bundle(path)
    out, fps, where = [], [], []
    for s in smiles_list:
        parent = parent_smiles(s.strip()) if isinstance(s, str) else None
        r = {"input": s, "smiles": parent, "error": None if parent else "invalid SMILES", "max_tanimoto": None,
             "abstain": None, "abstain_cutoff": b["abstain_cutoff"], "assays": {}}
        if parent:
            fp = morgan_fp(parent, b["radius"], b["n_bits"])
            r["max_tanimoto"] = float(tanimoto_to_train(fp, b["train_fps_packed"]).max())
            r["abstain"] = r["max_tanimoto"] < b["abstain_cutoff"]
            fps.append(fp)
            where.append(len(out))
        out.append(r)
    if fps:
        X = np.stack(fps)
        for task, m in b["models"].items():
            for i, p in zip(where, m.predict_proba(X)[:, 1]):
                out[i]["assays"][task] = {"p_active": float(p), "flag": bool(p >= 0.5)}
    return out


def write_md(res: dict) -> None:
    g, ds, sp = res["tasks"], res["dataset"], res["split"]
    k, low = res["shipped_model"], res["underpowered_actives"]
    sname = NAMES[k]

    def note(r):
        notes = [f"underpowered: {r['test_actives']} test actives"] if r["test_actives"] < low else []
        if r[k]["roc_auc"] is None or r["nn1"]["roc_auc"] is None or r[k]["roc_auc"] <= r["nn1"]["roc_auc"]:
            notes.append("no better than nearest-neighbour lookup")
        return "; ".join(notes)

    def ci(r):
        return "n/a" if r[k]["roc_auc_ci95"] is None else "{:.3f} to {:.3f}".format(*r[k]["roc_auc_ci95"])

    def per_model(metric):
        return [[t, *(f3(r[x][metric]) for x in KINDS), note(r)] for t, r in g.items()]

    def margin(r):
        return "n/a" if None in (r["lr"]["roc_auc"], r["rf"]["roc_auc"]) else f"{r['lr']['roc_auc'] - r['rf']['roc_auc']:+.4g}"

    def vs_nn(metric: str, label: str) -> str:
        below = [(t, r) for t, r in g.items() if r[k][metric] < r["nn1"][metric]]
        detail = ", ".join(f"{t} {r[k][metric]:.3f} vs {r['nn1'][metric]:.3f}" for t, r in below)
        return f"- {label}: below 1-NN on {len(below)} of {len(g)} assays" + (f" ({detail})." if below else ".")

    beats = sum(1 for r in g.values() if "nearest" not in note(r))
    bal = [r[k]["balanced_acc"] for r in g.values()]
    under = [t for t, r in g.items() if r["test_actives"] < low]
    lines = [
        "# Safety flags (loop 3): held-out results on Tox21", "",
        "Protocol `docs/evaluation-loop3.md` (committed with the model parameters before any training). All numbers",
        "come from `results/tox21_models.json`, written by `uv run python -m molscreen.tox`. Morgan fingerprints",
        "(radius 2, 2048 bits); one scaffold split (seed 0) shared by all 12 assays; per assay only the molecules",
        "tested in it. Every metric is on the held-out test set.",
        f"**Shipped model: {sname}.** \"Underpowered\" marks an assay with fewer than {low} active molecules in",
        "its test set.", "",
        f"**{FLAG_WORDING}** The assays are cell-based and biochemical lab tests, not people. Research and",
        "learning tool, not medical advice.", "",
        "## Data", "",
        (f"Source: `tox21.csv.gz` ({res['source']['bytes']} bytes, SHA-256 `{res['source']['sha256']}`, pulled "
         f"{res['source']['date']}). {ds['rows']} rows; {ds['rows_unparseable']} did not parse in RDKit and were "
         f"dropped; {ds['rows_salt_stripped']} had more than one fragment and were stripped to the parent; "
         f"{ds['rows_collapsed']} rows collapsed into another row's parent, leaving {ds['molecules']} parent "
         f"molecules; {ds['conflicting_cells']} (parent, assay) cells had conflicting labels and took the active "
         f"call. Split: {sp['n_train']} train, {sp['n_test']} test parents."), "",
        *table(["Assay", "Tested", "Actives", "Active fraction"],
               [[t, d["tested"], d["actives"], f"{d['active_frac']:.3f}"] for t, d in ds["tasks"].items()]),
        "", "## Headline: shipped model against 1-NN", "",
        (f"ROC-AUC 95% CI: bootstrap over the test set ({res['n_boot']} resamples, seed 0). PR-AUC uses active "
         "(the minority) as the positive class; a random ranking scores the test active fraction. Balanced accuracy "
         "uses a 0.5 threshold. 1-NN scores with its neighbour's label, so its ROC-AUC equals its balanced accuracy."),
        "",
        *table(["Assay", "n train", "n test", "Test actives", f"ROC-AUC {sname} (95% CI)", "ROC-AUC 1-NN",
                f"PR-AUC {sname}", "PR-AUC random", f"Bal. acc. {sname}", "Bal. acc. 1-NN", "Note"],
               [[t, r["n_train"], r["n_test"], r["test_actives"], f"{f3(r[k]['roc_auc'])} ({ci(r)})",
                 f3(r["nn1"]["roc_auc"]), f3(r[k]["pr_auc"]), f"{r['test_active_frac']:.3f}",
                 f3(r[k]["balanced_acc"]), f3(r["nn1"]["balanced_acc"]), note(r)] for t, r in g.items()]),
        "",
        (f"Must-beat rule: the {sname} exceeds 1-NN on held-out ROC-AUC on {beats} of {len(g)} assays; any assay "
         "where it does not is marked \"no better than nearest-neighbour lookup\" (it still ships)."),
        "", f"The {sname} against 1-NN, per metric:", "",
        vs_nn("roc_auc", "ROC-AUC"), vs_nn("pr_auc", "PR-AUC, active class"),
        vs_nn("balanced_acc", "Balanced accuracy at 0.5 (the app's flag threshold)"),
        "", "## All models", "", "### ROC-AUC", "",
        *table(["Assay", "Majority", "1-NN", "Logistic regression", "Random forest", "Note"], per_model("roc_auc")),
        "", "### PR-AUC, active as the positive class", "",
        *table(["Assay", "Random", "Majority", "1-NN", "Logistic regression", "Random forest", "Note"],
               [[t, f"{r['test_active_frac']:.3f}", *row[1:]] for (t, r), row in zip(g.items(), per_model("pr_auc"))]),
        "", "### Balanced accuracy at 0.5", "",
        *table(["Assay", "Majority", "1-NN", "Logistic regression", "Random forest", "Note"],
               per_model("balanced_acc")),
        "", "## Switch rule", "",
        *table(["Assay", "ROC-AUC logistic regression", "ROC-AUC random forest", "LR - RF"],
               [[t, f3(r["lr"]["roc_auc"]), f3(r["rf"]["roc_auc"]), margin(r)] for t, r in g.items()]),
        "",
        (f"Logistic regression had the higher held-out ROC-AUC on {res['lr_roc_auc_wins']} of {len(g)} assays (it "
         f"needs more than 6), so **{sname}** ships for every assay. The rule read the test set once."),
    ]
    if under:
        lines += ["", "Underpowered assays (fewer than {} test actives): {}. Their AUCs and CIs rest on few "
                  "molecules.".format(low, ", ".join(f"{t} ({g[t]['test_actives']})" for t in under))]
    mf = res.get("model_file")
    lines += [
        "", "## Abstain", "",
        (f"One cut-off for all assays: {sp['abstain_cutoff']:.3f} (5th percentile of the train leave-one-out max "
         f"Tanimoto). {sp['n_test_abstain']} of {sp['n_test']} held-out parents fall below it. Per assay: held-out "
         "molecules tested in it that would abstain, and the shipped model's ROC-AUC on all of them and on the rest."),
        "",
        *table(["Assay", "Held-out abstain", f"ROC-AUC {sname}, all", "ROC-AUC kept"],
               [[t, f"{r['n_test_abstain']} of {r['n_test']}", f3(r[k]["roc_auc"]), f3(r[k]["roc_auc_kept"])]
                for t, r in g.items()]),
    ]
    sv = res.get("split_variance")
    if sv and sv.get("kind") == k:
        def mmm(v):
            v = [x for x in v if x is not None]
            return f"{min(v):.3f} / {float(np.median(v)):.3f} / {max(v):.3f}"
        lines += [
            "", "## Split variance (disclosure)", "",
            (f"The shared scaffold split recomputed with seeds {sv['seeds']}, the {sname} and 1-NN refit per assay "
             "(`uv run python -m molscreen.tox --split-seeds 0 1 2 3 4`). Nothing is saved or chosen from these "
             "runs; seed 0 stays the reported split. Held-out ROC-AUC, min / median / max over seeds."), "",
            *table(["Assay", f"{sname} min / median / max", "1-NN min / median / max"],
                   [[t, mmm(v[k]), mmm(v["nn1"])] for t, v in sv["tasks"].items()]),
        ]
        rng = {t: max(v[k]) - min(v[k]) for t, v in sv["tasks"].items()}
        lead = {t: g[t][k]["roc_auc"] - g[t]["nn1"]["roc_auc"] for t in sv["tasks"]}
        xt, lt = max(rng, key=rng.get), min(lead, key=lead.get)
        lines += ["", (f"Changing the split alone moves the {sname}'s ROC-AUC by up to {rng[xt]:.4f} ({xt}). Its "
                       f"smallest seed-0 lead over 1-NN is {lead[lt]:+.4f} ({lt}). The bootstrap CIs above cover "
                       "one fixed test set only.")]
    lines += [
        "", "## Known limits", "",
        ("- **Licence not stated.** Neither MoleculeNet/DeepChem nor the NCATS challenge page states a licence for "
         "the data. Tox21 is a US-government programme, so it is probably public domain (inferred, not verified). The "
         "raw file is never committed; `scripts/pull_tox21.py` downloads it."),
        (f"- **Salts stripped, charges kept.** {ds['rows_salt_stripped']} of {ds['rows']} rows were mixtures or salts "
         "reduced to their largest fragment; a counter-ion's own activity is lost, and charged forms are not "
         "neutralised."),
        (f"- **Any active call wins on collapse.** {ds['conflicting_cells']} (parent, assay) cells had both an active "
         "and an inactive row; they count as active."),
        ("- **Probabilities are not risks.** Both models use balanced class weights, so a probability above 0.5 "
         "does not mean a 50% chance of being active; the flag at 0.5 is a ranking cut, not a calibrated one."),
        (f"- **The flag at 0.5 is weaker than the ranking.** The {sname}'s balanced accuracy at 0.5 is "
         f"{min(bal):.3f} to {max(bal):.3f} across assays (per-metric list above). Its ranking (ROC-AUC) is the "
         "stronger signal: read a probability as a rank among molecules, not as a yes or no."),
        (f"- **Abstain is common**: {sp['n_test_abstain']} of {sp['n_test']} held-out parents are below the cut-off, "
         "because a scaffold split makes held-out molecules unlike train by design."),
        ("- **The assays are lab tests on cells and proteins**, at the concentrations screened; they say nothing "
         "direct about dose, exposure or harm in people."),
        "", "## The 12 assays", "",
        "From the Tox21 Data Challenge data page (https://tripod.nih.gov/tox21/challenge/data.jsp) and each PubChem",
        "assay record. Active = the compound did this in the assay.", "",
        *[f"- **{t}** (PubChem AID {a['aid']}, https://pubchem.ncbi.nlm.nih.gov/bioassay/{a['aid']}): {a['what']}."
          for t, a in res["assays"].items()],
    ]
    if mf:
        lines += ["", "## Model file", "",
                  (f"`{mf['path']}` holds the 12 shipped {sname} models, the packed train fingerprints, the "
                   f"train table, the cut-off and the metrics: {mf['bytes']} bytes. It is git-ignored.")]
    lines += [
        "", "## Credits", "",
        "Tox21 data (Tox21 Data Challenge 2014, NCATS/NIEHS/EPA/FDA), MoleculeNet copy.",
        "Wu Z, Ramsundar B, Feinberg EN, et al. MoleculeNet: a benchmark for molecular machine learning. Chem. Sci.",
        "2018;9(2):513-530. doi:10.1039/C7SC02664A",
        "Huang R, Xia M, et al. Tox21Challenge to build predictive models of nuclear receptor and stress response",
        "pathways as mediated by exposure to environmental chemicals and drugs. Front. Environ. Sci. 2016;3:85.",
        "doi:10.3389/fenvs.2015.00085",
    ]
    (RESULTS / "tox21_models.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Train loop-3 Tox21 safety-flag models.")
    ap.add_argument("--tasks", nargs="+", default=TASKS, choices=TASKS)
    ap.add_argument("--split-seeds", nargs="+", type=int,
                    help="disclosure run only: shipped model and 1-NN ROC-AUC under these seeds; saves no model")
    args = ap.parse_args()
    tasks = [t for t in TASKS if t in args.tasks]
    path = RESULTS / "tox21_models.json"
    res = json.loads(path.read_text()) if path.exists() else {"tasks": {}}
    ds, stats = build_dataset()

    if args.split_seeds:
        k = res["shipped_model"]
        sv = res.get("split_variance")
        if not sv or sv["seeds"] != args.split_seeds or sv["kind"] != k:
            sv = res["split_variance"] = {"seeds": args.split_seeds, "kind": k, "tasks": {}}
        runs = [evaluate(ds, tasks, seed, (k,))[0] for seed in args.split_seeds]
        for t in tasks:
            sv["tasks"][t] = {x: [r[t][x]["roc_auc"] for r in runs] for x in (k, "nn1")}
            print(f"{t}: {k} ROC-AUC per seed {[f3(a) for a in sv['tasks'][t][k]]}")
        sv["tasks"] = {t: sv["tasks"][t] for t in TASKS if t in sv["tasks"]}
    else:
        results, fitted, tr, X_tr, info = evaluate(ds, tasks)
        res["tasks"].update(results)
        res["tasks"] = {t: res["tasks"][t] for t in TASKS if t in res["tasks"]}
        shipped, wins = switch_rule(res["tasks"])
        res.update(
            protocol="docs/evaluation-loop3.md", source=json.loads((TOX / "PULL_INFO.json").read_text()),
            dataset=stats, split=info, lr_params=LR_PARAMS, rf_params=RF_PARAMS, n_boot=N_BOOT,
            underpowered_actives=UNDERPOWERED_ACTIVES, shipped_model=shipped, lr_roc_auc_wins=wins,
            assays={t: {"aid": a, "what": w} for t, (a, w) in ASSAYS.items()},
        )
        for t in tasks:
            r = res["tasks"][t]
            print(f"{t}: n_test={r['n_test']} actives={r['test_actives']} ROC-AUC lr={f3(r['lr']['roc_auc'])} "
                  f"rf={f3(r['rf']['roc_auc'])} 1-NN={f3(r['nn1']['roc_auc'])}")
        if tasks == TASKS:
            size = save_bundle(MODEL_PATH, shipped, fitted, tr, X_tr, info, res["tasks"])
            res["model_file"] = {"path": "models/tox21.joblib", "kind": shipped, "bytes": size}
            print(f"saved models/tox21.joblib ({shipped}, {size} bytes)")
        else:
            print("subset run: models/tox21.joblib not rewritten (a full run writes it)")
        print(f"shipped={shipped} (logistic regression won ROC-AUC on {wins} of {len(res['tasks'])})")
    RESULTS.mkdir(exist_ok=True)
    path.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    write_md(res)
    print(f"wrote {path} and results/tox21_models.md")


if __name__ == "__main__":
    main()
