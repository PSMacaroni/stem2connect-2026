"""Zip every trained model under models/ into dist/models-<tag>.zip with a MANIFEST.json, for a GitHub release.

Usage: uv run python scripts/bundle_models.py [tag]   (default tag: molscreen.assets.TAG)
The manifest lists each file's name, bytes and SHA-256, the last commit of results/activity_models.json (the
run whose results these models are), the commit bundled from, and the date. A copy goes to models/MANIFEST.json
so this checkout counts as installed. Publish with: gh release create <tag> dist/models-<tag>.zip
"""

import json
import subprocess
import sys
import zipfile
from datetime import date

from molscreen.assets import MANIFEST, TAG, sha256
from molscreen.train import MODELS


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], check=False, capture_output=True, text=True, cwd=MODELS.parent).stdout
    return out.strip() or "unknown"


tag = sys.argv[1] if len(sys.argv) > 1 else TAG
paths = sorted(MODELS.rglob("*.joblib"))
if not paths:
    sys.exit(f"no *.joblib under {MODELS}: train first (uv run python -m molscreen.train)")

manifest = {
    "tag": tag,
    "date": date.today().isoformat(),
    "results_commit": git("log", "-1", "--format=%h", "--", "results/activity_models.json"),
    "bundled_commit": git("rev-parse", "--short", "HEAD"),
    "files": [{"name": p.relative_to(MODELS).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
              for p in paths],
}
out = MODELS.parent / "dist" / f"models-{tag}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for p, f in zip(paths, manifest["files"]):
        zf.write(p, f["name"])
    zf.writestr(MANIFEST, json.dumps(manifest, indent=2))
(MODELS / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"{out}: {len(paths)} models, {out.stat().st_size / 1e6:.1f} MB")
print(f"SHA-256 {sha256(out)}")
