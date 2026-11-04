import numpy as np

from molscreen.chem import canonical_smiles, morgan_fp, murcko_scaffold, scaffold_split, tanimoto

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"


def test_invalid_smiles_returns_none():
    assert canonical_smiles("not a smiles") is None
    assert canonical_smiles("C1CC") is None  # unclosed ring
    assert canonical_smiles("") is None


def test_canonicalization_is_idempotent():
    for s in [ASPIRIN, "OCC", "c1ccccc1O"]:
        once = canonical_smiles(s)
        assert once is not None and canonical_smiles(once) == once
    assert canonical_smiles("OCC") == canonical_smiles("CCO")


def test_morgan_fp_shape_and_dtype():
    fp = morgan_fp("CCO")
    assert fp.shape == (2048,) and fp.dtype == np.uint8 and fp.sum() > 0


def test_tanimoto():
    a = morgan_fp(ASPIRIN)
    assert tanimoto(a, a) == 1.0
    assert tanimoto(a, morgan_fp("CCCCCCCCCC")) < 1.0


def test_scaffold_split_is_disjoint_and_complete():
    smiles = [
        "c1ccccc1O", "c1ccccc1N", "c1ccccc1C", "c1ccccc1Cl",  # benzene scaffold x4
        "C1CCNCC1C", "C1CCNCC1O",  # piperidine x2
        "c1ccc2ccccc2c1O", "c1ccc2ccccc2c1N",  # naphthalene x2
        "c1ccncc1C",  # pyridine
        "CCO",  # acyclic, empty scaffold
    ]
    train, test = scaffold_split(smiles, test_frac=0.2)
    assert sorted(train + test) == list(range(len(smiles)))
    assert train and test
    train_scaffolds = {murcko_scaffold(smiles[i]) for i in train}
    test_scaffolds = {murcko_scaffold(smiles[i]) for i in test}
    assert not train_scaffolds & test_scaffolds
