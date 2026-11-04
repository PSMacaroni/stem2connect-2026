# Loop 2 per-drug sensitivity models: held-out results

Built by `python -m molscreen.drugs`; every number is in `results/loop2_models.json`. Protocol:
`docs/evaluation-loop2.md` ("Per-drug models"). **Cell lines, not patients.** Research and learning tool,
not medical advice. Features: the 0/1 hotspot vector (542 genes). Label: sensitive when `auc` is below the
10th percentile of the drug's `auc` over its training lines.

## Drug set

1,173 compounds name a gene in `target` and have >= 300 lines in the hotspot matrix;
361 of them match the oncology target list; the 60 with the most lines
are kept (ties by Broad ID). The table lists every trained drug with its name, Broad ID and PRISM target.

## Split (leave-lineage-out, one split for every drug)

726 cell lines in 24 lineages. Train: 580 lines in 14 lineages. Test: 146 lines in 10 lineages (Bone 26, Bladder/Urinary Tract 24, Kidney 24, Soft Tissue 23, Liver 21, Pleura 10, Thyroid 9, Biliary Tract 6, Ampulla of Vater 2, Fibroblast 1).

## Results

ROC-AUC 95% CI: bootstrap over the test lines (1000 resamples, seed 0), shown for the shipped model (random forest). PR-AUC is for the sensitive class, next to its test prevalence (a random ranking's PR-AUC).
Balanced accuracy at 0.5. "Underpowered": fewer than 5 sensitive test lines.

| Drug | Broad ID | Target | n train | n test | Sensitive in test | Majority | 1-NN | Logistic | RF | random forest ROC-AUC (95% CI) | PR-AUC vs prevalence | Bal. acc. | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AZD2014 | BRD-K99113996 | MTOR | 574 | 144 | 9 | 0.500 | 0.530 | 0.522 | 0.525 | 0.525 (0.341 to 0.698) | 0.068 vs 0.062 | 0.489 |  |
| osimertinib | BRD-K42805893 | EGFR | 573 | 141 | 10 | 0.500 | 0.463 | 0.479 | 0.498 | 0.498 (0.363 to 0.639) | 0.071 vs 0.071 | 0.414 |  |
| ponatinib | BRD-K44227013 | ABL1, BCR, FGFR1, FGFR2, FGFR3, FGFR4, FLT3, KDR, KIT, LCK, LYN, PDGFRA, RET, SRC, TEK | 568 | 142 | 12 | 0.500 | 0.602 | 0.614 | 0.636 | 0.636 (0.513 to 0.748) | 0.127 vs 0.085 | 0.663 |  |
| trametinib | BRD-K12343256 | MAP2K1, MAP2K2 | 569 | 140 | 6 | 0.500 | 0.606 | 0.757 | 0.738 | 0.738 (0.620 to 0.872) | 0.092 vs 0.043 | 0.553 |  |
| everolimus | BRD-K13514097 | MTOR | 567 | 142 | 14 | 0.500 | 0.491 | 0.489 | 0.416 | 0.416 (0.277 to 0.564) | 0.089 vs 0.099 | 0.473 |  |
| tozasertib | BRD-K59369769 | AURKA, AURKB, AURKC, LCK | 568 | 141 | 25 | 0.500 | 0.503 | 0.604 | 0.563 | 0.563 (0.455 to 0.663) | 0.212 vs 0.177 | 0.546 |  |
| pelitinib | BRD-K08799216 | EGFR | 563 | 144 | 13 | 0.500 | 0.506 | 0.526 | 0.505 | 0.505 (0.363 to 0.663) | 0.091 vs 0.090 | 0.522 |  |
| abemaciclib | BRD-K33622447 | CDK4, CDK6 | 565 | 142 | 22 | 0.500 | 0.565 | 0.624 | 0.644 | 0.644 (0.546 to 0.735) | 0.222 vs 0.155 | 0.608 |  |
| canertinib | BRD-K50168500 | AKT1, EGFR, ERBB2, ERBB4 | 566 | 141 | 7 | 0.500 | 0.401 | 0.469 | 0.516 | 0.516 (0.349 to 0.688) | 0.051 vs 0.050 | 0.494 |  |
| atiprimod | BRD-K38527262 | JAK2, STAT3 | 563 | 143 | 14 | 0.500 | 0.313 | 0.541 | 0.510 | 0.510 (0.351 to 0.665) | 0.106 vs 0.098 | 0.524 |  |
| poziotinib | BRD-K50010139 | EGFR, ERBB2, ERBB4 | 565 | 141 | 13 | 0.500 | 0.400 | 0.358 | 0.545 | 0.545 (0.363 to 0.723) | 0.192 vs 0.092 | 0.506 |  |
| brigatinib | BRD-K56981171 | ALK, EGFR | 564 | 142 | 15 | 0.500 | 0.649 | 0.548 | 0.605 | 0.605 (0.487 to 0.718) | 0.135 vs 0.106 | 0.525 |  |
| vorinostat | BRD-K81418486 | HDAC1, HDAC10, HDAC11, HDAC2, HDAC3, HDAC5, HDAC6, HDAC8, HDAC9 | 562 | 144 | 10 | 0.500 | 0.608 | 0.488 | 0.643 | 0.643 (0.475 to 0.800) | 0.126 vs 0.069 | 0.575 |  |
| sorafenib | BRD-K23984367 | BRAF, DDR2, FGFR1, FLT1, FLT3, FLT4, KDR, KIT, PDGFRB, RAF1, RET | 563 | 142 | 18 | 0.500 | 0.500 | 0.537 | 0.596 | 0.596 (0.451 to 0.735) | 0.166 vs 0.127 | 0.626 |  |
| 2-methoxyestradiol | BRD-K44408410 | COMT, CYP19A1, CYP1A1, CYP1B1, HIF1A, TUBB | 563 | 142 | 13 | 0.500 | 0.568 | 0.575 | 0.576 | 0.576 (0.397 to 0.728) | 0.122 vs 0.092 | 0.582 |  |
| belinostat | BRD-K17743125 | HDAC1, HDAC10, HDAC11, HDAC2, HDAC3, HDAC4, HDAC5, HDAC6, HDAC7, HDAC8, HDAC9 | 562 | 142 | 12 | 0.500 | 0.457 | 0.485 | 0.504 | 0.504 (0.304 to 0.693) | 0.098 vs 0.085 | 0.517 |  |
| daunorubicin | BRD-K43389675 | TOP2A, TOP2B | 562 | 142 | 17 | 0.500 | 0.471 | 0.464 | 0.572 | 0.572 (0.438 to 0.711) | 0.151 vs 0.120 | 0.548 |  |
| rociletinib | BRD-K33610132 | EGFR | 560 | 143 | 11 | 0.500 | 0.580 | 0.571 | 0.599 | 0.599 (0.438 to 0.745) | 0.110 vs 0.077 | 0.595 |  |
| palbociclib | BRD-K51313569 | CDK4, CDK6 | 560 | 142 | 22 | 0.500 | 0.528 | 0.590 | 0.562 | 0.562 (0.435 to 0.678) | 0.179 vs 0.155 | 0.593 |  |
| volasertib | BRD-K69776681 | PLK1 | 561 | 141 | 7 | 0.500 | 0.463 | 0.564 | 0.477 | 0.477 (0.275 to 0.683) | 0.052 vs 0.050 | 0.518 |  |
| navitoclax | BRD-K82746043 | BCL2, BCL2L1, BCL2L2 | 556 | 146 | 12 | 0.500 | 0.443 | 0.474 | 0.463 | 0.463 (0.309 to 0.617) | 0.082 vs 0.082 | 0.488 |  |
| dovitinib | BRD-K85402309 | CSF1R, EGFR, FGFR1, FGFR2, FGFR3, FLT1, FLT3, FLT4, INSR, KDR, KIT, PDGFRA, PDGFRB | 559 | 143 | 23 | 0.500 | 0.516 | 0.593 | 0.639 | 0.639 (0.522 to 0.742) | 0.222 vs 0.161 | 0.634 |  |
| LY2801653 | BRD-K18961567 | MET | 555 | 145 | 24 | 0.500 | 0.616 | 0.493 | 0.596 | 0.596 (0.491 to 0.690) | 0.213 vs 0.166 | 0.509 |  |
| resminostat | BRD-K28822270 | HDAC1, HDAC3, HDAC6, HDAC8 | 556 | 144 | 12 | 0.500 | 0.528 | 0.577 | 0.487 | 0.487 (0.335 to 0.661) | 0.089 vs 0.083 | 0.473 |  |
| erlotinib | BRD-K70401845 | EGFR, NR1I2 | 558 | 141 | 16 | 0.500 | 0.484 | 0.558 | 0.693 | 0.693 (0.550 to 0.820) | 0.241 vs 0.113 | 0.621 |  |
| GDC-0980 | BRD-K23228615 | FGR, MAP3K9, MTOR, PIK3CA, PIK3CB, PIK3CD, PIK3CG, SYK | 556 | 142 | 12 | 0.500 | 0.308 | 0.636 | 0.532 | 0.532 (0.293 to 0.768) | 0.154 vs 0.085 | 0.628 |  |
| XL-647 | BRD-K03765900 | EGFR, EPHB4, ERBB2, FLT4, KDR | 554 | 143 | 16 | 0.500 | 0.472 | 0.536 | 0.554 | 0.554 (0.411 to 0.691) | 0.125 vs 0.112 | 0.513 |  |
| gambogic-acid | BRD-K08542803 | BCL2 | 554 | 143 | 10 | 0.500 | 0.626 | 0.697 | 0.540 | 0.540 (0.390 to 0.665) | 0.087 vs 0.070 | 0.618 |  |
| carfilzomib | BRD-K15179879 | PSMA1, PSMA2, PSMA3, PSMA4, PSMA5, PSMA6, PSMA7, PSMA8, PSMB1, PSMB10, PSMB11, PSMB2, PSMB3, PSMB4, PSMB5, PSMB6, PSMB7, PSMB8, PSMB9 | 559 | 138 | 9 | 0.500 | 0.403 | 0.463 | 0.420 | 0.420 (0.207 to 0.636) | 0.062 vs 0.065 | 0.517 |  |
| P276-00 | BRD-K51791723 | CDK1, CDK4, CDK9 | 555 | 142 | 20 | 0.500 | 0.520 | 0.643 | 0.653 | 0.653 (0.497 to 0.778) | 0.269 vs 0.141 | 0.632 |  |
| dacomitinib | BRD-K57169635 | EGFR, ERBB2, ERBB4 | 554 | 143 | 14 | 0.500 | 0.404 | 0.410 | 0.489 | 0.489 (0.339 to 0.645) | 0.107 vs 0.098 | 0.449 |  |
| regorafenib | BRD-K16730910 | ABL1, BRAF, DDR2, EPHA2, FGFR1, FGFR2, FLT1, FLT4, FRK, KDR, KIT, MAPK11, NTRK1, PDGFRA, PDGFRB, RAF1, RET, TEK | 553 | 141 | 18 | 0.500 | 0.583 | 0.600 | 0.659 | 0.659 (0.527 to 0.780) | 0.209 vs 0.128 | 0.666 |  |
| BMS-690514 | BRD-K76239644 | EGFR, ERBB2, FLT3, KDR | 554 | 140 | 14 | 0.500 | 0.345 | 0.380 | 0.423 | 0.423 (0.260 to 0.599) | 0.093 vs 0.100 | 0.369 |  |
| irinotecan | BRD-K08547377 | TOP1, TOP1MT | 552 | 141 | 15 | 0.500 | 0.617 | 0.619 | 0.613 | 0.613 (0.499 to 0.712) | 0.139 vs 0.106 | 0.531 |  |
| paclitaxel | BRD-K62008436 | BCL2, MAP2, MAP4, MAPT, NR1I2, TLR4, TUBB, TUBB1 | 552 | 141 | 14 | 0.500 | 0.662 | 0.749 | 0.630 | 0.630 (0.455 to 0.804) | 0.192 vs 0.099 | 0.612 |  |
| teniposide | BRD-K10362825 | TOP2A, TOP2B | 554 | 138 | 17 | 0.500 | 0.533 | 0.462 | 0.508 | 0.508 (0.361 to 0.650) | 0.152 vs 0.123 | 0.497 |  |
| NVP-BEZ235 | BRD-K12184916 | ATR, MTOR, PIK3CA, PIK3CD, PIK3CG | 549 | 142 | 15 | 0.500 | 0.456 | 0.602 | 0.524 | 0.524 (0.367 to 0.667) | 0.118 vs 0.106 | 0.462 |  |
| docetaxel | BRD-K30577245 | BCL2, MAP2, MAP4, MAPT, NR1I2, TUBB, TUBB1 | 550 | 141 | 16 | 0.500 | 0.436 | 0.606 | 0.578 | 0.578 (0.426 to 0.739) | 0.153 vs 0.113 | 0.591 |  |
| foretinib | BRD-K03449891 | FLT1, FLT4, KDR, MET | 546 | 143 | 16 | 0.500 | 0.594 | 0.590 | 0.557 | 0.557 (0.400 to 0.719) | 0.147 vs 0.112 | 0.474 |  |
| saracatinib | BRD-K19540840 | ABL1, LCK, SRC, YES1 | 546 | 143 | 17 | 0.500 | 0.556 | 0.410 | 0.435 | 0.435 (0.259 to 0.606) | 0.112 vs 0.119 | 0.446 |  |
| lenvatinib | BRD-K39974922 | FLT4, KDR | 552 | 137 | 15 | 0.500 | 0.460 | 0.410 | 0.328 | 0.328 (0.225 to 0.441) | 0.088 vs 0.109 | 0.380 |  |
| MLN0128 | BRD-K59317601 | MTOR, PIK3CA, PIK3CD, PIK3CG | 548 | 141 | 12 | 0.500 | 0.441 | 0.431 | 0.499 | 0.499 (0.374 to 0.624) | 0.087 vs 0.085 | 0.459 |  |
| vandetanib | BRD-K77625799 | EGFR, EPHA1, EPHA10, EPHA2, EPHA3, EPHA4, EPHA5, EPHA6, EPHA7, EPHA8, EPHB1, EPHB2, EPHB3, EPHB4, EPHB6, ERBB2, ERBB3, ERBB4, FLT1, FLT4, KDR, PTK6, RET, SRC, TEK, VEGFA | 550 | 139 | 21 | 0.500 | 0.515 | 0.636 | 0.589 | 0.589 (0.456 to 0.724) | 0.200 vs 0.151 | 0.558 |  |
| AT-7519 | BRD-K13390322 | CDK1, CDK2, CDK4, CDK5, CDK6, CDK9 | 548 | 140 | 11 | 0.500 | 0.533 | 0.498 | 0.555 | 0.555 (0.404 to 0.723) | 0.096 vs 0.079 | 0.580 |  |
| axitinib | BRD-K29905972 | CSF1, FLT1, FLT4, KDR, PLK4 | 550 | 137 | 18 | 0.500 | 0.630 | 0.578 | 0.627 | 0.627 (0.476 to 0.748) | 0.202 vs 0.131 | 0.616 |  |
| temsirolimus | BRD-K42898655 | MTOR | 547 | 140 | 13 | 0.500 | 0.582 | 0.554 | 0.469 | 0.469 (0.299 to 0.653) | 0.102 vs 0.093 | 0.502 |  |
| alpelisib | BRD-K54997624 | PIK3CA, PIK3CB, PIK3CD, PIK3CG | 550 | 137 | 13 | 0.500 | 0.461 | 0.521 | 0.456 | 0.456 (0.311 to 0.615) | 0.085 vs 0.095 | 0.467 |  |
| panobinostat | BRD-K02130563 | HDAC1, HDAC2, HDAC3, HDAC4, HDAC6, HDAC7, HDAC8, HDAC9 | 548 | 138 | 13 | 0.500 | 0.575 | 0.580 | 0.564 | 0.564 (0.434 to 0.710) | 0.139 vs 0.094 | 0.537 |  |
| barasertib | BRD-K31928526 | AURKA, AURKB | 548 | 138 | 17 | 0.500 | 0.531 | 0.583 | 0.597 | 0.597 (0.481 to 0.705) | 0.161 vs 0.123 | 0.656 |  |
| tivozanib | BRD-K53414658 | FLT1, FLT4, KDR, KIT, PDGFRA, PDGFRB | 548 | 138 | 12 | 0.500 | 0.599 | 0.792 | 0.664 | 0.664 (0.494 to 0.812) | 0.150 vs 0.087 | 0.605 |  |
| selumetinib | BRD-K57080016 | MAP2K1 | 549 | 137 | 6 | 0.500 | 0.467 | 0.860 | 0.622 | 0.622 (0.324 to 0.897) | 0.098 vs 0.044 | 0.621 |  |
| cyt387 | BRD-K87737963 | JAK1, JAK2, JAK3 | 548 | 138 | 18 | 0.500 | 0.509 | 0.483 | 0.418 | 0.418 (0.286 to 0.557) | 0.115 vs 0.130 | 0.450 |  |
| bortezomib | BRD-K88510285 | PSMA1, PSMA2, PSMA3, PSMA4, PSMA5, PSMA6, PSMA7, PSMA8, PSMB1, PSMB10, PSMB11, PSMB2, PSMB3, PSMB4, PSMB5, PSMB6, PSMB7, PSMB8, PSMB9, PSMD1, PSMD2, RELA | 546 | 140 | 8 | 0.500 | 0.454 | 0.454 | 0.606 | 0.606 (0.353 to 0.823) | 0.088 vs 0.057 | 0.572 |  |
| tivantinib | BRD-K33379087 | MET | 544 | 141 | 7 | 0.500 | 0.471 | 0.435 | 0.409 | 0.409 (0.262 to 0.569) | 0.042 vs 0.050 | 0.412 |  |
| AVL-292 | BRD-K87782578 | BTK, YES1 | 543 | 142 | 14 | 0.500 | 0.366 | 0.546 | 0.566 | 0.566 (0.432 to 0.702) | 0.117 vs 0.099 | 0.551 |  |
| obatoclax | BRD-K15600710 | BCL2 | 543 | 141 | 8 | 0.500 | 0.488 | 0.598 | 0.621 | 0.621 (0.498 to 0.741) | 0.077 vs 0.057 | 0.583 |  |
| golvatinib | BRD-K69001009 | KDR, MET | 544 | 140 | 14 | 0.500 | 0.483 | 0.439 | 0.571 | 0.571 (0.410 to 0.730) | 0.145 vs 0.100 | 0.556 |  |
| PHA-848125 | BRD-K60997853 | CDK2, CDK4, CDK7, NTRK1 | 540 | 143 | 17 | 0.500 | 0.617 | 0.550 | 0.699 | 0.699 (0.583 to 0.803) | 0.205 vs 0.119 | 0.641 |  |
| AS-703026 | BRD-K89014967 | MAP2K1, MAP2K2 | 541 | 142 | 9 | 0.500 | 0.623 | 0.650 | 0.589 | 0.589 (0.354 to 0.798) | 0.111 vs 0.063 | 0.629 |  |
| ibrutinib | BRD-K70301465 | BLK, BMX, BTK | 545 | 136 | 5 | 0.500 | 0.260 | 0.361 | 0.286 | 0.286 (0.044 to 0.521) | 0.028 vs 0.037 | 0.483 |  |

**Switch rule:** the random forest had the higher held-out ROC-AUC on 32 of 60 drugs that are not underpowered (it needed more than half), so **random forest** ships for every drug. Underpowered drugs: 0 of 60. The models are close: median ROC-AUC 0.549 (logistic) vs 0.562 (random forest).

## What this says

Of the 60 drugs that are not underpowered, the shipped model (random forest) has a higher held-out ROC-AUC than the 1-NN baseline on 40 (1-NN median 0.507), and its 95% CI includes 0.5 on 52 (no better than chance at this test size); 16 are below 0.5. Its median ROC-AUC is 0.562 over those drugs (0.562 over all 60); the highest is 0.738 (trametinib). Hotspot mutations alone explain little of how a cell line responds to most of these drugs; the models are shown as a weak, honest signal next to the measured responses of the nearest cell lines, not as a prediction for a person.

Models: `models/loop2/<broad_id>.joblib` (git-ignored), random forest fit on the training lines, 73,143,794 bytes in total.
