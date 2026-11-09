"""Turn the narration in docs/video.md into one SSML file per shot, ready for a speech synthesiser.

Usage: uv run python scripts/narrate.py            (writes dist/narration/shot-N.ssml)
       uv run python scripts/narrate.py --list      (print the word counts and leave the files alone)

Why this exists: the demo video needs a voice-over, and reading 796 words while clicking through nine shots in one
take is the hard part. These files let a synthesiser read the script instead, one file per shot, so the recorder
clicks, plays the shot, clicks again.

**If the video uses this audio, say so.** The README and the Devpost description already disclose which AI tools
did what; a synthesised narration belongs in that list. See "AI tools and services used" in README.md.

The text is not rewritten here. It is the same narration the teleprompter sheet shows, parsed by the same code in
scripts/teleprompter.py, so the audio cannot say something the script does not. The only change is spelling for
the synthesiser's benefit (SAY below), which must never change the words a listener hears.

Pace: the voice is left at its own default rate, which measured 142 wpm (Microsoft David Desktop) and 146 wpm
(Microsoft Zira Desktop) on 2026-11-08 over shot 1's 72 words. The script budgets 145, so no slowing is needed.
Pauses are set here, not spoken: BEAT after each sentence (the `//` in the sheet), END at the end of a shot.
"""

import pathlib
import sys
from xml.sax.saxutils import escape

from teleprompter import SRC, sentences, shots, spoken

OUT = pathlib.Path(__file__).resolve().parent.parent / "dist" / "narration"
BEAT_MS = 300  # between sentences: the `//` beat in the teleprompter sheet
END_MS = 700   # after the last sentence of a shot, before the recorder clicks on

# Respellings for the synthesiser only. Nothing here may change what a listener hears: "Tox21" -> "Tox twenty-one"
# is the same words, "Tox21" -> "the Tox21 panel" would not be. Pronunciation was NOT verified when these files
# were first generated (there is no way to hear the output from the session that wrote this), so listen to shot 1
# and shot 3 before recording, and add a line here for anything that comes out wrong. Example:
#     "ChEMBL": "Chembl",
SAY: dict[str, str] = {}


def spell_for_speech(text: str) -> str:
    for written, spoken_as in SAY.items():
        text = text.replace(written, spoken_as)
    return text


def ssml(say: list[str]) -> str:
    """One SSML document for one shot: a sentence, a beat, a sentence, and a longer pause at the end."""
    body = f'<break time="{BEAT_MS}ms"/>\n  '.join(
        f"<s>{escape(spell_for_speech(s))}</s>" for s in sentences(spoken(say))
    )
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\n  '
        f'{body}<break time="{END_MS}ms"/>\n</speak>\n'
    )


def main(argv: list[str]) -> int:
    sh = shots(SRC.read_text(encoding="utf-8"))
    if not sh:
        print("FAIL  no shots found in docs/video.md")
        return 1
    listing = "--list" in argv
    if not listing:
        OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for s in sh:
        words = len(spoken(s["say"]).split())
        total += words
        if not listing:
            (OUT / f"shot-{s['n']}.ssml").write_text(ssml(s["say"]), encoding="utf-8")
        print(f"shot {s['n']:>2}  {words:>4} words  {s['title']}")
    where = "(nothing written)" if listing else f"-> {OUT}"
    print(f"\n{len(sh)} shots, {total} words of narration {where}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
