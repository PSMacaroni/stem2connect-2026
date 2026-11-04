import numpy as np
import pandas as pd

from molscreen.chem import murcko_scaffold
from molscreen.train import abstain_cutoff, fingerprints, max_tanimoto, metrics, roc_auc_ci, split

SMILES = [
    "c1ccccc1O", "c1ccccc1N", "c1ccccc1C", "c1ccccc1Cl", "c1ccccc1CC",
    "C1CCNCC1C", "C1CCNCC1O", "c1ccc2ccccc2c1O", "c1ccc2ccccc2c1N", "c1ccncc1C", "CCO", "CCCN",
]


def test_split_scaffolds_disjoint():
    ds = pd.DataFrame({"smiles": SMILES})
    tr, te = split(ds)
    assert len(tr) + len(te) == len(SMILES) and len(te) > 0
    assert not {murcko_scaffold(s) for s in tr["smiles"]} & {murcko_scaffold(s) for s in te["smiles"]}


def test_metrics_on_toy_set():
    y = np.array([0, 0, 1, 1])
    perfect = metrics(y, np.array([0.1, 0.2, 0.8, 0.9]), np.array([0, 0, 1, 1]))
    assert perfect == {"roc_auc": 1.0, "pr_auc": 1.0, "pr_auc_inactive": 1.0, "balanced_acc": 1.0}
    const = metrics(y, np.zeros(4), np.zeros(4, int))
    assert const["roc_auc"] == 0.5 and const["pr_auc"] == 0.5 and const["balanced_acc"] == 0.5
    assert metrics(np.ones(3, int), np.ones(3), np.ones(3, int))["roc_auc"] is None
    # inactive-class PR-AUC of a constant score = the inactive fraction (here 3 of 4)
    assert metrics(np.array([0, 0, 0, 1]), np.zeros(4), np.zeros(4, int))["pr_auc_inactive"] == 0.75


def test_roc_auc_ci_brackets_the_auc():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 200)
    score = y + rng.normal(0, 1, 200)
    lo, hi = roc_auc_ci(y, score, n=200)
    assert 0.5 < lo < metrics(y, score, y)["roc_auc"] < hi <= 1.0
    assert roc_auc_ci(y, score, n=200) == [lo, hi]  # seeded


def test_max_tanimoto_and_abstain_cutoff():
    fps = fingerprints(SMILES)
    sim, nn = max_tanimoto(fps[:2], fps)
    assert np.allclose(sim, 1.0) and list(nn) == [0, 1]  # each finds itself
    loo, nn = max_tanimoto(fps, fps, leave_one_out=True)
    assert (nn != np.arange(len(SMILES))).all() and (loo < 1.0).all()
    assert 0.0 < abstain_cutoff(fps) < 1.0
