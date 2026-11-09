# Molecule Screening Workbench

Entry for the [STEM2Connect AI Hackathon 2026](https://stem2connect-online-hackathon.devpost.com/).
Primary track: Scientific Research

**Live app:** https://stem2connect-2026-cjfcmxcaxddeqtfvyvjzbw.streamlit.app/
Free hosting, so it sleeps after 12 idle hours; the first visit then takes about a minute to wake (timed once,
2026-11-05, on the "Yes, get this app back up!" screen; about 70 seconds on a second timing, 2026-11-08).
The free tier also caps memory at about 1 GB, and opening all four tabs in one visit needs about 1.6 GB (measured
2026-11-08; the twelve Tox21 forests are a gigabyte of it), so the hosted app can stop with "gone over its
resource limits". If that happens, the local run below has no such limit.

**Demo video:** not recorded yet. The script is `docs/video.md` and the sheet to read from is
`docs/video-teleprompter.md`; the link replaces this line once it is uploaded. The narration will be either read
aloud by the owner or spoken by the speech synthesiser built into Windows (`scripts/narrate.py` turns the script
into SSML, `scripts/narrate.ps1` renders it). **Which one was used is stated here when the link goes in** — a
synthesised voice is an AI tool and belongs in the disclosure below.

## What it does

A learning tool for students: paste a molecule (as SMILES), pick one of 9 cancer-related protein targets, and the
app estimates whether the molecule is likely to be active on that target, using a model trained on public ChEMBL
lab measurements. Next to each answer it shows the 3 most similar molecules the model learned from, with their
structures and measured activity, so you can see the evidence. The models use wild-type protein measurements only,
and when a molecule is unlike anything in the training data the app abstains and says so instead of guessing.
The Cell lines tab takes a list of mutated genes, finds the PRISM-screened cancer cell lines that share the most of
those hotspot-mutated genes, and shows the measured PRISM drug responses of the line you pick as the main evidence:
a lookup on cell lines, not a prediction for a patient. Per-drug model ranks come second and are greyed out when
weak (the lower end of their held-out 95% CI is at or below 0.5, so they are not shown to beat chance). The Safety
flags tab scores a molecule in each of 12 Tox21 lab assays and
shows each score next to that assay's active rate and its held-out ROC-AUC, with no toxicity verdict; like the
Activity tab, it abstains on molecules unlike its training data. The Analogs tab takes one molecule, applies a
fixed list of nine small RDKit edits to it one at a time, and shows the edited copies with their activity and
Tox21 scores next to the parent's; the molecules it makes are not real measurements and the tab says so. The
data comes from lab assays on proteins and cell lines, not patients: this is a research and learning tool, not
medical advice, and it does not discover drugs.

## Results at a glance

Held-out results for the three model loops. Each number is copied from the results file in the last column, which
the training run writes. All three loops have a tab in the app (Activity, Cell lines, Safety flags). The Analogs
tab reuses the activity and Tox21 models rather than training one of its own, so it has no held-out numbers of its
own.

| Loop | What is predicted | Held-out test | Result on the held-out test | Source |
|---|---|---|---|---|
| 1. Molecules to activity | Whether a molecule is active (1 µM cut-off, `docs/evaluation.md`) on each of 9 cancer protein targets, wild-type assays only | Scaffold split (seed 0): test molecules share no core structure with training | Random forest ROC-AUC 0.845 (ERBB2) to 0.971 (BCL2); 1-nearest-neighbour baseline 0.787 (BRAF) to 0.950 (BCL2). Above the baseline on 9 of 9 targets; below it on balanced accuracy at 0.5 on 8 of 9. | `results/activity_models.md` |
| 2. Mutations to drug response | Whether a cancer cell line is among the most sensitive to each of 202 drugs (`auc` below the drug's 10th percentile), from its hotspot mutations alone | Leave-lineage-out: 146 test cell lines in 10 lineages never seen in training | **Negative result.** Median ROC-AUC 0.546 (logistic regression) vs 0.516 (1-nearest-neighbour) over the 198 drugs that are not underpowered; 171 of 202 shipped models are weak (95% CI lower bound at or below 0.5, the definition in `results/loop2_models.md`). The app leads with the nearest cell lines' measured responses. | `results/loop2_models.md` |
| 3. Molecules to safety flags | Whether a molecule resembles compounds that were active in each of 12 Tox21 lab assays (not a toxicity verdict) | Scaffold split (seed 0) shared by all 12 assays | Random forest ROC-AUC 0.664 (NR-ER) to 0.830 (NR-AR-LBD). Above 1-nearest-neighbour on 12 of 12 assays; below it on balanced accuracy at 0.5 on 8 of 12. | `results/tox21_models.md` |

ROC-AUC 0.5 is a coin flip and 1.0 is a perfect ranking. Confidence intervals, every baseline, the abstain counts
and the split-variance checks are in the results files.

## The problem it addresses

Checking whether a molecule might act on a cancer protein, which cancer cell lines respond to a drug, or whether a
compound trips a lab toxicity assay usually takes commercial screening software or a specialist pipeline, which
students and small labs often cannot afford. The data to do this is public (ChEMBL, DepMap and PRISM, Tox21), but
using it honestly is hard: the files are large, the licences differ, and a model tested on molecules close to its
training data looks better than it is. Most free tools show one confident score and hide how uncertain it is, or
how far the question is from anything the model has seen. This workbench is built around four questions. Three are
answered with held-out numbers and the evidence behind the answer: is this molecule likely to be active on a given
cancer target; for a set of mutated genes, which cancer cell lines carry them and how did those lines respond to
drugs; and does this molecule resemble compounds that were active in the Tox21 safety assays? The fourth asks what
single edits to a molecule do to its score, and measures the spread of its own answers before presenting them as a
ranking. When a molecule is unlike the training data, it says so instead of guessing.

## How to run it

These steps use WSL (Linux inside Windows). On the owner's PC, Windows Smart App Control blocks numpy, so we run
everything in WSL. On Linux or macOS, skip step 1 and run the rest in a normal terminal.

1. Open a WSL terminal: press the Windows key, type `wsl`, press Enter.
2. Install uv (it installs Python and the libraries for you). Run this once:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
   Then close the terminal and open a new one, so the `uv` command is found.
3. Get the code and go into it:
   `git clone https://github.com/PSMacaroni/stem2connect-2026`
   `cd stem2connect-2026`
   (If you already have the folder, just go to it: `cd /mnt/c/Users/<you>/Documents/stem2connect-2026`.)
4. Install Python 3.12 and every library the project needs:
   `uv sync`
   The first time takes a few minutes (on a Windows drive, about 3).
5. Run the tests:
   `uv run pytest -q`
   It worked if the last line says `passed` and nothing `failed`. In a fresh clone 14 of the 61 tests say
   `skipped`: they need the trained models and the data tables, which arrive in step 7. Run it again after that
   step and 60 pass; the last one stays skipped because it needs the raw ChEMBL download, which the models bundle
   does not carry.
6. Optional: check the code style with `uv run ruff check .` (it should say `All checks passed!`).
7. Get the trained models and the cell-line tables (they are not in git). Download them, a 188 MB zip from the
   GitHub release holding all 212 models and the 4 DepMap tables the Cell lines tab reads:
   `uv run python -c "from molscreen.assets import ensure_models; ensure_models()"`
   It worked if the last line says `217 files verified`, `models/` holds `.joblib` files and
   `data/depmap/derived/` holds four `.csv` files.
   Building them yourself instead takes hours. Each tab needs its data downloaded first, then built from it:
   - Activity: `uv run python scripts/pull_chembl.py`, then `uv run python -m molscreen.train` (about 15 minutes).
   - Cell lines: `uv run python scripts/pull_depmap.py` (raw files only), then `uv run python -m molscreen.depmap`
     to build the four tables, then `uv run python -m molscreen.drugs` for the drug models, which read those tables.
   - Safety flags: `uv run python scripts/pull_tox21.py`, then `uv run python -m molscreen.tox`.
   For the owner: `uv run python scripts/bundle_models.py` makes `dist/models-v2.zip`; publish it with
   `gh release create v2 dist/models-v2.zip`, then update `TAG` in `src/molscreen/assets.py` if you used another tag.
8. Start the app: `uv run streamlit run app.py`, then open http://localhost:8501 in your browser. The first time,
   Streamlit asks for an email address: leave it blank and press Enter. If you skipped step 7 the app downloads the
   models itself on the first page load.

## AI tools and services used
**Inside the project:** classic machine learning, trained here on public lab data. No large language model or
external AI API is called by the app.
- **Activity (loop 1):** one random forest per target on Morgan fingerprints (radius 2, 2048 bits), built with
  scikit-learn and RDKit. LightGBM was trained and compared; the random forest won the pre-registered switch rule
  and ships (`results/activity_models.md`).
- **Drug response (loop 2):** one logistic regression per drug on the cell line's 0/1 hotspot mutation vector
  (542 genes); a random forest was compared. Logistic regression ships by a dated amendment
  (`docs/evaluation-loop2.md`, `results/loop2_models.md`).
- **Safety (loop 3):** one random forest per Tox21 assay on Morgan fingerprints; logistic regression was compared
  (`results/tox21_models.md`).
- **Baselines** on every held-out set: majority class and 1-nearest-neighbour (Tanimoto similarity for molecules).
  The nearest cell lines for a set of genes are a lookup (shared mutated genes, then Jaccard), not a model.
- **Evaluation rules written before training** (`docs/evaluation.md`, `docs/evaluation-loop2.md`,
  `docs/evaluation-loop3.md`), with every later change written as a dated amendment: scaffold-split testing for
  molecules, leave-lineage-out testing for cell lines, bootstrap 95% confidence intervals, and a split-variance check.
- **Abstain rule:** when a molecule's highest Tanimoto similarity to the training molecules is below the 5th
  percentile of the training set's own leave-one-out similarities, the app shows no prediction and says why
  (`docs/evaluation.md`).

**AI coding assistants (disclosure):** Claude Code (Anthropic) was used throughout this project. A manager
session running Claude Fable 5.1 planned the work with the owner, wrote each task brief and reviewed every result.
Subagents running Claude Opus 5.5 wrote the code, the tests, the evaluation protocols, the results reports and the
docs, including this README section and the Devpost draft. An independent reviewer subagent recomputed the loop-1
numbers from scratch and found the reporting and data problems that changed the protocol: assays on mutant
proteins pooled with wild-type ones, the same parent molecule counted under several ChEMBL IDs as different salts,
an active-class PR-AUC that looked high only because most molecules are active, and balanced accuracy missing from
the table. Those findings led to the wild-type-only and salt-stripping amendments in `docs/evaluation.md`. The
owner, Prakhar Suryansh, chose the project, the data sources, the metrics and the cut-offs, and made every decision
in the Decisions table of `PLAN.md` after seeing the evidence for it. Before anything was merged, the manager
session re-ran the tests and the reproduction of the reported numbers.
Commits carry Co-Authored-By trailers. Of the 73 non-merge commits as of 7308fed (2026-11-05), 46 name Claude Fable 5.1, 24 name Claude Opus 5.5, 1 names Claude Opus 5 and 2 setup commits name Claude Sonnet 5.5. Recount with `git log --no-merges --format='%(trailers:key=Co-Authored-By,valueonly)' | grep -oE "Claude (Fable 5\.1|Opus 5\.5|Opus 5|Sonnet 5\.5)" | sort | uniq -c`, which sums to exactly the 73 commits; grepping whole commit messages instead gives 75, because two commit bodies discuss these model names in prose. The figures are pinned to a commit because every new commit changes them: the commit that records these ones adds a further Opus 5. Of the 46 naming Fable, 24 were in fact written by subagents running Claude Opus 5.5 (the scaffold, data registry, loop-1, loop-2 and activity-tab work): the manager's task briefs specified the manager's own attribution line by mistake, which an audit of the trailers caught while this section was first written. The other 22 are the manager session's own commits, made while it ran Fable 5.1. The 24 naming Opus 5.5 are later subagent work (loop 3, the model bundle, the analogs tab) together with the manager session's own commits after it switched to Opus 5.5, and the one naming Opus 5 is the manager session's own work after its model moved again. Git history was not rewritten; every commit since the audit names the model that wrote it.
No AI tool decided what this project claims: the
wording rules (a research and learning tool, not medical advice; cell lines, not patients) are the owner's, in
`PLAN.md`.

## Credits and reused work
The code is MIT-licensed (`LICENSE`). ChEMBL-derived data in this repository or its release files is shared under
CC BY-SA 3.0, as ChEMBL's licence requires.

### Data
- **ChEMBL** (bioactivity data, loop 1). ChEMBL data is from http://www.ebi.ac.uk/chembl - the version of ChEMBL is
  chembl_37. Licensed under CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/). Any ChEMBL-derived data
  in this repository is shared under the same licence. Mendez D, et al. ChEMBL: towards direct deposition of
  bioassay data. Nucleic Acids Res. 2019;47(D1):D930-D940. doi:10.1093/nar/gky1075
- **DepMap 24Q4 Public** (hotspot mutations, cell-line annotations, compound map, loop 2), Broad Institute.
  Figshare+, doi:10.25452/figshare.plus.27993248. CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- **PRISM Repurposing 20Q2** (secondary-screen dose-response, loop 2), Broad Institute; DepMap, Corsello S, Kocak M,
  Golub T. figshare, doi:10.6084/m9.figshare.20564034. CC BY 4.0. Corsello SM, Nagari RT, Spangler RD, et al.
  Discovering the anticancer potential of non-oncology drugs by systematic viability profiling. *Nat Cancer.*
  2020;1(2):235-248. doi:10.1038/s43018-019-0018-6
- Tsherniak A, Vazquez F, Montgomery PG, et al. Defining a Cancer Dependency Map. *Cell.* 2017;170(3):564-576.e16.
  doi:10.1016/j.cell.2017.06.010
- Mutation data: Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer Cell
  Line Encyclopedia. *Nature.* 2019;569(7757):503-508. doi:10.1038/s41586-019-1186-3
- **Tox21** (12 toxicity assays, loop 3) as distributed by MoleculeNet/DeepChem
  (https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz). Wu Z, et al. MoleculeNet: a benchmark for
  molecular machine learning. Chem. Sci. 2018;9:513-530. doi:10.1039/C7SC02664A. Huang R, et al. Tox21Challenge to
  build predictive models of nuclear receptor and stress response pathways as mediated by exposure to environmental
  chemicals and drugs. Front. Environ. Sci. 2016;3:85. doi:10.3389/fenvs.2015.00085. **Licence not stated:** neither
  MoleculeNet/DeepChem nor the NCATS challenge page states a licence for the data. Tox21 is a US federal programme,
  so it is probably public domain (inferred, not verified).

Raw data is never committed: `scripts/pull_chembl.py`, `scripts/pull_depmap.py` and `scripts/pull_tox21.py` download
it. Licences were checked on the official pages before any download (`docs/data-registry.md`).

### Libraries
RDKit (BSD-3-Clause), scikit-learn (BSD-3-Clause), LightGBM (MIT), Streamlit (Apache-2.0), pandas (BSD-3-Clause),
NumPy (BSD-3-Clause), joblib (BSD-3-Clause), pytest (MIT), ruff (MIT), uv (MIT or Apache-2.0). Versions are pinned
in `pyproject.toml` and `uv.lock`; licence links are in `docs/data-registry.md`.

### Reused work
No code, data or design from the owner's earlier hackathon projects (Ashby, MuFFLe++) was reused. The only
carried-over ideas are evaluation habits: testing on held-out data the model never saw, abstaining instead of
guessing, and recording where every cut-off comes from. They are described in the owner's notes and were written
fresh here. Everything in this repository was created between Nov 3 and Nov 21, 2026 (first commit 2026-11-03).
`scripts/sync_to_vault.py`, a utility that copies this project into the owner's notes, was written on 2026-11-03;
a copy of it is also in the owner's repository for another challenge (Enveda CASMI). It is not part of the app.

## What we learned
- **A high score can come from the data, not the model.** Most ChEMBL molecules in these sets are active, so a
  random ranking already scores 0.68 to 0.95 on active-class PR-AUC (`results/activity_models.md`). We lead with
  ROC-AUC and its confidence interval next to the nearest-neighbour baseline instead.
- **Read what each assay measured.** A review found assays on mutant proteins pooled with wild-type ones; dropping
  them removed 42.8% of BRAF rows, 23.8% of EGFR rows and 22.0% of ALK rows (`results/activity_models.md`). The
  activity models now answer one clean question: activity on the normal protein.
- **One test set's confidence interval understates the uncertainty.** Changing the scaffold split alone moves
  ROC-AUC by up to 0.0549 (CDK4, 1-nearest-neighbour), more than the random forest's lead over the baseline on ABL1
  (+0.0199) and BCL2 (+0.0215) (`results/activity_models.md`). We report this instead of picking the best split.
- **"Beats the baseline" depends on the metric.** The random forest ranks better than 1-nearest-neighbour on 9 of 9
  targets and 12 of 12 Tox21 assays, but is below it on balanced accuracy at a 0.5 cut on 8 of 9 targets and 8 of 12
  assays (`results/activity_models.md`, `results/tox21_models.md`). So the safety tab shows each score next to
  the assay's active rate rather than a yes/no flag.
- **Negative results are results.** Per-drug models on hotspot mutations alone are near chance: median ROC-AUC
  0.546 and 73 below 0.5 over the 198 drugs that are not underpowered; 171 of 202 weak counting every drug
  (`results/loop2_models.md`). The app leads with the measured responses of
  the nearest cell lines and greys out weak models.
- **Check the licence before downloading.** The first choice for loop 2 (Sanger GDSC and Cell Model Passports) is
  under a non-commercial, non-transferable policy, so we switched to Broad's CC BY 4.0 Figshare snapshots; the
  smallest ChemBERTa-2 weights carry no licence at all; Tox21 states none (`docs/data-registry.md`).
- **Free hosting changes.** Hugging Face Spaces now needs a paid plan for Gradio and Docker Spaces, and Streamlit
  needs a Docker Space there, so the app is hosted on Streamlit Community Cloud instead
  (`docs/data-registry.md`, read 2026-11-04).
- **A cloud image is not your machine.** The first deploy crashed at import: RDKit's drawing module needs the system
  library libXrender, which the Streamlit Cloud image does not ship. A two-line `packages.txt` (`libxrender1`,
  `libxext6`) fixed it. Nothing in the Python lock file could have caught this, because it is not a Python package.

## What's next
- **A wider analog list:** the Analogs tab ships nine single-point edits; ring-size and linker changes would need
  a bigger transform list and a chemist's eye on which ones are sane.
- **Richer features for loop 2:** damaging mutations beyond hotspots, and other cell-line data, to test whether the
  per-drug models can get clearly above chance.
- **Mutant-specific activity models:** use the mutant-protein assay rows that the wild-type models leave out, for
  targets where mutations change which drugs work.
- **A chemist's review:** ask a medicinal chemist to check the examples, the wording and the abstain behaviour.

## Team
Prakhar Suryansh (solo entry).
