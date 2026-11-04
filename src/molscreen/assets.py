"""Get the trained models: download the release zip once, verify every file, keep what already matches.

The zip is made by scripts/bundle_models.py and holds the models plus MANIFEST.json (name, bytes, SHA-256 of each).
Stdlib only, anonymous download (the release is public). Env overrides: MOLSCREEN_MODELS_URL, MOLSCREEN_MODELS_SHA256.
"""

import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from molscreen.train import MODELS

TAG = "v1"  # the release tag; change it (or set MOLSCREEN_MODELS_URL) when a new bundle is published
DEFAULT_URL = f"https://github.com/PSMacaroni/stem2connect-2026/releases/download/{TAG}/models-{TAG}.zip"
MANIFEST = "MANIFEST.json"


def models_url() -> str:
    return os.environ.get("MOLSCREEN_MODELS_URL") or DEFAULT_URL


def sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def installed(dest: Path) -> bool:
    """True when dest/MANIFEST.json exists and every file it names is there with the same SHA-256."""
    try:
        files = json.loads((dest / MANIFEST).read_text(encoding="utf-8"))["files"]
    except (OSError, ValueError, KeyError):
        return False
    return all((dest / f["name"]).is_file() and sha256(dest / f["name"]) == f["sha256"] for f in files)


def ensure_models(url: str | None = None, dest: Path = MODELS) -> Path:
    """Make sure dest holds the verified models; download and unpack the release zip only when it does not."""
    dest = Path(dest)
    if installed(dest):
        print(f"models: {dest} already verified, nothing to do")
        return dest
    url = url or models_url()
    print(f"models: downloading {url}")
    with tempfile.TemporaryFile() as tmp:
        h = hashlib.sha256()
        with urllib.request.urlopen(url, timeout=60) as r:
            while chunk := r.read(1 << 20):
                h.update(chunk)
                tmp.write(chunk)
        want = os.environ.get("MOLSCREEN_MODELS_SHA256")
        if not want:
            print(f"models: WARNING MOLSCREEN_MODELS_SHA256 not set, zip SHA-256 {h.hexdigest()} not checked")
        elif h.hexdigest() != want.lower():
            raise ValueError(f"models zip from {url} has SHA-256 {h.hexdigest()}, expected {want}")
        else:
            print("models: zip SHA-256 matches MOLSCREEN_MODELS_SHA256")
        tmp.seek(0)
        with zipfile.ZipFile(tmp) as zf:
            manifest = json.loads(zf.read(MANIFEST))
            dest.mkdir(parents=True, exist_ok=True)
            for f in manifest["files"]:
                target = (dest / f["name"]).resolve()
                if not target.is_relative_to(dest.resolve()):
                    raise ValueError(f"models zip names a file outside {dest}: {f['name']}")
                if target.is_file() and sha256(target) == f["sha256"]:
                    print(f"models: {f['name']} already matches, kept")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                part = target.with_name(target.name + ".part")
                with zf.open(f["name"]) as src, open(part, "wb") as out:
                    shutil.copyfileobj(src, out)
                if sha256(part) != f["sha256"]:
                    part.unlink()
                    raise ValueError(f"models zip file {f['name']} does not match its SHA-256 in {MANIFEST}")
                os.replace(part, target)
                print(f"models: {f['name']} extracted and verified")
    (dest / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")  # last: marks a complete install
    print(f"models: {len(manifest['files'])} files verified in {dest}")
    return dest
