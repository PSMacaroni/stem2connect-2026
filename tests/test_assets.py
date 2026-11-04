import hashlib
import json
import zipfile

import pytest

from molscreen.assets import MANIFEST, ensure_models

FILES = {"models/A.joblib": b"model a", "models/loop2/B.joblib": b"model b", "data/x/y.csv": b"a,b\n1,2\n"}


def make_zip(path, files=FILES, lie=None):
    manifest = {"files": [{"name": n, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
                          for n, b in files.items()]}
    with zipfile.ZipFile(path, "w") as zf:
        for n, b in files.items():
            zf.writestr(n, lie if lie and n == "data/x/y.csv" else b)
        zf.writestr(MANIFEST, json.dumps(manifest))
    return path.as_uri()


def test_install_verify_and_noop(tmp_path, monkeypatch):
    monkeypatch.delenv("MOLSCREEN_MODELS_SHA256", raising=False)
    url, dest = make_zip(tmp_path / "m.zip"), tmp_path / "repo"
    ensure_models(url, dest)
    assert {n: (dest / n).read_bytes() for n in FILES} == FILES
    assert (dest / MANIFEST).exists()
    mtime = (dest / "data/x/y.csv").stat().st_mtime_ns
    ensure_models(tmp_path.joinpath("missing.zip").as_uri(), dest)  # no download: a bad URL would raise
    assert (dest / "data/x/y.csv").stat().st_mtime_ns == mtime


def test_tampered_file_raises(tmp_path):
    url, dest = make_zip(tmp_path / "m.zip", lie=b"tampered"), tmp_path / "repo"
    with pytest.raises(ValueError, match="y.csv"):
        ensure_models(url, dest)
    assert not (dest / MANIFEST).exists()


def test_path_outside_dest_raises(tmp_path):
    url, dest = make_zip(tmp_path / "m.zip", files={"../evil.csv": b"x"}), tmp_path / "repo"
    with pytest.raises(ValueError, match="outside"):
        ensure_models(url, dest)
    assert not (tmp_path / "evil.csv").exists()


def test_zip_sha_mismatch_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("MOLSCREEN_MODELS_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="expected"):
        ensure_models(make_zip(tmp_path / "m.zip"), tmp_path / "repo")
