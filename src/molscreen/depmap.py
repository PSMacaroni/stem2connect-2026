"""Loop 2 data layer: DepMap 24Q4 hotspot mutations + PRISM 20Q2 drug sensitivity (cell lines, not patients).

Rules are in docs/evaluation-loop2.md. `nearest_cell_lines` is a lookup, not a prediction.

    python -m molscreen.depmap [--raw data/depmap] [--report results/loop2_data.md]
"""

import argparse
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from molscreen.chem import canonical_smiles

RAW = Path("data/depmap")
HOTSPOT = "OmicsSomaticMutationsMatrixHotspot.csv"
MODELS = "Model.csv"
PORTAL = "PortalCompounds.csv"
PRISM = "prism-repurposing-20q2-secondary-screen-dose-response-curve-parameters.csv"
# Only these are ever read from Model.csv; donor columns (Age, Sex, PatientRace, PatientID, ...) are never loaded.
MODEL_COLS = ["ModelID", "CellLineName", "OncotreeLineage", "OncotreePrimaryDisease"]
PRISM_COLS = ["broad_id", "depmap_id", "auc", "passed_str_profiling", "name", "moa", "target", "smiles"]


def hotspot_binary(raw: pd.DataFrame) -> pd.DataFrame:
    """0/1/2 hotspot matrix -> 0/1 (any hotspot mutation), columns `SYMBOL (Entrez)` -> `SYMBOL`."""
    out = (raw.fillna(0) > 0).astype("uint8")
    out.columns = out.columns.str.replace(r" \(.*\)$", "", regex=True)
    out.index.name = "ModelID"
    return out


def compound_id(broad_id: pd.Series) -> pd.Series:
    """Broad ID without the batch suffix: BRD-K36949735-001-01-1 -> BRD-K36949735."""
    return broad_id.str.split("-").str[:2].str.join("-")


def sensitivity_tables(prism: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """QC + median over replicate rows. Returns (sensitivity, compound annotations, counts)."""
    counts = {"prism_rows": len(prism)}
    p = prism[prism["passed_str_profiling"].astype(str).str.upper() == "TRUE"]
    counts["rows_after_str_qc"] = len(p)
    p = p.dropna(subset=["auc", "depmap_id"]).assign(compound=lambda d: compound_id(d["broad_id"]))
    counts["rows_after_dropping_missing_auc_or_id"] = len(p)
    # PRISM repeats one SMILES per batch, joined by ", " (a comma is not a SMILES character): keep the first.
    p = p.assign(smiles=p["smiles"].str.split(", ").str[0])
    grouped = p.groupby(["depmap_id", "compound"])["auc"]
    sens = grouped.median().reset_index().rename(columns={"depmap_id": "ModelID"})
    counts["pairs_with_replicates"] = int((grouped.size() > 1).sum())
    cpd = p.groupby("compound")[["name", "broad_id", "smiles", "target", "moa"]].first()
    cpd["name"] = cpd["name"].fillna(pd.Series(cpd.index, index=cpd.index))
    cpd["n_cell_lines"] = sens.groupby("compound").size()
    return sens, cpd.reset_index(), counts


def portal_chembl(portal: pd.DataFrame) -> pd.Series:
    """compound (BRD-K...) -> ChEMBL ID, via the BRD: sample IDs in DepMap's PortalCompounds.csv."""
    s = portal.assign(sid=portal["SampleIDs"].str.split(";")).explode("sid")
    s = s[s["sid"].str.startswith("BRD:", na=False)].dropna(subset=["ChEMBLID"])
    return s.assign(compound=compound_id(s["sid"].str[4:])).groupby("compound")["ChEMBLID"].first()


def build_tables(raw: Path = RAW, out: Path | None = None) -> dict:
    """Read the raw files in `raw`, write the derived CSVs to `out` (default raw/derived), return counts."""
    out = out or raw / "derived"
    out.mkdir(parents=True, exist_ok=True)
    hot = hotspot_binary(pd.read_csv(raw / HOTSPOT, index_col=0))
    models = pd.read_csv(raw / MODELS, usecols=MODEL_COLS)[MODEL_COLS]
    sens, cpd, counts = sensitivity_tables(pd.read_csv(raw / PRISM, usecols=PRISM_COLS, low_memory=False))
    cpd["chembl_id"] = cpd["compound"].map(portal_chembl(pd.read_csv(raw / PORTAL)))

    hot.to_csv(out / "hotspot_binary.csv")
    models.to_csv(out / "models.csv", index=False)
    sens.to_csv(out / "sensitivity.csv", index=False)
    cpd.to_csv(out / "compounds.csv", index=False)

    lines = set(sens["ModelID"])
    counts |= {
        "hotspot_cell_lines": hot.shape[0],
        "hotspot_genes": hot.shape[1],
        "hotspot_lines_with_any_mutation": int((hot.sum(axis=1) > 0).sum()),
        "model_rows": len(models),
        "prism_cell_lines": len(lines),
        "prism_compounds": len(cpd),
        "sensitivity_pairs": len(sens),
        "overlap_prism_and_hotspot": len(lines & set(hot.index)),
        "overlap_prism_and_model": len(lines & set(models["ModelID"])),
        "compounds_with_smiles": int(cpd["smiles"].notna().sum()),
        "compounds_smiles_parse_rdkit": int(cpd["smiles"].dropna().map(canonical_smiles).notna().sum()),
        "compounds_with_chembl_id": int(cpd["chembl_id"].notna().sum()),
        "compounds_with_300_plus_lines_in_hotspot": int(
            (sens[sens["ModelID"].isin(hot.index)].groupby("compound").size() >= 300).sum()
        ),
        "derived_bytes": {f.name: f.stat().st_size for f in sorted(out.glob("*.csv"))},
    }
    _load.cache_clear()
    return counts


@lru_cache(maxsize=4)
def _load(derived: str):
    d = Path(derived)
    hot = pd.read_csv(d / "hotspot_binary.csv", index_col=0)
    models = pd.read_csv(d / "models.csv").set_index("ModelID")
    sens = pd.read_csv(d / "sensitivity.csv")
    cpd = pd.read_csv(d / "compounds.csv").set_index("compound")
    return hot, models, sens, cpd


def gene_symbols(derived: Path = RAW / "derived") -> list[str]:
    """Gene symbols the lookup knows (the hotspot-matrix columns)."""
    return list(_load(str(derived))[0].columns)


def nearest_cell_lines(genes: list[str], k: int = 10, derived: Path = RAW / "derived") -> list[dict]:
    """The k screened cell lines whose hotspot genes are most like `genes` (Jaccard), ties by name.

    Only cell lines with PRISM data are searched. Genes not in the matrix are ignored; none known is an error.
    """
    hot, models, sens, _ = _load(str(derived))
    query = {g.strip().upper() for g in genes} & set(hot.columns)
    if not query:
        raise ValueError(f"none of {genes} is a gene in the DepMap hotspot matrix")
    hot = hot[hot.index.isin(sens["ModelID"])]
    x = hot.to_numpy(dtype=bool)
    q = hot.columns.isin(query)
    inter = x[:, q].sum(axis=1)
    jac = inter / (x.sum(axis=1) + q.sum() - inter)  # union >= |query| > 0
    res = pd.DataFrame({"ModelID": hot.index, "jaccard": jac}).join(models, on="ModelID")
    res["CellLineName"] = res["CellLineName"].fillna(res["ModelID"])
    res = res.sort_values(["jaccard", "CellLineName"], ascending=[False, True], kind="stable").head(k)
    cols = hot.columns.to_numpy()
    return [
        r
        | {
            "jaccard": round(float(r["jaccard"]), 4),
            "shared_genes": sorted(cols[x[hot.index.get_loc(r["ModelID"])] & q]),
        }
        for r in res.to_dict("records")
    ]


def top_compounds(model_id: str, n: int = 10, derived: Path = RAW / "derived") -> list[dict]:
    """The n compounds with the lowest `auc` (most sensitive) measured on one cell line, ties by name."""
    _, _, sens, cpd = _load(str(derived))
    s = sens[sens["ModelID"] == model_id].join(cpd[["name", "smiles", "target"]], on="compound")
    s = s.sort_values(["auc", "name"], kind="stable").head(n)
    return s[["compound", "name", "auc", "smiles", "target"]].to_dict("records")


def _report(
    counts: dict, pull_info: dict, example: list[dict], top: list[dict], genes: list[str], tied: int
) -> str:
    def cell(v):
        return "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v).replace("|", "/")

    c = counts
    total = sum(c["derived_bytes"].values())
    out = [
        "# Loop 2 data: DepMap 24Q4 hotspot mutations + PRISM 20Q2 sensitivity",
        "",
        (
            "Built by `python -m molscreen.depmap` from the files pulled by `scripts/pull_depmap.py` "
            f"(pulled {pull_info['date']}). Rules: `docs/evaluation-loop2.md`. Cell lines, not patients. "
            "Research and learning tool, not medical advice."
        ),
        "",
        "## Counts (from the run)",
        "| What | Count | How |",
        "|---|---|---|",
        f"| Cell lines in the hotspot matrix | {c['hotspot_cell_lines']:,} | rows of `{HOTSPOT}` |",
        f"| Genes in the hotspot matrix | {c['hotspot_genes']:,} | columns of the same file |",
        f"| Hotspot lines with at least one hotspot | {c['hotspot_lines_with_any_mutation']:,} | row sum > 0 |",
        f"| Rows in `Model.csv` | {c['model_rows']:,} | 4 columns read, donor columns never read |",
        f"| PRISM rows | {c['prism_rows']:,} | all rows of the 20Q2 secondary dose-response file |",
        f"| PRISM rows after QC | {c['rows_after_str_qc']:,} | `passed_str_profiling` TRUE |",
        (
            f"| PRISM rows with `auc` and `depmap_id` | {c['rows_after_dropping_missing_auc_or_id']:,} | "
            "rows without a `depmap_id` cannot be joined |"
        ),
        f"| PRISM cell lines (after QC) | {c['prism_cell_lines']:,} | distinct `depmap_id` |",
        f"| PRISM compounds | {c['prism_compounds']:,} | Broad ID without batch suffix |",
        f"| (cell line, compound) values | {c['sensitivity_pairs']:,} | median `auc` per pair |",
        f"| Pairs with more than one row (median taken) | {c['pairs_with_replicates']:,} | replicate screens |",
        (
            f"| PRISM lines also in the hotspot matrix | {c['overlap_prism_and_hotspot']:,} | "
            "`depmap_id` = matrix row ID |"
        ),
        f"| PRISM lines also in `Model.csv` | {c['overlap_prism_and_model']:,} | `depmap_id` = `ModelID` |",
        f"| Compounds with a SMILES | {c['compounds_with_smiles']:,} | PRISM `smiles` column |",
        (
            f"| Compounds whose SMILES parses in RDKit | {c['compounds_smiles_parse_rdkit']:,} | "
            "`molscreen.chem.canonical_smiles` |"
        ),
        f"| Compounds with a ChEMBL ID | {c['compounds_with_chembl_id']:,} | via `BRD:` IDs in `{PORTAL}` |",
        (
            f"| Compounds with >= 300 lines in the hotspot matrix | "
            f"{c['compounds_with_300_plus_lines_in_hotspot']:,} | candidates for per-drug models |"
        ),
        "",
        "## Raw files (SHA-256 recorded on download)",
        "| File | Bytes | SHA-256 |",
        "|---|---|---|",
        *[f"| `{n}` | {f['bytes']:,} | `{f['sha256']}` |" for n, f in pull_info["files"].items()],
        "",
        "## Derived tables (`data/depmap/derived/`, git-ignored, not committed)",
        *[f"- `{n}`: {b:,} bytes" for n, b in c["derived_bytes"].items()],
        f"- Total {total:,} bytes: {'under' if total < 5e6 else 'over'} 5 MB.",
        "",
        f"## Worked example: nearest cell lines for {genes}",
        "| # | ModelID | Cell line | Lineage | Primary disease | Jaccard | Shared genes |",
        "|---|---|---|---|---|---|---|",
        *[
            f"| {i} | {r['ModelID']} | {cell(r['CellLineName'])} | {cell(r['OncotreeLineage'])} | "
            f"{cell(r['OncotreePrimaryDisease'])} | {r['jaccard']} | {', '.join(r['shared_genes'])} |"
            for i, r in enumerate(example, 1)
        ],
        "",
        (
            f"{tied:,} screened cell lines have Jaccard {example[-1]['jaccard']} (the 10th value), so the order among "
            "them is only the tie-break by cell line name (case-sensitive sort)."
        ),
        "",
        f"### Top 10 compounds (lowest `auc`) for {example[0]['ModelID']} ({cell(example[0]['CellLineName'])})",
        "| # | Compound | Name | auc | Target | SMILES |",
        "|---|---|---|---|---|---|",
        *[
            f"| {i} | {t['compound']} | {cell(t['name'])} | {t['auc']:.3f} | {cell(t['target'])} | "
            f"`{cell(t['smiles'])}` |"
            for i, t in enumerate(top, 1)
        ],
        "",
        "## Credit lines (for the README)",
        (
            "- **DepMap 24Q4 Public** (hotspot mutations, cell-line annotations, compound map), Broad Institute. Figshare+, "
            "doi:10.25452/figshare.plus.27993248. CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)."
        ),
        (
            "- **PRISM Repurposing 20Q2** (secondary-screen dose-response), Broad Institute; DepMap, Corsello S, Kocak M, "
            "Golub T. figshare, doi:10.6084/m9.figshare.20564034. CC BY 4.0. Corsello SM, Nagari RT, Spangler RD, et al. "
            "Discovering the anticancer potential of non-oncology drugs by systematic viability profiling. "
            "*Nat Cancer.* 2020;1(2):235-248. doi:10.1038/s43018-019-0018-6"
        ),
        (
            "- Tsherniak A, Vazquez F, Montgomery PG, et al. Defining a Cancer Dependency Map. *Cell.* "
            "2017;170(3):564-576.e16. doi:10.1016/j.cell.2017.06.010"
        ),
        (
            "- Mutation data: Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer "
            "Cell Line Encyclopedia. *Nature.* 2019;569(7757):503-508. doi:10.1038/s41586-019-1186-3"
        ),
        "",
    ]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build loop-2 derived tables and the data report.")
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--report", type=Path, default=Path("results/loop2_data.md"))
    a = ap.parse_args()
    counts = build_tables(a.raw)
    genes = ["KRAS", "TP53", "STK11"]
    example = nearest_cell_lines(genes, derived=a.raw / "derived")
    top = top_compounds(example[0]["ModelID"], derived=a.raw / "derived")
    every = nearest_cell_lines(genes, k=10**6, derived=a.raw / "derived")
    tied = sum(r["jaccard"] == example[-1]["jaccard"] for r in every)
    pull_info = json.loads((a.raw / "PULL_INFO.json").read_text())
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(_report(counts, pull_info, example, top, genes, tied), encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
