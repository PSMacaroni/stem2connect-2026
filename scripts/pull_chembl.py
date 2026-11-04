"""Pull IC50/Ki/EC50 activities with a pChEMBL value for the loop-1 targets from the ChEMBL REST API.

Writes data/chembl/<GENE>.csv and data/chembl/PULL_INFO.json. Sequential requests only (be polite to EBI).
Usage: uv run python scripts/pull_chembl.py [--genes CDK6 EGFR]
"""

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

BASE = "https://www.ebi.ac.uk"
API = BASE + "/chembl/api/data"
TARGETS = {  # gene -> ChEMBL target ID, from docs/data-registry.md section 1
    "EGFR": "CHEMBL203", "BRAF": "CHEMBL5145", "ERBB2": "CHEMBL1824", "CDK4": "CHEMBL331", "CDK6": "CHEMBL2508",
    "ALK": "CHEMBL4247", "ABL1": "CHEMBL1862", "PARP1": "CHEMBL3105", "BCL2": "CHEMBL4860",
}
FIELDS = [
    "molecule_chembl_id", "canonical_smiles", "standard_type", "standard_relation", "standard_value",
    "standard_units", "pchembl_value", "assay_chembl_id", "assay_type", "data_validity_comment",
    "document_chembl_id", "target_organism", "assay_variant_mutation",
]
OUT = Path(__file__).resolve().parents[1] / "data" / "chembl"


def get_json(url: str, tries: int = 5) -> dict:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "molscreen/0.1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:
                raise
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
        time.sleep(2 * (attempt + 1))
    raise AssertionError("unreachable")


def query_url(target_id: str) -> str:
    params = {
        "target_chembl_id": target_id, "pchembl_value__isnull": "false", "standard_type__in": "IC50,Ki,EC50",
        "only": ",".join(FIELDS), "limit": 1000, "offset": 0,
    }
    return f"{API}/activity.json?{urllib.parse.urlencode(params, safe=',')}"


def pull(gene: str) -> tuple[int, str]:
    first = url = query_url(TARGETS[gene])
    rows: list[dict] = []
    total = None
    while url:
        page = get_json(url)
        rows += [{f: a.get(f) for f in FIELDS} for a in page["activities"]]
        total = page["page_meta"]["total_count"]
        nxt = page["page_meta"]["next"]
        url = BASE + nxt if nxt else None
        time.sleep(0.2)
    if len(rows) != total:
        raise RuntimeError(f"{gene}: got {len(rows)} rows, API says {total}")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{gene}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows), first


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--genes", nargs="+", default=list(TARGETS), choices=list(TARGETS))
    genes = ap.parse_args().genes

    status = get_json(f"{API}/status.json")
    info_path = OUT / "PULL_INFO.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {"targets": {}}
    info["release"] = status["chembl_db_version"]
    info["release_date"] = status["chembl_release_date"]
    for gene in genes:
        n, url = pull(gene)
        info["targets"][gene] = {
            "target_chembl_id": TARGETS[gene], "rows": n, "pulled": date.today().isoformat(),
            "release": status["chembl_db_version"], "query_url": url,
        }
        print(f"{gene} {TARGETS[gene]}: {n} rows")
    info_path.write_text(json.dumps(info, indent=2) + "\n")
    print(f"release {info['release']}; wrote {info_path}")


if __name__ == "__main__":
    main()
