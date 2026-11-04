"""Streamlit app. Run: uv run streamlit run app.py

Every number shown comes from results/activity_models.json or the shipped models at runtime; none is typed here.
"""

import json
import re

import pandas as pd
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw

from molscreen import ui_cells, ui_safety
from molscreen.assets import ensure_models, models_url
from molscreen.data import ACTIVE_PCHEMBL
from molscreen.predict import examples, predict
from molscreen.train import MODELS, NAMES, RESULTS

MAX_MOLECULES = 200  # a public app: keep one request small

st.set_page_config(page_title="Molecule Screening Workbench", layout="wide")


@st.cache_resource(show_spinner="downloading models (one-time)")
def models_error() -> str | None:
    """None once the models are in models/, else the error. Cached, so a failed download is not retried per click."""
    try:
        ensure_models()
    except Exception as e:  # noqa: BLE001 (any failure: say so and keep the rest of the app working)
        return f"{type(e).__name__}: {e}"
    return None


@st.cache_data
def results() -> dict:
    return json.loads((RESULTS / "activity_models.json").read_text(encoding="utf-8"))


@st.cache_data
def md_section(title: str) -> str:
    """One `## title` section of results/activity_models.md, as written by molscreen.train."""
    text = (RESULTS / "activity_models.md").read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def draw(smiles: str):
    return Draw.MolToImage(Chem.MolFromSmiles(smiles), size=(260, 200))


def sidebar(res: dict) -> str:
    genes = list(res["genes"])
    gene = st.sidebar.selectbox("Target", genes, index=genes.index("CDK6") if "CDK6" in genes else 0)
    r, kind = res["genes"][gene], res["shipped_model"]
    lo, hi = r[kind]["roc_auc_ci95"]
    st.sidebar.markdown(
        f"**{gene}**, ChEMBL target `{r['target_chembl_id']}`  \n"
        f"Model: {NAMES[kind]}, trained on {r['n_train']} molecules  \n"
        f"Held-out ROC-AUC: **{r[kind]['roc_auc']:.3f}** (95% CI {lo:.3f} to {hi:.3f}), {r['n_test']} molecules  \n"
        f"1-NN baseline ROC-AUC: {r['nn1']['roc_auc']:.3f}  \n"
        f"Abstain cut-off (max Tanimoto): {r['abstain']['cutoff']:.3f}"
    )
    if r["test_inactives"] < res["underpowered_inactives"]:
        st.sidebar.warning(f"Underpowered: only {r['test_inactives']} inactive molecules in the test set, so these "
                           "AUCs can move a lot with a few molecules.")
    if r[kind]["roc_auc"] <= r["nn1"]["roc_auc"]:
        st.sidebar.warning("No better than nearest-neighbour lookup: trust the nearest molecules below, not the score.")
    d = r["dataset"]
    dropped = d["rows_mutant_dropped"] / (d["rows_kept"] + d["rows_mutant_dropped"])
    st.sidebar.info(f"Wild-type protein only, as far as ChEMBL says: {100 * dropped:.1f}% of rows came from assays "
                    "declaring a mutant and were dropped. Says nothing about mutant forms of the target.")
    st.sidebar.caption(f"Held-out = scaffold-split test set, {res['release']}. Details: results/activity_models.md.")
    return gene


def show_result(r: dict) -> None:
    label = f"{r['input'][:60]}: " + (r["error"] or ("abstains" if r["abstain"] else f"p_active {r['p_active']:.2f}"))
    with st.expander(label):
        if r["error"]:
            st.error(f"{r['error']}: RDKit could not read this line.")
            return
        if r["abstain"]:
            st.warning(f"Outside what this model has seen (max similarity {r['max_tanimoto']:.2f} < cut-off "
                       f"{r['abstain_cutoff']:.2f}). No prediction shown.")
        else:
            st.write(f"Probability of active (pChEMBL >= {ACTIVE_PCHEMBL}): **{r['p_active']:.2f}**; "
                     f"max similarity to training {r['max_tanimoto']:.2f}.")
        cols = st.columns(1 + len(r["neighbours"]))
        cols[0].image(draw(r["smiles"]), caption="Query (salts stripped)")
        for col, n in zip(cols[1:], r["neighbours"]):
            col.image(draw(n["smiles"]), caption=f"{n['chembl_ids']}: pChEMBL {n['pchembl']:.2f}, "
                      f"{'active' if n['active'] else 'inactive'}, Tanimoto {n['tanimoto']:.2f}")


def activity_tab(res: dict, gene: str) -> None:
    st.subheader(f"Is a molecule likely active on {gene}?")
    if not (MODELS / f"{gene}.joblib").exists():
        st.error(f"models/{gene}.joblib is missing. Train it with `uv run python -m molscreen.train`.")
        return
    st.button("Example", help=f"Fill in 3 known {gene} inhibitors from this model's training table",
              on_click=lambda: st.session_state.update(smiles="\n".join(examples(gene))))
    text = st.text_area("SMILES, one per line", key="smiles", height=120)
    lines = [s.strip() for s in text.splitlines() if s.strip()]
    if not lines:
        return
    if len(lines) > MAX_MOLECULES:
        st.warning(f"Only the first {MAX_MOLECULES} lines are scored.")
        lines = lines[:MAX_MOLECULES]
    out = predict(gene, lines)
    st.dataframe(pd.DataFrame([{
        "input": r["input"],
        "p_active": None if r["error"] or r["abstain"] else round(r["p_active"], 3),
        "abstain": r["abstain"],
        "max similarity": None if r["error"] else round(r["max_tanimoto"], 3),
        "note": r["error"] or ("outside what this model has seen" if r["abstain"] else ""),
    } for r in out]), hide_index=True)
    st.caption("Each molecule below shows its 3 most similar training molecules (Morgan fingerprint, Tanimoto). "
               "The Example molecules are in the training table, so their nearest match is themselves.")
    for r in out:
        show_result(r)


res = results()
st.title("Molecule Screening Workbench")
st.info("Research and learning tool, not medical advice. Cell lines and public assay data, not patients.")
if err := models_error():
    st.error(f"Could not get the trained models and data tables from {models_url()}: {err}")
gene = sidebar(res)
tabs = st.tabs(["Activity", "Cell lines", "Safety flags", "Analogs"])
with tabs[0]:
    activity_tab(res, gene)
    with st.expander("How this works and its limits"):
        st.markdown(f"One model per target, trained on ChEMBL measurements; a molecule counts as active at pChEMBL "
                    f"{ACTIVE_PCHEMBL} or more. If a query's max similarity to the training molecules is below the target's "
                    f"cut-off, the app abstains. Known limits, from `results/activity_models.md`:\n\n"
                    f"{md_section('Known limits')}")
with tabs[1]:
    ui_cells.render()
with tabs[2]:
    ui_safety.render(MAX_MOLECULES)
tabs[3].write("Coming: similar molecules to explore (loop 4).")
st.divider()
st.caption(md_section("Credits").replace("\n", "  \n") + f"  \n{res['release']}, CC BY-SA 3.0.")
