import numpy as np
import pandas as pd
import pytest

from molscreen.chem import murcko_scaffold
from molscreen.tox import MODEL_PATH, TASKS, clean, evaluate, predict_tox, save_bundle

SUBS = ["C", "CC", "O", "N", "Cl", "CN", "CO", "C(=O)O", "CCN", "F"]
SCAFFOLDS = ["c1ccccc1{}", "c1ccncc1{}", "C1CCCCC1{}", "c1ccc2ccccc2c1{}", "C1CCNCC1{}"]


def toy_raw() -> pd.DataFrame:
    pairs = [(s.format(x), x) for s in SCAFFOLDS for x in SUBS]
    raw = pd.DataFrame({"smiles": [p[0] for p in pairs], "mol_id": [f"TOX{i}" for i in range(len(pairs))]})
    for t in TASKS:
        raw[t] = [float("N" in x) for _, x in pairs]  # a learnable toy label, both classes in every scaffold
    raw.loc[::7, "NR-AR"] = np.nan  # some molecules not tested in NR-AR
    return raw


def test_clean_collapses_parents_with_max_and_keeps_blanks():
    raw = pd.DataFrame({"smiles": ["CCO", "CCO.Cl", "not a smiles", "c1ccccc1"], "mol_id": ["a", "b", "c", "d"]})
    for t in TASKS:
        raw[t] = np.nan
    raw["NR-AR"] = [0.0, 1.0, 1.0, 0.0]
    raw["SR-p53"] = [np.nan, 0.0, 0.0, np.nan]
    ds, st = clean(raw)
    row = ds.set_index("smiles").loc["CCO"]
    assert row["NR-AR"] == 1 and row["SR-p53"] == 0 and row["mol_ids"] == "a;b"  # any active call wins
    assert np.isnan(ds.set_index("smiles").loc["c1ccccc1", "SR-p53"])  # untested stays blank, not 0
    assert st["rows_unparseable"] == 1 and st["rows_salt_stripped"] == 1 and st["rows_collapsed"] == 1
    assert st["conflicting_cells"] == 1 and st["molecules"] == 2
    assert st["tasks"]["NR-AR"] == {"tested": 2, "actives": 1, "active_frac": 0.5}
    assert st["tasks"]["NR-ER"]["tested"] == 0


def test_evaluate_shares_one_scaffold_split_and_excludes_blanks():
    ds, _ = clean(toy_raw())
    res, fitted, tr, _, info = evaluate(ds, ["NR-AR", "SR-p53"])
    te = ds[~ds["smiles"].isin(tr["smiles"])]
    assert info["n_train"] + info["n_test"] == len(ds) == len(tr) + len(te)
    assert not {murcko_scaffold(s) for s in tr["smiles"]} & {murcko_scaffold(s) for s in te["smiles"]}
    # blanks are left out per task: NR-AR uses fewer molecules than SR-p53, on the same split
    assert res["NR-AR"]["n_train"] + res["NR-AR"]["n_test"] == ds["NR-AR"].notna().sum() < len(ds)
    assert res["SR-p53"]["n_train"] + res["SR-p53"]["n_test"] == len(ds)
    assert res["NR-AR"]["n_train"] == tr["NR-AR"].notna().sum()
    for r in res.values():
        assert r["majority"]["roc_auc"] == 0.5
        for k in ("lr", "rf"):
            lo, hi = r[k]["roc_auc_ci95"]
            assert 0.0 <= lo <= hi <= 1.0 and 0.0 <= r[k]["roc_auc"] <= 1.0
            assert 0.0 <= r[k]["pr_auc"] <= 1.0 and 0.0 <= r[k]["balanced_acc"] <= 1.0
    assert set(fitted["NR-AR"]) == {"lr", "rf"}


def test_predict_tox_abstains_on_methane_and_reports_bad_smiles(tmp_path):
    ds, _ = clean(toy_raw())
    res, fitted, tr, X_tr, info = evaluate(ds, ["NR-AR", "SR-p53"], kinds=("lr",))
    path = tmp_path / "tox21.joblib"
    assert save_bundle(path, "lr", fitted, tr, X_tr, info, res) > 0
    known = tr["smiles"].iloc[0]
    meth, bad, salt = predict_tox(["C", "not a smiles", known + ".Cl"], path=path)
    assert meth["abstain"] is True and meth["max_tanimoto"] < meth["abstain_cutoff"]
    assert bad["error"] == "invalid SMILES" and bad["assays"] == {} and bad["abstain"] is None
    assert salt["smiles"] == known and salt["max_tanimoto"] == 1.0 and salt["abstain"] is False
    assert set(salt["assays"]) == {"NR-AR", "SR-p53"}
    ar = salt["assays"]["NR-AR"]
    assert set(ar) == {"p_active", "prevalence", "ratio", "above_prevalence", "roc_auc", "roc_auc_ci95"}
    assert ar["prevalence"] == res["NR-AR"]["train_actives"] / res["NR-AR"]["n_train"]
    assert ar["roc_auc"] == res["NR-AR"]["lr"]["roc_auc"] and ar["roc_auc_ci95"] == res["NR-AR"]["lr"]["roc_auc_ci95"]
    for a in salt["assays"].values():
        assert 0.0 <= a["p_active"] <= 1.0 and 0.0 < a["prevalence"] < 1.0
        assert a["ratio"] == pytest.approx(a["p_active"] / a["prevalence"])
        assert a["above_prevalence"] == (a["p_active"] > a["prevalence"])


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="needs models/tox21.joblib from `python -m molscreen.tox`")
def test_real_model_gives_12_probabilities_for_aspirin():
    (r,) = predict_tox(["CC(=O)Oc1ccccc1C(=O)O"])
    assert r["error"] is None and set(r["assays"]) == set(TASKS)
    assert all(0.0 <= a["p_active"] <= 1.0 and 0.0 < a["prevalence"] < 1.0 for a in r["assays"].values())
    assert all(a["roc_auc"] > 0.5 and len(a["roc_auc_ci95"]) == 2 for a in r["assays"].values())
