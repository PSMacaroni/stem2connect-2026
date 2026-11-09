"""The narration SSML must be valid XML and must say exactly what the script says, no more and no less."""

import pathlib
import sys
from xml.etree import ElementTree

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

narrate = pytest.importorskip("narrate")
from teleprompter import SRC, sentences, shots, spoken

NS = "{http://www.w3.org/2001/10/synthesis}"


@pytest.fixture(scope="module")
def script_shots() -> list[dict]:
    return shots(SRC.read_text(encoding="utf-8"))


def test_every_shot_is_valid_ssml_with_one_s_per_sentence(script_shots: list[dict]) -> None:
    assert len(script_shots) == 9, "docs/video.md should still have 9 shots"
    for s in script_shots:
        root = ElementTree.fromstring(narrate.ssml(s["say"]))  # raises if the XML is malformed
        said = [e.text for e in root.iter(f"{NS}s")]
        assert said == sentences(spoken(s["say"])), f"shot {s['n']} does not match the script"


def test_the_cut_sentence_is_never_spoken(script_shots: list[dict]) -> None:
    """The sentence marked (cut first) is cut by default, so the audio must not contain it."""
    joined = "".join(narrate.ssml(s["say"]) for s in script_shots)
    assert "cut first" not in joined
    assert "Most free tools show one confident number" not in joined


def test_xml_special_characters_are_escaped() -> None:
    out = narrate.ssml(["Baselines & limits are <shown>."])
    assert "&amp;" in out and "&lt;shown&gt;" in out
    ElementTree.fromstring(out)


def test_respelling_changes_the_spelling_only() -> None:
    """A SAY entry must not be able to inject markup, and must leave the sentence count alone."""
    narrate.SAY["Tox21"] = "Tox twenty-one"
    try:
        out = narrate.ssml(["It shows Tox21 assays."])
        assert "Tox twenty-one" in out
        assert len(ElementTree.fromstring(out).findall(f"{NS}s")) == 1
    finally:
        del narrate.SAY["Tox21"]
