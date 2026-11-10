"""Drive the whole demo in a real Chrome window, in time with the narration, so recording is one keypress.

Windows only. Run it from the repo root with the driver venv (see docs/video.md):

    dist\\demo-driver\\Scripts\\python.exe scripts\\demo_drive.py --rehearse   # check every click, no audio, fast
    dist\\demo-driver\\Scripts\\python.exe scripts\\demo_drive.py              # the real run, with the narration

What it does, shot by shot: opens the app, clicks what `docs/video.md` says to click, and holds each shot for
exactly as long as that shot's narration lasts. The hold comes from the WAV itself, not from a number typed here,
so re-rendering the audio re-times the demo. `--rehearse` does the same clicks with 1-second holds and prints
whether each one found what it expected, which is how the selectors get checked without sitting through 5:45.

It does not record. Focus the Chrome window it opens, press Win+Alt+R to start the Windows recorder, then run it.

Everything on screen is the live app answering for real. Nothing here fakes a result.
"""

import argparse
import pathlib
import sys
import time
import wave
import winsound

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIO = ROOT / "dist" / "narration"
URL = "http://localhost:8511"
CAFFEINE = "CN1C=NC2=C1C(=O)N(C)C(=O)N2C"
TABS = {"activity": "Activity", "cells": "Cell lines", "safety": "Safety flags", "analogs": "Analogs"}


def audio_seconds(shot: int) -> float:
    """How long this shot's narration runs, read out of the file that will play."""
    with wave.open(str(AUDIO / f"shot-{shot}.wav")) as w:
        return w.getnframes() / w.getframerate()


class Driver:
    """One method per thing the script asks for on screen. Each one says whether it found what it expected."""

    def __init__(self, page, rehearsing: bool) -> None:
        self.page, self.rehearsing, self.faults = page, rehearsing, []

    def note(self, ok: bool, what: str) -> None:
        print(f"    {'ok  ' if ok else 'FAIL'} {what}")
        if not ok:
            self.faults.append(what)

    def visible(self, selector: str, has_text: str | None = None):
        """Streamlit keeps every tab's panel in the DOM, so a selector has to take the visible one."""
        loc = self.page.locator(f"{selector}:visible")
        return (loc.filter(has_text=has_text) if has_text else loc).first

    def tab(self, key: str) -> None:
        self.page.get_by_role("tab", name=TABS[key], exact=True).click()
        self.page.wait_for_timeout(900)
        self.note(TABS[key] in self.page.inner_text("body"), f"tab {TABS[key]}")

    def example(self, expect: str) -> None:
        self.visible("button", "Example").click()
        self.page.wait_for_timeout(300)
        self.wait_for(expect, f"Example -> {expect!r}")

    def wait_for(self, text: str, what: str, timeout: int = 60_000) -> None:
        """Wait for text that is actually on screen.

        Two tabs word the abstain warning the same way, and Streamlit leaves every tab's panel in the DOM, so
        matching without `visible=true` can find a copy in a hidden panel and wait forever for it to appear.
        """
        try:
            self.page.locator(f"text={text} >> visible=true").first.wait_for(timeout=timeout)
            self.note(True, what)
        except PlaywrightError:
            self.note(False, f"{what} (never appeared)")

    def expander(self) -> None:
        """Open the first result row, where the drawn evidence and the abstain reason live.

        Streamlit keeps an expander open across a re-render, so clicking blind would shut the one a previous shot
        opened. Check first, then click only if it is closed.
        """
        details = self.visible('[data-testid="stExpander"] details')
        if details.count() and details.get_attribute("open") is not None:
            self.note(True, "the first expander was already open")
            return
        self.visible('[data-testid="stExpander"] summary').click()
        self.page.wait_for_timeout(700)
        self.note(self.visible('[data-testid="stExpander"] details').get_attribute("open") is not None,
                  "opened the first expander")

    def type_smiles(self, smiles: str) -> None:
        box = self.visible("textarea")
        box.click()
        box.fill(smiles)
        box.press("Control+Enter")
        self.page.wait_for_timeout(500)
        self.note(smiles in box.input_value(), "typed the molecule")

    def target_dropdown(self) -> None:
        """Shot 2 opens the Target picker so all nine targets are on screen."""
        self.page.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').first.click()
        self.page.wait_for_timeout(600)
        self.note(True, "opened the Target dropdown")
        self.page.keyboard.press("Escape")

    def scroll_to(self, text: str) -> None:
        try:
            self.page.locator(f"text={text} >> visible=true").first.scroll_into_view_if_needed(timeout=15_000)
            self.note(True, f"scrolled to {text!r}")
        except PlaywrightError:
            self.note(False, f"scrolled to {text!r} (not found)")

    def top(self) -> None:
        self.page.mouse.wheel(0, -4000)
        self.page.wait_for_timeout(400)


def shots(d: Driver) -> list[tuple[int, str, list]]:
    """(number, title, actions). Actions run in order at the start of the shot; the hold does the rest."""
    return [
        (1, "The problem", [lambda: d.wait_for("Research and learning tool", "front page is up")]),
        (2, "What it is", [lambda: d.target_dropdown()]),
        (3, "Activity", [lambda: d.example("p_active"), lambda: d.expander()]),
        # The abstain warning sits inside the molecule's expander (app.py:84), so it has to be opened first.
        (4, "The abstain", [lambda: d.type_smiles(CAFFEINE),
                            lambda: d.wait_for("abstains", "the row says abstains"),
                            lambda: d.expander(),
                            lambda: d.wait_for("Outside what this model has seen", "the reason is on screen")]),
        (5, "Cell lines", [lambda: d.tab("cells"), lambda: d.example("NCI-H1573"),
                           lambda: d.scroll_to("most sensitive PRISM compounds")]),
        (6, "Safety flags", [lambda: d.tab("safety"), lambda: d.example("Assay active rate"),
                             lambda: d.expander()]),
        (7, "Analogs", [lambda: d.tab("analogs"), lambda: d.example("transforms"),
                        lambda: d.scroll_to("not a real ranking")]),
        (8, "The honest part", [lambda: d.tab("cells"), lambda: d.scroll_to("Model ranks")]),
        (9, "Learning, AI, next", [lambda: d.tab("activity"), lambda: d.top()]),
    ]


def run(rehearsing: bool, video: bool = False, countdown: int = 6) -> int:
    if not rehearsing:
        missing = [n for n in range(1, 10) if not (AUDIO / f"shot-{n}.wav").exists()]
        if missing:
            print(f"No audio for shot(s) {missing}. Run scripts/narrate.py then scripts/narrate.ps1.")
            return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False,
                                    args=["--window-size=1280,800", "--window-position=0,0",
                                          "--hide-crash-restore-bubble"])
        clip = {"width": 1280, "height": 720}
        extra = {"record_video_dir": str(ROOT / "dist" / "demo-video"), "record_video_size": clip} if video else {}
        page = browser.new_page(viewport=clip, device_scale_factor=1, **extra)
        page.goto(URL, wait_until="domcontentloaded")
        d = Driver(page, rehearsing)
        d.wait_for("Molecule Screening Workbench", "the app loaded", timeout=120_000)

        # --video is the silent route: Playwright captures the page itself, and the audio is laid over it
        # afterwards. Playing the narration as well would only get captured twice over, by whatever records it.
        play_audio = not rehearsing and not video
        if play_audio:
            shots_total = sum(audio_seconds(n) for n in range(1, 10))
            print(f"\n  The shots run {shots_total:.0f}s. The limit is 360s, so everything you add either side of"
                  f" them -\n  this countdown and however long you take to stop the recorder - has to fit in"
                  f" {360 - shots_total:.0f}s.\n  If the file does end up over 6:00, trim the start in the Photos"
                  " app rather than re-recording.\n")
            for n in range(countdown, 0, -1):
                print(f"  starting in {n}... (click the Chrome window, then press Win+Alt+R)")
                time.sleep(1)

        for n, title, actions in shots(d):
            hold = 1.0 if rehearsing else audio_seconds(n)
            print(f"\nshot {n} — {title}  ({hold:.1f}s)")
            started = time.monotonic()
            if play_audio:
                winsound.PlaySound(str(AUDIO / f"shot-{n}.wav"), winsound.SND_FILENAME | winsound.SND_ASYNC)
            for act in actions:
                act()
            left = hold - (time.monotonic() - started)
            if left > 0:
                time.sleep(left)
            elif not rehearsing:
                print(f"    note: the clicks took {-left:.1f}s longer than the narration")

        print("\ndone." if video else "\ndone — press Win+Alt+R now to stop. The file is in Videos\\Captures.")
        if video:
            path = page.video.path() if page.video else None
            page.close()  # the WebM is only written out when the page closes
            print(f"silent video: {path}")
            print("Its shot boundaries line up with dist/narration/narration-full.wav by construction, because")
            print("each shot was held for exactly that shot's audio length. Put the two on a timeline in")
            print("Clipchamp (built into Windows), both starting at 0, and export. Nothing needs nudging.")
        if d.faults:
            print(f"\n{len(d.faults)} step(s) did not find what they expected:")
            for f in d.faults:
                print(f"  - {f}")
            return 1
        print("every step found what it expected.")
        browser.close()
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rehearse", action="store_true", help="check the clicks with 1s holds and no audio")
    ap.add_argument("--video", action="store_true",
                    help="also save a silent WebM of the page to dist/demo-video (for muxing the audio yourself)")
    ap.add_argument("--countdown", type=int, default=6,
                    help="seconds to start the recorder in; every one of them lands in the file (default 6)")
    args = ap.parse_args()
    sys.exit(run(args.rehearse, args.video, args.countdown))
