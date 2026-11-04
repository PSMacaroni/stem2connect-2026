# Devpost submission text

<!-- Draft written 2026-11-04. Before pasting: update "What it does" when the cell-lines and safety tabs land, add the
links, and re-run the numbers pass against the results files (a re-run changes them). Every figure traces to a
source file or a run (Numbers appendix). -->

## Project name
Molecule Screening Workbench

## Track (one primary)
Scientific Research

## Tagline (one line)
A free cancer molecule-screening workbench for students: every answer comes with its evidence, a held-out score,
and an "I don't know" when the question is too far from the data.

## The problem
Checking whether a molecule might act on a cancer protein, which cancer cell lines respond to a drug, or whether a
compound trips a lab toxicity assay usually takes commercial screening software or a specialist pipeline, which
students and small labs often cannot afford. The data is public (ChEMBL, DepMap and PRISM, Tox21), but using it
honestly is hard: the files are large, the licences differ, and a model tested on molecules close to its training
data looks better than it is. Most free tools show one confident score and hide how uncertain it is.

The workbench is built around three questions:
1. Is this molecule likely to be active on a given cancer target?
2. For a set of mutated genes, which cancer cell lines carry them, and how did those lines respond to drugs?
3. Does this molecule resemble compounds that were active in the Tox21 safety assays?

It is a research and learning tool, not medical advice. All data comes from lab assays on proteins and cancer cell
lines, never from patients, and it does not discover drugs.

## What it does
Paste a molecule (as SMILES) and pick one of 9 cancer-related protein targets (EGFR, BRAF, HER2/ERBB2, CDK4, CDK6,
ALK, ABL1, PARP1, BCL2). The app estimates whether the molecule is likely to be active on that target and shows the
3 most similar molecules from the training data, with their structures and measured activity, as the evidence. The
models use wild-type protein measurements only. When the molecule is unlike anything in the training data, the app
abstains and says so instead of guessing.

The models behind the next two tabs are trained and evaluated; the tabs themselves are being built (update this
paragraph when they land):
- **Cell lines (loop 2):** enter mutated genes and see the most similar cancer cell lines with their measured drug
  responses from the PRISM screen. Per-drug models will be shown second and greyed out when weak, because they are
  close to chance (see below).
- **Safety flags (loop 3):** for each of 12 Tox21 assays, the app will show the molecule's score next to the assay's active rate,
  with the assay's held-out ROC-AUC. Not a toxicity verdict.

Held-out results (numbers from the results files in the repository):
- Activity, scaffold split: random forest ROC-AUC 0.845 to 0.971 across the 9 targets, against a
  1-nearest-neighbour baseline of 0.787 to 0.950; above the baseline on 9 of 9 targets
  (`results/activity_models.md`).
- Drug response, leave-lineage-out split: median ROC-AUC 0.546 against 0.516 for 1-nearest-neighbour; 171 of 202
  models are weak. We report this as a negative result (`results/loop2_models.md`).
- Safety, scaffold split: random forest ROC-AUC 0.664 to 0.830 across 12 assays; above 1-nearest-neighbour on 12 of
  12 (`results/tox21_models.md`).

## How it uses AI
**Inside the project.** The app runs machine-learning models trained here on public lab data; no large language
model or external AI API is called by the app.
- Activity: one random forest per target on Morgan fingerprints (radius 2, 2048 bits), with RDKit and scikit-learn.
  LightGBM was compared and lost the pre-registered switch rule.
- Drug response: one logistic regression per drug on the cell line's hotspot mutations (542 genes); a random forest
  was compared.
- Safety: one random forest per Tox21 assay on Morgan fingerprints; logistic regression was compared.
- Every model is compared on held-out data with a majority-class and a 1-nearest-neighbour baseline. Molecules are
  tested on a scaffold split (no shared core structure with training) and cell lines on a leave-lineage-out split.
  The rules were written before training, and every later change is a dated amendment in the repository.
- Abstain: if a molecule is less similar to the training data than the 5th percentile of the training set's own
  similarities, the app gives no prediction and says why.

**AI coding assistants (disclosure).** Claude Code (Anthropic) was used throughout. A manager session running
Claude Fable 5.1 planned the work with the owner, wrote each task brief and reviewed every result. Subagents running
Claude Opus 5.5 wrote the code, tests, evaluation protocols, results reports and docs, including this text. An
independent reviewer subagent recomputed the first activity results from scratch and found the problems that
changed the protocol (mutant-protein assays pooled with wild-type ones, salts counted as separate molecules, an
inflated metric, a missing metric); those led to the wild-type-only and salt-stripping amendments. Prakhar Suryansh
chose the project, the data sources, the metrics and the cut-offs, and made every decision in the plan's decisions
table after seeing the evidence. The manager session re-ran the tests and the reproduction of the reported numbers
before every merge. Commits carry Co-Authored-By trailers. Of the 46 non-merge commits at the time of writing, 14 written by the manager session (the plan updates and one CI fix) correctly name Claude Fable 5.1; 24 written by subagents running Claude Opus 5.5 (the scaffold, data registry, loop-1, loop-2 and activity-tab work) also name Claude Fable 5.1, because the manager's task briefs specified the manager's own attribution line by mistake, noticed during this README review; 6 (loop 3 and the model bundle) name Claude Opus 5.5; 2 setup commits name Claude Sonnet 5.5. Git history was not rewritten; later commits name the model that wrote them.

## What we learned
- A high score can come from the data, not the model: a random ranking already scores 0.68 to 0.95 on active-class
  PR-AUC because most ChEMBL molecules here are active. We lead with ROC-AUC next to a baseline.
- Read what each assay measured: 42.8% of BRAF rows came from assays on mutant proteins, pooled with wild-type ones.
  We dropped them, so the activity models answer one clean question.
- One test set's confidence interval understates uncertainty: changing the split alone moved ROC-AUC by up to 0.0549,
  more than the model's lead over the baseline on some targets. We report it rather than pick the best split.
- "Beats the baseline" depends on the metric: the activity and safety models rank better than nearest-neighbour lookup on every target and assay, but
  lose on balanced accuracy at a 0.5 cut on 8 of 9 targets and 8 of 12 assays.
- Negative results are results: drug-response models on hotspot mutations alone are near chance (171 of 202 weak),
  so the app will lead with the measured responses of similar cell lines.
- Check the licence before downloading: our first loop-2 data source has a non-transferable policy, so we switched
  to Broad's CC BY 4.0 snapshots. Free hosting changed too: Hugging Face Spaces now needs a paid plan for the kind of
  Space Streamlit needs, so we host on Streamlit Community Cloud.

## What's next
- Analog enumeration: small RDKit edits to a known active, scored by the activity and safety models.
- Richer features for the drug-response models (damaging mutations beyond hotspots, other cell-line data).
- Mutant-specific activity models from the mutant-protein assays the current models leave out.
- A medicinal chemist's review of the examples, the wording and the abstain behaviour.

## Built with
<!-- Devpost's tag box splits on spaces: one word per tag. -->

python rdkit scikit-learn lightgbm streamlit pandas numpy joblib uv pytest ruff chembl depmap prism tox21
moleculenet streamlit-community-cloud github claude-code

## Links
- Repository (must be public): https://github.com/PSMacaroni/stem2connect-2026 (private today; make it public before submitting)
- Demo video (YouTube or Vimeo, public or unlisted, 6 minutes or less): [video URL]
- Live demo, if any: [Streamlit Community Cloud URL]

## Team members (all added on Devpost)
Prakhar Suryansh (solo)

## Numbers appendix
Every figure in the README sections filled on 2026-11-04 and in this Devpost text. "README" covers the README
sections; "Devpost" covers this file.

| Figure | Where it appears | Source (file, run, commit) |
|---|---|---|
| 9 cancer protein targets | README What it does, Results at a glance; Devpost | `results/activity_models.md` (headline table, 9 rows) |
| 3 most similar training molecules shown | README What it does; Devpost | `src/molscreen/predict.py` (docstring: "the 3 nearest training molecules") |
| 1 µM activity cut-off (median pChEMBL >= 6.0) | README Results at a glance | `docs/evaluation.md`, Data and label |
| Scaffold split seed 0 | README Results at a glance | `results/activity_models.md`, `results/tox21_models.md` |
| Random forest ROC-AUC 0.845 (ERBB2) to 0.971 (BCL2) | README Results at a glance; Devpost | `results/activity_models.md`, headline table |
| 1-NN ROC-AUC 0.787 (BRAF) to 0.950 (BCL2) | README Results at a glance; Devpost | `results/activity_models.md`, headline table (min and max of the 1-NN column) |
| Random forest above 1-NN on ROC-AUC on 9 of 9 targets | README Results at a glance, What we learned; Devpost | `results/activity_models.md`, "Random forest against 1-NN, per metric" |
| Below 1-NN on balanced accuracy at 0.5 on 8 of 9 targets | README Results at a glance, What we learned; Devpost | `results/activity_models.md`, same list |
| Random active-class PR-AUC 0.68 to 0.95 | README What we learned; Devpost | `results/activity_models.md`, headline note ("0.68 to 0.95 here") |
| Variant-assay rows dropped: BRAF 42.8%, EGFR 23.8%, ALK 22.0% | README What we learned; Devpost (BRAF only) | `results/activity_models.md`, Known limits ("Wild type only") |
| Split alone moves ROC-AUC by up to 0.0549 (CDK4, 1-NN) | README What we learned; Devpost | `results/activity_models.md`, Split variance |
| Random forest seed-0 lead over 1-NN: ABL1 +0.0199, BCL2 +0.0215 | README What we learned | `results/activity_models.md`, Split variance |
| Morgan fingerprints radius 2, 2048 bits | README AI tools; Devpost | `results/activity_models.md` and `results/tox21_models.md`, intro |
| 5th-percentile abstain cut-off (train leave-one-out max Tanimoto) | README AI tools; Devpost | `docs/evaluation.md`, Abstain rule |
| 202 drugs | README Results at a glance, What we learned; Devpost | `results/loop2_models.md`, "What this says" |
| Sensitive = `auc` below the drug's 10th percentile on training lines | README Results at a glance | `results/loop2_models.md`, intro |
| 542 hotspot genes | README AI tools; Devpost | `results/loop2_models.md`, intro |
| 146 test cell lines in 10 lineages | README Results at a glance | `results/loop2_models.md`, Split |
| 198 drugs not underpowered | README Results at a glance | `results/loop2_models.md`, "What this says" |
| Median ROC-AUC 0.546 (logistic regression) vs 0.516 (1-NN) | README Results at a glance, What we learned; Devpost | `results/loop2_models.md`, "What this says" |
| 171 of 202 shipped models weak (95% CI reaches 0.5) | README Results at a glance, What we learned; Devpost | `results/loop2_models.md`, "What this says" |
| 73 models below 0.5 | README What we learned | `results/loop2_models.md`, "What this says" |
| 12 Tox21 assays | README Results at a glance, What we learned; Devpost | `results/tox21_models.md`, headline table |
| Random forest ROC-AUC 0.664 (NR-ER) to 0.830 (NR-AR-LBD) | README Results at a glance; Devpost | `results/tox21_models.md`, headline table |
| Above 1-NN on ROC-AUC on 12 of 12 assays | README Results at a glance, What we learned; Devpost | `results/tox21_models.md`, must-beat rule |
| Below 1-NN on balanced accuracy at 0.5 on 8 of 12 assays | README Results at a glance, What we learned; Devpost | `results/tox21_models.md`, per-metric list |
| ROC-AUC 0.5 = coin flip, 1.0 = perfect ranking | README Results at a glance | definition of ROC-AUC |
| Hugging Face Spaces paid plan for Gradio and Docker Spaces (read 2026-11-04) | README What we learned; Devpost | `docs/data-registry.md`, Hosting and Blocker 1 |
| Repository created Nov 3 to Nov 21, 2026; first commit 2026-11-03 | README Reused work | `git log --reverse` (88889f6, 2026-11-03) |
| `scripts/sync_to_vault.py` written 2026-11-03 | README Reused work | commit 88889f6 |
| ChEMBL release chembl_37; CC BY-SA 3.0; CC BY 4.0; DOIs | README Credits | `docs/data-registry.md`, README credit lines and section 3b; `results/loop2_data.md`, credit lines |
| 50 MB models zip, about 15 minutes to train, about 3 minutes for the first `uv sync` | README How to run it (not filled in this pass) | not from a results file; check on a fresh clone before submitting |
