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
in both train and test. The test set is never used for any choice (params, features, cut-offs). The one exception
is the switch rule below, fixed now, so its outcome cannot bend it. Any other model choice uses a second scaffold
split inside train (same function, on train only).

## Baselines every model must beat on the held-out set
1. Majority class: predicts the train majority for every molecule (constant score, so ROC-AUC = 0.5).
2. 1-nearest-neighbour by Tanimoto on Morgan fingerprints (radius 2, 2048 bits): predicted label = the label of the
   most similar train molecule; score = that neighbour's median pChEMBL.

## Models
Morgan fingerprints (radius 2, 2048 bits, `molscreen.chem.morgan_fp`). LightGBM and scikit-learn RandomForest
(500 trees), fixed parameters written in `src/molscreen/train.py`, no tuning on test.

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
