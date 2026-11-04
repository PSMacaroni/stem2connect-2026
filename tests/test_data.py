import pandas as pd
import pytest

from molscreen.data import PULLS, build_dataset, load_dataset

BENZ, PHENOL, ANILINE = "c1ccccc1", "Oc1ccccc1", "Nc1ccccc1"


def row(mol, smiles, p, relation="=", comment=None, assay="B", stype="IC50"):
    return {
        "molecule_chembl_id": mol, "canonical_smiles": smiles, "standard_type": stype,
        "standard_relation": relation, "pchembl_value": p, "assay_type": assay,
        "data_validity_comment": comment,
    }


def test_filters_aggregation_and_label():
    acts = pd.DataFrame([
        row("M1", PHENOL, 5.0), row("M1", PHENOL, 6.0), row("M1", PHENOL, 7.0),  # median 6.0 -> active
        row("M1", PHENOL, 9.9, relation="<"),  # bound, dropped
        row("M1", PHENOL, 9.9, comment="Outside typical range"),  # flagged, dropped
        row("M1", PHENOL, 9.9, assay="A"),  # ADMET assay, dropped
        row("M2", ANILINE, 5.9), row("M2", ANILINE, 9.0, relation=">"),  # just under 6.0 -> inactive
        row("M3", "not a smiles", 8.0),  # unparseable, dropped
        row("M4", BENZ, 8.0, stype="Kd"),  # not IC50/Ki/EC50, dropped
        row("M5", BENZ, 7.0, assay="F", stype="Ki"),
    ])
    ds = build_dataset("TEST", acts).set_index("molecule_chembl_id")
    assert set(ds.index) == {"M1", "M2", "M5"}
    assert ds.loc["M1", "pchembl"] == 6.0 and ds.loc["M1", "active"] == 1 and ds.loc["M1", "n_rows"] == 3
    assert ds.loc["M2", "active"] == 0 and ds.loc["M2", "n_rows"] == 1
    assert ds.loc["M5", "active"] == 1 and ds.loc["M5", "smiles"] == BENZ


@pytest.mark.skipif(not (PULLS / "CDK6.csv").exists(), reason="needs the CDK6 ChEMBL pull")
def test_real_cdk6_dataset():
    ds = build_dataset("CDK6")
    assert ds["molecule_chembl_id"].is_unique and set(ds["active"]) == {0, 1}
    assert load_dataset("CDK6").shape == ds.shape
