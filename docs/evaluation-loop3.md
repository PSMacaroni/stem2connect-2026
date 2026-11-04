# Evaluation protocol: safety flags on Tox21 (loop 3)

Written 2026-11-04, before the Tox21 download and any training. A rule changed later needs a dated note here.

## Source
MoleculeNet `tox21.csv.gz` from https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz, pulled by
`scripts/pull_tox21.py`, which records the URL, byte size and SHA-256 in `data/tox21/PULL_INFO.json`. No licence is
stated (a US-government programme, so probably public domain; not verified): the raw file is never committed, only
cited (Wu et al. 2018, doi:10.1039/C7SC02664A; Huang et al. 2016, doi:10.3389/fenvs.2015.00085).

## Cleaning
- Parse each SMILES with RDKit and strip salts to the parent with `molscreen.data.parent_smiles` (largest fragment,
  stereo kept, charges not neutralised). Drop rows that do not parse. Report how many rows changed SMILES.
- Collapse rows with the same parent: per assay, the **max** label over the rows that were tested (any active call
  wins; blanks ignored). Why: a flag should not be hidden because one salt form tested inactive. Report how many
  parents were collapsed and how many (parent, assay) cells had conflicting labels.

## Tasks and split
- The 12 assays are 12 binary classifiers (1 = active in the assay). A blank is "not tested" and that molecule is
  left out of that task's train and test sets; it is never treated as 0.
- ONE scaffold split, `molscreen.chem.scaffold_split(test_frac=0.2, seed=0)` on all parent molecules, shared by all
  12 tasks so results are comparable. Each task uses the molecules of each side that were tested in it.
- The test set is used once, for the reporting and the switch rule below, and for no other choice.

## Features and models (fixed here, not tuned)
Morgan fingerprints, radius 2, 2048 bits (`molscreen.train.fingerprints`). Parameters, as passed to scikit-learn:
- Logistic regression: `{"C": 1.0, "class_weight": "balanced", "max_iter": 2000}` (default L2 penalty, lbfgs).
- Random forest: `{"n_estimators": 500, "class_weight": "balanced", "random_state": 0, "n_jobs": -1}`;
  predictions with `n_jobs=1` (loop-1 lesson: parallel vote sums move PR-AUC at 1e-8).

## Baselines
1. Majority class of the task's train molecules (constant score, ROC-AUC 0.5).
2. 1-NN by Tanimoto: label of the most similar train molecule tested in that task; score = that label, so its
   ROC-AUC equals its balanced accuracy.

## Metrics (held-out, per task)
ROC-AUC with a bootstrap 95% CI (`molscreen.train.roc_auc_ci`, 1000 resamples, seed 0); PR-AUC with ACTIVE as the
positive class next to the test active fraction (actives are the minority, so this is the honest PR-AUC); balanced
accuracy at 0.5; test size and test actives. A task with fewer than 20 test actives is marked "underpowered".

## Which model ships (switch rule)
The random forest ships for all 12 tasks unless logistic regression has the higher held-out ROC-AUC on more than 6
of them (7 or more; ties and n/a are not wins). Applied once, across tasks. Margins reported to 4 significant figures.

## Must beat
Held-out ROC-AUC on the seed-0 split. A task where the shipped model does not exceed 1-NN is marked "no better than
nearest-neighbour lookup". It still ships.

## Abstain
As loop 1: cut-off = 5th percentile of the leave-one-out max Tanimoto over the shared train set, one cut-off for all
tasks. Report held-out abstain count and the shipped model's ROC-AUC on all and on non-abstained test molecules.

## Split variance (disclosure)
Seeds 0 to 4: recompute the shared split, refit the shipped model and 1-NN per task, report held-out ROC-AUC
min / median / max. Nothing is saved or chosen from it; seed 0 stays the reported split.

## Wording
"A flag means the molecule resembles compounds that were active in that assay; it is not a toxicity verdict." The
assays are cell-based and biochemical lab tests, not people. Research and learning tool, not medical advice.
