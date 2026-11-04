"""Loop-1 predictions from the shipped models in models/<GENE>.joblib. Pure functions, no Streamlit.

For each query: the parent SMILES (salts stripped as in data.py), the model's probability of active, the max
Tanimoto to the training molecules, the abstain flag (docs/evaluation.md) and the 3 nearest training molecules.
"""

from functools import cache

import joblib
import numpy as np

from molscreen.chem import morgan_fp
from molscreen.data import parent_smiles
from molscreen.train import MODELS

N_NEIGHBOURS = 3


@cache  # functools.lru_cache without a size limit
def load_model(gene: str) -> dict:
    """The saved dict from train.save_model, read once per process."""
    m = joblib.load(MODELS / f"{gene}.joblib")
    m["model"].set_params(n_jobs=1)  # same as training-time predictions
    return m


def tanimoto_to_train(fp: np.ndarray, train_packed: np.ndarray) -> np.ndarray:
    """Tanimoto of one 0/1 fingerprint to every row of the packed train fingerprints."""
    q = np.packbits(fp)
    inter = np.bitwise_count(train_packed & q).sum(1)
    union = np.bitwise_count(train_packed | q).sum(1)
    return np.divide(inter, union, out=np.zeros(len(inter)), where=union > 0)


def examples(gene: str, n: int = 3) -> list[str]:
    """The `n` most potent actives in the model's training table (real, known inhibitors of the target)."""
    train = load_model(gene)["train"]
    return train[train["active"] == 1].nlargest(n, "pchembl")["smiles"].tolist()


def predict(gene: str, smiles_list: list[str]) -> list[dict]:
    """One dict per input. An unparseable input gets `error` set and no prediction; it never stops the batch."""
    m = load_model(gene)
    train, cutoff = m["train"], m["abstain_cutoff"]
    out, fps, where = [], [], []
    for s in smiles_list:
        parent = parent_smiles(s.strip()) if isinstance(s, str) else None
        r = {"input": s, "smiles": parent, "error": None if parent else "invalid SMILES", "p_active": None,
             "max_tanimoto": None, "abstain": None, "abstain_cutoff": cutoff, "neighbours": []}
        if parent:
            fp = morgan_fp(parent, m["radius"], m["n_bits"])
            sim = tanimoto_to_train(fp, m["train_fps_packed"])
            near = np.argsort(-sim, kind="stable")[:N_NEIGHBOURS]
            r["max_tanimoto"] = float(sim[near[0]])
            r["abstain"] = r["max_tanimoto"] < cutoff
            r["neighbours"] = [
                {"chembl_ids": row.molecule_chembl_ids, "smiles": row.smiles, "pchembl": float(row.pchembl),
                 "active": bool(row.active), "tanimoto": float(sim[i])}
                for i, row in zip(near, train.iloc[near].itertuples())
            ]
            fps.append(fp)
            where.append(len(out))
        out.append(r)
    if fps:
        for i, p in zip(where, m["model"].predict_proba(np.stack(fps))[:, 1]):
            out[i]["p_active"] = float(p)
    return out
