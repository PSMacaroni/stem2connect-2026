# Plan

This file is Prakhar's. Agreed with the manager session on 2026-11-04. Keep it current.

## Idea and track
**Working name: (decide later).** A free cancer drug-screening workbench for students and small labs.
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
after 12 idle hours: wake it before judging. Repo private until the last week, then public.

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
| 2026-11-04 | CDK4 and CDK6 stay, marked "underpowered" with their test inactive counts (36 and 6) | Keeps the 9-target panel without hiding the noise | Drop CDK6; merge CDK4/6 |
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
- Done 2026-11-04: loop 3 (Tox21) data and models PASS on substance: random forest beats 1-NN on 12 of 12 assays (ROC-AUC 0.66 to 0.83), 7,709 parent molecules, shared scaffold split; contract amendment to score-vs-prevalence in progress.
- In progress: loop-2 per-drug models, round 2 verification (202 drugs).
- Then: loop-2 and loop-3 app tabs; README disclosures; hosting on Streamlit Community Cloud; first video take.

## Problems
- Tox21 has no stated licence (probably US-government public domain): raw file never committed, cited only.
- CDK6 has 6 inactives in its test set, CDK4 36: both marked underpowered.
- Loop 2 per-drug models on hotspot mutations alone explain little (median ROC-AUC 0.56 at 5b7d361 on the branch); the write-up reports this as a negative result and the app leads with the lookup.
- Leave-lineage-out test set never asks about Skin (BRAF melanoma) or blood lineages: they all sit in train.
- Loop 2 derived tables are 31 MB (sensitivity.csv 28.9 MB): too big to commit as is for the hosted app; trim or compress before hosting.
- Only 117 of 1,494 PRISM compounds carry a ChEMBL ID, so linking loop 2 drugs to loop 1 targets needs the SMILES, not the ID.
- Changing the scaffold-split seed alone moves ROC-AUC by up to about 0.046 (ERBB2, CDK6), more than the RF lead over 1-NN on ABL1 and BCL2 and more than any RF-vs-LightGBM gap; bootstrap CIs cover one test set only. Reported as a disclosure over 5 seeds; nothing is chosen from it.
- The switch rule reads the held-out set once (pre-registered); README must say so. Model parameters were committed with the first results, not with the protocol.
