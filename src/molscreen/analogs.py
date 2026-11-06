"""Loop 4: single-point RDKit edits to one molecule, scored by the loop-1 activity model and the loop-3 Tox21 models.

This is enumeration, not generation: a fixed list of reaction SMARTS is applied to the parent, one edit at a time.
There is no trained generator and no sampling, so the whole output is reproducible and every analog can be named by
the edit that made it.

The nine transforms, and what each does:

| name                              | what changes                                              |
|-----------------------------------|-----------------------------------------------------------|
| add fluorine to a ring            | an aromatic C-H becomes C-F                                |
| add chlorine to a ring            | an aromatic C-H becomes C-Cl                               |
| add a methyl to a ring            | an aromatic C-H becomes C-CH3                              |
| swap a ring CH for N              | an aromatic C-H becomes a ring nitrogen (aza-scan)         |
| swap ring chlorine for fluorine   | an aromatic C-Cl becomes C-F                               |
| methylate a phenol                | an aromatic O-H becomes O-CH3                              |
| strip the methyl off a ring ether | an aromatic O-CH3 becomes O-H                              |
| methylate an N-H                  | an amine N-H gains a methyl                                |
| acid to primary amide             | -C(=O)OH becomes -C(=O)NH2                                 |

Why this list. These are the cheapest and most common single-point changes in medicinal chemistry: the halogen,
methyl and aza scans, O- and N-methylation, a halogen swap, and the acid-to-amide bioisostere. Each one edits a
single atom or a single small group, so the analog stays close to the parent and a student can see exactly what
moved. The list is also balanced rather than one-directional: methylating a phenol and stripping a ring methyl
ether are each other's inverse, as are adding a ring halogen and swapping one halogen for a smaller one, so the
set does not drift towards bigger, greasier molecules the way an "add a group" list would.

Scoring reuses loops 1 and 3 unchanged, including both abstain rules: an analog whose max Tanimoto to the activity
model's training set is below the target's cut-off gets no p_active, and the Tox21 models' own abstain flag comes
back with the count so the caller can withhold that too. The two scores are reported side by side and never
combined: nothing in the held-out evaluation supports a single "goodness" number.
"""

from rdkit import Chem
from rdkit.Chem import AllChem

from molscreen.chem import canonical_smiles, morgan_fp, tanimoto
from molscreen.data import parent_smiles
from molscreen.predict import predict
from molscreen.tox import predict_tox

# name -> reaction SMARTS. One edit per reaction; see the module docstring for why these nine.
TRANSFORMS = {
    "add fluorine to a ring": "[cH:1]>>[c:1]F",
    "add chlorine to a ring": "[cH:1]>>[c:1]Cl",
    "add a methyl to a ring": "[cH:1]>>[c:1]C",
    "swap a ring CH for N": "[cH:1]>>[n:1]",
    "swap ring chlorine for fluorine": "[c:1]Cl>>[c:1]F",
    "methylate a phenol": "[c:1][OX2H:2]>>[c:1][O:2]C",
    "strip the methyl off a ring ether": "[c:1][OX2:2][CH3]>>[c:1][O:2]",
    "methylate an N-H": "[NX3;H1,H2;!$(N=*):1]>>[N:1]C",
    "acid to primary amide": "[CX3:1](=[OX1:2])[OX2H]>>[C:1](=[O:2])N",
}
MAX_ANALOGS = 200  # cap before scoring, so one click stays responsive
DEFAULT_TOP = 10
MAX_TOP = 25


def _products(mol: Chem.Mol, smarts: str) -> list[str]:
    """Canonical SMILES of every product RDKit can sanitise from one transform on `mol`."""
    out = []
    for (product,) in AllChem.ReactionFromSmarts(smarts).RunReactants((mol,)):
        try:
            Chem.SanitizeMol(product)
        except (Chem.AtomValenceException, Chem.KekulizeException, ValueError):
            continue
        if (s := canonical_smiles(Chem.MolToSmiles(product))) is not None:
            out.append(s)
    return out


def enumerate_analogs(smiles: str, limit: int = MAX_ANALOGS) -> list[dict]:
    """Single-point analogs of `smiles`, as dicts with `smiles` and the `transform` that made them.

    Salts are stripped first (data.parent_smiles), products RDKit cannot sanitise are dropped, duplicates are
    deduplicated by canonical SMILES keeping the first transform that reached them, and the parent itself is
    dropped. At most `limit` analogs come back; the transforms are tried in TRANSFORMS order, so a cap that bites
    drops the later ones. Returns [] if `smiles` does not parse.
    """
    parent = parent_smiles(smiles)
    if parent is None:
        return []
    mol = Chem.MolFromSmiles(parent)
    seen, out = {parent}, []
    for name, smarts in TRANSFORMS.items():
        for s in _products(mol, smarts):
            if s in seen:
                continue
            seen.add(s)
            out.append({"smiles": s, "transform": name})
            if len(out) == limit:
                return out
    return out


def score_analogs(gene: str, smiles: str, limit: int = MAX_ANALOGS) -> list[dict]:
    """The parent first, then its analogs ranked by p_active (highest first); abstaining analogs come last.

    One dict per molecule: `smiles`, `transform` (None for the parent), `is_parent`, `p_active` (None when the
    activity model abstains), `abstain`, `abstain_cutoff`, `max_tanimoto` (to the activity model's training set),
    `tanimoto_to_parent`, `tox_above` (how many of the 12 Tox21 assays score above their own active rate),
    `tox_abstain` (the Tox21 models' own abstain flag). Returns [] if `smiles` does not parse.

    The activity and safety numbers are never combined: see the module docstring.
    """
    analogs = enumerate_analogs(smiles, limit)
    parent = parent_smiles(smiles)
    if parent is None:
        return []
    all_smiles = [parent] + [a["smiles"] for a in analogs]
    fp_parent = morgan_fp(parent)
    rows = []
    for mol, act, tox in zip([{"transform": None}] + analogs, predict(gene, all_smiles), predict_tox(all_smiles)):
        rows.append({
            "smiles": act["smiles"], "transform": mol["transform"], "is_parent": mol["transform"] is None,
            "p_active": None if act["abstain"] else act["p_active"], "abstain": act["abstain"],
            "abstain_cutoff": act["abstain_cutoff"], "max_tanimoto": act["max_tanimoto"],
            "tanimoto_to_parent": tanimoto(fp_parent, morgan_fp(act["smiles"])),
            "tox_above": sum(a["above_prevalence"] for a in tox["assays"].values()),
            "tox_abstain": tox["abstain"],
        })
    head, rest = rows[0], rows[1:]
    rest.sort(key=lambda r: (r["p_active"] is None, -(r["p_active"] or 0.0), r["smiles"]))
    return [head] + rest
