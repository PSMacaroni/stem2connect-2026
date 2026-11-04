"""Per-target activity datasets from ChEMBL pulls, following docs/evaluation.md (with its amendments)."""

from pathlib import Path

import pandas as pd
from rdkit import Chem

from molscreen.chem import canonical_smiles

ROOT = Path(__file__).resolve().parents[2]
PULLS = ROOT / "data" / "chembl"
DATASETS = ROOT / "data" / "datasets"
ACTIVE_PCHEMBL = 6.0  # 1 µM


def _text(col: pd.Series) -> pd.Series:
    return col.astype("string").fillna("").str.strip()


def is_mutant(acts: pd.DataFrame) -> pd.Series:
    """Rows whose assay declares a protein variant (non-empty `assay_variant_mutation`)."""
    return _text(acts["assay_variant_mutation"]) != ""


def parent_smiles(smiles: str) -> str | None:
    """Strip salts: canonical SMILES (stereo kept) of the fragment with the most heavy atoms. None if unparseable.
    Charges are not neutralised, so e.g. a sodium carboxylate stays a carboxylate anion."""
    mol = Chem.MolFromSmiles(smiles) if isinstance(smiles, str) and smiles else None
    if mol is None:
        return None
    frags = Chem.GetMolFrags(mol, asMols=True)
    return canonical_smiles(Chem.MolToSmiles(max(frags, key=lambda m: (m.GetNumHeavyAtoms(), Chem.MolToSmiles(m)))))


def filter_activities(acts: pd.DataFrame) -> pd.DataFrame:
    """Rows that pass the docs/evaluation.md rules, with the parent SMILES in a `smiles` column."""
    keep = (
        acts["standard_type"].isin(["IC50", "Ki", "EC50"])
        & (acts["standard_relation"] == "=")
        & (_text(acts["data_validity_comment"]) == "")
        & acts["assay_type"].isin(["B", "F"])
        & ~is_mutant(acts)
        & acts["pchembl_value"].notna()
        & acts["canonical_smiles"].notna()
    )
    rows = acts[keep].copy()
    parents = {s: parent_smiles(s) for s in rows["canonical_smiles"].unique()}
    rows["smiles"] = rows["canonical_smiles"].map(parents)
    return rows[rows["smiles"].notna()]


def aggregate(rows: pd.DataFrame) -> pd.DataFrame:
    """One row per parent molecule: its ChEMBL IDs, median pChEMBL over all their rows, active if >= 6.0."""
    out = rows.groupby("smiles", as_index=False).agg(
        molecule_chembl_ids=("molecule_chembl_id", lambda s: ";".join(sorted(set(s)))),
        n_ids=("molecule_chembl_id", "nunique"),
        pchembl=("pchembl_value", "median"),
        n_rows=("pchembl_value", "size"),
    )
    out["active"] = (out["pchembl"] >= ACTIVE_PCHEMBL).astype(int)
    return out[["smiles", "molecule_chembl_ids", "n_ids", "pchembl", "active", "n_rows"]]


def build_dataset(gene: str, activities: pd.DataFrame | None = None) -> pd.DataFrame:
    """Clean dataset for `gene`, in memory. Reads data/chembl/<GENE>.csv when `activities` is not given."""
    acts = pd.read_csv(PULLS / f"{gene}.csv") if activities is None else activities
    return aggregate(filter_activities(acts))


def save_dataset(gene: str, ds: pd.DataFrame) -> None:
    DATASETS.mkdir(parents=True, exist_ok=True)
    ds.to_csv(DATASETS / f"{gene}.csv", index=False)


def load_dataset(gene: str) -> pd.DataFrame:
    return pd.read_csv(DATASETS / f"{gene}.csv")
