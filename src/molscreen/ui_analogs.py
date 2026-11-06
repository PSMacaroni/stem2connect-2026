"""The "Analogs" tab (loop 4): single-point RDKit edits to one molecule, scored by loops 1 and 3 side by side.

Every number comes from the shipped activity model, models/tox21.joblib or results/*.md at runtime.
"""

import pandas as pd
import streamlit as st

from molscreen.analogs import DEFAULT_TOP, MAX_ANALOGS, MAX_TOP, TRANSFORMS, score_analogs
from molscreen.predict import examples
from molscreen.tox import MODEL_PATH
from molscreen.train import MODELS, RESULTS
from molscreen.ui_cells import md_section, mol_png

FRAMING = ("Every molecule below the parent was made up by this app, by editing the parent. None of them has been "
           "measured in any lab, so there is no experimental data on a single one.")
EXTRAPOLATION = ("An edited copy of a training molecule resembles that molecule by construction, so a high activity "
                 "score here is mostly the model recognising what it was trained on. It is extrapolation, not "
                 "evidence that the analog works. Read this tab as \"which single changes does the model react to\", "
                 "nothing more.")
# A display floor, not a statistical test. `results/activity_models.md` ("Split variance (disclosure)") refits each
# model on scaffold splits from seeds 0 to 4: the shipped random forests move by up to 0.0438 of held-out ROC-AUC
# (CDK6), and the 1-NN baseline by up to 0.0549 (CDK4). A floor just above the forests' own figure keeps a gap of a
# few hundredths inside noise the project already admits to. Under this spread the order of the rows is not
# something the evaluation can defend, so the tab says so instead of letting the ranking imply it.
FLAT_SPREAD = 0.05


def note(r: dict) -> str:
    """A row's own caveats, in the wording the Activity and Safety flags tabs use for the same abstains."""
    parts = []
    if r["abstain"]:
        parts.append("no activity score: outside what this model has seen "
                     f"(max similarity {r['max_tanimoto']:.2f} < cut-off {r['abstain_cutoff']:.2f})")
    if r["tox_abstain"]:
        parts.append("no Tox21 count: outside what the Tox21 models have seen")
    return "; ".join(parts)


def flatness(rows: list[dict], top: int) -> str:
    """What the scored rows on show say about their own ranking ("" when there is nothing to warn about).

    Computed from the scores in front of the reader, never hardcoded: the spread of the analogs' p_active, and
    whether any of them beats the parent.
    """
    parent, scored = rows[0], [r for r in rows[1:top + 1] if r["p_active"] is not None]
    if len(scored) < 2:
        return ""
    lo, hi = min(r["p_active"] for r in scored), max(r["p_active"] for r in scored)
    msg = []
    if hi - lo < FLAT_SPREAD:
        msg.append(f"**The model does not separate these analogs.** All {len(scored)} scored ones fall between "
                   f"{lo:.3f} and {hi:.3f}, a spread of {hi - lo:.3f}, which is smaller than the 0.044 these "
                   f"models move when they are refit on a different scaffold split. Their order below is not a "
                   "real ranking: "
                   "row 1 is not a better molecule than row 2.")
    if parent["p_active"] is not None and hi <= parent["p_active"]:
        msg.append(f"No analog scores above the parent ({parent['p_active']:.3f}): this edit list found nothing the "
                   "model prefers to the molecule you typed.")
    return " ".join(msg)


def table(rows: list[dict], top: int) -> None:
    shown = [rows[0]] + rows[1:top + 1]
    st.dataframe(pd.DataFrame([{
        "row": "parent" if r["is_parent"] else str(i),
        "structure": mol_png(r["smiles"]),
        "change": r["transform"] or "— (the molecule you typed)",
        "p_active": None if r["p_active"] is None else round(r["p_active"], 3),
        "Tanimoto to parent": round(r["tanimoto_to_parent"], 3),
        "max Tanimoto to training": round(r["max_tanimoto"], 3),
        "Tox21 assays above their active rate": "" if r["tox_abstain"] else f"{r['tox_above']} of 12",
        "note": note(r),
        "SMILES": r["smiles"],
    } for i, r in enumerate(shown)]), hide_index=True, row_height=60, height=60 * len(shown) + 38,
        column_config={"structure": st.column_config.ImageColumn(width="small")})


def analogs(gene: str) -> None:
    st.button("Example", key="analog_example", help=f"Fill in the most potent known {gene} active in this model's "
              "training table", on_click=lambda: st.session_state.update(analog_smiles=examples(gene, 1)[0]))
    smiles = st.text_input("SMILES of one molecule to edit", key="analog_smiles")
    top = st.number_input("How many analogs to show", 1, MAX_TOP, DEFAULT_TOP, key="analog_top")
    if not smiles.strip():
        return
    with st.spinner("editing the molecule and scoring the analogs"):
        rows = score_analogs(gene, smiles.strip())
    if not rows:
        st.error("invalid SMILES: RDKit could not read that line.")
        return
    if len(rows) == 1:
        st.warning("None of the transforms applies to this molecule, so there are no analogs to show.")
        return
    st.caption(f"{len(rows) - 1} analogs from {len(TRANSFORMS)} transforms, ranked by p_active, highest first "
               f"(at most {MAX_ANALOGS} are generated). The parent is the first row and is scored the same way. "
               "p_active = the activity model's score for the selected target; Tox21 = how many of the 12 safety "
               "assays score above that assay's own active rate. The two are shown side by side and never "
               "combined: the held-out results do not support one overall score. Either number is left blank when "
               "its own model abstains, with the reason in the note.")
    if warning := flatness(rows, int(top)):
        st.warning(warning)
    table(rows, int(top))


def render(gene: str) -> None:
    st.subheader(f"What do single edits to a molecule do to its {gene} score?")
    missing = [p for p in (MODELS / f"{gene}.joblib", MODEL_PATH) if not p.exists()]
    if missing:
        st.error(f"{', '.join(str(p) for p in missing)} is missing. Train with `uv run python -m molscreen.train` "
                 "and `uv run python -m molscreen.tox`.")
        return
    st.warning(f"**{FRAMING}** {EXTRAPOLATION}")
    analogs(gene)
    with st.expander("How this works and its limits"):
        st.markdown(
            "A fixed list of RDKit transforms is applied to the molecule you type, one edit at a time. No generative "
            "model is involved and nothing is sampled, so the same input always gives the same analogs. Products "
            "RDKit cannot sanitise are dropped, duplicates are removed, and the parent is not repeated as an "
            "analog. The transforms are:\n\n"
            + "\n".join(f"- {name}" for name in TRANSFORMS)
            + "\n\nEach analog is then scored by the activity model for the selected target and by the 12 Tox21 "
            "models, with both abstain rules unchanged: an analog whose max Tanimoto to the activity model's "
            "training molecules is below the target's cut-off gets no p_active at all, and one that is as far from "
            "the Tox21 training molecules gets no Tox21 count. The ranking is checked against itself too: when the "
            "scored analogs' p_active values are closer together than this model's own split-to-split movement, the "
            "tab says the order is not a ranking.\n\n"
            "Known limits of the activity model, from `results/activity_models.md`:\n\n"
            + md_section(str(RESULTS / "activity_models.md"), "Known limits")
            + "\n\nKnown limits of the Tox21 models, from `results/tox21_models.md`:\n\n"
            + md_section(str(RESULTS / "tox21_models.md"), "Known limits"))
