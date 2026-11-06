"""Loop 4: the transforms, the scoring, the abstain rule, and the real Analogs tab run headless with AppTest."""

import json

import pytest
from rdkit import Chem
from streamlit.testing.v1 import AppTest

from molscreen import assets
from molscreen.analogs import MAX_ANALOGS, TRANSFORMS, enumerate_analogs, score_analogs
from molscreen.chem import canonical_smiles
from molscreen.data import ROOT, parent_smiles
from molscreen.depmap import RAW
from molscreen.drugs import MODELS as LOOP2
from molscreen.predict import examples
from molscreen.tox import MODEL_PATH
from molscreen.train import MODELS
from molscreen.ui_analogs import FLAT_SPREAD, flatness, note

# Palbociclib, an approved CDK4/6 inhibitor. Used only as an input here; no claim is made about it.
PALBOCICLIB = "CC(=O)c1c(C)c2cnc(Nc3ccc(N4CCNCC4)nc3)nc2n(C2CCCC2)c1=O"
CAFFEINE = "CN1C=NC2=C1C(=O)N(C)C(=O)N2C"
GENE = "CDK6"
TIMEOUT = 300  # first run loads the 129 MB Tox21 bundle from disk

needs_models = pytest.mark.skipif(
    not ((MODELS / f"{GENE}.joblib").exists() and MODEL_PATH.exists()),
    reason="trained models not present",
)


def test_transforms_each_fire_on_a_molecule_that_carries_their_group():
    """Every named transform produces at least one analog on a molecule built to match it, so none is dead code."""
    probe = "Oc1ccc(Cl)cc1OC"  # aromatic C-H, C-Cl, phenol O-H and a ring methyl ether
    fired = {a["transform"] for a in enumerate_analogs(probe)}
    fired |= {a["transform"] for a in enumerate_analogs("NCCC(=O)O")}  # an N-H and a carboxylic acid
    assert fired == set(TRANSFORMS)


def test_known_cdk6_active_gives_distinct_valid_analogs():
    rows = enumerate_analogs(PALBOCICLIB)
    parent = canonical_smiles(PALBOCICLIB)
    assert len(rows) >= 5
    assert len(rows) <= MAX_ANALOGS
    smiles = [r["smiles"] for r in rows]
    assert len(set(smiles)) == len(smiles)  # deduplicated
    assert parent not in smiles  # the parent is not one of its own analogs
    assert all(Chem.MolFromSmiles(s) is not None for s in smiles)  # every one sanitises


def test_invalid_smiles_gives_no_analogs():
    assert enumerate_analogs("not a molecule") == []
    assert score_analogs(GENE, "not a molecule") == []


def test_limit_caps_the_enumeration():
    assert len(enumerate_analogs(PALBOCICLIB, limit=4)) == 4


@needs_models
def test_parent_is_first_and_analogs_are_ranked_by_p_active():
    rows = score_analogs(GENE, examples(GENE, 1)[0], limit=12)
    assert rows[0]["is_parent"] and rows[0]["transform"] is None
    assert rows[0]["tanimoto_to_parent"] == 1.0
    assert not any(r["is_parent"] for r in rows[1:])
    scored = [r["p_active"] for r in rows[1:] if r["p_active"] is not None]
    assert scored == sorted(scored, reverse=True)
    assert all(r["p_active"] is None for r in rows[1 + len(scored):])  # abstainers last
    assert all(0 <= r["tox_above"] <= 12 for r in rows)


@needs_models
def test_caffeine_abstains_and_its_p_active_is_withheld():
    """The loop-1 abstain rule, unchanged: caffeine is unlike the CDK6 training set, so no score is reported."""
    rows = score_analogs(GENE, CAFFEINE, limit=5)
    parent = rows[0]
    assert parent["smiles"] == parent_smiles(CAFFEINE)
    assert parent["abstain"] is True
    assert parent["p_active"] is None
    assert parent["max_tanimoto"] < parent["abstain_cutoff"]
    assert all(r["abstain"] and r["p_active"] is None for r in rows)  # its analogs are just as far away


def row(p_active=0.5, tox_abstain=False, **kw):
    """A score_analogs-shaped row, for the display rules that need no model."""
    return {"smiles": "c1ccccc1", "transform": None, "is_parent": False, "p_active": p_active,
            "abstain": p_active is None, "abstain_cutoff": 0.7, "max_tanimoto": 0.8,
            "tanimoto_to_parent": 0.8, "tox_above": 12, "tox_abstain": tox_abstain} | kw


def test_note_names_each_abstain_and_stays_quiet_otherwise():
    assert note(row()) == ""
    assert "no activity score" in note(row(p_active=None))
    assert "no Tox21 count" in note(row(tox_abstain=True))
    both = note(row(p_active=None, tox_abstain=True))
    assert "no activity score" in both and "no Tox21 count" in both


def test_flatness_calls_a_flat_ranking_flat_and_leaves_a_spread_one_alone():
    flat = [row(p_active=1.0, is_parent=True)] + [row(p_active=p) for p in (1.0, 0.99, 0.98)]
    msg = flatness(flat, top=3)
    assert "does not separate" in msg and "0.020" in msg  # the spread it measured, not a fixed sentence
    assert "No analog scores above the parent (1.000)" in msg
    wide = [row(p_active=0.4, is_parent=True)] + [row(p_active=p) for p in (0.9, 0.5, 0.1)]
    assert flatness(wide, top=3) == ""
    assert flatness([row(p_active=0.4, is_parent=True), row(p_active=0.9)], top=3) == ""  # one analog: no claim


def test_flat_spread_covers_the_movement_the_tab_claims_it_covers():
    """The tab tells the reader the floor is above the 0.044 these models move between scaffold splits.

    That sentence is only true if the shipped random forests really move by at most 0.044 across the disclosed
    seeds, so the number is recomputed here from results/activity_models.json rather than trusted.
    """
    sv = json.loads((ROOT / "results" / "activity_models.json").read_text(encoding="utf-8"))["split_variance"]
    rf_movement = max(max(g["rf"]) - min(g["rf"]) for g in sv["genes"].values())
    assert rf_movement == pytest.approx(0.0438, abs=5e-4)  # CDK6, seeds 0 to 4
    assert rf_movement <= FLAT_SPREAD  # the floor covers it, so the sentence on the tab holds
    text = (ROOT / "results" / "activity_models.md").read_text(encoding="utf-8")
    assert "moves ROC-AUC by up to 0.0549" in text  # the 1-NN baseline's figure, quoted in the module comment


@pytest.fixture(scope="module")
def app():
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(ROOT)
        mp.setattr(assets, "ensure_models", lambda *a, **k: None)  # models are local; no download in tests
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=TIMEOUT)
        at.run()
        assert not at.exception
        yield at


@pytest.mark.skipif(
    not (MODEL_PATH.exists() and (ROOT / LOOP2).is_dir() and (ROOT / RAW / "derived").is_dir()),
    reason="trained models or DepMap tables not present",
)
def test_analogs_tab_renders_the_example_and_abstains_on_caffeine(app):
    app.button(key="analog_example").click().run()
    assert not app.exception
    assert any("made up by this app" in w.value and "extrapolation" in w.value for w in app.warning)
    df = next(d.value for d in app.dataframe if "Tanimoto to parent" in d.value.columns)
    assert df.iloc[0]["row"] == "parent" and df.iloc[0]["Tanimoto to parent"] == 1.0
    assert len(df) == 11  # the parent plus the default 10 analogs
    assert list(df["row"])[1:] == [str(i) for i in range(1, 11)]
    assert tox_counts_match_their_abstains(df)
    assert any("does not separate these analogs" in w.value for w in app.warning)  # measured, not asserted blind
    app.number_input(key="analog_top").set_value(3).run()
    assert not app.exception
    assert len(next(d.value for d in app.dataframe if "Tanimoto to parent" in d.value.columns)) == 4
    app.text_input(key="analog_smiles").set_value(CAFFEINE).run()
    assert not app.exception
    caf = next(d.value for d in app.dataframe if "Tanimoto to parent" in d.value.columns)
    assert caf["p_active"].isna().all()
    assert all("no activity score: outside what this model has seen" in n for n in caf["note"])
    assert tox_counts_match_their_abstains(caf)
    assert caf["Tox21 assays above their active rate"].notna().any()  # caffeine is inside the Tox21 training range


def tox_counts_match_their_abstains(df) -> bool:
    """A Tox21 count is shown only where the note does not say the Tox21 models abstained, and vice versa."""
    shown = df["Tox21 assays above their active rate"].notna()
    said = ~df["note"].str.contains("no Tox21 count")
    return bool((shown == said).all())
