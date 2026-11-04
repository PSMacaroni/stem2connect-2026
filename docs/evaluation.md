# Evaluation protocol: activity models (loop 1)

Written 2026-11-04, before any model was trained. Changing a rule after seeing results needs a dated note here
saying what changed and why.

## Data and label
Source: ChEMBL_37 activities for the 9 targets in `docs/data-registry.md`, pulled by `scripts/pull_chembl.py`.
- Keep rows with `standard_type` in IC50, Ki, EC50 and a pChEMBL value. Why: pChEMBL puts these on one
  -log10(molar) scale, so they can be pooled.
- Drop rows whose `standard_relation` is not "=". Why: "<" or ">" is a bound, not a measured value.
- Drop rows with a non-empty `data_validity_comment`. Why: ChEMBL curators flagged them (outside range, possible
  unit error, duplicate, ...).
- Keep `assay_type` "B" (binding) or "F" (functional) only. Why: those measure the compound against the target;
  other types (ADMET, physchem) do not.
- Drop rows whose SMILES does not parse in RDKit; group rows by `molecule_chembl_id`.
- Aggregate: the **median** pChEMBL over all kept rows of a molecule for that target. Why: robust to one outlier lab.
- Label: **active** when the median pChEMBL >= 6.0 (1 µM), else inactive. Why: 1 µM is a common hit cut-off, and
  it is fixed before seeing the data.

## Split
`molscreen.chem.scaffold_split(smiles, test_frac=0.2, seed=0)` on the de-duplicated molecules. No Murcko scaffold is
in both train and test. The test set is used once, for the pre-registered model-type pick (the switch rule below),
and for no other choice (params, features, cut-offs). Any other model choice uses a second scaffold split inside
train (same function, on train only).

## Baselines every model must beat on the held-out set
1. Majority class: predicts the train majority for every molecule (constant score, so ROC-AUC = 0.5).
2. 1-nearest-neighbour by Tanimoto on Morgan fingerprints (radius 2, 2048 bits): predicted label = the label of the
   most similar train molecule; score = that neighbour's median pChEMBL.

## Models
Morgan fingerprints (radius 2, 2048 bits, `molscreen.chem.morgan_fp`). LightGBM and scikit-learn RandomForest
(500 trees), fixed parameters written in `src/molscreen/train.py`, no tuning on test. Note added in review: the
parameter values (`LGBM_PARAMS`, `RF_PARAMS`) were first committed with the results (4c71e50), not with this
protocol (1cc2650); that they were not tuned rests on the author's word.

## Metrics (held-out set)
- Headline: ROC-AUC and PR-AUC (average precision).
- Also: balanced accuracy at a 0.5 probability threshold (1-NN: its predicted label), the held-out active fraction
  (= the PR-AUC of a random ranker) and the held-out size.

## Abstain rule
For a query, take its max Tanimoto to the train molecules. Below the cut-off it is "outside what this model has
seen" and the app shows no prediction. Cut-off = the 5th percentile of the train-set leave-one-out max Tanimoto
(each train molecule against all other train molecules), computed on train only. Report how many held-out
molecules would abstain, and the ROC-AUC on all held-out molecules and on the non-abstained ones.

## Which model ships (switch rule)
LightGBM is the shipped model unless the random forest beats it on held-out PR-AUC on at least 6 of the 9 targets.
The rule is applied once, across all targets, and the same model type ships for every target.

## Reporting
All numbers go to `results/activity_models.json` (and `results/datasets.md`, `results/activity_models.md` built from
the same run). A target with too few actives or inactives in test to compute an AUC is reported as such, not hidden.

## Amendment 2026-11-04 (a): reporting, added after the first run
Adds reporting only, changes no decision rule.
- PR-AUC with **inactive** as the positive class, for every model and for a random ranker (= 1 - active fraction).
- Bootstrap 95% CI on ROC-AUC for the shipped model: 1000 resamples of the test set, seed 0.
- Column order: ROC-AUC with its CI next to 1-NN, inactive-class PR-AUC next to its random value, balanced
  accuracy, then active-class PR-AUC (a random ranker already scores the active fraction there).
- A target with fewer than 50 test inactives is marked "underpowered" with its count.
- The first run's random-forest-minus-LightGBM active-class PR-AUC margins (4c71e50): EGFR +0.015, BRAF -0.003,
  ERBB2 +0.003, CDK4 +0.003, CDK6 +0.024, ALK +0.009, ABL1 +0.005, PARP1 +0.004, BCL2 -0.001. The switch rule
  rested on margins of 0.003 to 0.024.

## Amendment 2026-11-04 (b): data rules, decided by Prakhar
Reason: found in review after the first run; results before the change are in git history at 4c71e50. These
replace "group rows by `molecule_chembl_id`" above. Split, models, metrics, abstain and switch rules are unchanged;
the switch rule is re-applied once on the new data.
- **Wild type only.** Drop every row whose assay declares a protein variant: non-empty `assay_variant_mutation`,
  a field of the ChEMBL activity endpoint, fetched in the same paged query (`only=...,assay_variant_mutation`).
- **Parent molecule.** Strip salts before aggregating: keep the fragment with the most heavy atoms
  (`Chem.GetMolFrags`, ties broken by SMILES), canonical SMILES with stereo kept, charges not neutralised.
  Group rows by that parent SMILES, keep the list of ChEMBL IDs per parent, and take the median pChEMBL over all
  their rows.
