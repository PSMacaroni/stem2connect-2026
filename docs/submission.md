# Devpost submission text

<!-- Draft written 2026-11-04. Before pasting: add the links, and re-run the numbers pass against the results files (a re-run changes them). Every figure traces to a
source file or a run (Numbers appendix). -->

## How to paste this into the Devpost form

The sections below are the text; this table says which box each one goes in. Nothing is duplicated, so edit the
section and the form gets the edit too. Devpost keeps a draft until you press **Submit** — a draft is not an entry.

| Devpost box | What to paste |
|---|---|
| Project name | **Project name** |
| Elevator pitch | **Tagline**. 178 characters, inside the 200-character cap Devpost used when this was written. Check the counter in the form; if it has changed, cut the clause after the colon. |
| About the project (one rich-text box) | **The problem**, then **What it does**, then **How it uses AI**, then **What we learned**, then **What's next** — in that order, keeping the headings. This is the box the judges read, and the AI disclosure has to be in it (rules, `docs/hackathon.md`). |
| Built with | **Built with**, as separate tags. Devpost splits on spaces, so paste one word per tag. |
| Try it out links | The repository and live-demo URLs from **Links**. |
| Video demo link | The YouTube or Vimeo URL from **Links**, once it exists. |
| Additional questions | **Track** (Scientific Research). If the form asks about AI use separately, paste the "AI coding assistants (disclosure)" paragraph from **How it uses AI** again. |
| Team members | **Team members**: solo, so there is nobody to add, but open the box and confirm it. |

### Before you press Submit
- [ ] Registered on Devpost, and joined the Discord (`docs/hackathon.md` still lists both as not done).
- [ ] Video uploaded, under 6:00, public or unlisted, link opens in a signed-out browser.
- [ ] Video URL pasted in three places: the Devpost form, **Links** below, and the README.
- [ ] `uv run python scripts/check_numbers.py --strict` passes on this checkout (it needs the models bundle).
- [ ] Repository is public and a fresh clone runs from the README.
- [ ] The AI-disclosure commit counts re-pinned to the final commit (they are pinned to 7308fed and drift with
      every commit; see the note in **How it uses AI**).
- [ ] If the video's narration was spoken by the Windows speech synthesiser rather than read aloud, that is
      disclosed. Paste this sentence into **How it uses AI** below and into the README's AI disclosure, and delete
      the "either read aloud or spoken" clause from the README's video line:
      *The narration in the demo video is not a human voice: the script in `docs/video.md` was rendered by the
      speech synthesiser built into Windows (Microsoft David Desktop, SAPI) via `scripts/narrate.py` and
      `scripts/narrate.ps1`. The words are the owner's own script; only the voice is synthetic. Everything shown
      on screen is the app running.*
- [ ] Pressed **Submit**, and the entry shows as submitted rather than draft.

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

The workbench is built around four questions:
1. Is this molecule likely to be active on a given cancer target?
2. For a set of mutated genes, which cancer cell lines carry them, and how did those lines respond to drugs?
3. Does this molecule resemble compounds that were active in the Tox21 safety assays?
4. What do single edits to a molecule do to its score? The tab answers this by measuring the spread of its own
   scores and saying when that spread is too small to read as a ranking.

It is a research and learning tool, not medical advice. All data comes from lab assays on proteins and cancer cell
lines, never from patients, and it does not discover drugs.

## What it does
Paste a molecule (as SMILES) and pick one of 9 cancer-related protein targets (EGFR, BRAF, HER2/ERBB2, CDK4, CDK6,
ALK, ABL1, PARP1, BCL2). The app estimates whether the molecule is likely to be active on that target and shows the
3 most similar molecules from the training data, with their structures and measured activity, as the evidence. The
models use wild-type protein measurements only. When the molecule is unlike anything in the training data, the app
abstains and says so instead of guessing.

Three more tabs are live:
- **Cell lines (loop 2):** enter mutated genes and see the PRISM-screened cancer cell lines that share the most of
  those hotspot-mutated genes, with the measured PRISM drug responses of the line you pick as the main evidence. It
  is a lookup on cell lines, not a prediction for a patient. Per-drug model ranks come second and are greyed out
  when weak (the lower end of their held-out 95% CI is at or below 0.5), because most are close to chance (see below).
- **Safety flags (loop 3):** for each of 12 Tox21 lab assays, the molecule's score next to that assay's active
  rate and its held-out ROC-AUC. No toxicity verdict, and it abstains on molecules unlike its training data.
- **Analogs (loop 4):** paste one molecule and the app applies a fixed list of nine small RDKit edits to it, one
  at a time, then scores every edited copy with the activity model for the selected target and the 12 Tox21
  models, side by side and never combined into one number. The parent is shown first for comparison. It is
  enumeration, not a generative model: nothing is sampled and the same input always gives the same analogs.
  None of the molecules it makes has been measured anywhere, and when the analogs' scores sit closer together
  than the model's own split-to-split movement the tab says the ranking is not a ranking.

Held-out results (numbers from the results files in the repository):
- Activity, scaffold split: random forest ROC-AUC 0.845 to 0.971 across the 9 targets, against a
  1-nearest-neighbour baseline of 0.787 to 0.950; above the baseline on 9 of 9 targets
  (`results/activity_models.md`).
- Drug response, leave-lineage-out split: median ROC-AUC 0.546 against 0.516 for 1-nearest-neighbour, both over
  the 198 drugs that are not underpowered; 171 of 202 models are weak. We report this as a negative result
  (`results/loop2_models.md`).
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
before every merge. Commits carry Co-Authored-By trailers. Of the 73 non-merge commits as of 7308fed (2026-11-05), 46 name Claude Fable 5.1, 24 name Claude Opus 5.5, 1 names Claude Opus 5 and 2 setup commits name Claude Sonnet 5.5. Recount with `git log --no-merges --format='%(trailers:key=Co-Authored-By,valueonly)' | grep -oE "Claude (Fable 5\.1|Opus 5\.5|Opus 5|Sonnet 5\.5)" | sort | uniq -c`, which sums to exactly the 73 commits; grepping whole commit messages instead gives 75, because two commit bodies discuss these model names in prose. The figures are pinned to a commit because every new commit changes them: the commit that records these ones adds a further Opus 5. Of the 46 naming Fable, 24 were in fact written by subagents running Claude Opus 5.5 (the scaffold, data registry, loop-1, loop-2 and activity-tab work): the manager's task briefs specified the manager's own attribution line by mistake, which an audit of the trailers caught while this section was first written. The other 22 are the manager session's own commits, made while it ran Fable 5.1. The 24 naming Opus 5.5 are later subagent work (loop 3, the model bundle, the analogs tab) together with the manager session's own commits after it switched to Opus 5.5, and the one naming Opus 5 is the manager session's own work after its model moved again. Git history was not rewritten; every commit since the audit names the model that wrote it.

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
  so the app leads with the measured responses of similar cell lines.
- Check the licence before downloading: our first loop-2 data source has a non-transferable policy, so we switched
  to Broad's CC BY 4.0 snapshots. Free hosting changed too: Hugging Face Spaces now needs a paid plan for the kind of
  Space Streamlit needs, so we host on Streamlit Community Cloud.

## What's next
- A wider analog list: ring-size and linker changes, beyond the nine single-point edits now shipped.
- Richer features for the drug-response models (damaging mutations beyond hotspots, other cell-line data).
- Mutant-specific activity models from the mutant-protein assays the current models leave out.
- A medicinal chemist's review of the examples, the wording and the abstain behaviour.

## Built with
<!-- Devpost's tag box splits on spaces: one word per tag. -->

python rdkit scikit-learn lightgbm streamlit pandas numpy joblib uv pytest ruff chembl depmap prism tox21
moleculenet streamlit-community-cloud github claude-code

## Links
- Repository (public since 2026-11-04): https://github.com/PSMacaroni/stem2connect-2026
- Demo video (YouTube or Vimeo, public or unlisted, 6 minutes or less): [video URL]
- Live demo: https://stem2connect-2026-cjfcmxcaxddeqtfvyvjzbw.streamlit.app/ (Streamlit Community Cloud; sleeps after 12 idle hours, wakes in about a minute)

## Team members (all added on Devpost)
Prakhar Suryansh (solo)

## Numbers appendix
Every figure in the README, in this Devpost text and in the video script. "README" covers the README sections;
"Devpost" covers this file; "Video" covers `docs/video.md`, the numbers said out loud.

**Most of this table is machine-checked, and CI checks it on every push.** `uv run python
scripts/check_numbers.py` recomputes 38 of these figures from `results/*.json`, the bundle manifest and the repo
itself, formats each one the way the documents write it, and fails if that string is missing from every document
that claims it. It catches drift in both directions: a results file that changes under a document, and a document
edited away from its source. No copy of any figure lives in the script. Last full run 2026-11-05: 38 of 38
matched.

The CI job can only check what is in git. `models/`, `data/` and `dist/` are not, so a CI run checks **33 of the
38** and prints the five it skipped with the file each one needs: the 212 models, the 4 DepMap tables, the 217
files, the 188 MB zip and the 542 hotspot genes. Before submitting, run `scripts/check_numbers.py --strict` on a
checkout that has the models bundle; `--strict` fails on a skip, so no figure can pass by being unverifiable.

Two kinds of figure the script cannot own are marked "not machine-checked" below: wall-clock timings, which depend
on the machine, and the commit-trailer counts, which change with every commit and are pinned to a named commit in
the text instead.

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
| Median ROC-AUC 0.546 (logistic regression) vs 0.516 (1-NN) | README Results at a glance, What we learned; Devpost | `results/loop2_models.md`, "What this says". **Both are medians over the 198 drugs that are not underpowered**, and every place that quotes them now says so: over all 202 the logistic median still rounds to 0.546, but the 1-NN median is 0.517, not 0.516; machine-checked against the 198 |
| 171 of 202 shipped models weak | README Results at a glance, What we learned; Devpost | `results/loop2_models.md`, "What this says". **Weak = the shipped model's 95% CI lower bound is at or below 0.5**, i.e. it is not shown to beat chance. Counting instead the models whose CI *contains* 0.5 gives 166, which is why the earlier phrase "CI reaches 0.5" was replaced |
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
| 188 MB models zip | README How to run it | `dist/models-v2.zip` is 188,245,280 bytes; machine-checked |
| 212 models and 4 DepMap tables; `217 files verified` on download | README How to run it | `models/MANIFEST.json` has 212 entries (9 target models + `tox21.joblib` + 202 loop-2 models); `data/depmap/derived/` has 4 CSVs; 212 + 4 + `PULL_INFO.json` = 217; machine-checked |
| about 15 minutes to train, about 3 minutes for the first `uv sync` | README How to run it | **not machine-checked**: wall-clock on the owner's PC, WSL on a Windows drive. Hardware-dependent, so the README says "about" |
| 129 MB Tox21 bundle | `tests/test_analogs.py` comment | `models/tox21.joblib` is 129,165,820 bytes |
| 9 single-point transforms | Devpost What it does; Video shot 7 | `TRANSFORMS` in `src/molscreen/analogs.py`; machine-checked |
| Analog scores flat below a 0.05 floor | Analogs tab; Devpost | `FLAT_SPREAD` in `src/molscreen/ui_analogs.py`. Justified by the largest held-out ROC-AUC movement of the shipped forests across scaffold-split seeds 0 to 4, 0.0438 (CDK6), from `split_variance` in `results/activity_models.json`. `scripts/check_numbers.py` asserts the floor still covers that movement; `tests/test_analogs.py` asserts the 0.0438 |
| Analogs on the CDK6 example: 10 scored, spread 0.000 | Video shot 7 | computed by `flatness()` at render time from the rows on screen, so it is not a fixed figure. Seen 2026-11-05 on the live app. The script tells the recorder to read the app, not recite it |
| CDK6 held-out ROC-AUC 0.894, 95% CI 0.784 to 0.980 | Video shot 3 | `genes.CDK6.rf` in `results/activity_models.json`; machine-checked |
| caffeine: max Tanimoto 0.15 against a 0.71 cut-off | Video shot 4 | recomputed 2026-11-05: `predict("CDK6", [caffeine])` gives `max_tanimoto` 0.152778 and `abstain_cutoff` 0.712329. The model's hidden score (0.888) is never shown by the app and is deliberately not said in the video |
| 61 tests in the suite | README How to run it | counted from `tests/test_*.py`; machine-checked |
| 14 of the 61 skip in a fresh clone, 60 pass after step 7 | README How to run it | measured 2026-11-08 on WSL's own disk, with `models/` and `data/` emptied to stand in for a fresh clone: **47 passed, 14 skipped** in 32 s; with the models bundle present, **60 passed, 1 skipped** in 2 min 36. The skip is `tests/test_data.py::test_real_cdk6_dataset`, which needs `scripts/pull_chembl.py`; the owner's own checkout has that pull, which is why it reports 61 passed. The earlier figures (57 tests, 43 passed, 56 passed, measured 2026-11-05 on 30b4cb0) held until `tests/test_narrate.py` added 4 |
| Python 3.12 | README How to run it | `.python-version` says `3.12`; `pyproject.toml` allows `>=3.11,<3.13` |
| about a minute to wake from sleep | README live-app line; Devpost | timed once on 2026-11-05. Not a repeated measurement, and the README says so |
| 145 words a minute, so 792 words is 5:28 | Video budget line | the pace is an assumption the script now states, not a measurement; the word count is machine-checked. The script tells the recorder to time shot 1 against it before recording the rest |
| the ten most sensitive compounds, not 202 drugs | Video shot 5 | `top_compounds(model_id, n=10)` in `src/molscreen/depmap.py`, titled "10 most sensitive PRISM compounds measured on ..." by `src/molscreen/ui_cells.py`. The pool is every PRISM compound measured on that line: for NCI-H1573 (ACH-000916) that is 1,389 compounds, of which 196 are among the 202 modelled drugs (counted from `data/depmap/derived/sensitivity.csv` on 2026-11-05). An earlier draft of the script said "202 drugs in the PRISM screen", a figure the screen never shows |
