"""The "Cell lines" tab (loop 2): nearest screened cell lines by hotspot genes, then per-drug model ranks.

Every number comes from the derived DepMap/PRISM tables, models/loop2 or results/*.md at runtime.
"""

import base64
import io
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw

from molscreen.depmap import RAW, gene_symbols, nearest_cell_lines, top_compounds
from molscreen.drugs import NAMES, predict_drugs
from molscreen.train import RESULTS

EXAMPLE = "KRAS, TP53, STK11"


@st.cache_data
def md_section(path: str, title: str) -> str:
    """One `## title` section of a results Markdown file ("" when the file or section is missing)."""
    p = Path(path)
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    m = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


@st.cache_data
def mol_png(smiles: str) -> str | None:
    """A small drawing as a data URI for st.column_config.ImageColumn (None if RDKit cannot read it)."""
    mol = Chem.MolFromSmiles(smiles) if isinstance(smiles, str) else None
    if mol is None:
        return None
    buf = io.BytesIO()
    Draw.MolToImage(mol, size=(160, 110)).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def compounds(line: dict) -> None:
    st.markdown(f"**10 most sensitive PRISM compounds measured on {line['CellLineName']}** (`{line['ModelID']}`; "
                "AUC = area under the dose-response viability curve; lower = more sensitive)")
    rows = top_compounds(line["ModelID"])
    st.dataframe(pd.DataFrame([{
        "name": r["name"], "AUC": round(r["auc"], 3), "target": r["target"] if isinstance(r["target"], str) else "",
        "structure": mol_png(r["smiles"]), "SMILES": r["smiles"],
    } for r in rows]), hide_index=True, row_height=60, height=60 * len(rows) + 38,
        column_config={"structure": st.column_config.ImageColumn(width="small")})


def model_ranks(genes: list[str]) -> None:
    st.markdown("#### Model ranks (second evidence)")
    out = predict_drugs(genes)
    if not out:
        st.info("Every drug model abstained: none of their training cell lines carries a hotspot mutation in a "
                "listed gene, so no rank is shown.")
        return
    df = pd.DataFrame([{
        "rank": r["rank"], "name": r["name"], "target": r["target"],
        "held-out ROC-AUC (95% CI)": "n/a" if r["roc_auc"] is None
        else "{:.3f} ({:.3f} to {:.3f})".format(r["roc_auc"], *r["roc_auc_ci95"]),
        "sensitive test lines": r["n_sensitive_test"],
        "weak": r["weak"], "underpowered": r["underpowered"],
    } for r in out])
    st.dataframe(df.style.apply(lambda row: ["color: #999" if row["weak"] else ""] * len(row), axis=1),
                 hide_index=True)
    st.caption(f"{len(out)} drug models ranked; a model is left out when none of its training lines carries a "
               "listed gene. Rank 1 = the model's highest score for sensitive. The scores are not calibrated "
               "probabilities, so only the rank is shown. Greyed (weak) = the held-out ROC-AUC 95% CI reaches 0.5, "
               "so that model is no better than chance on held-out lineages. Underpowered = few sensitive lines in "
               "its test set. The measured responses above are the main evidence.")


def lookup() -> None:
    st.button("Example", key="cells_example", help=f"Fill in {EXAMPLE}",
              on_click=lambda: st.session_state.update(genes=EXAMPLE))
    text = st.text_input("Mutated genes (symbols, comma or space separated)", key="genes")
    asked = list(dict.fromkeys(g.upper() for g in re.split(r"[,\s]+", text) if g))
    if not asked:
        return
    known_set = set(gene_symbols())
    known = [g for g in asked if g in known_set]
    if unknown := [g for g in asked if g not in known_set]:
        st.warning(f"Not in the DepMap hotspot matrix, ignored: {', '.join(unknown)}.")
    if not known:
        return
    lines = nearest_cell_lines(known)
    st.dataframe(pd.DataFrame([{
        "cell line": r["CellLineName"], "lineage": r["OncotreeLineage"], "primary disease": r["OncotreePrimaryDisease"],
        "shared genes": ", ".join(r["shared_genes"]), "number shared": r["n_shared"], "Jaccard": r["jaccard"],
    } for r in lines]), hide_index=True)
    st.caption(f"The {len(lines)} screened cell lines sharing the most of these hotspot-mutated genes (then Jaccard, "
               "then name). Cell lines, not patients; a lookup, not a prediction.")
    by_id = {r["ModelID"]: r for r in lines}
    pick = st.selectbox("See the measured drug responses of one of these cell lines", list(by_id), key="cell_line",
                        format_func=lambda i: f"{by_id[i]['CellLineName']} ({by_id[i]['OncotreePrimaryDisease']})")
    compounds(by_id[pick])
    model_ranks(known)


def render() -> None:
    st.subheader("Which screened cancer cell lines look like these mutations?")
    if not (RAW / "derived" / "hotspot_binary.csv").exists():
        st.error(f"The DepMap/PRISM tables are missing from {RAW / 'derived'}. Build them with "
                 "`uv run python scripts/pull_depmap.py` and `uv run python -m molscreen.depmap`.")
    else:
        lookup()
    shipped = json.loads((RESULTS / "loop2_models.json").read_text(encoding="utf-8"))["shipped_model"]
    with st.expander("How this works and its limits"):
        st.markdown("Cell lines are matched on DepMap hotspot mutations only (any hotspot call in a gene counts). "
                    "The compound list is what PRISM measured on that line. Each drug model is a "
                    f"{NAMES[shipped]} on the same hotspot genes, tested on cancer lineages it never saw.")
        for f in ("loop2_data.md", "loop2_models.md"):
            if limits := md_section(str(RESULTS / f), "Known limits"):
                st.markdown(f"**Known limits, from `results/{f}`:**\n\n{limits}")
        st.markdown("**Credits, from `results/loop2_data.md`:**\n\n"
                    + md_section(str(RESULTS / "loop2_data.md"), "Credit lines (for the README)"))
