"""Small pure chemistry helpers built on RDKit."""

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

from molscreen.split import group_split

RDLogger.DisableLog("rdApp.*")  # invalid SMILES are expected input; we return None instead of printing


def _mol(smiles: str) -> Chem.Mol:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"invalid SMILES: {smiles!r}")
    return mol


def canonical_smiles(s: str) -> str | None:
    """RDKit canonical SMILES, or None if `s` does not parse."""
    mol = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToSmiles(mol) if mol is not None else None


def morgan_fp(smiles: str, radius: int = 2, n_bits: int = 2048) -> np.ndarray:
    """Morgan (ECFP-like) bit fingerprint as a uint8 0/1 array of length `n_bits`."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    return gen.GetFingerprintAsNumPy(_mol(smiles)).astype(np.uint8)


def tanimoto(a: np.ndarray, b: np.ndarray) -> float:
    """Tanimoto similarity of two 0/1 fingerprints. Two empty fingerprints score 0.0."""
    a, b = a.astype(bool), b.astype(bool)
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 0.0


def murcko_scaffold(smiles: str) -> str:
    """Bemis-Murcko scaffold SMILES (ring systems plus linkers). Acyclic molecules give ""."""
    return MurckoScaffold.MurckoScaffoldSmiles(mol=_mol(smiles), includeChirality=False)


def scaffold_split(smiles_list: list[str], test_frac: float = 0.2, seed: int = 0) -> tuple[list[int], list[int]]:
    """MoleculeNet-style scaffold split: no Murcko scaffold appears in both train and test.

    Scaffold groups go to train largest first while they fit under (1 - test_frac) of the data;
    groups that do not fit go to test. `seed` only breaks ties between groups of equal size.
    """
    return group_split([murcko_scaffold(s) for s in smiles_list], test_frac, seed)
