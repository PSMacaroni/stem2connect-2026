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
| 2026-11-08 | The demo narration may be spoken by the Windows synthesiser instead of read aloud, if Prakhar prefers; disclosed as an AI tool either way | He asked twice for the video to be voiced for him, and Claude cannot record or speak; generating the audio on his machine is the part of that which is actually possible, and it removes the hardest bit of recording (talking and clicking at once) | Claude recording or voicing the video (no speech or screen capture exists in the session); a slideshow of screenshots (would not show the app working); leaving him to read all 796 words live |
| 2026-11-08 | Reboot the hosted app for judges, but record the demo against a local app | The hosted free tier caps memory at about 1 GB and the four-tab walk needs 1,607 MB, so a take could die mid-shot; a local run has 16 GB behind it and changes no code, no model and no published figure | Retraining the Tox21 forests smaller (a protocol change: dated amendment, loop-3 re-run, every Tox21 figure re-checked); paying for more memory |
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
  has 57; `tests/test_data.py::test_real_cdk6_dataset` is skipped wherever `data/chembl/CDK6.csv` is absent, which
  is where the earlier "56 tests" figure came from). Corrected the next day: a *fresh clone* skips 14, not 1, since
  13 more tests need the models and the DepMap tables. Measured figures are in `docs/submission.md`.
- Done 2026-11-05: **final numbers pass**, run early rather than in the last week. Every figure in `README.md`,
  `docs/submission.md` and `docs/video.md` traced to a source. Five faults found and fixed, two of them by an
  independent audit that the manager then re-verified from the code itself:
  1. The README said the suite has 47 tests with 11 skipped in a fresh clone. It has 57. Measured in a clean
     worktree by following the README: **43 passed, 14 skipped** with no models, then **56 passed, 1 skipped**
     after `ensure_models()` (`217 files verified`, 50 s), which is what step 5 now says.
  2. The video said the Cell lines tab shows responses to "two hundred and two drugs in the PRISM screen". The tab
     shows ten rows (`top_compounds(model_id, n=10)`), drawn from every PRISM compound measured on that line, 1,389
     for NCI-H1573, of which 196 are among the 202 modelled drugs. 202 is loop 2's model count, not what the screen
     shows, so the script broke its own "say it only if the screen shows it" rule.
  3. "171 of 202 weak (95% CI reaches 0.5)" invites the reading "CI contains 0.5", which counts 166. The project's
     definition is "CI lower bound at or below 0.5", which counts 171. Reworded everywhere.
  4. "171 of 202 weak, 73 below 0.5" mixed denominators: `weak` is over all 202, `below_half` over the 198 that are
     not underpowered (76 over all 202). Fixed in the generator template in `src/molscreen/drugs.py` and
     `results/loop2_models.md` regenerated from the stored JSON, so nothing was retrained to change one sentence.
  5. The Devpost text gave the loop-2 medians with no scope; the 1-NN median is 0.516 over the 198 and 0.517 over
     all 202, so the figure was right for one group only.
  Also sourced three figures the audit could not trace: Python 3.12 (`.python-version`), the wake time (timed once,
  now dated in the README) and the 145-words-a-minute pace the script's budget assumes, now stated.
  The pass is now a script: `uv run python scripts/check_numbers.py` recomputes 38 figures and asserts each one
  still appears in the documents that claim it. 38 of 38 match.
- Done 2026-11-05: **the numbers check runs in CI** on every push, after ruff and pytest. It can only check what
  is in git, and `models/`, `data/` and `dist/` are not, so a CI run checks 33 of the 38 and prints the five it
  skipped with the file each needs. `--strict` turns a skip into a failure, verified both ways: on a full checkout
  38 checked and 0 skipped, exit 0; on a clean worktree 33 checked and 5 skipped, exit 0 plain and exit 1 strict.
- Done 2026-11-08: **walked the live app shot by shot against the script**, which found three things no test or
  figure check covers, because they are wording on screen rather than numbers:
  1. The Cell lines tab said weak models are "no better than chance on held-out lineages". A CI lower bound at or
     below 0.5 means *not shown to* beat chance, not shown *not to*. The app was claiming more than the evidence.
     Reworded in `src/molscreen/ui_cells.py` to the README's wording, and the same loose phrase fixed in two
     docstrings in `src/molscreen/drugs.py`. The code was always right; only the prose overreached.
  2. The Analogs tab captioned "25 analogs from 9 transforms, ranked by p_active, highest first" directly above a
     ten-row table, because the caption counted what was generated and the table showed `top`. On camera a judge
     counts ten. The caption now says which it is showing and out of how many.
  3. Shot 3 of the script never said the Example molecules are in the training table, though the app says so on
     screen and the open expander shows `Tanimoto 1.00` on the top row. The narration must not be less honest
     than the app, so it gained one sentence; the budget note now cuts the shot-1 sentence by default to pay for
     it (809 words written, 796 spoken, 5:29 against a 5:35 shot list).
  Also checked: NCI-H1573 is already selected when the Cell lines Example loads (the script said to pick it), the
  caffeine abstain reads exactly "max similarity 0.15 < cut-off 0.71", and the live app woke in about 70 seconds,
  which is the second measurement behind the README's "about a minute".
- Done 2026-11-08: **`docs/video-teleprompter.md`**, the script one sentence to a line with the beats marked and a
  running clock, generated from `docs/video.md` by `scripts/teleprompter.py` so it cannot drift. `--check` runs in
  CI. Nothing in it is typed by hand: every word count and time is computed, and the 145-words-a-minute pace is
  labelled an assumption with a shot-1 stopwatch test to confirm it.
- Done 2026-11-08: **`docs/submission.md` now says which Devpost box each section goes in**, with a pre-submit
  checklist. No text is duplicated, so the form and the file cannot disagree.
- Done 2026-11-08: **the local run for the recording is tested and written down** in `docs/video.md`. Two things
  had to be worked around: port 8501 is held by another Streamlit app on the Windows side (use 8511), and running
  from `C:\` inside WSL never finished starting in over two minutes. From a copy on WSL's own disk
  (`~/s2c-demo`, 176 MB, no `data/` or `dist/`) it binds in under 5 s, draws the first page in about 10 s, and all
  four tabs work: Activity gives the 3 Example predictions with the training-molecule note, Cell lines has
  NCI-H1573 already selected with the reworded weak-model caption, Safety flags scores the 3 Example molecules,
  Analogs prints "The 10 shown below are the highest-scoring of 25 analogs" and the flat-ranking warning. Peak
  **1,607 MB**, which independently confirms the 1,605 MB measured with the synthetic loader, in the real app this
  time. Suite in that copy: **56 passed, 1 skipped in 56 s** (the skip needs `data/chembl/CDK6.csv`, not copied).
- Done 2026-11-08: **the hosted app is back up** (Prakhar rebooted it; front page and all four tabs render again).
- Done 2026-11-08: **a synthesised voice-over, so the recording is clicking rather than talking and clicking at
  once.** `scripts/narrate.py` turns the narration in `docs/video.md` into one SSML file per shot, reusing the
  parser in `scripts/teleprompter.py`, so the audio cannot say anything the script does not; `scripts/narrate.ps1`
  renders it with the speech synthesiser built into Windows and reports every length read back out of the WAV it
  wrote. Measured: the voices' own default rate is **142 wpm (David) and 146 wpm (Zira)** over shot 1's 72 words,
  so the 145 the script budgets for needed no slowing. Totals **5:40 (Zira)** and **5:45 (David)**, both inside
  6:00, leaving about 20 s for the gaps between shots. Audio goes to `dist/narration/` and is not in git.
  **Unverified: the pronunciation.** Nothing in this session can play audio, so `ChEMBL`, `Tox21`, `KRAS`, `TP53`
  and `STK11` have not been heard; `docs/video.md` tells him to listen to two shots first and gives him a `SAY`
  respelling table for anything that comes out wrong. Using the audio is an AI tool and has to be disclosed: the
  sentence to paste is in the pre-submit checklist, and the README's video line says the choice is still open.
  **Voice chosen 2026-11-09: Microsoft David Desktop**, after hearing shot 1 in both. `dist/narration/` is now
  David throughout (5:45, 15 s under the limit) and the script's default matches, so a re-render cannot silently
  change voice. Rendering is deterministic: the second David run gave 345.2 s again, to the tenth of a second.
  `tests/test_narrate.py` (4 tests) holds the SSML to the script, which took the suite from 57 to **61 tests** —
  caught immediately by `scripts/check_numbers.py`, since the README's counts are machine-checked. Re-measured
  rather than adjusted: **47 passed, 14 skipped** with `models/` and `data/` emptied, **60 passed, 1 skipped**
  with the models present.
- Waiting on Prakhar: record the demo video (read `docs/video-teleprompter.md`); Devpost registration; Discord.
  Claude cannot record it: there is no way to produce speech or capture a screencast from this session, and the
  presentation in a judged student entry should be his voice regardless.
- Then, before submitting: `uv run python scripts/check_numbers.py --strict` on this checkout, which has the models
  bundle, so none of the 38 passes by being unverifiable. Wake the app on 2026-11-22 (judging) and 2026-11-24
  (Demo Day).

## Problems
- **The hosted app ran out of memory on 2026-11-08 and is down**, showing "This app has gone over its resource
  limits. It's using too much memory!" It did not come back on reload; Streamlit Cloud needs a **Reboot app** from
  share.streamlit.io, which only Prakhar can do. Measured peak RSS on the owner's machine, loading one loop at a
  time: 178 MB imports, 241 MB with one activity model, 581 MB once the DepMap tables are in (the 28 MB
  `sensitivity.csv` is most of that), still 581 MB after all 202 per-drug models, and **1,605 MB once the Tox21
  bundle loads**. The bundle itself is the problem and the forests are all of it: `train_fps_packed` is 1.6 MB and
  the `train` frame 0.9 MB, but the 12 random forests hold **7,776,632 tree nodes** at 500 estimators each, which
  is about a gigabyte of `tree_` arrays. Exercising all four tabs in one session is what reaches that peak, and it
  is exactly the video's running order, with the Analogs tab (which scores 25 analogs against the activity model
  and all 12 Tox21 models) last and heaviest. This did not bite on 2026-11-05 because the Analogs tab was not
  live yet. **Needs a decision before submitting**, because a judge who opens the link sees the same error:
  (a) reboot and record against a local app, changing no code and leaving the hosted app fragile; (b) retrain the
  Tox21 forests smaller (fewer estimators, or a `min_samples_leaf` floor), which is a protocol change needing a
  dated amendment, a re-run of the loop-3 evaluation and an update to every Tox21 figure in the README, the
  Devpost text and the video script; (c) pay for more memory. **Decided 2026-11-08: (a).** Prakhar reboots the
  hosted app so the link works for a judge, and the video is recorded against a local app. No code, model or
  published figure changes. What this does not fix: a judge who opens all four tabs in one visit can still hit the
  error. The README now says so, and says the local run has no such limit, which is the honest hedge. Prakhar
  looked at that paragraph and **kept it** (2026-11-08), so it stands: a judge who hits the error finds the cap,
  the 1.6 GB measurement and the local run written down a screen above it.
- Tox21 has no stated licence (probably US-government public domain): raw file never committed, cited only.
- CDK6 has 8 inactives in its test set (6 in the first run), CDK4 36: both marked underpowered.
- Loop 2 per-drug models on hotspot mutations alone explain little (median ROC-AUC 0.56 at 5b7d361 on the branch); the write-up reports this as a negative result and the app leads with the lookup.
- Leave-lineage-out test set never asks about Skin (BRAF melanoma) or blood lineages: they all sit in train.
- Loop 2 derived tables are 31 MB (sensitivity.csv 28.9 MB): too big to commit as is for the hosted app; trim or compress before hosting.
- Only 117 of 1,494 PRISM compounds carry a ChEMBL ID, so linking loop 2 drugs to loop 1 targets needs the SMILES, not the ID.
- Changing the scaffold-split seed alone moves ROC-AUC by up to about 0.046 (ERBB2, CDK6), more than the RF lead over 1-NN on ABL1 and BCL2 and more than any RF-vs-LightGBM gap; bootstrap CIs cover one test set only. Reported as a disclosure over 5 seeds; nothing is chosen from it.
- The switch rule reads the held-out set once (pre-registered); README must say so. Model parameters were committed with the first results, not with the protocol.
