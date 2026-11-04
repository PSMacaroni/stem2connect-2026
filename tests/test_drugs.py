import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from molscreen import drugs
from molscreen.split import group_split

LINEAGES = {"A": 20, "B": 15, "C": 8, "D": 7}  # 50 lines: A and B fit under 40 (train), C and D go to test


@pytest.fixture
def derived(tmp_path: Path, monkeypatch) -> Path:
    """Toy derived tables: BRAF-mutant lines are sensitive to BRD-K1; G4 is mutated only in test lineages."""
    monkeypatch.setattr(drugs, "MIN_LINES", 10)
    rng = np.random.default_rng(0)
    lin = [x for x, n in LINEAGES.items() for _ in range(n)]
    ids = [f"ACH-{i:02d}" for i in range(len(lin))]
    hot = pd.DataFrame(
        {
            "KRAS": rng.integers(0, 2, len(ids)),
            "TP53": rng.integers(0, 2, len(ids)),
            "BRAF": [i % 4 == 0 for i in range(len(ids))],
            "G4": [x in "CD" for x in lin],
        },
        index=pd.Index(ids, name="ModelID"),
    ).astype(int)
    hot.to_csv(tmp_path / "hotspot_binary.csv")
    pd.DataFrame(
        {"ModelID": ids, "CellLineName": ids, "OncotreeLineage": lin, "OncotreePrimaryDisease": "x"}
    ).to_csv(tmp_path / "models.csv", index=False)
    auc = 0.9 - 0.5 * hot["BRAF"] + rng.normal(0, 0.05, len(ids))
    sens = pd.concat(
        [
            pd.DataFrame({"ModelID": ids, "compound": "BRD-K1", "auc": auc.to_numpy()}),
            pd.DataFrame({"ModelID": ids, "compound": "BRD-K2", "auc": rng.uniform(0.3, 1, len(ids))}),
            pd.DataFrame({"ModelID": ids, "compound": "BRD-K3", "auc": rng.uniform(0.3, 1, len(ids))}),
            pd.DataFrame({"ModelID": ids[:5], "compound": "BRD-K4", "auc": 0.5}),  # too few lines
        ]
    )
    sens.to_csv(tmp_path / "sensitivity.csv", index=False)
    pd.DataFrame(
        {
            "compound": ["BRD-K1", "BRD-K2", "BRD-K3", "BRD-K4"],
            "name": ["rafdrug", "nogene", "othergene", "fewlines"],
            "target": ["BRAF, RAF1", None, "XYZ1", "EGFR"],
            "moa": ["RAF inhibitor", "unknown", "something", "EGFR inhibitor"],
            "smiles": "CCO",
        }
    ).to_csv(tmp_path / "compounds.csv", index=False)
    return tmp_path


def test_group_split_keeps_groups_disjoint_and_covers_all():
    groups = [x for x, n in LINEAGES.items() for _ in range(n)]
    train, test = group_split(groups, test_frac=0.2, seed=0)
    assert sorted(train + test) == list(range(len(groups)))
    assert not {groups[i] for i in train} & {groups[i] for i in test}
    assert {groups[i] for i in test} == {"C", "D"}


def test_lineage_split_shared_and_disjoint(derived):
    train, test = drugs.lineage_split(str(derived))
    assert len(train) == 35 and len(test) == 15 and not train & test
    lin = drugs.cell_lines(derived)
    assert set(lin[list(train)]) == {"A", "B"} and set(lin[list(test)]) == {"C", "D"}


def test_select_compounds_needs_a_gene_in_target(derived, monkeypatch):
    sel = drugs.select_compounds(derived)
    assert sel["compound"].tolist() == ["BRD-K1", "BRD-K3"]  # K2 has no target gene, K4 too few lines
    monkeypatch.setattr(drugs, "MAX_DRUGS", 1)  # more candidates than the cap: oncology list applies
    assert drugs.select_compounds(derived)["compound"].tolist() == ["BRD-K1"]


def test_label_threshold_from_training_lines_only(derived):
    d = drugs.build_xy("BRD-K1", derived)
    sens = pd.read_csv(derived / "sensitivity.csv").query("compound == 'BRD-K1'").set_index("ModelID")["auc"]
    assert d["threshold"] == pytest.approx(np.percentile(sens[d["ids_tr"]], 10))
    assert d["threshold"] != pytest.approx(np.percentile(sens, 10))
    assert (d["y_te"] == (sens[d["ids_te"]].to_numpy() < d["threshold"])).all()
    assert d["X_tr"].shape == (35, 4) and d["X_te"].shape == (15, 4)


def test_metrics_sane():
    y = np.array([0, 0, 0, 1, 1, 0, 1, 0])
    good = drugs.metrics(y, y.astype(float), y)
    assert good["roc_auc"] == 1.0 and good["roc_auc_ci95"] == [1.0, 1.0] and good["balanced_acc"] == 1.0
    assert good["pr_auc"] == 1.0
    assert drugs.metrics(y, -y.astype(float), 1 - y)["roc_auc"] == 0.0
    const = drugs.metrics(y, np.zeros(len(y)), np.zeros(len(y), int))
    assert const["roc_auc"] == 0.5 and const["balanced_acc"] == 0.5
    assert drugs.metrics(np.zeros(4, int), np.arange(4.0), np.zeros(4, int))["roc_auc"] is None


def test_jaccard_nn():
    ref = np.array([[1, 0, 0], [1, 1, 0], [0, 0, 0]])
    assert drugs.jaccard_nn(np.array([[1, 1, 0], [0, 0, 1], [0, 0, 0]]), ref).tolist() == [1, 0, 0]


def test_train_all_and_predict_abstains(derived, tmp_path):
    res = drugs.train_all(["BRD-K1"], derived, tmp_path / "results", tmp_path / "models")
    r = res["drugs"]["BRD-K1"]
    assert r["n_train"] == 35 and r["n_test"] == 15 and r["sensitive_test"] > 0
    assert r["logreg"]["roc_auc"] > 0.7  # BRAF drives the toy auc
    assert json.loads((tmp_path / "results" / "loop2_models.json").read_text())["shipped_model"] in ("logreg", "rf")
    assert "rafdrug" in (tmp_path / "results" / "loop2_models.md").read_text()
    out = drugs.predict_drugs(["braf"], tmp_path / "models")
    assert [o["name"] for o in out] == ["rafdrug"] and 0 <= out[0]["p_sensitive"] <= 1
    assert drugs.predict_drugs(["NOTAGENE"], tmp_path / "models") == []
    assert drugs.predict_drugs(["G4"], tmp_path / "models") == []  # mutated only in test lineages


REAL = Path("data/depmap/derived")


@pytest.mark.skipif(not (REAL / "sensitivity.csv").exists(), reason="real DepMap/PRISM tables not built")
def test_real_data_smoke():
    sel = drugs.select_compounds()
    assert len(sel) == 60 and sel["target"].notna().all() and (sel["n_lines"] >= 300).all()
    train, test = drugs.lineage_split()
    lin = drugs.cell_lines()
    assert not set(lin[list(train)]) & set(lin[list(test)]) and len(train) + len(test) == len(lin)
    if any(drugs.MODELS.glob("*.joblib")):
        out = drugs.predict_drugs(["KRAS", "TP53"])
        assert out and out == sorted(out, key=lambda o: (-o["p_sensitive"], o["name"]))
