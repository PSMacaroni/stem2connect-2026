# Activity datasets (loop 1)

From `uv run python -m molscreen.train` on ChEMBL pulls (ChEMBL_37). Numbers are in
`results/activity_models.json` under `genes.<GENE>.dataset`. Rules: `docs/evaluation.md`.

| Gene | Rows pulled | Rows kept | Unique molecules | Actives | Active fraction | Train | Test | Scaffolds |
|---|---|---|---|---|---|---|---|---|
| EGFR | 20384 | 19814 | 11023 | 8307 | 0.754 | 8818 | 2205 | 3964 |
| BRAF | 9268 | 9260 | 5381 | 4628 | 0.860 | 4304 | 1077 | 1881 |
| ERBB2 | 3481 | 3458 | 2560 | 1870 | 0.730 | 2048 | 512 | 1042 |
| CDK4 | 1675 | 1669 | 1404 | 1238 | 0.882 | 1123 | 281 | 520 |
| CDK6 | 1026 | 1026 | 821 | 795 | 0.968 | 656 | 165 | 337 |
| ALK | 4201 | 4201 | 2476 | 1950 | 0.788 | 1980 | 496 | 1143 |
| ABL1 | 5350 | 5337 | 3038 | 2430 | 0.800 | 2430 | 608 | 1255 |
| PARP1 | 5787 | 5782 | 4510 | 3833 | 0.850 | 3608 | 902 | 2013 |
| BCL2 | 5873 | 5855 | 3142 | 2701 | 0.860 | 2513 | 629 | 1470 |
