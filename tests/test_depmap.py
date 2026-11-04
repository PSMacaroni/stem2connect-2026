from pathlib import Path

import pandas as pd
import pytest

from molscreen import depmap

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"


@pytest.fixture
def derived(tmp_path: Path) -> Path:
    """Toy raw files in the real formats -> build_tables -> the derived folder."""
    pd.DataFrame(
        {"KRAS (3845)": [2, 1, 1, 0, 1], "TP53 (7157)": [1, 2, 0, 0, 1], "BRAF (673)": [0, 0, 0, 1, 0]},
        index=["ACH-1", "ACH-2", "ACH-3", "ACH-4", "ACH-5"],
    ).to_csv(tmp_path / depmap.HOTSPOT)
    pd.DataFrame(
        {
            "ModelID": ["ACH-1", "ACH-2", "ACH-3", "ACH-4", "ACH-5"],
            "PatientID": ["PT-a", "PT-b", "PT-c", "PT-d", "PT-e"],
            "CellLineName": ["Bline", "Aline", "Cline", "Dline", "Eline"],
            "OncotreeLineage": ["Lung", "Lung", "Pancreas", "Skin", "Lung"],
            "OncotreePrimaryDisease": ["NSCLC", "NSCLC", "PDAC", "Melanoma", "NSCLC"],
            "Age": [60, 50, 40, 30, 20],
            "Sex": ["Female", "Male", "Female", "Male", "Male"],
            "PatientRace": ["x", "y", "z", "w", "v"],
        }
    ).to_csv(tmp_path / depmap.MODELS, index=False)
    a1, a2, b, c = (
        "BRD-K00000001-001-01-1",
        "BRD-K00000001-001-02-5",
        "BRD-K00000002-001-01-1",
        "BRD-K00000003-001-01-1",
    )
    rows = [  # broad_id, depmap_id, auc, passed_str_profiling, name
        (a1, "ACH-1", 0.2, "TRUE", "drugA"),
        (a2, "ACH-1", 0.4, "TRUE", "drugA"),  # second batch of the same compound
        (a1, "ACH-1", 0.9, "TRUE", "drugA"),  # median of 0.2, 0.4, 0.9 = 0.4
        (b, "ACH-1", 0.01, "FALSE", "drugB"),  # failed STR profiling: dropped
        (b, "ACH-1", 0.6, "TRUE", "drugB"),
        (c, "ACH-1", 0.1, "TRUE", "drugC"),
        (c, "ACH-2", 0.5, "TRUE", "drugC"),
        (c, "ACH-3", 0.5, "TRUE", "drugC"),
        (c, "ACH-4", 0.5, "TRUE", "drugC"),
        (c, None, 0.5, "TRUE", "drugC"),  # no depmap_id: cannot join
    ]
    prism = pd.DataFrame(rows, columns=["broad_id", "depmap_id", "auc", "passed_str_profiling", "name"])
    prism["moa"], prism["target"], prism["screen_id"] = "m", "T1, T2", "MTS010"
    prism["smiles"] = f"{ASPIRIN}, {ASPIRIN}"
    prism.to_csv(tmp_path / depmap.PRISM, index=False)
    pd.DataFrame(
        {
            "CompoundID": ["DPC-1"],
            "SampleIDs": [f"BRD:{c};GDSC1:1"],
            "ChEMBLID": ["CHEMBL25"],
            "SMILES": [None],
        }
    ).to_csv(tmp_path / depmap.PORTAL, index=False)
    depmap.build_tables(tmp_path)
    return tmp_path / "derived"


def test_hotspot_collapsed_to_binary_symbols(derived):
    hot = pd.read_csv(derived / "hotspot_binary.csv", index_col=0)
    assert list(hot.columns) == ["KRAS", "TP53", "BRAF"]
    assert set(hot.to_numpy().ravel()) == {0, 1}
    assert hot.loc["ACH-1"].tolist() == [1, 1, 0]


def test_personal_columns_never_written(derived):
    text = (derived / "models.csv").read_text()
    assert list(pd.read_csv(derived / "models.csv").columns) == depmap.MODEL_COLS
    for leaked in ["Age", "Sex", "PatientRace", "PatientID", "PT-a", "Female"]:
        assert leaked not in text


def test_qc_drop_median_and_compound_table(derived):
    sens = pd.read_csv(derived / "sensitivity.csv").set_index(["ModelID", "compound"])["auc"]
    assert sens[("ACH-1", "BRD-K00000001")] == pytest.approx(0.4)  # two batches, three rows, median
    assert sens[("ACH-1", "BRD-K00000002")] == pytest.approx(0.6)  # the failed-QC 0.01 is gone
    assert len(sens) == 6
    cpd = pd.read_csv(derived / "compounds.csv").set_index("compound")
    assert cpd.loc["BRD-K00000003", "smiles"] == ASPIRIN  # ", "-joined repeats -> one SMILES
    assert cpd.loc["BRD-K00000003", "chembl_id"] == "CHEMBL25"
    assert cpd.loc["BRD-K00000003", "n_cell_lines"] == 4


def test_nearest_ranking_tiebreak_and_screened_only(derived):
    res = depmap.nearest_cell_lines(["kras", "TP53", "STK11"], k=10, derived=derived)
    # ACH-1 and ACH-2 tie at 2/2 (STK11 is not in the matrix): name breaks the tie. ACH-5 has no PRISM data.
    assert [r["ModelID"] for r in res] == ["ACH-2", "ACH-1", "ACH-3", "ACH-4"]
    assert [r["jaccard"] for r in res] == [1.0, 1.0, 0.5, 0.0]
    assert [r["n_shared"] for r in res] == [2, 2, 1, 0]
    assert res[0]["shared_genes"] == ["KRAS", "TP53"] and res[3]["shared_genes"] == []
    assert res[0]["OncotreeLineage"] == "Lung" and "Age" not in res[0]
    assert len(depmap.nearest_cell_lines(["KRAS"], k=2, derived=derived)) == 2
    with pytest.raises(ValueError):
        depmap.nearest_cell_lines(["NOTAGENE"], derived=derived)


def test_nearest_ranks_shared_genes_before_jaccard(tmp_path):
    # X carries only KRAS (1 shared, Jaccard 1/2); Y carries KRAS, TP53 and three more (2 shared, Jaccard 2/5).
    pd.DataFrame(
        {"KRAS": [1, 1], "TP53": [0, 1], "G1": [0, 1], "G2": [0, 1], "G3": [0, 1]}, index=["ACH-X", "ACH-Y"]
    ).rename_axis("ModelID").to_csv(tmp_path / "hotspot_binary.csv")
    pd.DataFrame({"ModelID": ["ACH-X", "ACH-Y"], "CellLineName": ["A", "B"]}).to_csv(
        tmp_path / "models.csv", index=False
    )
    pd.DataFrame({"ModelID": ["ACH-X", "ACH-Y"], "compound": "c", "auc": 0.5}).to_csv(
        tmp_path / "sensitivity.csv", index=False
    )
    pd.DataFrame({"compound": ["c"]}).to_csv(tmp_path / "compounds.csv", index=False)
    res = depmap.nearest_cell_lines(["KRAS", "TP53"], derived=tmp_path)
    assert [(r["ModelID"], r["n_shared"], r["jaccard"]) for r in res] == [("ACH-Y", 2, 0.4), ("ACH-X", 1, 0.5)]


def test_top_compounds_order(derived):
    top = depmap.top_compounds("ACH-1", derived=derived)
    assert [t["name"] for t in top] == ["drugC", "drugA", "drugB"]
    assert [t["auc"] for t in top] == pytest.approx([0.1, 0.4, 0.6])
    assert len(depmap.top_compounds("ACH-1", n=1, derived=derived)) == 1


REAL = Path("data/depmap/derived")


@pytest.mark.skipif(not (REAL / "sensitivity.csv").exists(), reason="real DepMap/PRISM tables not built")
def test_real_data_smoke():
    res = depmap.nearest_cell_lines(["KRAS", "TP53", "STK11"])
    assert len(res) == 10
    keys = [(r["n_shared"], r["jaccard"]) for r in res]
    assert keys == sorted(keys, reverse=True)
    top = depmap.top_compounds(res[0]["ModelID"])
    assert len(top) == 10 and [t["auc"] for t in top] == sorted(t["auc"] for t in top)
