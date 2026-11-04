import pytest

from molscreen.predict import examples, predict
from molscreen.train import MODELS

pytestmark = pytest.mark.skipif(not (MODELS / "CDK6.joblib").exists(), reason="trained models not present")


def test_known_actives_predicted_active():
    for r in predict("CDK6", examples("CDK6")):
        assert r["error"] is None and r["abstain"] is False and r["p_active"] > 0.5
        assert r["max_tanimoto"] == 1.0 and len(r["neighbours"]) == 3  # it is in train, so it finds itself


def test_invalid_smiles_does_not_crash_batch():
    good = examples("CDK6", 1)[0]
    bad, ok, empty = predict("CDK6", ["not a smiles", good, ""])
    assert bad["error"] == "invalid SMILES" and bad["p_active"] is None and empty["error"] == "invalid SMILES"
    assert ok["error"] is None and ok["p_active"] is not None


def test_salt_gives_free_base_result():
    base = examples("CDK6", 1)[0]
    salt, free = predict("CDK6", [base + ".Cl", base])
    assert salt["smiles"] == free["smiles"] and salt["p_active"] == free["p_active"]
    assert salt["max_tanimoto"] == free["max_tanimoto"]


def test_far_molecules_abstain():
    for r in predict("CDK6", ["C", "CCCCCCCCCCCCCCCC"]):
        assert r["abstain"] is True and r["max_tanimoto"] < r["abstain_cutoff"]
