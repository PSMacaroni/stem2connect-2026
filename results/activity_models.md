# Activity models (loop 1): held-out results

Scaffold-split held-out test sets, ChEMBL release ChEMBL_37, protocol `docs/evaluation.md` with its
2026-11-04 amendments (wild-type assays only, salts stripped to the parent; extra reporting).
All numbers come from `results/activity_models.json`, written by `uv run python -m molscreen.train`.
Morgan fingerprints (radius 2, 2048 bits). Model parameters are fixed in `src/molscreen/train.py`; nothing
was tuned, so no inner split was used. Every metric below is on the held-out test set.
**Shipped model: random forest.** "Underpowered" marks a target with fewer than 50 inactive molecules
in its test set: its AUCs can move a lot with a few molecules.

## Headline: shipped model against the baselines

ROC-AUC 95% CI: bootstrap over the test set (1000 resamples, seed 0). The random value of
inactive-class PR-AUC is the test inactive fraction. Balanced accuracy uses a 0.5 threshold (1-NN: its
neighbour's label). Active-class PR-AUC comes last because a random ranking already scores the test
active fraction there (0.68 to 0.95 here), so high values are expected.

| Gene | n train | n test | Test inactives | ROC-AUC random forest (95% CI) | ROC-AUC 1-NN | Inactive PR-AUC random forest | Inactive PR-AUC random | Bal. acc. random forest | Bal. acc. 1-NN | Active PR-AUC random forest | Active PR-AUC random | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EGFR | 7822 | 1956 | 597 | 0.879 (0.863 to 0.894) | 0.818 | 0.757 | 0.305 | 0.757 | 0.741 | 0.941 | 0.695 |  |
| BRAF | 2392 | 599 | 95 | 0.859 (0.820 to 0.898) | 0.787 | 0.637 | 0.159 | 0.684 | 0.702 | 0.966 | 0.841 |  |
| ERBB2 | 2042 | 511 | 126 | 0.845 (0.801 to 0.881) | 0.794 | 0.712 | 0.247 | 0.729 | 0.735 | 0.930 | 0.753 |  |
| CDK4 | 1120 | 281 | 36 | 0.892 (0.831 to 0.942) | 0.855 | 0.639 | 0.128 | 0.661 | 0.683 | 0.980 | 0.872 | underpowered: 36 test inactives |
| CDK6 | 656 | 165 | 8 | 0.894 (0.784 to 0.980) | 0.818 | 0.411 | 0.048 | 0.500 | 0.625 | 0.994 | 0.952 | underpowered: 8 test inactives |
| ALK | 1942 | 486 | 154 | 0.914 (0.888 to 0.938) | 0.852 | 0.814 | 0.317 | 0.749 | 0.771 | 0.961 | 0.683 |  |
| ABL1 | 2329 | 583 | 171 | 0.879 (0.853 to 0.906) | 0.859 | 0.741 | 0.293 | 0.704 | 0.752 | 0.949 | 0.707 |  |
| PARP1 | 3603 | 901 | 157 | 0.897 (0.869 to 0.922) | 0.842 | 0.698 | 0.174 | 0.657 | 0.698 | 0.974 | 0.826 |  |
| BCL2 | 2513 | 629 | 107 | 0.971 (0.957 to 0.982) | 0.950 | 0.885 | 0.170 | 0.847 | 0.856 | 0.994 | 0.830 |  |

## All models

### ROC-AUC

| Gene | Majority | 1-NN | Random forest | LightGBM | Note |
|---|---|---|---|---|---|
| EGFR | 0.500 | 0.818 | 0.879 | 0.848 |  |
| BRAF | 0.500 | 0.787 | 0.859 | 0.857 |  |
| ERBB2 | 0.500 | 0.794 | 0.845 | 0.824 |  |
| CDK4 | 0.500 | 0.855 | 0.892 | 0.884 | underpowered: 36 test inactives |
| CDK6 | 0.500 | 0.818 | 0.894 | 0.799 | underpowered: 8 test inactives |
| ALK | 0.500 | 0.852 | 0.914 | 0.906 |  |
| ABL1 | 0.500 | 0.859 | 0.879 | 0.870 |  |
| PARP1 | 0.500 | 0.842 | 0.897 | 0.892 |  |
| BCL2 | 0.500 | 0.950 | 0.971 | 0.965 |  |

### PR-AUC, inactive as the positive class

| Gene | Random | Majority | 1-NN | Random forest | LightGBM | Note |
|---|---|---|---|---|---|---|
| EGFR | 0.305 | 0.305 | 0.658 | 0.757 | 0.710 |  |
| BRAF | 0.159 | 0.159 | 0.516 | 0.637 | 0.649 |  |
| ERBB2 | 0.247 | 0.247 | 0.613 | 0.712 | 0.663 |  |
| CDK4 | 0.128 | 0.128 | 0.528 | 0.639 | 0.580 | underpowered: 36 test inactives |
| CDK6 | 0.048 | 0.048 | 0.538 | 0.411 | 0.398 | underpowered: 8 test inactives |
| ALK | 0.317 | 0.317 | 0.753 | 0.814 | 0.814 |  |
| ABL1 | 0.293 | 0.293 | 0.689 | 0.741 | 0.706 |  |
| PARP1 | 0.174 | 0.174 | 0.599 | 0.698 | 0.694 |  |
| BCL2 | 0.170 | 0.170 | 0.835 | 0.885 | 0.871 |  |

### Balanced accuracy at 0.5

| Gene | Majority | 1-NN | Random forest | LightGBM | Note |
|---|---|---|---|---|---|
| EGFR | 0.500 | 0.741 | 0.757 | 0.754 |  |
| BRAF | 0.500 | 0.702 | 0.684 | 0.704 |  |
| ERBB2 | 0.500 | 0.735 | 0.729 | 0.731 |  |
| CDK4 | 0.500 | 0.683 | 0.661 | 0.710 | underpowered: 36 test inactives |
| CDK6 | 0.500 | 0.625 | 0.500 | 0.625 | underpowered: 8 test inactives |
| ALK | 0.500 | 0.771 | 0.749 | 0.770 |  |
| ABL1 | 0.500 | 0.752 | 0.704 | 0.755 |  |
| PARP1 | 0.500 | 0.698 | 0.657 | 0.697 |  |
| BCL2 | 0.500 | 0.856 | 0.847 | 0.856 |  |

### Random forest against 1-NN, per metric

- ROC-AUC: below 1-NN on 0 of 9 targets.
- PR-AUC, inactive class: below 1-NN on 1 of 9 targets (CDK6 0.411 vs 0.538).
- Balanced accuracy at 0.5: below 1-NN on 8 of 9 targets (BRAF 0.684 vs 0.702, ERBB2 0.729 vs 0.735, CDK4 0.661 vs 0.683, CDK6 0.500 vs 0.625, ALK 0.749 vs 0.771, ABL1 0.704 vs 0.752, PARP1 0.657 vs 0.698, BCL2 0.847 vs 0.856).
- PR-AUC, active class: below 1-NN on 0 of 9 targets.

### PR-AUC, active as the positive class (the switch rule's metric)

A random ranking scores the test active fraction here.

| Gene | Random | Majority | 1-NN | Random forest | LightGBM | RF - LightGBM | Note |
|---|---|---|---|---|---|---|---|
| EGFR | 0.695 | 0.695 | 0.888 | 0.941 | 0.920 | +0.0204 |  |
| BRAF | 0.841 | 0.841 | 0.940 | 0.966 | 0.966 | -0.0000 |  |
| ERBB2 | 0.753 | 0.753 | 0.910 | 0.930 | 0.919 | +0.0116 |  |
| CDK4 | 0.872 | 0.872 | 0.970 | 0.980 | 0.976 | +0.0038 | underpowered: 36 test inactives |
| CDK6 | 0.952 | 0.952 | 0.981 | 0.994 | 0.966 | +0.0273 | underpowered: 8 test inactives |
| ALK | 0.683 | 0.683 | 0.894 | 0.961 | 0.952 | +0.0089 |  |
| ABL1 | 0.707 | 0.707 | 0.934 | 0.949 | 0.946 | +0.0033 |  |
| PARP1 | 0.826 | 0.826 | 0.954 | 0.974 | 0.969 | +0.0049 |  |
| BCL2 | 0.830 | 0.830 | 0.987 | 0.994 | 0.992 | +0.0015 |  |

Switch rule (re-applied after the amendment): the random forest had the higher active-class PR-AUC on 8 of 9 targets (it needs at least 6), so **random forest** ships for every target. In the first run (4c71e50) the count was 7 of 9, also the random forest.
CDK4 is underpowered: its RF-vs-LightGBM PR-AUC margin (+0.0038) rests on 36 test inactives.
CDK6 is underpowered: its RF-vs-LightGBM PR-AUC margin (+0.0273) rests on 8 test inactives.

## Abstain

Held-out abstain = held-out molecules whose max Tanimoto to train is below the cut-off. AUC kept = the
shipped model's ROC-AUC on the other, non-abstained molecules (the ones closer to train).

| Gene | Abstain cut-off | Held-out abstain | ROC-AUC random forest, all | AUC kept |
|---|---|---|---|---|
| EGFR | 0.654 | 673 of 1956 | 0.879 | 0.914 |
| BRAF | 0.719 | 276 of 599 | 0.859 | 0.905 |
| ERBB2 | 0.644 | 147 of 511 | 0.845 | 0.826 |
| CDK4 | 0.705 | 97 of 281 | 0.892 | 0.924 |
| CDK6 | 0.712 | 53 of 165 | 0.894 | 0.827 |
| ALK | 0.527 | 111 of 486 | 0.914 | 0.937 |
| ABL1 | 0.553 | 189 of 583 | 0.879 | 0.935 |
| PARP1 | 0.615 | 178 of 901 | 0.897 | 0.903 |
| BCL2 | 0.739 | 102 of 629 | 0.971 | 0.971 |

## What changed from the first run

Before = commit 4c71e50 (all assays incl. mutant, one molecule per ChEMBL ID). After = this run
(wild-type assays only, salts stripped to the parent). ROC-AUC on each run's own held-out set; the
held-out sets differ: the split is recomputed on the new molecule list, and scaffold groups of equal size
can land on the other side, so even a target with the same molecules (CDK6, BCL2) gets a new test set.

| Gene | Molecules before | Molecules after | RF ROC-AUC before | RF ROC-AUC after | LightGBM ROC-AUC before | LightGBM ROC-AUC after |
|---|---|---|---|---|---|---|
| EGFR | 11023 | 9778 | 0.877 | 0.879 | 0.850 | 0.848 |
| BRAF | 5381 | 2991 | 0.870 | 0.859 | 0.876 | 0.857 |
| ERBB2 | 2560 | 2553 | 0.880 | 0.845 | 0.870 | 0.824 |
| CDK4 | 1404 | 1401 | 0.886 | 0.892 | 0.879 | 0.884 |
| CDK6 | 821 | 821 | 0.901 | 0.894 | 0.770 | 0.799 |
| ALK | 2476 | 2428 | 0.908 | 0.914 | 0.891 | 0.906 |
| ABL1 | 3038 | 2912 | 0.855 | 0.879 | 0.837 | 0.870 |
| PARP1 | 4510 | 4504 | 0.900 | 0.897 | 0.898 | 0.892 |
| BCL2 | 3142 | 3142 | 0.962 | 0.971 | 0.963 | 0.965 |

## Known limits

- **Measurement types and assay types are pooled.** Of the 46032 kept rows: IC50 85.2%, Ki 13.1%, EC50 1.7%. Functional (F) assays, the rest binding (B): EGFR 5.6%, BRAF 0.9%, ERBB2 9.2%, CDK4 1.7%, CDK6 1.9%, ALK 8.4%, ABL1 5.2%, PARP1 0.1%, BCL2 1.2% of kept rows.
- **Wild type only, as far as ChEMBL says.** Rows from assays declaring a variant were dropped (EGFR 23.8%, BRAF 42.8%, ERBB2 0.4%, CDK4 0.0%, CDK6 0.0%, ALK 22.0%, ABL1 13.5%, PARP1 0.0%, BCL2 0.8% of the rows that pass every other rule). An assay on a mutant protein that does not declare it is still in (inferred risk).
- **The abstain rule holds back 16% (BCL2) to 46% (BRAF) of held-out molecules**: a scaffold split makes held-out molecules unlike train by design.
- **Stereoisomers stay separate training points, and charged salt forms are not neutralised.** Parent molecules that share a structure once stereo is removed: EGFR 408 of 9778, BRAF 115 of 2991, ERBB2 178 of 2553, CDK4 235 of 1401, CDK6 69 of 821, ALK 98 of 2428, ABL1 231 of 2912, PARP1 195 of 4504, BCL2 280 of 3142.
- **The active rate (72% to 97% of molecules) reflects what gets published** (mostly optimised series), not a screening library, so these numbers do not predict real hit rates.
- **AUC kept is measured on the non-abstained subset, closer to train and usually easier**; it is above the all-molecule ROC-AUC on 6 of 9 targets. Quote the all-molecule ROC-AUC as the headline.

## Credits

Bioactivity data: ChEMBL.
ChEMBL data is from http://www.ebi.ac.uk/chembl - the version of ChEMBL is chembl_37.
Licensed under CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/); any ChEMBL-derived data
published from this project is shared under the same licence. Mendez D, Gaulton A, Bento AP, et al.
ChEMBL: towards direct deposition of bioassay data. Nucleic Acids Res. 2019;47(D1):D930-D940.
doi:10.1093/nar/gky1075
