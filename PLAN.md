# Plan

This file is Prakhar's. Agreed with the manager session on 2026-11-04. Keep it current.

## Idea and track
**Name: Molecule Screening Workbench** (decided 2026-11-04). A free cancer drug-screening workbench for students and small labs.
Track: **Scientific Research** ("tools for analysis"). Solo entry.

Four loops, in ship order. Loops 1 and 2 are never cut.
1. **Molecules → activity.** Paste SMILES, pick a cancer target (EGFR, BRAF, HER2/ERBB2, CDK4, CDK6, ALK, ABL1,
   PARP1, BCL2), get a ranked activity prediction plus the nearest known actives from ChEMBL shown as evidence.
2. **Mutations → drugs.** Enter mutated genes; see the most similar cancer cell lines with their measured drug
   sensitivities, plus trained sensitivity models for the 20 to 30 best-sampled drugs. Cell-line data, never patients: the Broad
   **Figshare snapshots** DepMap 24Q4 Public (mutations, `Model.csv` without the donor age/sex/race columns) and PRISM
   Repurposing 20Q2 (dose-response: `auc`, `ic50`, `smiles`), joined on `ModelID`; all CC BY 4.0 (verified 2026-11-04).
   The current DepMap portal releases (25Q2 onward) are NOT used: new terms restrict ML use and the portal is captcha-gated.
3. **Molecules → safety flags.** Tox21 assays per molecule, with confidence and an abstain when the molecule is
   unlike the training set.
4. **Analog enumeration.** RDKit transforms on a known active, scored by loops 1 and 3, top few shown.

Why this and not a third slide-analysis tool: Learning and Growth is 20% of the score; the new-work rule and the
non-commercial pathology encoder licences make slide reuse a drag in a public repo; and generalist judges can
grade a screening tool's problem and impact. See the vault decision note.

## Facts that bound the plan
Details in `docs/hackathon.md`.
- Submission deadline: Sat 2026-11-21, 11:59 PM EST (10:59 PM Chicago). Demo Day: Tue 2026-11-24.
- Needed to be eligible: public GitHub repo with README, demo video (6 min or less) showing it working,
  Devpost description, one track, all team members added.
- New work only (Oct 11 to Nov 21). Credit libraries, datasets, APIs. Disclose reused work and AI assistants.
- Time: 10 to 20 hours a week from Prakhar, counting review. Enveda CASMI runs at the same time; no code crosses
  between the two repos.
- Spend cap: **$0**. CPU in WSL on this PC, Google Colab free for one-off GPU runs.

## Approach
**AI.** Floor: RDKit Morgan fingerprints + LightGBM or random forest, one model per target. Comparison: ChemBERTa
(or a similar open chemistry model from Hugging Face) embeddings + small head, the same linear-probe idea as Ashby.
Stretch: a graph neural network trained on Colab.

**Honest evaluation, decided before any result.**
- Scaffold-split held-out test sets (the molecule version of patient-disjoint testing). Never tune on them.
- Baselines on every held-out set: majority class and 1-nearest-neighbour by Tanimoto. "Beats the baseline" means
  held-out ROC-AUC on the pre-registered split; a model that does not exceed 1-NN there is marked "no better than
  nearest-neighbour lookup" and the app leads with the nearest actives instead. All other metrics are reported even
  where the model loses (first run: RF below 1-NN on balanced accuracy on 8 of 9 targets).
- Abstain when a query is far from the training data (Tanimoto distance cutoff set on the training set).
- Every number in the README, the write-up and the video traces to a run file and says how it was computed.

**Wording.** "Research and learning tool, not medical advice." Never "discovers drugs", never "predicts a patient's
response". GDSC rows are cell lines.

**Data and licences.** ChEMBL_37 (activities, CC BY-SA 3.0: derived data files carry the same licence), Tox21 via
MoleculeNet (safety; licence unstated, so the raw file is never committed), Broad DepMap 24Q4 + PRISM 20Q2 Figshare snapshots (drug
sensitivity and cell-line mutations, CC BY 4.0; replaces Sanger GDSC / Cell Model Passports, whose policy is non-transferable), an open
chemistry encoder from Hugging Face (ChemBERTa-100M MIT or MoLFormer Apache-2.0; not ChemBERTa-77M, which has no
licence). Each licence is checked and written into `docs/data-registry.md` before any download, and credited in the
README. Raw data never goes in git; pull scripts do.

**Build.** Models (loop 1 forests 51 MB, loop 3 forest 129 MB, loop 2 logistic 1.5 MB) ship as a GitHub release asset
that the app downloads once at startup and caches (decided 2026-11-04). Streamlit app hosted on **Streamlit Community Cloud** (Hugging Face Spaces no longer runs code for free,
checked 2026-11-04). Memory ceiling about 2.7 GB, so models stay small and are bundled with the app. The app sleeps
after 12 idle hours: wake it before judging. Repo **public since 2026-11-04** (flipped early so hosting can be tested; release v2 holds the models and the DepMap tables, v1 the models only).

**Way of working.** Manager session (Fable) plans and reviews; Opus subagents build, one task each, on branches
`area/topic`. PASS only when tests and lint pass, the "done" checks hold, and the vault is updated.

## Weeks
- **Nov 4 to 10:** licence and data registry; data pulls; activity models with the evaluation protocol; app with the
  activity tab; README with AI disclosure; GitHub repo created (private).
- **Nov 11 to 17:** mutations loop; safety flags; ChemBERTa comparison; hosting on Streamlit Community Cloud; first video take.
- **Nov 18 to 20:** analogs if time; numbers pass; fresh-clone test; final video; repo public; submit Nov 20
  with a day spare.

## Cut order
What gets dropped first if time runs out.
1. Analog enumeration (loop 4)
2. GNN stretch
3. ChemBERTa comparison
4. Hosting (fall back to the video plus a local run from the README)
5. Safety flags (loop 3)
Never cut: loops 1 and 2, the evaluation protocol, the README disclosures, the video.

## Decisions
| Date | Decision | Why | Rejected |
|---|---|---|---|
| 2026-11-04 | Molecule screening workbench, Scientific Research track | Learning and Growth score; licence and new-work friction of slide reuse; impact legible to generalist judges | A third slide-analysis tool |
| 2026-11-04 | Loops 1 and 2 are the core; 3 and 4 are extras | 10 to 20 h/week, solo | Generation as a core feature |
| 2026-11-04 | Nearest cell lines + per-drug models for loop 2 | Honest, demoable in a week | One drug+genomics model; lookup only |
| 2026-11-04 | Analog enumeration, not a generative model | Simple and explainable | Training a generator |
| 2026-11-04 | Streamlit on Hugging Face Spaces, Community Cloud fallback | More memory and disk; named on the Resources page; Streamlit known | Gradio; local only |
| 2026-11-04 | $0 spend cap | Everything fits free tiers | $10, $25 |
| 2026-11-04 | Activity models are wild-type only; rows from mutant-protein assays are dropped | Review found 43% of BRAF rows and 22 to 24% of EGFR and ALK rows came from mutant assays pooled with wild-type; a clean claim beats a bigger dataset | Keep pooled and disclose; separate mutant models (maybe week 2) |
| 2026-11-04 | Strip salts to the parent molecule before aggregating | 614 EGFR and 113 ALK molecules were the same parent under different ChEMBL IDs (double-counted, no leak) | Keep as is and disclose |
| 2026-11-04 | CDK4 and CDK6 stay, marked "underpowered" with their test inactive counts (36 and 8 after the re-run; 6 in the first run) | Keeps the 9-target panel without hiding the noise | Drop CDK6; merge CDK4/6 |
| 2026-11-04 | Headline metric is ROC-AUC with a bootstrap 95% CI next to the 1-NN baseline; then inactive-class PR-AUC vs random; balanced accuracy shown even where RF loses; active-class PR-AUC last | Actives are 70 to 97% of molecules, so active-class PR-AUC is inflated by construction | Inactive-class PR-AUC as the headline |
| 2026-11-04 | Nearest cell lines rank by number of shared mutated genes first, then Jaccard | Plain Jaccard put lines carrying only the listed genes first (43 ties at 0.667 for KRAS/TP53/STK11) | Plain Jaccard; rarity-weighted genes |
| 2026-11-04 | Per-drug models only for compounds whose PRISM target names a gene, oncology drugs first (about 30 to 60) | 1,457 of 1,494 compounds pass the 300-line rule, so "best-sampled" selects nothing | Most variable 30; all 1,457 |
| 2026-11-04 | Loop 2 shows the nearest cell lines and their measured sensitivities first; model ranks second, greyed when the ROC-AUC CI includes 0.5; probabilities never shown as percentages | 60 hotspot-only per-drug models are near chance (median held-out ROC-AUC 0.56; 52 of 60 CIs include 0.5; 16 below 0.5) | Add damaging mutations and lineage as features (lineage is the split key); drop the models |
| 2026-11-04 | Loop 2 drug set: up to 3 most-screened drugs per oncology target gene, no overall cap | The top-60-by-line-count cap dropped the BRAF inhibitors, where hotspot mutations should matter most | Keep the 60 |
| 2026-11-04 | Loop 2 ships logistic regression, overriding the pre-registered switch rule by a dated amendment | The random forest won 32 of 60 (a tie-sized margin) and weighs 73 MB; logistic regression is a few hundred KB and within 0.01 median ROC-AUC | Bundle the random forest |
| 2026-11-04 | Loop 2 drug set also includes every selective (single-target) compound for an oncology gene with 300+ lines; multi-target compounds go to the gene with the fewest compounds so far | 3 per gene by screening count still left out dabrafenib and vemurafenib; "first listed gene" put paclitaxel under BCL2 | 5 per gene; leave the gap |
| 2026-11-04 | Main is pushed to the private repo after each PASS without asking; the public flip is a separate ask | Keeps CI honest; private and reversible | Ask before every push |
| 2026-11-04 | Trained models ship as a GitHub release asset that the app downloads once at startup and caches; the pre-registered random forests stay | Loop 1 is 51 MB and loop 3 is 129 MB, too big for git; Streamlit Community Cloud builds from the repo | Smaller forests (a re-evaluation); logistic regression for loop 3 (lost on 12 of 12 by 0.01 to 0.11) |
| 2026-11-04 | The safety tab shows each assay's score against the assay's active rate, with the assay's ROC-AUC and CI; no hard flag | Balanced accuracy at 0.5 is 0.52 to 0.70 and below 1-NN on 8 of 12 assays, while ROC-AUC beats 1-NN on 12 of 12 | A flag at a train-set threshold; the 0.5 flag |
| 2026-11-04 | Loop 2 keeps all 202 drugs from the 3-per-gene plus selective rules, with the odd single-target picks (antibiotics under TOP2A, thiram under JAK2, anthelmintics under TUBB) named in Known limits | They are real PRISM screens on cancer cell lines; the app leads with the lookup; no fourth round | A moa blocklist; selective drugs only for the 9 loop-1 targets |
| 2026-11-04 | Name: Molecule Screening Workbench | Plain and clear | OncoScreen; HitBench |
| 2026-11-05 | The Analogs tab reports the spread of its own scores and calls a flat ranking flat | Analogs of a known active all score at the ceiling (CDK6: parent 1.000, ten analogs 1.000), so an ordered list would imply a discrimination the evaluation cannot defend | Showing the ranking plainly; dropping the ranking; a combined activity-and-safety score |
| 2026-11-05 | Ship a `packages.txt` with libxrender1 and libxext6 | Streamlit Cloud's image has no libXrender, so `from rdkit.Chem import Draw` kills the app at import | Dropping the drawn structures; a Docker-based host |
| 2026-11-04 | Release v1 with the full models bundle on the private repo | The app needs it at startup; hosting cannot be tested without it | Keep the zip local |
| 2026-11-04 | Co-author trailers: the manager's early briefs made Opus subagents sign commits with the manager's Fable line; disclosed in the README, history not rewritten | Honesty about who wrote what; a rewrite would hide the mistake and break the pushed history | Rewriting history |
| 2026-11-04 | Repo flipped public the same day, after the README disclosures merged | The app's startup download is anonymous; hosting cannot be tested on a private repo; a week of buffer | Public after the tabs merge; last week as first planned |
| 2026-11-04 | Private GitHub repo PSMacaroni/stem2connect-2026 created and main pushed | CI on GitHub Actions; public flip in the last week | Stay local |
| 2026-11-04 | Host on Streamlit Community Cloud, not Hugging Face Spaces | Spaces now needs a paid plan for Gradio and Docker Spaces; Community Cloud is free and known | Gradio on a free ZeroGPU Space; paying for HF PRO |
| 2026-11-04 | Loop 2 uses the Broad Figshare snapshots (DepMap 24Q4 + PRISM 20Q2, CC BY 4.0) instead of Sanger GDSC + Cell Model Passports | Sanger's policy is non-transferable and bans use in third-party websites; the Figshare records carry CC BY 4.0 (checked on the Figshare API); current portal releases have restrictive terms and a captcha | Emailing Sanger for permission; keeping GDSC local-only; the 26Q3 portal release |

## Done
- 2026-11-03: scaffold (README skeleton, rules, templates).
- 2026-11-04: plan agreed. Python scaffold (`molscreen`, chem helpers, scaffold split, tests, CI) merged.
  Data registry with licences merged (`docs/data-registry.md`).

## Next
- Done 2026-11-04: Broad DepMap / PRISM licence check (registry section 3b).
- Done 2026-11-04: loop-2 data layer (DepMap 24Q4 + PRISM 20Q2 pull, derived tables, nearest-cell-line lookup, protocol first). Private GitHub repo created and pushed.
- Done 2026-11-04: loop 1 data and models PASS after two review rounds (wild-type only, salts stripped, RF shipped, ROC-AUC 0.845 to 0.971 with CIs, split variance disclosed). Results: `results/activity_models.md`.
- Done 2026-11-04: the Streamlit app with the activity tab (loop 1) merged; headless health ok, example molecules and nearest actives render.
- Done 2026-11-04: loop 3 (Tox21) data and models PASS and merged: random forest beats 1-NN on 12 of 12 assays (ROC-AUC 0.66 to 0.83), 7,709 parent molecules, shared scaffold split; contract is score vs prevalence. Results: `results/tox21_models.md`.
- Done 2026-11-04: loop 2 per-drug models PASS after three rounds and merged: 202 drugs, logistic regression ships, median ROC-AUC 0.546, 171 of 202 weak, lookup is the main evidence. Results: `results/loop2_models.md`.
- Done 2026-11-04: models release bundle and startup download merged; release v1 published (212 files, 178,693,014 bytes); README disclosures, credits and results table and the Devpost draft merged (three review rounds); repo made public; anonymous download verified with the hash check.
- Done 2026-11-04: loop-2 (Cell lines) and loop-3 (Safety flags) tabs merged; all four loops' evidence shown as decided; 46 tests.
- Done 2026-11-04: bundle v2 (212 models + 4 DepMap tables + PULL_INFO, 217 files, 188,245,280 bytes, SHA-256 c1407c0b...7402) merged; README and Devpost describe the live tabs.
- Done 2026-11-04: release v2 published by Prakhar (`gh release create v2`, 188,245,280 bytes, target main); the manager verified an anonymous download through `ensure_models` with the SHA-256 secret set: 217 files verified.
- Done 2026-11-05: **app live** at https://stem2connect-2026-cjfcmxcaxddeqtfvyvjzbw.streamlit.app/ . Deploy crashed first on `libXrender.so.1` (RDKit drawing needs a system
  library the Streamlit image lacks); fixed with a two-line `packages.txt`. All three built tabs checked in the browser on the
  hosted app: Activity (3 predictions, structures of nearest actives with ChEMBL IDs and Tanimoto), Cell lines (KRAS/TP53/STK11
  gives NCI-H1573 first on 3 shared genes above higher-Jaccard lines, then the PRISM responses), Safety flags (12 assays with
  score, active rate, ratio and ROC-AUC CI), Analogs shows "Coming". Anonymous fetch with cookies returns 200.
- Done 2026-11-05: **fresh-clone test passed** (commit 5c06d12). Cloned the public repo into a clean directory and
  followed README "How to run it" literally: `uv sync` fine, `pytest -q` 36 passed 11 skipped, `ruff` clean,
  the download printed `217 files verified` (212 models + 4 tables, 16 s), the app started and the Activity
  Example gave 3 predictions; a second test run gave 46 passed 1 skipped. Four README faults found and fixed:
  no step told the reader to clone the repo; `scripts/pull_depmap.py` alone does not build the derived tables
  (`python -m molscreen.depmap` does); `molscreen.train` needs `scripts/pull_chembl.py` first; and the note that
  the app needs models from `molscreen.train` was wrong, since the app downloads them itself. Also documented
  Streamlit's first-run email prompt.
- Done 2026-11-05: an independent run of the same test (a second session) matched every count and found two more
  faults of the same class, fixed in b2381a7: `molscreen.tox` needs `scripts/pull_tox21.py` first, and
  `molscreen.drugs` reads the derived DepMap tables, so it runs after `molscreen.depmap`, not beside it.
  Evidence for the two step-8 claims: the hosted app's repo carries no models yet serves predictions, which only
  the startup download explains; the email prompt was seen in this machine's own run log.
- Done 2026-11-05: **Analogs tab (loop 4) built and merged** (cbc580c, then c064ade). Nine single-point RDKit
  transforms on one molecule; each copy scored by the loop-1 activity model and the 12 loop-3 Tox21 models, side
  by side, never combined. Parent shown first; both abstain rules unchanged. 56 tests pass, ruff clean, checked on
  the live app. Two honesty problems found in review and fixed before merge: the scores saturate (CDK6 example
  parent 1.000, the 10 shown analogs all 1.000, spread 0.000), so the tab now measures the spread and says the
  order is not a ranking when it falls under 0.044, the most these forests move across split seeds 0 to 4; and the
  Tox21 count was shown even when the Tox21 models abstained, which it no longer is. All four loops now have a tab.
- Done 2026-11-05: **video script covers the Analogs tab** (7308fed, 9bf3d0d). The script had said the tab was not
  built and closed by promising it. It now has a 0:40 shot on it, and it tells the recorder to read the warning the
  app prints rather than recite numbers, because the spread is computed at render time. Paid for the shot by
  trimming five others: 797 narration words (counted from the file) and 5:35 of shots, 25 s under the limit. The
  same sweep caught two places still saying the workbench answers three questions (README, `docs/submission.md`),
  and the AI disclosure counts going stale again, so those counts are now pinned to a commit with the recount
  command beside them. Docs only: ruff clean, and the full suite in this checkout gives **57 passed** (the suite
  has 57; `tests/test_data.py::test_real_cdk6_dataset` is skipped wherever `data/chembl/CDK6.csv` is absent, so a
  worktree or fresh clone reports 56 passed 1 skipped, which is where the earlier "56 tests" figure came from).
- Waiting on Prakhar: record the demo video (`docs/video.md`); Devpost registration; Discord.
- Then: a final numbers pass over the README, the write-up and the video script, each figure against its source
  file; wake the app on 2026-11-22 (judging) and 2026-11-24 (Demo Day).

## Problems
- Tox21 has no stated licence (probably US-government public domain): raw file never committed, cited only.
- CDK6 has 8 inactives in its test set (6 in the first run), CDK4 36: both marked underpowered.
- Loop 2 per-drug models on hotspot mutations alone explain little (median ROC-AUC 0.56 at 5b7d361 on the branch); the write-up reports this as a negative result and the app leads with the lookup.
- Leave-lineage-out test set never asks about Skin (BRAF melanoma) or blood lineages: they all sit in train.
- Loop 2 derived tables are 31 MB (sensitivity.csv 28.9 MB): too big to commit as is for the hosted app; trim or compress before hosting.
- Only 117 of 1,494 PRISM compounds carry a ChEMBL ID, so linking loop 2 drugs to loop 1 targets needs the SMILES, not the ID.
- Changing the scaffold-split seed alone moves ROC-AUC by up to about 0.046 (ERBB2, CDK6), more than the RF lead over 1-NN on ABL1 and BCL2 and more than any RF-vs-LightGBM gap; bootstrap CIs cover one test set only. Reported as a disclosure over 5 seeds; nothing is chosen from it.
- The switch rule reads the held-out set once (pre-registered); README must say so. Model parameters were committed with the first results, not with the protocol.
