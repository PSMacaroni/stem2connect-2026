#!/usr/bin/env python3
"""Download the DepMap 24Q4 and PRISM 20Q2 Figshare files used by loop 2 (all CC BY 4.0).

    python scripts/pull_depmap.py [--out data/depmap]

File IDs and DOIs come from docs/data-registry.md section 3b. Writes PULL_INFO.json next to the files.
"""

import argparse
import datetime
import hashlib
import json
import time
import urllib.request
from pathlib import Path

DEPMAP_DOI = "10.25452/figshare.plus.27993248.v1"
PRISM_DOI = "10.6084/m9.figshare.20564034.v1"
FILES = {  # name on disk: (Figshare file ID, DOI of the record)
    "OmicsSomaticMutationsMatrixHotspot.csv": (51065750, DEPMAP_DOI),
    "OmicsSomaticMutations.csv": (51065732, DEPMAP_DOI),
    "Model.csv": (51065297, DEPMAP_DOI),
    "PortalCompounds.csv": (51065762, DEPMAP_DOI),
    "prism-repurposing-20q2-secondary-screen-dose-response-curve-parameters.csv": (36794595, PRISM_DOI),
}


def download(url: str, dest: Path) -> tuple[int, str]:
    """Stream `url` to `dest` (urllib follows the 302 to S3); return (bytes, sha256). Retries once."""
    for attempt in (1, 2):
        try:
            sha, n = hashlib.sha256(), 0
            tmp = dest.with_suffix(dest.suffix + ".part")
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
                    sha.update(chunk)
                    n += len(chunk)
            tmp.replace(dest)
            return n, sha.hexdigest()
        except OSError as e:
            if attempt == 2:
                raise
            print(f"  retrying after {e}")
            time.sleep(5)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="data/depmap")
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    info = {"licence": "CC BY 4.0", "date": datetime.date.today().isoformat(), "files": {}}
    for name, (fid, doi) in FILES.items():
        url = f"https://ndownloader.figshare.com/files/{fid}"
        print(f"{name} <- {url}")
        n, sha = download(url, out / name)
        info["files"][name] = {"url": url, "doi": doi, "bytes": n, "sha256": sha}
        print(f"  {n:,} bytes, sha256 {sha}")
    (out / "PULL_INFO.json").write_text(json.dumps(info, indent=2) + "\n")


if __name__ == "__main__":
    main()
