import pandas as pd
import pytest

from molscreen.data import DATASETS, PULLS, build_dataset, load_dataset, parent_smiles

BENZ, PHENOL, ANILINE = "c1ccccc1", "Oc1ccccc1", "Nc1ccccc1"


def row(mol, smiles, p, relation="=", comment=None, assay="B", stype="IC50", variant=None):
    return {
        "molecule_chembl_id": mol, "canonical_smiles": smiles, "standard_type": stype,
        "standard_relation": relation, "pchembl_value": p, "assay_type": assay,
        "data_validity_comment": comment, "assay_variant_mutation": variant,
    }


def test_filters_aggregation_and_label():
    acts = pd.DataFrame([
        row("M1", PHENOL, 5.0), row("M1", PHENOL, 6.0), row("M1", PHENOL, 7.0),  # median 6.0 -> active
        row("M1", PHENOL, 9.9, relation="<"),  # bound, dropped
        row("M1", PHENOL, 9.9, comment="Outside typical range"),  # flagged, dropped
        row("M1", PHENOL, 9.9, assay="A"),  # ADMET assay, dropped
        row("M1", PHENOL, 9.9, variant="T790M"),  # mutant protein, dropped
        row("M2", ANILINE, 5.9), row("M2", ANILINE, 9.0, relation=">"),  # just under 6.0 -> inactive
        row("M3", "not a smiles", 8.0),  # unparseable, dropped
        row("M4", BENZ, 8.0, stype="Kd"),  # not IC50/Ki/EC50, dropped
        row("M5", BENZ, 7.0, assay="F", stype="Ki"),
    ])
    ds = build_dataset("TEST", acts).set_index("molecule_chembl_ids")
    assert set(ds.index) == {"M1", "M2", "M5"}
    assert ds.loc["M1", "pchembl"] == 6.0 and ds.loc["M1", "active"] == 1 and ds.loc["M1", "n_rows"] == 3
    assert ds.loc["M2", "active"] == 0 and ds.loc["M2", "n_rows"] == 1
    assert ds.loc["M5", "active"] == 1 and ds.loc["M5", "smiles"] == BENZ


def test_mutant_only_molecule_is_dropped():
    acts = pd.DataFrame([row("M1", PHENOL, 7.0, variant="V600E"), row("M2", ANILINE, 7.0, variant=" ")])
    assert list(build_dataset("TEST", acts)["molecule_chembl_ids"]) == ["M2"]  # blank variant = wild type


def test_salt_collapses_to_free_base_and_stereo_is_kept():
    base, hcl = "CC(N)c1ccccc1", "CC(N)c1ccccc1.Cl"
    assert parent_smiles(hcl) == parent_smiles(base)
    acts = pd.DataFrame([
        row("FREE", base, 5.0), row("SALT", hcl, 7.0), row("SALT", hcl, 8.0),  # one parent, median of 3 rows = 7.0
        row("R", "C[C@@H](N)c1ccccc1", 7.0), row("S", "C[C@H](N)c1ccccc1", 5.0),  # enantiomers stay apart
    ])
    ds = build_dataset("TEST", acts).set_index("molecule_chembl_ids")
    assert ds.loc["FREE;SALT", "n_ids"] == 2 and ds.loc["FREE;SALT", "pchembl"] == 7.0
    assert ds.loc["FREE;SALT", "smiles"] == parent_smiles(base)
    assert {"R", "S"} <= set(ds.index) and len(ds) == 3


@pytest.mark.skipif(not (PULLS / "CDK6.csv").exists(), reason="needs the CDK6 ChEMBL pull")
def test_real_cdk6_dataset():
    ds = build_dataset("CDK6")  # in memory only: this test writes nothing
    assert ds["smiles"].is_unique and set(ds["active"]) == {0, 1}
    if (DATASETS / "CDK6.csv").exists():
        assert load_dataset("CDK6").shape == ds.shape
