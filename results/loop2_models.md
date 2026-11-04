# Loop 2 per-drug sensitivity models: held-out results

Built by `python -m molscreen.drugs`; every number is in `results/loop2_models.json`. Protocol:
`docs/evaluation-loop2.md` ("Per-drug models" and its dated Changes). **Cell lines, not patients.**
Research and learning tool, not medical advice. Features: the 0/1 hotspot vector (542 genes). Label: sensitive
when `auc` is below the 10th percentile of the drug's `auc` over its training lines.

**How the app uses this.** The nearest cell lines and their measured sensitivities are the main evidence in loop 2; model ranks are shown second and greyed when `weak` (95% CI lower bound <= 0.5); the probabilities are not calibrated and must be shown as ranks, never as percentages.

## Drug set

1,173 compounds name a gene in `target` and have >= 300 lines in the hotspot matrix. For each of the 32 oncology-list genes, up to 3 of them whose `target` names that gene are kept, the most screened first (ties by Broad ID); a compound counts once, under the first oncology-list gene it names. 32 genes have at least one compound, giving **86 compounds**. The "Gene" column is the gene a compound was picked under.

## Split (leave-lineage-out, one split for every drug)

726 cell lines in 24 lineages. Train: 580 lines in 14 lineages. Test: 146 lines in 10 lineages (Bone 26, Bladder/Urinary Tract 24, Kidney 24, Soft Tissue 23, Liver 21, Pleura 10, Thyroid 9, Biliary Tract 6, Ampulla of Vater 2, Fibroblast 1).

## Results

ROC-AUC with its 95% CI: bootstrap over the test lines (1000 resamples, seed 0). PR-AUC (sensitive class, next to its test prevalence = a random ranking's PR-AUC) and balanced accuracy at 0.5 are for the shipped model (logistic regression). "Weak": the shipped model's CI lower bound is <= 0.5. "Underpowered": fewer than 5 sensitive test lines.

| Drug | Broad ID | Target | Gene | n train | n test | Sensitive in test | Majority | 1-NN | Logistic (95% CI) | RF (95% CI) | PR-AUC vs prevalence | Bal. acc. | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| osimertinib | BRD-K42805893 | EGFR | EGFR | 573 | 141 | 10 | 0.500 | 0.463 | 0.479 (0.339 to 0.639) | 0.498 (0.363 to 0.639) | 0.068 vs 0.071 | 0.460 | weak |
| pelitinib | BRD-K08799216 | EGFR | EGFR | 563 | 144 | 13 | 0.500 | 0.506 | 0.526 (0.403 to 0.651) | 0.505 (0.363 to 0.663) | 0.094 vs 0.090 | 0.537 | weak |
| canertinib | BRD-K50168500 | AKT1, EGFR, ERBB2, ERBB4 | EGFR | 566 | 141 | 7 | 0.500 | 0.401 | 0.469 (0.289 to 0.655) | 0.516 (0.349 to 0.688) | 0.047 vs 0.050 | 0.480 | weak |
| sorafenib | BRD-K23984367 | BRAF, DDR2, FGFR1, FLT1, FLT3, FLT4, KDR, KIT, PDGFRB, RAF1, RET | BRAF | 563 | 142 | 18 | 0.500 | 0.500 | 0.537 (0.415 to 0.651) | 0.596 (0.451 to 0.735) | 0.141 vs 0.127 | 0.478 | weak |
| regorafenib | BRD-K16730910 | ABL1, BRAF, DDR2, EPHA2, FGFR1, FGFR2, FLT1, FLT4, FRK, KDR, KIT, MAPK11, NTRK1, PDGFRA, PDGFRB, RAF1, RET, TEK | BRAF | 553 | 141 | 18 | 0.500 | 0.583 | 0.600 (0.467 to 0.706) | 0.659 (0.527 to 0.780) | 0.169 vs 0.128 | 0.467 | weak |
| AZ-628 | BRD-K05804044 | BRAF, RAF1 | BRAF | 545 | 131 | 12 | 0.500 | 0.483 | 0.744 (0.611 to 0.859) | 0.600 (0.414 to 0.775) | 0.214 vs 0.092 | 0.633 |  |
| CP-724714 | BRD-K76908866 | ERBB2 | ERBB2 | 543 | 138 | 14 | 0.500 | 0.537 | 0.685 (0.510 to 0.836) | 0.486 (0.296 to 0.676) | 0.187 vs 0.101 | 0.626 |  |
| ARRY-334543 | BRD-K46386702 | ERBB2 | ERBB2 | 542 | 135 | 17 | 0.500 | 0.340 | 0.377 (0.229 to 0.521) | 0.370 (0.242 to 0.510) | 0.100 vs 0.126 | 0.393 | weak |
| tucatinib | BRD-K26026438 | ERBB2 | ERBB2 | 524 | 138 | 9 | 0.500 | 0.396 | 0.463 (0.261 to 0.669) | 0.514 (0.299 to 0.739) | 0.067 vs 0.065 | 0.479 | weak |
| abemaciclib | BRD-K33622447 | CDK4, CDK6 | CDK4 | 565 | 142 | 22 | 0.500 | 0.565 | 0.624 (0.513 to 0.723) | 0.644 (0.546 to 0.735) | 0.219 vs 0.155 | 0.639 |  |
| palbociclib | BRD-K51313569 | CDK4, CDK6 | CDK4 | 560 | 142 | 22 | 0.500 | 0.528 | 0.590 (0.460 to 0.718) | 0.562 (0.435 to 0.678) | 0.211 vs 0.155 | 0.556 | weak |
| P276-00 | BRD-K51791723 | CDK1, CDK4, CDK9 | CDK4 | 555 | 142 | 20 | 0.500 | 0.520 | 0.643 (0.503 to 0.755) | 0.653 (0.497 to 0.778) | 0.208 vs 0.141 | 0.620 |  |
| aminopurvalanol-a | BRD-K07762753 | CDK1, CDK2, CDK5, CDK6 | CDK6 | 364 | 101 | 7 | 0.500 | 0.675 | 0.658 (0.505 to 0.799) | 0.614 (0.453 to 0.779) | 0.108 vs 0.069 | 0.608 |  |
| crizotinib | BRD-K78431006 | ALK, MET | ALK | 531 | 141 | 13 | 0.500 | 0.511 | 0.480 (0.296 to 0.683) | 0.447 (0.281 to 0.636) | 0.130 vs 0.092 | 0.508 | weak |
| alectinib | BRD-K11267252 | ALK, MET | ALK | 535 | 132 | 9 | 0.500 | 0.564 | 0.429 (0.227 to 0.625) | 0.589 (0.384 to 0.796) | 0.061 vs 0.068 | 0.489 | weak |
| AZD3463 | BRD-K24593301 | ALK, IGF1R | ALK | 359 | 103 | 13 | 0.500 | 0.643 | 0.642 (0.514 to 0.754) | 0.540 (0.395 to 0.675) | 0.172 vs 0.126 | 0.618 |  |
| ponatinib | BRD-K44227013 | ABL1, BCR, FGFR1, FGFR2, FGFR3, FGFR4, FLT3, KDR, KIT, LCK, LYN, PDGFRA, RET, SRC, TEK | ABL1 | 568 | 142 | 12 | 0.500 | 0.602 | 0.614 (0.482 to 0.735) | 0.636 (0.513 to 0.748) | 0.124 vs 0.085 | 0.622 | weak |
| saracatinib | BRD-K19540840 | ABL1, LCK, SRC, YES1 | ABL1 | 546 | 143 | 17 | 0.500 | 0.556 | 0.410 (0.265 to 0.569) | 0.435 (0.259 to 0.606) | 0.105 vs 0.119 | 0.412 | weak |
| dasatinib | BRD-K49328571 | ABL1, ABL2, BLK, EPHA2, FGR, FRK, FYN, HCK, KIT, LCK, LYN, PDGFRB, SRC, SRMS, STAT5B, YES1 | ABL1 | 534 | 139 | 28 | 0.500 | 0.477 | 0.471 (0.358 to 0.579) | 0.531 (0.414 to 0.651) | 0.186 vs 0.201 | 0.477 | weak |
| niraparib | BRD-K54955827 | PARP1 | PARP1 | 540 | 140 | 16 | 0.500 | 0.737 | 0.665 (0.561 to 0.753) | 0.682 (0.569 to 0.781) | 0.165 vs 0.114 | 0.596 |  |
| olaparib | BRD-K02113016 | PARP1, PARP2 | PARP1 | 543 | 136 | 16 | 0.500 | 0.499 | 0.746 (0.654 to 0.828) | 0.627 (0.528 to 0.721) | 0.228 vs 0.118 | 0.615 |  |
| 3-amino-benzamide | BRD-K08703257 | PARP1 | PARP1 | 464 | 125 | 20 | 0.500 | 0.375 | 0.489 (0.341 to 0.640) | 0.390 (0.241 to 0.543) | 0.163 vs 0.160 | 0.471 | weak |
| navitoclax | BRD-K82746043 | BCL2, BCL2L1, BCL2L2 | BCL2 | 556 | 146 | 12 | 0.500 | 0.443 | 0.474 (0.304 to 0.626) | 0.463 (0.309 to 0.617) | 0.083 vs 0.082 | 0.466 | weak |
| gambogic-acid | BRD-K08542803 | BCL2 | BCL2 | 554 | 143 | 10 | 0.500 | 0.626 | 0.697 (0.556 to 0.810) | 0.540 (0.390 to 0.665) | 0.120 vs 0.070 | 0.701 |  |
| paclitaxel | BRD-K62008436 | BCL2, MAP2, MAP4, MAPT, NR1I2, TLR4, TUBB, TUBB1 | BCL2 | 552 | 141 | 14 | 0.500 | 0.662 | 0.749 (0.619 to 0.865) | 0.630 (0.455 to 0.804) | 0.229 vs 0.099 | 0.675 |  |
| trametinib | BRD-K12343256 | MAP2K1, MAP2K2 | MAP2K1 | 569 | 140 | 6 | 0.500 | 0.606 | 0.757 (0.587 to 0.934) | 0.738 (0.620 to 0.872) | 0.135 vs 0.043 | 0.618 |  |
| selumetinib | BRD-K57080016 | MAP2K1 | MAP2K1 | 549 | 137 | 6 | 0.500 | 0.467 | 0.860 (0.710 to 0.966) | 0.622 (0.324 to 0.897) | 0.225 vs 0.044 | 0.780 |  |
| AS-703026 | BRD-K89014967 | MAP2K1, MAP2K2 | MAP2K1 | 541 | 142 | 9 | 0.500 | 0.623 | 0.650 (0.417 to 0.841) | 0.589 (0.354 to 0.798) | 0.152 vs 0.063 | 0.577 | weak |
| MEK1-2-inhibitor | BRD-K12244279 | MAP2K2 | MAP2K2 | 339 | 96 | 13 | 0.500 | 0.582 | 0.513 (0.352 to 0.689) | 0.427 (0.286 to 0.584) | 0.158 vs 0.135 | 0.446 | weak |
| AZD2014 | BRD-K99113996 | MTOR | MTOR | 574 | 144 | 9 | 0.500 | 0.530 | 0.522 (0.340 to 0.700) | 0.525 (0.341 to 0.698) | 0.071 vs 0.062 | 0.478 | weak |
| everolimus | BRD-K13514097 | MTOR | MTOR | 567 | 142 | 14 | 0.500 | 0.491 | 0.489 (0.335 to 0.635) | 0.416 (0.277 to 0.564) | 0.111 vs 0.099 | 0.465 | weak |
| GDC-0980 | BRD-K23228615 | FGR, MAP3K9, MTOR, PIK3CA, PIK3CB, PIK3CD, PIK3CG, SYK | MTOR | 556 | 142 | 12 | 0.500 | 0.308 | 0.636 (0.413 to 0.815) | 0.532 (0.293 to 0.768) | 0.225 vs 0.085 | 0.601 | weak |
| alpelisib | BRD-K54997624 | PIK3CA, PIK3CB, PIK3CD, PIK3CG | PIK3CA | 550 | 137 | 13 | 0.500 | 0.461 | 0.521 (0.389 to 0.651) | 0.456 (0.311 to 0.615) | 0.097 vs 0.095 | 0.414 | weak |
| copanlisib | BRD-K24666289 | PIK3CA, PIK3CB, PIK3CD, PIK3CG | PIK3CA | 539 | 141 | 13 | 0.500 | 0.538 | 0.653 (0.514 to 0.780) | 0.634 (0.495 to 0.752) | 0.151 vs 0.092 | 0.631 |  |
| idelalisib | BRD-K60866521 | PIK3CA, PIK3CB, PIK3CD, PIK3CG | PIK3CA | 529 | 133 | 16 | 0.500 | 0.697 | 0.604 (0.460 to 0.745) | 0.538 (0.428 to 0.650) | 0.162 vs 0.120 | 0.595 | weak |
| tivozanib | BRD-K53414658 | FLT1, FLT4, KDR, KIT, PDGFRA, PDGFRB | KIT | 548 | 138 | 12 | 0.500 | 0.599 | 0.792 (0.671 to 0.893) | 0.664 (0.494 to 0.812) | 0.242 vs 0.087 | 0.685 |  |
| sunitinib | BRD-K42828737 | CSF1R, FGFR1, FLT1, FLT3, FLT4, KDR, KIT, PDGFRA, PDGFRB, RET | KIT | 536 | 142 | 19 | 0.500 | 0.556 | 0.583 (0.449 to 0.708) | 0.670 (0.540 to 0.783) | 0.175 vs 0.134 | 0.568 | weak |
| pazopanib | BRD-K74514084 | CSF1R, FGF1, FGFR1, FGFR3, FLT1, FLT4, ITK, KDR, KIT, PDGFRA, PDGFRB, SH2B3 | KIT | 531 | 137 | 13 | 0.500 | 0.569 | 0.518 (0.379 to 0.643) | 0.680 (0.526 to 0.805) | 0.131 vs 0.095 | 0.639 | weak |
| TG-02 | BRD-K14560436 | CDK1, CDK2, CDK7, CDK9, FLT3, JAK2 | FLT3 | 369 | 104 | 11 | 0.500 | 0.432 | 0.469 (0.242 to 0.711) | 0.489 (0.310 to 0.673) | 0.142 vs 0.106 | 0.583 | weak |
| toceranib | BRD-K62040061 | FLT1, FLT3, KDR, PDGFRA, PDGFRB | FLT3 | 373 | 97 | 8 | 0.500 | 0.419 | 0.537 (0.330 to 0.750) | 0.465 (0.302 to 0.613) | 0.111 vs 0.082 | 0.565 | weak |
| midostaurin | BRD-K13646352 | FLT3, PRKCG | FLT3 | 366 | 103 | 18 | 0.500 | 0.649 | 0.457 (0.344 to 0.564) | 0.448 (0.342 to 0.565) | 0.170 vs 0.175 | 0.387 | weak |
| AVL-292 | BRD-K87782578 | BTK, YES1 | BTK | 543 | 142 | 14 | 0.500 | 0.366 | 0.546 (0.407 to 0.681) | 0.566 (0.432 to 0.702) | 0.112 vs 0.099 | 0.506 | weak |
| ibrutinib | BRD-K70301465 | BLK, BMX, BTK | BTK | 545 | 136 | 5 | 0.500 | 0.260 | 0.361 (0.165 to 0.566) | 0.286 (0.044 to 0.521) | 0.031 vs 0.037 | 0.321 | weak |
| acalabrutinib | BRD-K64034691 | BTK | BTK | 414 | 100 | 11 | 0.500 | 0.392 | 0.387 (0.187 to 0.602) | 0.463 (0.228 to 0.710) | 0.134 vs 0.110 | 0.407 | weak |
| cyt387 | BRD-K87737963 | JAK1, JAK2, JAK3 | JAK1 | 548 | 138 | 18 | 0.500 | 0.509 | 0.483 (0.349 to 0.613) | 0.418 (0.286 to 0.557) | 0.126 vs 0.130 | 0.436 | weak |
| ruxolitinib | BRD-K53972329 | JAK1, JAK2, JAK3, TYK2 | JAK1 | 505 | 131 | 9 | 0.500 | 0.568 | 0.547 (0.404 to 0.701) | 0.493 (0.315 to 0.676) | 0.077 vs 0.069 | 0.538 | weak |
| itacitinib | BRD-K67482377 | JAK1 | JAK1 | 365 | 101 | 14 | 0.500 | 0.474 | 0.546 (0.369 to 0.705) | 0.519 (0.344 to 0.679) | 0.218 vs 0.139 | 0.545 | weak |
| atiprimod | BRD-K38527262 | JAK2, STAT3 | JAK2 | 563 | 143 | 14 | 0.500 | 0.313 | 0.541 (0.385 to 0.692) | 0.510 (0.351 to 0.665) | 0.120 vs 0.098 | 0.521 | weak |
| TG-101209 | BRD-K39841531 | JAK2, JAK3 | JAK2 | 365 | 104 | 14 | 0.500 | 0.552 | 0.409 (0.266 to 0.562) | 0.491 (0.370 to 0.618) | 0.139 vs 0.135 | 0.494 | weak |
| WP1130 | BRD-K43644456 | JAK2, UCHL5, USP14, USP9X | JAK2 | 364 | 104 | 11 | 0.500 | 0.409 | 0.446 (0.287 to 0.622) | 0.447 (0.297 to 0.602) | 0.098 vs 0.106 | 0.405 | weak |
| tozasertib | BRD-K59369769 | AURKA, AURKB, AURKC, LCK | AURKA | 568 | 141 | 25 | 0.500 | 0.503 | 0.604 (0.496 to 0.709) | 0.563 (0.455 to 0.663) | 0.229 vs 0.177 | 0.560 | weak |
| barasertib | BRD-K31928526 | AURKA, AURKB | AURKA | 548 | 138 | 17 | 0.500 | 0.531 | 0.583 (0.469 to 0.689) | 0.597 (0.481 to 0.705) | 0.157 vs 0.123 | 0.627 | weak |
| alisertib | BRD-K75295174 | AURKA | AURKA | 373 | 101 | 9 | 0.500 | 0.450 | 0.472 (0.291 to 0.641) | 0.582 (0.410 to 0.744) | 0.088 vs 0.089 | 0.455 | weak |
| TAK-901 | BRD-K01683783 | AURKB | AURKB | 371 | 103 | 11 | 0.500 | 0.596 | 0.672 (0.506 to 0.826) | 0.596 (0.396 to 0.799) | 0.205 vs 0.107 | 0.705 |  |
| barasertib-HQPA | BRD-K63923597 | AURKB | AURKB | 350 | 98 | 15 | 0.500 | 0.644 | 0.590 (0.424 to 0.755) | 0.687 (0.517 to 0.850) | 0.243 vs 0.153 | 0.574 | weak |
| hesperadin | BRD-K58122457 | AURKB | AURKB | 290 | 76 | 13 | 0.500 | 0.621 | 0.582 (0.417 to 0.727) | 0.549 (0.402 to 0.688) | 0.220 vs 0.171 | 0.587 | weak |
| volasertib | BRD-K69776681 | PLK1 | PLK1 | 561 | 141 | 7 | 0.500 | 0.463 | 0.564 (0.381 to 0.767) | 0.477 (0.275 to 0.683) | 0.060 vs 0.050 | 0.513 | weak |
| rigosertib | BRD-K55187425 | PLK1 | PLK1 | 533 | 135 | 9 | 0.500 | 0.311 | 0.457 (0.225 to 0.695) | 0.437 (0.207 to 0.670) | 0.073 vs 0.067 | 0.437 | weak |
| HMN-214 | BRD-K70511574 | PLK1 | PLK1 | 367 | 102 | 11 | 0.500 | 0.585 | 0.488 (0.325 to 0.655) | 0.504 (0.349 to 0.654) | 0.114 vs 0.108 | 0.440 | weak |
| irinotecan | BRD-K08547377 | TOP1, TOP1MT | TOP1 | 552 | 141 | 15 | 0.500 | 0.617 | 0.619 (0.508 to 0.719) | 0.613 (0.499 to 0.712) | 0.141 vs 0.106 | 0.539 |  |
| rubitecan | BRD-K79821389 | TOP1 | TOP1 | 370 | 103 | 16 | 0.500 | 0.373 | 0.544 (0.360 to 0.718) | 0.462 (0.303 to 0.623) | 0.250 vs 0.155 | 0.590 | weak |
| nemorubicin | BRD-K51911221 | TOP1, TOP2A | TOP1 | 368 | 103 | 12 | 0.500 | 0.499 | 0.477 (0.332 to 0.632) | 0.465 (0.326 to 0.624) | 0.123 vs 0.117 | 0.435 | weak |
| daunorubicin | BRD-K43389675 | TOP2A, TOP2B | TOP2A | 562 | 142 | 17 | 0.500 | 0.471 | 0.464 (0.329 to 0.597) | 0.572 (0.438 to 0.711) | 0.111 vs 0.120 | 0.485 | weak |
| teniposide | BRD-K10362825 | TOP2A, TOP2B | TOP2A | 554 | 138 | 17 | 0.500 | 0.533 | 0.462 (0.315 to 0.596) | 0.508 (0.361 to 0.650) | 0.116 vs 0.123 | 0.488 | weak |
| genistein | BRD-K43797669 | CFTR, ESR1, ESR2, ESRRA, ESRRB, ESRRG, NCOA1, NCOA2, PPARG, PTK2B, TOP2A, TRPC5 | TOP2A | 473 | 120 | 9 | 0.500 | 0.562 | 0.613 (0.496 to 0.729) | 0.661 (0.522 to 0.781) | 0.109 vs 0.075 | 0.459 | weak |
| 2-methoxyestradiol | BRD-K44408410 | COMT, CYP19A1, CYP1A1, CYP1B1, HIF1A, TUBB | TUBB | 563 | 142 | 13 | 0.500 | 0.568 | 0.575 (0.414 to 0.730) | 0.576 (0.397 to 0.728) | 0.134 vs 0.092 | 0.547 | weak |
| flubendazole | BRD-K86003836 | TUBB | TUBB | 372 | 104 | 7 | 0.500 | 0.330 | 0.451 (0.255 to 0.659) | 0.464 (0.162 to 0.761) | 0.070 vs 0.067 | 0.350 | weak |
| verubulin | BRD-K42673188 | TUBB | TUBB | 367 | 102 | 10 | 0.500 | 0.523 | 0.397 (0.239 to 0.568) | 0.583 (0.408 to 0.743) | 0.084 vs 0.098 | 0.420 | weak |
| vorinostat | BRD-K81418486 | HDAC1, HDAC10, HDAC11, HDAC2, HDAC3, HDAC5, HDAC6, HDAC8, HDAC9 | HDAC1 | 562 | 144 | 10 | 0.500 | 0.608 | 0.488 (0.360 to 0.613) | 0.643 (0.475 to 0.800) | 0.080 vs 0.069 | 0.369 | weak |
| belinostat | BRD-K17743125 | HDAC1, HDAC10, HDAC11, HDAC2, HDAC3, HDAC4, HDAC5, HDAC6, HDAC7, HDAC8, HDAC9 | HDAC1 | 562 | 142 | 12 | 0.500 | 0.457 | 0.485 (0.333 to 0.631) | 0.504 (0.304 to 0.693) | 0.081 vs 0.085 | 0.431 | weak |
| resminostat | BRD-K28822270 | HDAC1, HDAC3, HDAC6, HDAC8 | HDAC1 | 556 | 144 | 12 | 0.500 | 0.528 | 0.577 (0.413 to 0.745) | 0.487 (0.335 to 0.661) | 0.132 vs 0.083 | 0.557 | weak |
| carfilzomib | BRD-K15179879 | PSMA1, PSMA2, PSMA3, PSMA4, PSMA5, PSMA6, PSMA7, PSMA8, PSMB1, PSMB10, PSMB11, PSMB2, PSMB3, PSMB4, PSMB5, PSMB6, PSMB7, PSMB8, PSMB9 | PSMB5 | 559 | 138 | 9 | 0.500 | 0.403 | 0.463 (0.270 to 0.658) | 0.420 (0.207 to 0.636) | 0.063 vs 0.065 | 0.486 | weak |
| bortezomib | BRD-K88510285 | PSMA1, PSMA2, PSMA3, PSMA4, PSMA5, PSMA6, PSMA7, PSMA8, PSMB1, PSMB10, PSMB11, PSMB2, PSMB3, PSMB4, PSMB5, PSMB6, PSMB7, PSMB8, PSMB9, PSMD1, PSMD2, RELA | PSMB5 | 546 | 140 | 8 | 0.500 | 0.454 | 0.454 (0.221 to 0.692) | 0.606 (0.353 to 0.823) | 0.064 vs 0.057 | 0.500 | weak |
| idasanutlin | BRD-K62627508 | MDM2, TP53 | MDM2 | 520 | 133 | 16 | 0.500 | 0.577 | 0.752 (0.651 to 0.838) | 0.780 (0.688 to 0.861) | 0.260 vs 0.120 | 0.711 |  |
| RITA | BRD-K00317371 | MDM2 | MDM2 | 352 | 102 | 18 | 0.500 | 0.517 | 0.604 (0.457 to 0.742) | 0.580 (0.438 to 0.714) | 0.284 vs 0.176 | 0.536 | weak |
| nutlin-3 | BRD-A12230535 | MDM2, TP53 | MDM2 | 343 | 97 | 14 | 0.500 | 0.771 | 0.655 (0.536 to 0.761) | 0.741 (0.639 to 0.836) | 0.233 vs 0.144 | 0.712 |  |
| 2,3-DCPE | BRD-K61734568 | BCL2L1 | BCL2L1 | 350 | 98 | 15 | 0.500 | 0.431 | 0.625 (0.502 to 0.746) | 0.641 (0.498 to 0.780) | 0.200 vs 0.153 | 0.546 |  |
| foretinib | BRD-K03449891 | FLT1, FLT4, KDR, MET | KDR | 546 | 143 | 16 | 0.500 | 0.594 | 0.590 (0.431 to 0.741) | 0.557 (0.400 to 0.719) | 0.155 vs 0.112 | 0.580 | weak |
| lenvatinib | BRD-K39974922 | FLT4, KDR | KDR | 552 | 137 | 15 | 0.500 | 0.460 | 0.410 (0.303 to 0.539) | 0.328 (0.225 to 0.441) | 0.095 vs 0.109 | 0.395 | weak |
| axitinib | BRD-K29905972 | CSF1, FLT1, FLT4, KDR, PLK4 | KDR | 550 | 137 | 18 | 0.500 | 0.630 | 0.578 (0.442 to 0.705) | 0.627 (0.476 to 0.748) | 0.167 vs 0.131 | 0.570 | weak |
| LY2801653 | BRD-K18961567 | MET | MET | 555 | 145 | 24 | 0.500 | 0.616 | 0.493 (0.380 to 0.599) | 0.596 (0.491 to 0.690) | 0.169 vs 0.166 | 0.459 | weak |
| tivantinib | BRD-K33379087 | MET | MET | 544 | 141 | 7 | 0.500 | 0.471 | 0.435 (0.196 to 0.697) | 0.409 (0.262 to 0.569) | 0.062 vs 0.050 | 0.412 | weak |
| INC-280 | BRD-K81016934 | MET | MET | 487 | 124 | 11 | 0.500 | 0.497 | 0.593 (0.434 to 0.733) | 0.465 (0.330 to 0.587) | 0.114 vs 0.089 | 0.542 | weak |
| R406 | BRD-K20285085 | RET, SYK | RET | 363 | 102 | 22 | 0.500 | 0.332 | 0.652 (0.527 to 0.749) | 0.582 (0.443 to 0.712) | 0.370 vs 0.216 | 0.557 |  |
| PP-1 | BRD-K47598052 | HCK, RET | RET | 352 | 101 | 11 | 0.500 | 0.515 | 0.519 (0.345 to 0.688) | 0.524 (0.349 to 0.703) | 0.140 vs 0.109 | 0.474 | weak |
| erdafitinib | BRD-K84868168 | FGFR1, FGFR2, FGFR3, FGFR4 | FGFR1 | 343 | 95 | 21 | 0.500 | 0.585 | 0.694 (0.574 to 0.804) | 0.703 (0.598 to 0.815) | 0.341 vs 0.221 | 0.589 |  |

**Which model ships:** the pre-registered switch rule, re-applied for the record, gives the random forest the higher held-out ROC-AUC on 40 of 86 drugs that are not underpowered (it needs more than half), so the rule alone would ship the logistic regression. **By the 2026-11-04 amendment, logistic regression ships for every drug**: the first run's random-forest win (32 of 60) was a tie-sized margin, and the hosted app's size matters (the first run's 60 random forests took 73,143,794 bytes). Random-forest results stay in every table. Underpowered drugs: 0 of 86.

## What this says

Over the 86 drugs that are not underpowered: median held-out ROC-AUC 0.545 (logistic), 0.540 (random forest), 0.518 (1-NN). Logistic regression beats 1-NN on 55 drugs; the random forest beats 1-NN on 54. 65 of 86 shipped models are weak (CI reaches 0.5) and 33 are below 0.5; the highest is 0.860 (selumetinib). Hotspot mutations alone explain little of how a cell line responds to most of these drugs; the models are a weak signal next to the measured responses of the nearest cell lines, not a prediction for a person.

## What changed from the first run

Before = commit 5b7d361 (60 drugs: the 60 oncology-list matches with the most lines; random forest shipped by the switch rule). After = this run (up to 3 per oncology gene; logistic regression ships by amendment). Same split, seed and model parameters. Medians and beat-1-NN are over drugs that are not underpowered; weak counts all drugs.

| | Before | After |
|---|---|---|
| Drugs | 60 | 86 |
| Underpowered | 0 | 0 |
| Median ROC-AUC, majority | 0.500 | 0.500 |
| Median ROC-AUC, 1-NN | 0.507 | 0.518 |
| Median ROC-AUC, logistic regression | 0.549 | 0.545 |
| Median ROC-AUC, random forest | 0.562 | 0.540 |
| Beats 1-NN, logistic regression | 40 | 55 |
| Beats 1-NN, random forest | 40 | 54 |
| Weak, logistic regression | 51 | 65 |
| Weak, random forest | 53 | 73 |
| Switch rule: RF wins | 32 of 60 | 40 of 86 |
| Shipped | random forest | logistic regression (amendment) |

Models: `models/loop2/<broad_id>.joblib` (git-ignored), logistic regression fit on the training lines, 675,367 bytes in total.
