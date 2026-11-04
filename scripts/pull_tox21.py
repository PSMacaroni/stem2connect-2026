#!/usr/bin/env python3
"""Download the MoleculeNet Tox21 file used by loop 3 (docs/data-registry.md section 2; no licence stated).

    python scripts/pull_tox21.py [--out data/tox21]

Writes tox21.csv.gz and PULL_INFO.json (URL, bytes, SHA-256). The raw file is git-ignored and never committed.
"""

import argparse
import datetime
import hashlib
import json
import urllib.request
from pathlib import Path

URL = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "data" / "tox21"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=120) as r:
        body = r.read()
    (out / "tox21.csv.gz").write_bytes(body)
    info = {
        "url": URL, "date": datetime.date.today().isoformat(), "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "licence": "none stated (US-government programme data, probably public domain, not verified)",
        "cite": ["doi:10.1039/C7SC02664A", "doi:10.3389/fenvs.2015.00085"],
    }
    (out / "PULL_INFO.json").write_text(json.dumps(info, indent=2) + "\n")
    print(f"tox21.csv.gz: {info['bytes']:,} bytes, sha256 {info['sha256']}")


if __name__ == "__main__":
    main()
