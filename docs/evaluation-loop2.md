# Evaluation protocol: mutations to drugs (loop 2)

Written 2026-11-04, before any loop-2 data was downloaded or processed. Changing a rule after seeing data needs a
dated note here saying what changed and why. Everything here is about **cell lines, not patients**. The app is a
**research and learning tool, not medical advice**.

## Sources (all CC BY 4.0, file IDs from `docs/data-registry.md` section 3b)
- DepMap 24Q4 Public (Figshare+, doi:10.25452/figshare.plus.27993248): `OmicsSomaticMutationsMatrixHotspot.csv`
  (51065750), `OmicsSomaticMutations.csv` (51065732), `Model.csv` (51065297), `PortalCompounds.csv` (51065762).
- PRISM Repurposing 20Q2 (figshare, doi:10.6084/m9.figshare.20564034): secondary-screen dose-response curve
  parameters (36794595). `scripts/pull_depmap.py` records URL, bytes and SHA-256 of each file in `PULL_INFO.json`.

## Mutation vector
The hotspot matrix, one row per `ModelID`, one column per gene (`SYMBOL (EntrezID)` renamed to `SYMBOL`). Values
0/1/2 become 0/1: 2 only means the summed allele frequency is above 0.95, and the app asks whether a gene is
mutated, not how many copies. All genes are kept in the derived table; the app's input is a list of gene symbols.

## Sensitivity
`auc` of the PRISM dose-response fit (lower = more sensitive). Drop rows with `passed_str_profiling` False (the
cell line's identity check failed) and rows with no `auc`. A compound is the Broad ID without its batch suffix
(`BRD-K12345678`). One value per (cell line, compound): the **median** `auc` over all remaining rows, which pools
the replicate screens (HTS002, MTS005, MTS006, MTS010). Name, SMILES and targets come from the PRISM rows.

## Join
PRISM `depmap_id` = DepMap `ModelID` = hotspot-matrix row ID. Never join on names. Report the overlap.

## Nearest cell lines (a lookup, not a prediction)
Query = 1 for each listed gene that is a matrix column, 0 elsewhere; listed genes not in the matrix are reported
and ignored (none in the matrix is an error). Rank by the number of shared mutated genes (query genes the
line carries), then by Jaccard similarity between the query and the line's 0/1 vector (0 when both are empty),
then by cell line name (amended 2026-11-04, see Changes). Top k = 10. It shows which screened cell lines
carry similar hotspot mutations and what was measured on them. It does not predict anything for a person.

## Evidence shown per nearest cell line
Name, lineage, primary disease (never `Age`, `Sex` or `PatientRace`; they are dropped when `Model.csv` is read and
never written), shared mutated genes, and its 10 most sensitive compounds (lowest `auc`) with name, SMILES and
target genes.

## Per-drug models (final rules and fixed parameters, written 2026-11-04 before any model was trained)
Code: `src/molscreen/drugs.py`. These are sensitivity models for **cell lines, not patients**. A model on 542
hotspot genes explains little of drug response; we expect many drugs near ROC-AUC 0.5 and will say so.

**Drug set** (Prakhar's decision, 2026-11-04; **amended in FIX round 1 to up to 3 per oncology gene, see Changes**). Candidates: compounds whose PRISM `target` field names at least one
gene symbol (every `target` token in the 20Q2 file is a symbol) and that have at least 300 screened cell lines
which are also in the hotspot matrix. That is far more than 60 (the 300-line rule alone passes 1,457 of 1,494),
so keep only candidates that match the oncology target list below, then the 60 with the most such lines (ties by
compound ID). A compound matches when a `target` token is in the list, or a listed symbol appears as a whole word
in `moa` (for example "EGFR inhibitor"). The final list (name, Broad ID, target) is written to
`results/loop2_models.md`.

Oncology target list: EGFR, BRAF, ERBB2, CDK4, CDK6, ALK, ABL1, PARP1, BCL2 (the loop-1 targets), MAP2K1,
MAP2K2 (MEK1/2), MTOR, PIK3CA, KIT, FLT3, BTK, JAK1, JAK2, AURKA, AURKB, PLK1, TOP1, TOP2A, TUBB, HDAC1, PSMB5,
MDM2, BCL2L1, KDR (VEGFR2), MET, RET, FGFR1.

**Features.** The cell line's 0/1 hotspot vector (all 542 genes of the matrix, `hotspot_binary.csv`), nothing else.

**Label.** Sensitive (1) when the line's `auc` for the drug is strictly below the 10th percentile
(`numpy.percentile`, linear) of that drug's `auc` over its **training lines only**; else 0. The same threshold
labels the test lines.

**Split.** Leave-lineage-out. The cell lines are those in PRISM after QC, in the hotspot matrix and with an
`OncotreeLineage` in `Model.csv`. Group them by `OncotreeLineage` and apply the greedy rule of
`molscreen.chem.scaffold_split` (both now call `molscreen.split.group_split(groups, test_frac=0.2, seed=0)`):
groups go to train largest first while they fit under 80% of the lines; groups that do not fit go to test; the
seed only breaks ties between equal-size groups. **One split shared by every drug**: a drug's train (test) lines
are the split's train (test) lines that were screened on that drug, so results are comparable across drugs.

**Baselines.** Majority class (constant score, ROC-AUC 0.5). 1-nearest-neighbour by hotspot Jaccard among the
drug's training lines: predicted label = the neighbour's label, score = 1 - the neighbour's `auc` (ties between
equally similar neighbours: the first by `ModelID`).

**Models** (scikit-learn, parameters fixed now, no tuning, no inner split):
- Logistic regression: L2, `C=1.0`, `class_weight="balanced"`, `max_iter=1000` (other arguments default).
- Random forest: 300 trees, `class_weight="balanced"`, `random_state=0` (other arguments default).

**Which model ships (switch rule, pre-registered, applied once across drugs; overridden in FIX round 1: logistic regression ships, see Changes).** Logistic regression ships for
every drug unless the random forest has the higher held-out ROC-AUC on more than half of the drugs that are not
underpowered. The shipped model is the one fit on the training lines, so its held-out numbers are its own.

**Metrics per drug, held-out lines.** ROC-AUC with a bootstrap 95% CI (1000 resamples of the test lines, seed 0;
one-class resamples skipped) for every model and baseline; PR-AUC of the sensitive class next to its test
prevalence (the PR-AUC of a random ranking); balanced accuracy at 0.5 (1-NN: its predicted label); test size and
number of sensitive test lines. A drug with **fewer than 5 sensitive test lines is "underpowered"**: reported,
not hidden, and left out of the switch-rule count.

**Abstain.** A query gene set that shares no gene with any of a model's training lines (no listed gene is mutated
in any of them) gets no prediction from that model; when that holds for every model the app says the query is
outside what the models have seen and shows no prediction.

**Wording.** "Cell lines, not patients." "A research and learning tool, not medical advice." Say that hotspot
genes explain little of drug response and that many drugs are near 0.5. Never "predicts a patient's response".

## Reporting
Counts and the worked example go to `results/loop2_data.md`, built from one run of `molscreen.depmap`.

## Changes
- 2026-11-04, after the download, before the lookup was first run: nearest cell lines are searched only among
  lines that have at least one PRISM `auc` after QC. Why: only 726 of the 1,929 hotspot-matrix lines are in PRISM,
  so most neighbours would otherwise have no drug evidence to show.
- 2026-11-04, after the first lookup run, decided by Prakhar: nearest cell lines rank by the **number of shared
  mutated genes first**, then Jaccard, then cell line name (was: Jaccard, then name). Each result also carries
  `n_shared`. Why: plain Jaccard rewards lines that carry nothing but the listed genes, so a line with 2 of 3
  listed genes and no other hotspot outranked a line with all 3 plus other hotspots. For KRAS/TP53/STK11, 43
  screened lines tied at Jaccard 0.667 and the top 10 was decided by the name sort. Rejected: plain Jaccard;
  weighting genes by rarity.
- 2026-11-04, after the data report, before any model was trained, decided by Prakhar: per-drug models only for
  compounds whose `target` names a gene, matched against an oncology target list and capped at 60 (was: every
  drug with at least 300 lines in the hotspot matrix). Why: 1,457 of 1,494 compounds pass the 300-line rule, so it
  selects nothing. The section above now also fixes the features, label rule, shared split, models, parameters,
  switch rule, underpowered flag and abstain rule. Rejected: the 30 most variable drugs; all 1,457.
- 2026-11-04, FIX round 1, decided by Prakhar after the first per-drug results existed (commit 5b7d361:
  60 drugs, random forest shipped by the switch rule, median held-out ROC-AUC 0.562). Three amendments; split,
  seed, features, label rule, model parameters and metrics are unchanged.
  - **Drug set: up to 3 compounds per oncology-list gene, no overall cap.** Candidates as before (a gene in
    `target`, at least 300 lines in the hotspot matrix). Each candidate is assigned to the first gene of the
    oncology list (in list order) that its `target` names, so it counts once; candidates naming no listed gene are
    dropped (the `moa` match is no longer used). Per gene, the 3 with the most lines are kept (ties by Broad ID).
    Why: capping at the 60 most-screened compounds filled the set with multi-kinase and EGFR drugs and dropped
    targets where hotspot genes should matter most (for example the BRAF inhibitors dabrafenib and vemurafenib).
  - **Shipped model: logistic regression, overriding the switch rule.** The switch rule is still computed and
    reported every run. Why: the random forest's win in 5b7d361 (32 of 60 drugs, needing more than 30) is a
    tie-sized margin, and the hosted app's size matters (the 60 random forests took 73,143,794 bytes; logistic
    models are a few hundred KB). Random-forest results stay in every table.
  - **App contract.** `predict_drugs` returns, for every shipped model that does not abstain, its rank,
    `p_sensitive`, `roc_auc`, `roc_auc_ci95`, `n_sensitive_test` and `weak` (= the 95% CI lower bound is
    <= 0.5). The nearest cell lines and their measured sensitivities are the main evidence in loop 2; model ranks
    are shown second and greyed when `weak`; the probabilities are not calibrated and are shown as ranks, never as
    percentages.
