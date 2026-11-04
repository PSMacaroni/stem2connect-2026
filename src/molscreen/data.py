"""Per-target activity datasets from ChEMBL pulls, following docs/evaluation.md."""

from pathlib import Path

import pandas as pd

from molscreen.chem import canonical_smiles

ROOT = Path(__file__).resolve().parents[2]
PULLS = ROOT / "data" / "chembl"
DATASETS = ROOT / "data" / "datasets"
ACTIVE_PCHEMBL = 6.0  # 1 µM


def filter_activities(acts: pd.DataFrame) -> pd.DataFrame:
    """Rows that pass the docs/evaluation.md rules, with a parsed `smiles` column added."""
    comment = acts["data_validity_comment"].astype("string").fillna("").str.strip()
    keep = (
        acts["standard_type"].isin(["IC50", "Ki", "EC50"])
        & (acts["standard_relation"] == "=")
        & (comment == "")
        & acts["assay_type"].isin(["B", "F"])
        & acts["pchembl_value"].notna()
        & acts["canonical_smiles"].notna()
    )
    rows = acts[keep].copy()
    rows["smiles"] = rows["canonical_smiles"].map(canonical_smiles)
    return rows[rows["smiles"].notna()]


def aggregate(rows: pd.DataFrame) -> pd.DataFrame:
    """One row per molecule: median pChEMBL over its rows, label active if median >= 6.0."""
    out = rows.groupby("molecule_chembl_id", as_index=False).agg(
        smiles=("smiles", "first"), pchembl=("pchembl_value", "median"), n_rows=("pchembl_value", "size")
    )
    out["active"] = (out["pchembl"] >= ACTIVE_PCHEMBL).astype(int)
    return out[["molecule_chembl_id", "smiles", "pchembl", "active", "n_rows"]]


def build_dataset(gene: str, activities: pd.DataFrame | None = None) -> pd.DataFrame:
    """Clean dataset for `gene`. Reads data/chembl/<GENE>.csv (and writes data/datasets/<GENE>.csv) when
    `activities` is not given."""
    if activities is not None:
        return aggregate(filter_activities(activities))
    ds = aggregate(filter_activities(pd.read_csv(PULLS / f"{gene}.csv")))
    DATASETS.mkdir(parents=True, exist_ok=True)
    ds.to_csv(DATASETS / f"{gene}.csv", index=False)
    return ds


def load_dataset(gene: str) -> pd.DataFrame:
    return pd.read_csv(DATASETS / f"{gene}.csv")
