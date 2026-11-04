"""The Cell lines and Safety flags tabs, run headless with Streamlit's AppTest on the real models and tables."""

import pytest
from streamlit.testing.v1 import AppTest

from molscreen import assets
from molscreen.data import ROOT
from molscreen.depmap import RAW
from molscreen.drugs import MODELS as LOOP2
from molscreen.tox import MODEL_PATH, TASKS, load_bundle
from molscreen.ui_safety import EXAMPLES

pytestmark = pytest.mark.skipif(
    not (MODEL_PATH.exists() and (ROOT / LOOP2).is_dir() and (ROOT / RAW / "derived").is_dir()),
    reason="trained models or DepMap tables not present",
)
TIMEOUT = 300  # first run loads the 129 MB Tox21 bundle from disk


@pytest.fixture(scope="module")
def app(monkeypatch_module):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=TIMEOUT)
    at.run()
    assert not at.exception
    return at


@pytest.fixture(scope="module")
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(ROOT)  # depmap and drugs use paths relative to the repo root
        mp.setattr(assets, "ensure_models", lambda *a, **k: None)  # models are local; no download in tests
        yield mp


def frame(at, column: str):
    return next(d.value for d in at.dataframe if column in d.value.columns)


def test_cell_lines_example_lookup_then_compounds(app):
    app.button(key="cells_example").click().run()
    assert not app.exception
    near = frame(app, "number shared")
    assert near.iloc[0]["cell line"] == "NCI-H1573" and len(near) == 10
    assert any("not patients; a lookup, not a prediction" in c.value for c in app.caption)
    ranks = frame(app, "rank")
    assert list(ranks["rank"]) == list(range(1, len(ranks) + 1)) and "p_sensitive" not in ranks.columns
    app.selectbox(key="cell_line").select_index(1).run()
    assert not app.exception
    cpds = frame(app, "AUC")
    assert len(cpds) == 10 and list(cpds["AUC"]) == sorted(cpds["AUC"])
    assert any(near.iloc[1]["cell line"] in m.value for m in app.markdown)


def test_safety_examples_are_in_training_table():
    train = load_bundle(MODEL_PATH)["train"].set_index("smiles")
    actives = [(train.loc[s, TASKS] == 1).any() for s in EXAMPLES]
    assert actives == [True, True, False]


def test_safety_aspirin_scores_and_methane_abstains(app):
    app.text_area(key="tox_smiles").input("CC(=O)Oc1ccccc1C(=O)O").run()
    assert not app.exception
    t = frame(app, "assay active rate")
    assert len(t) == 12 and set(t["assay"]) == set(TASKS)
    assert any("not a toxicity verdict" in m.value for m in app.markdown)
    app.text_area(key="tox_smiles").input("C").run()
    assert not app.exception
    assert any("Outside what this model has seen" in w.value for w in app.warning)
    assert not any("assay active rate" in d.value.columns for d in app.dataframe)
