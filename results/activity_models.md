# Activity models (loop 1): held-out results

Scaffold-split held-out test sets, ChEMBL release ChEMBL_37, protocol `docs/evaluation.md`.
All numbers come from `results/activity_models.json`, written by `uv run python -m molscreen.train`.
Morgan fingerprints (radius 2, 2048 bits). Model parameters are fixed in `src/molscreen/train.py`;
nothing was tuned, so no inner split was used. Each cell pair is ROC-AUC / PR-AUC on the held-out set.
Test active frac is also the PR-AUC of a random ranking. Held-out abstain counts held-out molecules whose
max Tanimoto to train is below the cut-off; AUC kept is the shipped model's ROC-AUC on the others.

| Gene | n train | n test | Test active frac | Majority | 1-NN | Random forest | LightGBM | Abstain cut-off | Held-out abstain | AUC kept | Shipped |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EGFR | 8818 | 2205 | 0.722 | 0.500 / 0.722 | 0.820 / 0.906 | 0.877 / 0.943 | 0.850 / 0.928 | 0.667 | 729 of 2205 | 0.907 | random forest |
| BRAF | 4304 | 1077 | 0.822 | 0.500 / 0.822 | 0.791 / 0.930 | 0.870 / 0.965 | 0.876 / 0.967 | 0.724 | 464 of 1077 | 0.897 | random forest |
| ERBB2 | 2048 | 512 | 0.742 | 0.500 / 0.742 | 0.791 / 0.887 | 0.880 / 0.950 | 0.870 / 0.946 | 0.644 | 144 of 512 | 0.879 | random forest |
| CDK4 | 1123 | 281 | 0.872 | 0.500 / 0.872 | 0.828 / 0.966 | 0.886 / 0.980 | 0.879 / 0.977 | 0.705 | 96 of 281 | 0.891 | random forest |
| CDK6 | 656 | 165 | 0.964 | 0.500 / 0.964 | 0.784 / 0.981 | 0.901 / 0.996 | 0.770 / 0.972 | 0.709 | 49 of 165 | 0.901 | random forest |
| ALK | 1980 | 496 | 0.698 | 0.500 / 0.698 | 0.857 / 0.913 | 0.908 / 0.956 | 0.891 / 0.947 | 0.539 | 114 of 496 | 0.928 | random forest |
| ABL1 | 2430 | 608 | 0.696 | 0.500 / 0.696 | 0.836 / 0.913 | 0.855 / 0.933 | 0.837 / 0.928 | 0.580 | 218 of 608 | 0.907 | random forest |
| PARP1 | 3608 | 902 | 0.837 | 0.500 / 0.837 | 0.872 / 0.959 | 0.900 / 0.973 | 0.898 / 0.969 | 0.621 | 171 of 902 | 0.907 | random forest |
| BCL2 | 2513 | 629 | 0.839 | 0.500 / 0.839 | 0.948 / 0.988 | 0.962 / 0.991 | 0.963 / 0.993 | 0.738 | 97 of 629 | 0.954 | random forest |

Switch rule: the random forest had the higher held-out PR-AUC on 7 of 9 targets
(it needed at least 6), so **random forest** ships for every target.

## Credits

Bioactivity data: ChEMBL.
ChEMBL data is from http://www.ebi.ac.uk/chembl - the version of ChEMBL is chembl_37.
Licensed under CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/); any ChEMBL-derived data
published from this project is shared under the same licence. Mendez D, Gaulton A, Bento AP, et al.
ChEMBL: towards direct deposition of bioassay data. Nucleic Acids Res. 2019;47(D1):D930-D940.
doi:10.1093/nar/gky1075
