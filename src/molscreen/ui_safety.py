"""The "Safety flags" tab (loop 3): each Tox21 assay's score next to the assay's active rate. No hard flag.

Every number comes from models/tox21.joblib or results/tox21_models.* at runtime.
"""

import json

import pandas as pd
import streamlit as st

from molscreen.tox import MODEL_PATH, NAMES, TASKS, load_bundle, predict_tox
from molscreen.train import RESULTS
from molscreen.ui_cells import md_section

# In the Tox21 training table: bisphenol A and estradiol have active calls, paracetamol has none (tests check this).
EXAMPLES = ["CC(C)(c1ccc(O)cc1)c1ccc(O)cc1", "C[C@]12CC[C@@H]3c4ccc(O)cc4CC[C@H]3[C@@H]1CC[C@@H]2O",
            "CC(=O)Nc1ccc(O)cc1"]
WORDING = ("A high score means the molecule resembles compounds that were active in that cell-based assay; it is "
           "not a toxicity verdict.")


@st.cache_data
def assays() -> dict:
    return json.loads((RESULTS / "tox21_models.json").read_text(encoding="utf-8"))["assays"]


def table(r: dict) -> None:
    what = assays()
    df = pd.DataFrame([{
        "assay": t, "what it measures": what[t]["what"], "score": round(a["p_active"], 3),
        "assay active rate": round(a["prevalence"], 3), "ratio": round(a["ratio"], 2),
        "above rate": "▲" if a["above_prevalence"] else "",
        "assay ROC-AUC (95% CI)": "{:.3f} ({:.3f} to {:.3f})".format(a["roc_auc"], *a["roc_auc_ci95"]),
    } for t, a in r["assays"].items()])
    st.dataframe(df.style.apply(
        lambda row: ["background-color: rgba(255, 170, 0, 0.18)" if row["above rate"] else ""] * len(row), axis=1),
        hide_index=True)
    train = load_bundle(MODEL_PATH)["train"].set_index("smiles")
    if r["smiles"] in train.index:
        calls = train.loc[r["smiles"], TASKS]
        active = [t for t in TASKS if calls[t] == 1]
        st.caption("This molecule is in the training table, so its scores partly echo its own measurements "
                   f"(active in: {', '.join(active) or 'none of the assays it was tested in'}).")


def scores(max_molecules: int, model: str) -> None:
    st.button("Example", key="tox_example", help="Fill in 3 molecules from the Tox21 training table",
              on_click=lambda: st.session_state.update(tox_smiles="\n".join(EXAMPLES)))
    text = st.text_area("SMILES, one per line", key="tox_smiles", height=120)
    lines = [s.strip() for s in text.splitlines() if s.strip()]
    if not lines:
        return
    if len(lines) > max_molecules:
        st.warning(f"Only the first {max_molecules} lines are scored.")
        lines = lines[:max_molecules]
    out = predict_tox(lines)
    st.markdown(f"**{WORDING}**")
    st.caption(f"Score = the {model}'s score for active (not a calibrated probability). Assay active rate = the "
               "fraction of training molecules active in that assay. Ratio = score / active rate; ▲ and the "
               "shaded rows mark a score above the assay's active rate. ROC-AUC = how well the model ranked "
               "held-out molecules in that assay (0.5 = chance).")
    for i, r in enumerate(out):
        with st.expander(f"{r['input'][:60]}: " + (r["error"] or ("abstains" if r["abstain"] else "scored")),
                         expanded=i == 0):
            if r["error"]:
                st.error(f"{r['error']}: RDKit could not read this line.")
            elif r["abstain"]:
                st.warning(f"Outside what this model has seen (max similarity {r['max_tanimoto']:.2f} < cut-off "
                           f"{r['abstain_cutoff']:.2f}). No prediction shown.")
            else:
                st.write(f"Max similarity to the training molecules: {r['max_tanimoto']:.2f}.")
                table(r)


def render(max_molecules: int) -> None:
    st.subheader("Does a molecule resemble compounds active in the Tox21 lab assays?")
    if not MODEL_PATH.exists():
        st.error(f"{MODEL_PATH} is missing. Train it with `uv run python -m molscreen.tox`.")
        return
    with st.spinner("loading the Tox21 models (first time only)"):
        model = NAMES[load_bundle(MODEL_PATH)["kind"]]
    scores(max_molecules, model)
    md = str(RESULTS / "tox21_models.md")
    with st.expander("How this works and its limits"):
        st.markdown(f"One {model} per Tox21 assay ({len(assays())} assays), trained on Morgan fingerprints. If a "
                    "molecule's max similarity to the training molecules is below the cut-off, the app abstains. "
                    f"Known limits, from `results/tox21_models.md`:\n\n{md_section(md, 'Known limits')}\n\n"
                    "**Credits, from `results/tox21_models.md`:**\n\n" + md_section(md, "Credits").replace("\n", "  \n"))
