"""Zip the trained models and the derived DepMap tables into dist/models-<tag>.zip, for a GitHub release.

Usage: uv run python scripts/bundle_models.py [tag]   (default tag: molscreen.assets.TAG)
Bundles models/**/*.joblib, data/depmap/derived/*.csv and data/depmap/PULL_INFO.json (provenance), each named by
its path from the repo root. models/MANIFEST.json lists each file's name, bytes and SHA-256, the last commit of
results/activity_models.json, the commit bundled from, and the date; a copy is written to this checkout so it
counts as installed. Publish with: gh release create <tag> dist/models-<tag>.zip
"""

import json
import subprocess
import sys
import zipfile
from datetime import date

from molscreen.assets import MANIFEST, TAG, sha256
from molscreen.data import ROOT


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], check=False, capture_output=True, text=True, cwd=ROOT).stdout
    return out.strip() or "unknown"


tag = sys.argv[1] if len(sys.argv) > 1 else TAG
models = sorted((ROOT / "models").rglob("*.joblib"))
tables = sorted((ROOT / "data" / "depmap" / "derived").glob("*.csv"))
if not models or not tables:
    sys.exit("need models/*.joblib (uv run python -m molscreen.train) and data/depmap/derived/*.csv "
             "(scripts/pull_depmap.py)")
paths = models + tables + [p for p in [ROOT / "data" / "depmap" / "PULL_INFO.json"] if p.exists()]

manifest = {
    "tag": tag,
    "date": date.today().isoformat(),
    "results_commit": git("log", "-1", "--format=%h", "--", "results/activity_models.json"),
    "bundled_commit": git("rev-parse", "--short", "HEAD"),
    "files": [{"name": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
              for p in paths],
}
out = ROOT / "dist" / f"models-{tag}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for p, f in zip(paths, manifest["files"]):
        zf.write(p, f["name"])
    zf.writestr(MANIFEST, json.dumps(manifest, indent=2))
(ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"{out}: {len(paths)} files ({len(models)} models, {len(tables)} tables), {out.stat().st_size:,} bytes")
print(f"SHA-256 {sha256(out)}")
