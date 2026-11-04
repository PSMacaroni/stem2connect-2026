# Safety flags (loop 3): held-out results on Tox21

Protocol `docs/evaluation-loop3.md` (committed with the model parameters before any training). All numbers
come from `results/tox21_models.json`, written by `uv run python -m molscreen.tox`. Morgan fingerprints
(radius 2, 2048 bits); one scaffold split (seed 0) shared by all 12 assays; per assay only the molecules
tested in it. Every metric is on the held-out test set.
**Shipped model: random forest.** "Underpowered" marks an assay with fewer than 20 active molecules in
its test set.

**A flag means the molecule resembles compounds that were active in that assay; it is not a toxicity verdict.** The assays are cell-based and biochemical lab tests, not people. Research and
learning tool, not medical advice.

## Data

Source: `tox21.csv.gz` (122925 bytes, SHA-256 `45d09792492ce049039dd24aa27b07fc79ce20c573187d4d90bcd178c0c0d360`, pulled 2026-11-04). 7831 rows; 8 did not parse in RDKit and were dropped; 244 had more than one fragment and were stripped to the parent; 114 rows collapsed into another row's parent, leaving 7709 parent molecules; 47 (parent, assay) cells had conflicting labels and took the active call. Split: 6167 train, 1542 test parents.

| Assay | Tested | Actives | Active fraction |
|---|---|---|---|
| NR-AR | 7146 | 308 | 0.043 |
| NR-AR-LBD | 6654 | 237 | 0.036 |
| NR-AhR | 6447 | 766 | 0.119 |
| NR-Aromatase | 5719 | 288 | 0.050 |
| NR-ER | 6112 | 790 | 0.129 |
| NR-ER-LBD | 6854 | 346 | 0.050 |
| NR-PPAR-gamma | 6355 | 186 | 0.029 |
| SR-ARE | 5748 | 926 | 0.161 |
| SR-ATAD5 | 6964 | 263 | 0.038 |
| SR-HSE | 6376 | 367 | 0.058 |
| SR-MMP | 5732 | 911 | 0.159 |
| SR-p53 | 6675 | 421 | 0.063 |

## Headline: shipped model against 1-NN

ROC-AUC 95% CI: bootstrap over the test set (1000 resamples, seed 0). PR-AUC uses active (the minority) as the positive class; a random ranking scores the test active fraction. Balanced accuracy uses a 0.5 threshold. 1-NN scores with its neighbour's label, so its ROC-AUC equals its balanced accuracy.

| Assay | n train | n test | Test actives | ROC-AUC random forest (95% CI) | ROC-AUC 1-NN | PR-AUC random forest | PR-AUC random | Bal. acc. random forest | Bal. acc. 1-NN | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| NR-AR | 5745 | 1401 | 54 | 0.731 (0.630 to 0.820) | 0.660 | 0.446 | 0.039 | 0.689 | 0.660 |  |
| NR-AR-LBD | 5428 | 1226 | 40 | 0.830 (0.739 to 0.899) | 0.741 | 0.464 | 0.033 | 0.696 | 0.741 |  |
| NR-AhR | 5238 | 1209 | 175 | 0.828 (0.791 to 0.860) | 0.648 | 0.532 | 0.145 | 0.688 | 0.648 |  |
| NR-Aromatase | 4703 | 1016 | 91 | 0.715 (0.653 to 0.777) | 0.613 | 0.345 | 0.090 | 0.574 | 0.613 |  |
| NR-ER | 5017 | 1095 | 138 | 0.664 (0.607 to 0.712) | 0.588 | 0.308 | 0.126 | 0.599 | 0.588 |  |
| NR-ER-LBD | 5557 | 1297 | 50 | 0.701 (0.610 to 0.783) | 0.633 | 0.324 | 0.039 | 0.616 | 0.633 |  |
| NR-PPAR-gamma | 5231 | 1124 | 53 | 0.776 (0.715 to 0.839) | 0.579 | 0.264 | 0.047 | 0.517 | 0.579 |  |
| SR-ARE | 4808 | 940 | 223 | 0.695 (0.655 to 0.732) | 0.585 | 0.460 | 0.237 | 0.597 | 0.585 |  |
| SR-ATAD5 | 5654 | 1310 | 66 | 0.757 (0.691 to 0.817) | 0.578 | 0.187 | 0.050 | 0.535 | 0.578 |  |
| SR-HSE | 5244 | 1132 | 94 | 0.673 (0.614 to 0.733) | 0.566 | 0.254 | 0.083 | 0.538 | 0.566 |  |
| SR-MMP | 4726 | 1006 | 200 | 0.797 (0.758 to 0.834) | 0.644 | 0.526 | 0.199 | 0.642 | 0.644 |  |
| SR-p53 | 5424 | 1251 | 137 | 0.747 (0.701 to 0.792) | 0.596 | 0.337 | 0.110 | 0.537 | 0.596 |  |

Must-beat rule: the random forest exceeds 1-NN on held-out ROC-AUC on 12 of 12 assays; any assay where it does not is marked "no better than nearest-neighbour lookup" (it still ships).

The random forest against 1-NN, per metric:

- ROC-AUC: below 1-NN on 0 of 12 assays.
- PR-AUC, active class: below 1-NN on 0 of 12 assays.
- Balanced accuracy at 0.5 (the app's flag threshold): below 1-NN on 8 of 12 assays (NR-AR-LBD 0.696 vs 0.741, NR-Aromatase 0.574 vs 0.613, NR-ER-LBD 0.616 vs 0.633, NR-PPAR-gamma 0.517 vs 0.579, SR-ATAD5 0.535 vs 0.578, SR-HSE 0.538 vs 0.566, SR-MMP 0.642 vs 0.644, SR-p53 0.537 vs 0.596).

## All models

### ROC-AUC

| Assay | Majority | 1-NN | Logistic regression | Random forest | Note |
|---|---|---|---|---|---|
| NR-AR | 0.500 | 0.660 | 0.700 | 0.731 |  |
| NR-AR-LBD | 0.500 | 0.741 | 0.776 | 0.830 |  |
| NR-AhR | 0.500 | 0.648 | 0.774 | 0.828 |  |
| NR-Aromatase | 0.500 | 0.613 | 0.701 | 0.715 |  |
| NR-ER | 0.500 | 0.588 | 0.632 | 0.664 |  |
| NR-ER-LBD | 0.500 | 0.633 | 0.666 | 0.701 |  |
| NR-PPAR-gamma | 0.500 | 0.579 | 0.664 | 0.776 |  |
| SR-ARE | 0.500 | 0.585 | 0.666 | 0.695 |  |
| SR-ATAD5 | 0.500 | 0.578 | 0.721 | 0.757 |  |
| SR-HSE | 0.500 | 0.566 | 0.637 | 0.673 |  |
| SR-MMP | 0.500 | 0.644 | 0.736 | 0.797 |  |
| SR-p53 | 0.500 | 0.596 | 0.648 | 0.747 |  |

### PR-AUC, active as the positive class

| Assay | Random | Majority | 1-NN | Logistic regression | Random forest | Note |
|---|---|---|---|---|---|---|
| NR-AR | 0.039 | 0.039 | 0.107 | 0.275 | 0.446 |  |
| NR-AR-LBD | 0.033 | 0.033 | 0.260 | 0.352 | 0.464 |  |
| NR-AhR | 0.145 | 0.145 | 0.251 | 0.369 | 0.532 |  |
| NR-Aromatase | 0.090 | 0.090 | 0.175 | 0.211 | 0.345 |  |
| NR-ER | 0.126 | 0.126 | 0.169 | 0.244 | 0.308 |  |
| NR-ER-LBD | 0.039 | 0.039 | 0.106 | 0.170 | 0.324 |  |
| NR-PPAR-gamma | 0.047 | 0.047 | 0.109 | 0.176 | 0.264 |  |
| SR-ARE | 0.237 | 0.237 | 0.296 | 0.393 | 0.460 |  |
| SR-ATAD5 | 0.050 | 0.050 | 0.092 | 0.144 | 0.187 |  |
| SR-HSE | 0.083 | 0.083 | 0.118 | 0.176 | 0.254 |  |
| SR-MMP | 0.199 | 0.199 | 0.318 | 0.413 | 0.526 |  |
| SR-p53 | 0.110 | 0.110 | 0.195 | 0.242 | 0.337 |  |

### Balanced accuracy at 0.5

| Assay | Majority | 1-NN | Logistic regression | Random forest | Note |
|---|---|---|---|---|---|
| NR-AR | 0.500 | 0.660 | 0.671 | 0.689 |  |
| NR-AR-LBD | 0.500 | 0.741 | 0.729 | 0.696 |  |
| NR-AhR | 0.500 | 0.648 | 0.696 | 0.688 |  |
| NR-Aromatase | 0.500 | 0.613 | 0.586 | 0.574 |  |
| NR-ER | 0.500 | 0.588 | 0.587 | 0.599 |  |
| NR-ER-LBD | 0.500 | 0.633 | 0.601 | 0.616 |  |
| NR-PPAR-gamma | 0.500 | 0.579 | 0.599 | 0.517 |  |
| SR-ARE | 0.500 | 0.585 | 0.625 | 0.597 |  |
| SR-ATAD5 | 0.500 | 0.578 | 0.630 | 0.535 |  |
| SR-HSE | 0.500 | 0.566 | 0.527 | 0.538 |  |
| SR-MMP | 0.500 | 0.644 | 0.652 | 0.642 |  |
| SR-p53 | 0.500 | 0.596 | 0.599 | 0.537 |  |

## Switch rule

| Assay | ROC-AUC logistic regression | ROC-AUC random forest | LR - RF |
|---|---|---|---|
| NR-AR | 0.700 | 0.731 | -0.03105 |
| NR-AR-LBD | 0.776 | 0.830 | -0.05371 |
| NR-AhR | 0.774 | 0.828 | -0.05391 |
| NR-Aromatase | 0.701 | 0.715 | -0.01446 |
| NR-ER | 0.632 | 0.664 | -0.03132 |
| NR-ER-LBD | 0.666 | 0.701 | -0.0355 |
| NR-PPAR-gamma | 0.664 | 0.776 | -0.1121 |
| SR-ARE | 0.666 | 0.695 | -0.02886 |
| SR-ATAD5 | 0.721 | 0.757 | -0.03595 |
| SR-HSE | 0.637 | 0.673 | -0.03692 |
| SR-MMP | 0.736 | 0.797 | -0.06027 |
| SR-p53 | 0.648 | 0.747 | -0.09896 |

Logistic regression had the higher held-out ROC-AUC on 0 of 12 assays (it needs more than 6), so **random forest** ships for every assay. The rule read the test set once.

## Abstain

One cut-off for all assays: 0.333 (5th percentile of the train leave-one-out max Tanimoto). 484 of 1542 held-out parents fall below it. Per assay: held-out molecules tested in it that would abstain, and the shipped model's ROC-AUC on all of them and on the rest.

| Assay | Held-out abstain | ROC-AUC random forest, all | ROC-AUC kept |
|---|---|---|---|
| NR-AR | 448 of 1401 | 0.731 | 0.764 |
| NR-AR-LBD | 381 of 1226 | 0.830 | 0.879 |
| NR-AhR | 384 of 1209 | 0.828 | 0.850 |
| NR-Aromatase | 321 of 1016 | 0.715 | 0.736 |
| NR-ER | 325 of 1095 | 0.664 | 0.689 |
| NR-ER-LBD | 412 of 1297 | 0.701 | 0.703 |
| NR-PPAR-gamma | 342 of 1124 | 0.776 | 0.803 |
| SR-ARE | 280 of 940 | 0.695 | 0.721 |
| SR-ATAD5 | 416 of 1310 | 0.757 | 0.785 |
| SR-HSE | 352 of 1132 | 0.673 | 0.711 |
| SR-MMP | 312 of 1006 | 0.797 | 0.814 |
| SR-p53 | 386 of 1251 | 0.747 | 0.780 |

## Split variance (disclosure)

The shared scaffold split recomputed with seeds [0, 1, 2, 3, 4], the random forest and 1-NN refit per assay (`uv run python -m molscreen.tox --split-seeds 0 1 2 3 4`). Nothing is saved or chosen from these runs; seed 0 stays the reported split. Held-out ROC-AUC, min / median / max over seeds.

| Assay | random forest min / median / max | 1-NN min / median / max |
|---|---|---|
| NR-AR | 0.713 / 0.726 / 0.740 | 0.660 / 0.682 / 0.687 |
| NR-AR-LBD | 0.805 / 0.828 / 0.844 | 0.723 / 0.753 / 0.759 |
| NR-AhR | 0.812 / 0.822 / 0.829 | 0.626 / 0.632 / 0.648 |
| NR-Aromatase | 0.664 / 0.680 / 0.715 | 0.594 / 0.606 / 0.613 |
| NR-ER | 0.637 / 0.642 / 0.664 | 0.574 / 0.588 / 0.593 |
| NR-ER-LBD | 0.701 / 0.718 / 0.742 | 0.633 / 0.647 / 0.679 |
| NR-PPAR-gamma | 0.762 / 0.778 / 0.801 | 0.558 / 0.579 / 0.590 |
| SR-ARE | 0.685 / 0.696 / 0.708 | 0.585 / 0.595 / 0.606 |
| SR-ATAD5 | 0.747 / 0.753 / 0.768 | 0.569 / 0.584 / 0.589 |
| SR-HSE | 0.673 / 0.676 / 0.704 | 0.562 / 0.569 / 0.574 |
| SR-MMP | 0.787 / 0.797 / 0.807 | 0.644 / 0.648 / 0.660 |
| SR-p53 | 0.733 / 0.747 / 0.756 | 0.585 / 0.588 / 0.596 |

Changing the split alone moves the random forest's ROC-AUC by up to 0.0511 (NR-Aromatase). Its smallest seed-0 lead over 1-NN is +0.0682 (NR-ER-LBD). The bootstrap CIs above cover one fixed test set only.

## Known limits

- **Licence not stated.** Neither MoleculeNet/DeepChem nor the NCATS challenge page states a licence for the data. Tox21 is a US-government programme, so it is probably public domain (inferred, not verified). The raw file is never committed; `scripts/pull_tox21.py` downloads it.
- **Salts stripped, charges kept.** 244 of 7831 rows were mixtures or salts reduced to their largest fragment; a counter-ion's own activity is lost, and charged forms are not neutralised.
- **Any active call wins on collapse.** 47 (parent, assay) cells had both an active and an inactive row; they count as active.
- **Probabilities are not risks.** Both models use balanced class weights, so a probability above 0.5 does not mean a 50% chance of being active; the flag at 0.5 is a ranking cut, not a calibrated one.
- **The flag at 0.5 is weaker than the ranking.** The random forest's balanced accuracy at 0.5 is 0.517 to 0.696 across assays (per-metric list above). Its ranking (ROC-AUC) is the stronger signal: read a probability as a rank among molecules, not as a yes or no.
- **Abstain is common**: 484 of 1542 held-out parents are below the cut-off, because a scaffold split makes held-out molecules unlike train by design.
- **The assays are lab tests on cells and proteins**, at the concentrations screened; they say nothing direct about dose, exposure or harm in people.

## The 12 assays

From the Tox21 Data Challenge data page (https://tripod.nih.gov/tox21/challenge/data.jsp) and each PubChem
assay record. Active = the compound did this in the assay.

- **NR-AR** (PubChem AID 743040, https://pubchem.ncbi.nlm.nih.gov/bioassay/743040): switches on the androgen receptor (full-length, MDA breast cancer cell line).
- **NR-AR-LBD** (PubChem AID 743053, https://pubchem.ncbi.nlm.nih.gov/bioassay/743053): switches on the androgen receptor ligand-binding domain (HEK293 reporter cells).
- **NR-AhR** (PubChem AID 743122, https://pubchem.ncbi.nlm.nih.gov/bioassay/743122): switches on the aryl hydrocarbon receptor (responds to dioxin-like chemicals).
- **NR-Aromatase** (PubChem AID 743139, https://pubchem.ncbi.nlm.nih.gov/bioassay/743139): blocks aromatase, the enzyme that turns androgens into estrogens (MCF-7 aro ERE cells).
- **NR-ER** (PubChem AID 743079, https://pubchem.ncbi.nlm.nih.gov/bioassay/743079): switches on estrogen receptor alpha (full-length, BG1 ovarian cell line).
- **NR-ER-LBD** (PubChem AID 743077, https://pubchem.ncbi.nlm.nih.gov/bioassay/743077): switches on the estrogen receptor alpha ligand-binding domain (HEK293 reporter cells).
- **NR-PPAR-gamma** (PubChem AID 743140, https://pubchem.ncbi.nlm.nih.gov/bioassay/743140): switches on PPAR-gamma, a receptor that controls fat and sugar metabolism.
- **SR-ARE** (PubChem AID 743219, https://pubchem.ncbi.nlm.nih.gov/bioassay/743219): switches on the antioxidant response element (an oxidative-stress signal).
- **SR-ATAD5** (PubChem AID 720516, https://pubchem.ncbi.nlm.nih.gov/bioassay/720516): raises ATAD5, a sign of DNA damage (genotoxicity; human embryonic kidney cells).
- **SR-HSE** (PubChem AID 743228, https://pubchem.ncbi.nlm.nih.gov/bioassay/743228): switches on the heat shock response (a protein-damage stress signal).
- **SR-MMP** (PubChem AID 720637, https://pubchem.ncbi.nlm.nih.gov/bioassay/720637): disrupts the mitochondrial membrane potential (mitochondria losing their charge).
- **SR-p53** (PubChem AID 720552, https://pubchem.ncbi.nlm.nih.gov/bioassay/720552): switches on p53 signalling (the cell's DNA-damage alarm).

## Model file

`models/tox21.joblib` holds the 12 shipped random forest models, the packed train fingerprints, the train table, the cut-off and the metrics: 129165820 bytes. It is git-ignored.

## Credits

Tox21 data (Tox21 Data Challenge 2014, NCATS/NIEHS/EPA/FDA), MoleculeNet copy.
Wu Z, Ramsundar B, Feinberg EN, et al. MoleculeNet: a benchmark for molecular machine learning. Chem. Sci.
2018;9(2):513-530. doi:10.1039/C7SC02664A
Huang R, Xia M, et al. Tox21Challenge to build predictive models of nuclear receptor and stress response
pathways as mediated by exposure to environmental chemicals and drugs. Front. Environ. Sci. 2016;3:85.
doi:10.3389/fenvs.2015.00085
