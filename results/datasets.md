# Activity datasets (loop 1)

From `uv run python -m molscreen.train` on ChEMBL pulls (ChEMBL_37). Numbers are in
`results/activity_models.json` under `genes.<GENE>.dataset`. Rules: `docs/evaluation.md` and its
2026-11-04 amendment. Mutant rows dropped = rows that pass every other rule but whose assay declares a
protein variant (`assay_variant_mutation`). IDs collapsed = ChEMBL IDs in the kept rows minus parent molecules
(salts stripped to the largest fragment, stereo kept).

| Gene | Rows pulled | Mutant rows dropped | Rows kept | ChEMBL IDs | Parent molecules | IDs collapsed | Actives | Active fraction | Train | Test | Scaffolds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EGFR | 20384 | 4708 | 15106 | 9823 | 9778 | 45 | 7061 | 0.722 | 7822 | 1956 | 3527 |
| BRAF | 9268 | 3960 | 5300 | 2992 | 2991 | 1 | 2571 | 0.860 | 2392 | 599 | 1053 |
| ERBB2 | 3481 | 13 | 3445 | 2560 | 2553 | 7 | 1865 | 0.731 | 2042 | 511 | 1039 |
| CDK4 | 1675 | 0 | 1669 | 1404 | 1401 | 3 | 1235 | 0.882 | 1120 | 281 | 520 |
| CDK6 | 1026 | 0 | 1026 | 821 | 821 | 0 | 795 | 0.968 | 656 | 165 | 337 |
| ALK | 4201 | 923 | 3278 | 2429 | 2428 | 1 | 1902 | 0.783 | 1942 | 486 | 1121 |
| ABL1 | 5350 | 722 | 4615 | 2935 | 2912 | 23 | 2316 | 0.795 | 2329 | 583 | 1207 |
| PARP1 | 5787 | 0 | 5782 | 4510 | 4504 | 6 | 3827 | 0.850 | 3603 | 901 | 2012 |
| BCL2 | 5873 | 44 | 5811 | 3142 | 3142 | 0 | 2701 | 0.860 | 2513 | 629 | 1470 |
