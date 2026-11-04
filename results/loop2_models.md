# Loop 2 per-drug sensitivity models: held-out results

Built by `python -m molscreen.drugs`; every number is in `results/loop2_models.json`. Protocol:
`docs/evaluation-loop2.md` ("Per-drug models" and its dated Changes). **Cell lines, not patients.**
Research and learning tool, not medical advice. Features: the 0/1 hotspot vector (542 genes). Label: sensitive
when `auc` is below the 10th percentile of the drug's `auc` over its training lines.

**How the app uses this.** The nearest cell lines and their measured sensitivities are the main evidence in loop 2; model ranks are shown second and greyed when `weak` (95% CI lower bound <= 0.5); the probabilities are not calibrated and must be shown as ranks, never as percentages.

## Drug set

1,173 compounds name a gene in `target` and have >= 300 lines in the hotspot matrix. Two rules pick from them (each compound counts once). **3 per gene:** compounds are taken most screened first (ties by Broad ID); each goes to the oncology-list gene its `target` names that has the fewest compounds so far (ties by list order), while that gene has fewer than 3. 30 of the 95 compounds picked this way went to a gene other than the first one they name in list order (the FIX round 1 assignment). **Selective:** every other candidate whose `target` names exactly one gene, on the oncology list: 107 added. 32 genes have at least one compound, giving **202 compounds**. The "Gene" column is the gene and rule a compound was picked under.

Selective drugs added: gefitinib (EGFR, 679 lines), icotinib (EGFR, 678 lines), EGF816 (EGFR, 625 lines), tyrphostin-AG-99 (EGFR, 471 lines), BIBU-1361 (EGFR, 460 lines), OSI-420 (EGFR, 455 lines), WZ8040 (EGFR, 455 lines), CGP-52411 (EGFR, 449 lines), WZ-3146 (EGFR, 444 lines), CNX-2006 (EGFR, 433 lines), tyrphostin-AG-494 (EGFR, 403 lines), RAF265 (BRAF, 461 lines), TAK-632 (BRAF, 446 lines), LGX818 (BRAF, 434 lines), SB-590885 (BRAF, 430 lines), GDC-0879 (BRAF, 402 lines), CP-724714 (ERBB2, 681 lines), ARRY-334543 (ERBB2, 677 lines), tucatinib (ERBB2, 662 lines), TAK-285 (ERBB2, 460 lines), FERb-033 (ERBB2, 410 lines), CEP-37440 (ALK, 457 lines), lorlatinib (ALK, 431 lines), S-111 (PARP1, 459 lines), AG-14361 (PARP1, 413 lines), iniparib (PARP1, 377 lines), obatoclax (BCL2, 684 lines), venetoclax (BCL2, 646 lines), gossypol (BCL2, 462 lines), oridonin (BCL2, 443 lines), HA14-1 (BCL2, 442 lines), Ro-4987655 (MAP2K1, 465 lines), TAK-733 (MAP2K1, 463 lines), PD-318088 (MAP2K1, 462 lines), PD-0325901 (MAP2K1, 462 lines), nobiletin (MAP2K1, 453 lines), MEK1-2-inhibitor (MAP2K2, 435 lines), temsirolimus (MTOR, 687 lines), ku-0063794 (MTOR, 475 lines), OSI-027 (MTOR, 475 lines), WAY-600 (MTOR, 473 lines), WYE-354 (MTOR, 471 lines), deforolimus (MTOR, 470 lines), LY3023414 (MTOR, 469 lines), torin-1 (MTOR, 468 lines), PKI-179 (MTOR, 467 lines), torin-2 (MTOR, 462 lines), WYE-125132 (MTOR, 461 lines), AZD8055 (MTOR, 453 lines), XL388 (MTOR, 444 lines), palomid-529 (MTOR, 421 lines), GDC-0349 (PIK3CA, 468 lines), taselisib (PIK3CA, 466 lines), tyrphostin-AG-1296 (FLT3, 458 lines), gilteritinib (FLT3, 437 lines), CNX-774 (BTK, 449 lines), AZ960 (JAK2, 458 lines), thiram (JAK2, 421 lines), CEP-33779 (JAK2, 391 lines), aurora-a-inhibitor-i (AURKA, 457 lines), MK-8745 (AURKA, 444 lines), MLN-8054 (AURKA, 368 lines), barasertib-HQPA (AURKB, 448 lines), hesperadin (AURKB, 366 lines), GSK461364 (PLK1, 467 lines), genz-644282 (TOP1, 469 lines), beta-lapachone (TOP1, 468 lines), 10-hydroxycamptothecin (TOP1, 462 lines), TAS-103 (TOP1, 446 lines), camptothecin (TOP1, 366 lines), SN-38 (TOP1, 320 lines), doxorubicin (TOP2A, 464 lines), valrubicin (TOP2A, 462 lines), norfloxacin (TOP2A, 456 lines), voreloxin (TOP2A, 453 lines), etoposide-phosphate (TOP2A, 452 lines), sparfloxacin (TOP2A, 444 lines), trovafloxacin (TOP2A, 433 lines), mitoxantrone (TOP2A, 421 lines), idarubicin (TOP2A, 421 lines), verubulin (TUBB, 469 lines), CYT-997 (TUBB, 468 lines), parbendazole (TUBB, 463 lines), ABT-751 (TUBB, 463 lines), dolastatin-10 (TUBB, 459 lines), fenbendazole (TUBB, 421 lines), D-64131 (TUBB, 418 lines), tacedinaline (HDAC1, 647 lines), AR-42 (HDAC1, 467 lines), parthenolide-(-) (HDAC1, 456 lines), NSC-3852 (HDAC1, 441 lines), pyroxamide (HDAC1, 434 lines), AMG-232 (MDM2, 438 lines), CGM097 (MDM2, 425 lines), serdemetan (MDM2, 307 lines), fruquintinib (KDR, 482 lines), SU014813 (KDR, 457 lines), KI-8751 (KDR, 456 lines), telatinib (KDR, 453 lines), INC-280 (MET, 611 lines), savolitinib (MET, 582 lines), AMG-337 (MET, 517 lines), AMG458 (MET, 453 lines), NVP-BVU972 (MET, 450 lines), PHA-665752 (MET, 443 lines), PF-04217903 (MET, 439 lines), AMG-208 (MET, 427 lines).

## Split (leave-lineage-out, one split for every drug)

726 cell lines in 24 lineages. Train: 580 lines in 14 lineages. Test: 146 lines in 10 lineages (Bone 26, Bladder/Urinary Tract 24, Kidney 24, Soft Tissue 23, Liver 21, Pleura 10, Thyroid 9, Biliary Tract 6, Ampulla of Vater 2, Fibroblast 1).

## Results

ROC-AUC with its 95% CI: bootstrap over the test lines (1000 resamples, seed 0). PR-AUC (sensitive class, next to its test prevalence = a random ranking's PR-AUC) and balanced accuracy at 0.5 are for the shipped model (logistic regression). "Weak": the shipped model's CI lower bound is <= 0.5. "Underpowered": fewer than 5 sensitive test lines.

| Drug | Broad ID | Target | Gene | n train | n test | Sensitive in test | Majority | 1-NN | Logistic (95% CI) | RF (95% CI) | PR-AUC vs prevalence | Bal. acc. | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| osimertinib | BRD-K42805893 | EGFR | EGFR (3 per gene) | 573 | 141 | 10 | 0.500 | 0.463 | 0.479 (0.339 to 0.639) | 0.498 (0.363 to 0.639) | 0.068 vs 0.071 | 0.460 | weak |
| pelitinib | BRD-K08799216 | EGFR | EGFR (3 per gene) | 563 | 144 | 13 | 0.500 | 0.506 | 0.526 (0.403 to 0.651) | 0.505 (0.363 to 0.663) | 0.094 vs 0.090 | 0.537 | weak |
| rociletinib | BRD-K33610132 | EGFR | EGFR (3 per gene) | 560 | 143 | 11 | 0.500 | 0.580 | 0.571 (0.408 to 0.727) | 0.599 (0.438 to 0.745) | 0.105 vs 0.077 | 0.598 | weak |
| gefitinib | BRD-K64052750 | EGFR | EGFR (selective) | 537 | 142 | 22 | 0.500 | 0.503 | 0.552 (0.437 to 0.669) | 0.486 (0.374 to 0.604) | 0.219 vs 0.155 | 0.576 | weak |
| icotinib | BRD-K31698212 | EGFR | EGFR (selective) | 543 | 135 | 17 | 0.500 | 0.443 | 0.562 (0.439 to 0.690) | 0.563 (0.422 to 0.694) | 0.147 vs 0.126 | 0.514 | weak |
| EGF816 | BRD-K22514639 | EGFR | EGFR (selective) | 496 | 129 | 17 | 0.500 | 0.434 | 0.640 (0.516 to 0.770) | 0.536 (0.398 to 0.665) | 0.225 vs 0.132 | 0.615 |  |
| tyrphostin-AG-99 | BRD-K60184833 | EGFR | EGFR (selective) | 367 | 104 | 15 | 0.500 | 0.537 | 0.580 (0.410 to 0.723) | 0.558 (0.409 to 0.702) | 0.178 vs 0.144 | 0.547 | weak |
| BIBU-1361 | BRD-K49294207 | EGFR | EGFR (selective) | 363 | 97 | 10 | 0.500 | 0.549 | 0.482 (0.277 to 0.663) | 0.514 (0.299 to 0.694) | 0.111 vs 0.103 | 0.434 | weak |
| OSI-420 | BRD-K73309154 | EGFR | EGFR (selective) | 358 | 97 | 16 | 0.500 | 0.498 | 0.546 (0.375 to 0.704) | 0.516 (0.357 to 0.669) | 0.194 vs 0.165 | 0.553 | weak |
| WZ8040 | BRD-K81728688 | EGFR | EGFR (selective) | 358 | 97 | 13 | 0.500 | 0.357 | 0.443 (0.284 to 0.618) | 0.428 (0.246 to 0.602) | 0.126 vs 0.134 | 0.451 | weak |
| CGP-52411 | BRD-K13087974 | EGFR | EGFR (selective) | 351 | 98 | 14 | 0.500 | 0.591 | 0.548 (0.379 to 0.740) | 0.515 (0.332 to 0.722) | 0.199 vs 0.143 | 0.560 | weak |
| WZ-3146 | BRD-K73293050 | EGFR | EGFR (selective) | 345 | 99 | 13 | 0.500 | 0.433 | 0.401 (0.225 to 0.593) | 0.376 (0.221 to 0.551) | 0.121 vs 0.131 | 0.392 | weak |
| CNX-2006 | BRD-K24869513 | EGFR | EGFR (selective) | 339 | 94 | 14 | 0.500 | 0.416 | 0.482 (0.273 to 0.674) | 0.635 (0.476 to 0.765) | 0.175 vs 0.149 | 0.508 | weak |
| tyrphostin-AG-494 | BRD-K34533029 | EGFR | EGFR (selective) | 313 | 90 | 10 | 0.500 | 0.572 | 0.417 (0.225 to 0.635) | 0.536 (0.364 to 0.730) | 0.200 vs 0.111 | 0.488 | weak |
| sorafenib | BRD-K23984367 | BRAF, DDR2, FGFR1, FLT1, FLT3, FLT4, KDR, KIT, PDGFRB, RAF1, RET | BRAF (3 per gene) | 563 | 142 | 18 | 0.500 | 0.500 | 0.537 (0.415 to 0.651) | 0.596 (0.451 to 0.735) | 0.141 vs 0.127 | 0.478 | weak |
| AZ-628 | BRD-K05804044 | BRAF, RAF1 | BRAF (3 per gene) | 545 | 131 | 12 | 0.500 | 0.483 | 0.744 (0.611 to 0.859) | 0.600 (0.414 to 0.775) | 0.214 vs 0.092 | 0.633 |  |
| dabrafenib | BRD-K09951645 | BRAF, LIMK1, NEK11, RAF1, SIK1 | BRAF (3 per gene) | 506 | 133 | 5 | 0.500 | 0.527 | 0.580 (0.206 to 0.996) | 0.762 (0.483 to 0.958) | 0.357 vs 0.038 | 0.677 | weak |
| RAF265 | BRD-K93123848 | BRAF | BRAF (selective) | 360 | 101 | 14 | 0.500 | 0.554 | 0.655 (0.519 to 0.787) | 0.699 (0.580 to 0.818) | 0.267 vs 0.139 | 0.504 |  |
| TAK-632 | BRD-K31866293 | BRAF | BRAF (selective) | 347 | 99 | 11 | 0.500 | 0.615 | 0.554 (0.350 to 0.749) | 0.546 (0.346 to 0.741) | 0.284 vs 0.111 | 0.545 | weak |
| LGX818 | BRD-A56085258 | BRAF | BRAF (selective) | 342 | 92 | 6 | 0.500 | 0.767 | 0.831 (0.516 to 1.000) | 0.730 (0.377 to 0.993) | 0.716 vs 0.065 | 0.816 |  |
| SB-590885 | BRD-K78809024 | BRAF | BRAF (selective) | 340 | 90 | 7 | 0.500 | 0.379 | 0.526 (0.282 to 0.751) | 0.600 (0.377 to 0.818) | 0.094 vs 0.078 | 0.511 | weak |
| GDC-0879 | BRD-K67578145 | BRAF | BRAF (selective) | 314 | 88 | 3 | 0.500 | 0.553 | 0.422 (0.081 to 1.000) | 0.645 (0.430 to 0.874) | 0.355 vs 0.034 | 0.631 | weak; underpowered (3) |
| canertinib | BRD-K50168500 | AKT1, EGFR, ERBB2, ERBB4 | ERBB2 (3 per gene) | 566 | 141 | 7 | 0.500 | 0.401 | 0.469 (0.289 to 0.655) | 0.516 (0.349 to 0.688) | 0.047 vs 0.050 | 0.480 | weak |
| poziotinib | BRD-K50010139 | EGFR, ERBB2, ERBB4 | ERBB2 (3 per gene) | 565 | 141 | 13 | 0.500 | 0.400 | 0.358 (0.255 to 0.473) | 0.545 (0.363 to 0.723) | 0.073 vs 0.092 | 0.360 | weak |
| dacomitinib | BRD-K57169635 | EGFR, ERBB2, ERBB4 | ERBB2 (3 per gene) | 554 | 143 | 14 | 0.500 | 0.404 | 0.410 (0.256 to 0.586) | 0.489 (0.339 to 0.645) | 0.088 vs 0.098 | 0.436 | weak |
| CP-724714 | BRD-K76908866 | ERBB2 | ERBB2 (selective) | 543 | 138 | 14 | 0.500 | 0.537 | 0.685 (0.510 to 0.836) | 0.486 (0.296 to 0.676) | 0.187 vs 0.101 | 0.626 |  |
| ARRY-334543 | BRD-K46386702 | ERBB2 | ERBB2 (selective) | 542 | 135 | 17 | 0.500 | 0.340 | 0.377 (0.229 to 0.521) | 0.370 (0.242 to 0.510) | 0.100 vs 0.126 | 0.393 | weak |
| tucatinib | BRD-K26026438 | ERBB2 | ERBB2 (selective) | 524 | 138 | 9 | 0.500 | 0.396 | 0.463 (0.261 to 0.669) | 0.514 (0.299 to 0.739) | 0.067 vs 0.065 | 0.479 | weak |
| TAK-285 | BRD-K80343549 | ERBB2 | ERBB2 (selective) | 360 | 100 | 10 | 0.500 | 0.593 | 0.595 (0.421 to 0.742) | 0.690 (0.500 to 0.848) | 0.132 vs 0.100 | 0.589 | weak |
| FERb-033 | BRD-K61642990 | ERBB2 | ERBB2 (selective) | 324 | 86 | 12 | 0.500 | 0.482 | 0.661 (0.519 to 0.802) | 0.618 (0.441 to 0.769) | 0.218 vs 0.140 | 0.573 |  |
| abemaciclib | BRD-K33622447 | CDK4, CDK6 | CDK4 (3 per gene) | 565 | 142 | 22 | 0.500 | 0.565 | 0.624 (0.513 to 0.723) | 0.644 (0.546 to 0.735) | 0.219 vs 0.155 | 0.639 |  |
| P276-00 | BRD-K51791723 | CDK1, CDK4, CDK9 | CDK4 (3 per gene) | 555 | 142 | 20 | 0.500 | 0.520 | 0.643 (0.503 to 0.755) | 0.653 (0.497 to 0.778) | 0.208 vs 0.141 | 0.620 |  |
| PHA-848125 | BRD-K60997853 | CDK2, CDK4, CDK7, NTRK1 | CDK4 (3 per gene) | 540 | 143 | 17 | 0.500 | 0.617 | 0.550 (0.436 to 0.674) | 0.699 (0.583 to 0.803) | 0.142 vs 0.119 | 0.564 | weak |
| palbociclib | BRD-K51313569 | CDK4, CDK6 | CDK6 (3 per gene) | 560 | 142 | 22 | 0.500 | 0.528 | 0.590 (0.460 to 0.718) | 0.562 (0.435 to 0.678) | 0.211 vs 0.155 | 0.556 | weak |
| AT-7519 | BRD-K13390322 | CDK1, CDK2, CDK4, CDK5, CDK6, CDK9 | CDK6 (3 per gene) | 548 | 140 | 11 | 0.500 | 0.533 | 0.498 (0.341 to 0.642) | 0.555 (0.404 to 0.723) | 0.087 vs 0.079 | 0.588 | weak |
| ribociclib | BRD-K36788280 | CDK4, CDK6 | CDK6 (3 per gene) | 535 | 138 | 13 | 0.500 | 0.765 | 0.744 (0.637 to 0.831) | 0.740 (0.635 to 0.822) | 0.191 vs 0.094 | 0.697 |  |
| brigatinib | BRD-K56981171 | ALK, EGFR | ALK (3 per gene) | 564 | 142 | 15 | 0.500 | 0.649 | 0.548 (0.406 to 0.685) | 0.605 (0.487 to 0.718) | 0.121 vs 0.106 | 0.513 | weak |
| crizotinib | BRD-K78431006 | ALK, MET | ALK (3 per gene) | 531 | 141 | 13 | 0.500 | 0.511 | 0.480 (0.296 to 0.683) | 0.447 (0.281 to 0.636) | 0.130 vs 0.092 | 0.508 | weak |
| alectinib | BRD-K11267252 | ALK, MET | ALK (3 per gene) | 535 | 132 | 9 | 0.500 | 0.564 | 0.429 (0.227 to 0.625) | 0.589 (0.384 to 0.796) | 0.061 vs 0.068 | 0.489 | weak |
| CEP-37440 | BRD-K72827473 | ALK | ALK (selective) | 357 | 100 | 16 | 0.500 | 0.423 | 0.446 (0.292 to 0.620) | 0.400 (0.254 to 0.560) | 0.200 vs 0.160 | 0.473 | weak |
| lorlatinib | BRD-K99879819 | ALK | ALK (selective) | 339 | 92 | 9 | 0.500 | 0.633 | 0.424 (0.202 to 0.635) | 0.456 (0.213 to 0.691) | 0.090 vs 0.098 | 0.398 | weak |
| ponatinib | BRD-K44227013 | ABL1, BCR, FGFR1, FGFR2, FGFR3, FGFR4, FLT3, KDR, KIT, LCK, LYN, PDGFRA, RET, SRC, TEK | ABL1 (3 per gene) | 568 | 142 | 12 | 0.500 | 0.602 | 0.614 (0.482 to 0.735) | 0.636 (0.513 to 0.748) | 0.124 vs 0.085 | 0.622 | weak |
| saracatinib | BRD-K19540840 | ABL1, LCK, SRC, YES1 | ABL1 (3 per gene) | 546 | 143 | 17 | 0.500 | 0.556 | 0.410 (0.265 to 0.569) | 0.435 (0.259 to 0.606) | 0.105 vs 0.119 | 0.412 | weak |
| dasatinib | BRD-K49328571 | ABL1, ABL2, BLK, EPHA2, FGR, FRK, FYN, HCK, KIT, LCK, LYN, PDGFRB, SRC, SRMS, STAT5B, YES1 | ABL1 (3 per gene) | 534 | 139 | 28 | 0.500 | 0.477 | 0.471 (0.358 to 0.579) | 0.531 (0.414 to 0.651) | 0.186 vs 0.201 | 0.477 | weak |
| niraparib | BRD-K54955827 | PARP1 | PARP1 (3 per gene) | 540 | 140 | 16 | 0.500 | 0.737 | 0.665 (0.561 to 0.753) | 0.682 (0.569 to 0.781) | 0.165 vs 0.114 | 0.596 |  |
| olaparib | BRD-K02113016 | PARP1, PARP2 | PARP1 (3 per gene) | 543 | 136 | 16 | 0.500 | 0.499 | 0.746 (0.654 to 0.828) | 0.627 (0.528 to 0.721) | 0.228 vs 0.118 | 0.615 |  |
| 3-amino-benzamide | BRD-K08703257 | PARP1 | PARP1 (3 per gene) | 464 | 125 | 20 | 0.500 | 0.375 | 0.489 (0.341 to 0.640) | 0.390 (0.241 to 0.543) | 0.163 vs 0.160 | 0.471 | weak |
| S-111 | BRD-K60005752 | PARP1 | PARP1 (selective) | 358 | 101 | 13 | 0.500 | 0.575 | 0.680 (0.504 to 0.850) | 0.618 (0.475 to 0.748) | 0.387 vs 0.129 | 0.640 |  |
| AG-14361 | BRD-K00615600 | PARP1 | PARP1 (selective) | 323 | 90 | 13 | 0.500 | 0.382 | 0.771 (0.654 to 0.870) | 0.768 (0.636 to 0.877) | 0.286 vs 0.144 | 0.696 |  |
| iniparib | BRD-K11153516 | PARP1 | PARP1 (selective) | 304 | 73 | 3 | 0.500 | 0.457 | 0.481 (0.000 to 0.903) | 0.552 (0.181 to 0.889) | 0.049 vs 0.041 | 0.486 | weak; underpowered (3) |
| navitoclax | BRD-K82746043 | BCL2, BCL2L1, BCL2L2 | BCL2 (3 per gene) | 556 | 146 | 12 | 0.500 | 0.443 | 0.474 (0.304 to 0.626) | 0.463 (0.309 to 0.617) | 0.083 vs 0.082 | 0.466 | weak |
| gambogic-acid | BRD-K08542803 | BCL2 | BCL2 (3 per gene) | 554 | 143 | 10 | 0.500 | 0.626 | 0.697 (0.556 to 0.810) | 0.540 (0.390 to 0.665) | 0.120 vs 0.070 | 0.701 |  |
| docetaxel | BRD-K30577245 | BCL2, MAP2, MAP4, MAPT, NR1I2, TUBB, TUBB1 | BCL2 (3 per gene) | 550 | 141 | 16 | 0.500 | 0.436 | 0.606 (0.461 to 0.746) | 0.578 (0.426 to 0.739) | 0.148 vs 0.113 | 0.606 | weak |
| obatoclax | BRD-K15600710 | BCL2 | BCL2 (selective) | 543 | 141 | 8 | 0.500 | 0.488 | 0.598 (0.481 to 0.709) | 0.621 (0.498 to 0.741) | 0.073 vs 0.057 | 0.517 | weak |
| venetoclax | BRD-K62391742 | BCL2 | BCL2 (selective) | 513 | 133 | 7 | 0.500 | 0.698 | 0.637 (0.407 to 0.802) | 0.618 (0.458 to 0.742) | 0.085 vs 0.053 | 0.607 | weak |
| gossypol | BRD-K19295594 | BCL2 | BCL2 (selective) | 360 | 102 | 16 | 0.500 | 0.446 | 0.511 (0.363 to 0.647) | 0.423 (0.300 to 0.546) | 0.160 vs 0.157 | 0.453 | weak |
| oridonin | BRD-K23925186 | BCL2 | BCL2 (selective) | 350 | 93 | 16 | 0.500 | 0.353 | 0.700 (0.558 to 0.819) | 0.649 (0.514 to 0.781) | 0.293 vs 0.172 | 0.590 |  |
| HA14-1 | BRD-K18163608 | BCL2 | BCL2 (selective) | 345 | 97 | 11 | 0.500 | 0.594 | 0.483 (0.321 to 0.617) | 0.501 (0.341 to 0.651) | 0.126 vs 0.113 | 0.384 | weak |
| trametinib | BRD-K12343256 | MAP2K1, MAP2K2 | MAP2K1 (3 per gene) | 569 | 140 | 6 | 0.500 | 0.606 | 0.757 (0.587 to 0.934) | 0.738 (0.620 to 0.872) | 0.135 vs 0.043 | 0.618 |  |
| selumetinib | BRD-K57080016 | MAP2K1 | MAP2K1 (3 per gene) | 549 | 137 | 6 | 0.500 | 0.467 | 0.860 (0.710 to 0.966) | 0.622 (0.324 to 0.897) | 0.225 vs 0.044 | 0.780 |  |
| U-0126 | BRD-K18787491 | AKT1, CHEK1, GSK3B, LCK, MAP2K1, MAP2K2, MAP2K7, MAPK1, MAPK11, MAPK12, MAPK14, MAPK8, PRKCA, RAF1, ROCK1, RPS6KB1, SGK1 | MAP2K1 (3 per gene) | 365 | 102 | 20 | 0.500 | 0.433 | 0.526 (0.398 to 0.653) | 0.396 (0.294 to 0.516) | 0.208 vs 0.196 | 0.440 | weak |
| Ro-4987655 | BRD-K64538373 | MAP2K1 | MAP2K1 (selective) | 364 | 101 | 7 | 0.500 | 0.584 | 0.644 (0.394 to 0.843) | 0.600 (0.324 to 0.858) | 0.115 vs 0.069 | 0.579 | weak |
| TAK-733 | BRD-K26667523 | MAP2K1 | MAP2K1 (selective) | 361 | 102 | 6 | 0.500 | 0.618 | 0.761 (0.488 to 0.946) | 0.758 (0.430 to 0.967) | 0.184 vs 0.059 | 0.771 | weak |
| PD-318088 | BRD-A57798112 | MAP2K1 | MAP2K1 (selective) | 364 | 98 | 10 | 0.500 | 0.510 | 0.722 (0.520 to 0.892) | 0.651 (0.468 to 0.820) | 0.252 vs 0.102 | 0.643 |  |
| PD-0325901 | BRD-K49865102 | MAP2K1 | MAP2K1 (selective) | 363 | 99 | 4 | 0.500 | 0.672 | 0.830 (0.624 to 0.946) | 0.883 (0.714 to 0.984) | 0.145 vs 0.040 | 0.578 | underpowered (4) |
| nobiletin | BRD-K06753942 | MAP2K1 | MAP2K1 (selective) | 356 | 97 | 10 | 0.500 | 0.480 | 0.691 (0.487 to 0.861) | 0.628 (0.427 to 0.830) | 0.288 vs 0.103 | 0.637 | weak |
| AS-703026 | BRD-K89014967 | MAP2K1, MAP2K2 | MAP2K2 (3 per gene) | 541 | 142 | 9 | 0.500 | 0.623 | 0.650 (0.417 to 0.841) | 0.589 (0.354 to 0.798) | 0.152 vs 0.063 | 0.577 | weak |
| PD-198306 | BRD-K88677950 | MAP2K1, MAP2K2 | MAP2K2 (3 per gene) | 367 | 104 | 14 | 0.500 | 0.494 | 0.629 (0.482 to 0.783) | 0.512 (0.345 to 0.663) | 0.203 vs 0.135 | 0.521 | weak |
| U-0126 | BRD-K91701654 | AKT1, CHEK1, GSK3B, LCK, MAP2K1, MAP2K2, MAP2K7, MAPK1, MAPK11, MAPK12, MAPK14, MAPK8, PRKCA, RAF1, ROCK1, RPS6KB1, SGK1 | MAP2K2 (3 per gene) | 359 | 98 | 10 | 0.500 | 0.662 | 0.567 (0.414 to 0.717) | 0.599 (0.436 to 0.753) | 0.127 vs 0.102 | 0.455 | weak |
| MEK1-2-inhibitor | BRD-K12244279 | MAP2K2 | MAP2K2 (selective) | 339 | 96 | 13 | 0.500 | 0.582 | 0.513 (0.352 to 0.689) | 0.427 (0.286 to 0.584) | 0.158 vs 0.135 | 0.446 | weak |
| AZD2014 | BRD-K99113996 | MTOR | MTOR (3 per gene) | 574 | 144 | 9 | 0.500 | 0.530 | 0.522 (0.340 to 0.700) | 0.525 (0.341 to 0.698) | 0.071 vs 0.062 | 0.478 | weak |
| everolimus | BRD-K13514097 | MTOR | MTOR (3 per gene) | 567 | 142 | 14 | 0.500 | 0.491 | 0.489 (0.335 to 0.635) | 0.416 (0.277 to 0.564) | 0.111 vs 0.099 | 0.465 | weak |
| MLN0128 | BRD-K59317601 | MTOR, PIK3CA, PIK3CD, PIK3CG | MTOR (3 per gene) | 548 | 141 | 12 | 0.500 | 0.441 | 0.431 (0.298 to 0.573) | 0.499 (0.374 to 0.624) | 0.080 vs 0.085 | 0.450 | weak |
| temsirolimus | BRD-K42898655 | MTOR | MTOR (selective) | 547 | 140 | 13 | 0.500 | 0.582 | 0.554 (0.356 to 0.748) | 0.469 (0.299 to 0.653) | 0.151 vs 0.093 | 0.590 | weak |
| ku-0063794 | BRD-K67566344 | MTOR | MTOR (selective) | 370 | 105 | 13 | 0.500 | 0.409 | 0.374 (0.253 to 0.504) | 0.356 (0.218 to 0.502) | 0.114 vs 0.124 | 0.424 | weak |
| OSI-027 | BRD-K87124298 | MTOR | MTOR (selective) | 371 | 104 | 15 | 0.500 | 0.480 | 0.483 (0.344 to 0.614) | 0.592 (0.443 to 0.744) | 0.142 vs 0.144 | 0.455 | weak |
| WAY-600 | BRD-K85920262 | MTOR | MTOR (selective) | 369 | 104 | 18 | 0.500 | 0.375 | 0.443 (0.302 to 0.569) | 0.513 (0.373 to 0.656) | 0.205 vs 0.173 | 0.458 | weak |
| WYE-354 | BRD-K77008974 | MTOR | MTOR (selective) | 367 | 104 | 9 | 0.500 | 0.478 | 0.558 (0.318 to 0.760) | 0.549 (0.381 to 0.708) | 0.111 vs 0.087 | 0.588 | weak |
| deforolimus | BRD-K62304154 | MTOR | MTOR (selective) | 367 | 103 | 17 | 0.500 | 0.399 | 0.546 (0.399 to 0.688) | 0.662 (0.522 to 0.794) | 0.186 vs 0.165 | 0.508 | weak |
| LY3023414 | BRD-K82967180 | MTOR | MTOR (selective) | 367 | 102 | 10 | 0.500 | 0.607 | 0.688 (0.456 to 0.908) | 0.569 (0.333 to 0.803) | 0.234 vs 0.098 | 0.708 | weak |
| torin-1 | BRD-K40175214 | MTOR | MTOR (selective) | 364 | 104 | 24 | 0.500 | 0.387 | 0.556 (0.439 to 0.678) | 0.544 (0.428 to 0.660) | 0.286 vs 0.231 | 0.508 | weak |
| PKI-179 | BRD-A28467416 | MTOR | MTOR (selective) | 364 | 103 | 9 | 0.500 | 0.312 | 0.563 (0.385 to 0.763) | 0.443 (0.230 to 0.690) | 0.125 vs 0.087 | 0.568 | weak |
| torin-2 | BRD-K68174511 | MTOR | MTOR (selective) | 359 | 103 | 11 | 0.500 | 0.488 | 0.645 (0.468 to 0.811) | 0.659 (0.474 to 0.841) | 0.187 vs 0.107 | 0.608 | weak |
| WYE-125132 | BRD-A45498368 | MTOR | MTOR (selective) | 359 | 102 | 13 | 0.500 | 0.414 | 0.500 (0.361 to 0.627) | 0.448 (0.287 to 0.591) | 0.138 vs 0.127 | 0.449 | weak |
| AZD8055 | BRD-K69932463 | MTOR | MTOR (selective) | 353 | 100 | 13 | 0.500 | 0.492 | 0.604 (0.460 to 0.748) | 0.549 (0.417 to 0.691) | 0.158 vs 0.130 | 0.560 | weak |
| XL388 | BRD-K03549949 | MTOR | MTOR (selective) | 345 | 99 | 12 | 0.500 | 0.554 | 0.363 (0.225 to 0.506) | 0.443 (0.285 to 0.598) | 0.102 vs 0.121 | 0.411 | weak |
| palomid-529 | BRD-A50998626 | MTOR | MTOR (selective) | 328 | 93 | 14 | 0.500 | 0.551 | 0.495 (0.340 to 0.661) | 0.519 (0.327 to 0.690) | 0.170 vs 0.151 | 0.470 | weak |
| GDC-0980 | BRD-K23228615 | FGR, MAP3K9, MTOR, PIK3CA, PIK3CB, PIK3CD, PIK3CG, SYK | PIK3CA (3 per gene) | 556 | 142 | 12 | 0.500 | 0.308 | 0.636 (0.413 to 0.815) | 0.532 (0.293 to 0.768) | 0.225 vs 0.085 | 0.601 | weak |
| NVP-BEZ235 | BRD-K12184916 | ATR, MTOR, PIK3CA, PIK3CD, PIK3CG | PIK3CA (3 per gene) | 549 | 142 | 15 | 0.500 | 0.456 | 0.602 (0.447 to 0.766) | 0.524 (0.367 to 0.667) | 0.229 vs 0.106 | 0.598 | weak |
| alpelisib | BRD-K54997624 | PIK3CA, PIK3CB, PIK3CD, PIK3CG | PIK3CA (3 per gene) | 550 | 137 | 13 | 0.500 | 0.461 | 0.521 (0.389 to 0.651) | 0.456 (0.311 to 0.615) | 0.097 vs 0.095 | 0.414 | weak |
| GDC-0349 | BRD-K43187018 | PIK3CA | PIK3CA (selective) | 367 | 101 | 16 | 0.500 | 0.410 | 0.425 (0.274 to 0.584) | 0.479 (0.324 to 0.633) | 0.143 vs 0.158 | 0.467 | weak |
| taselisib | BRD-K44844162 | PIK3CA | PIK3CA (selective) | 366 | 100 | 9 | 0.500 | 0.201 | 0.620 (0.406 to 0.843) | 0.455 (0.273 to 0.640) | 0.196 vs 0.090 | 0.623 | weak |
| dovitinib | BRD-K85402309 | CSF1R, EGFR, FGFR1, FGFR2, FGFR3, FLT1, FLT3, FLT4, INSR, KDR, KIT, PDGFRA, PDGFRB | KIT (3 per gene) | 559 | 143 | 23 | 0.500 | 0.516 | 0.593 (0.482 to 0.694) | 0.639 (0.522 to 0.742) | 0.205 vs 0.161 | 0.566 | weak |
| tivozanib | BRD-K53414658 | FLT1, FLT4, KDR, KIT, PDGFRA, PDGFRB | KIT (3 per gene) | 548 | 138 | 12 | 0.500 | 0.599 | 0.792 (0.671 to 0.893) | 0.664 (0.494 to 0.812) | 0.242 vs 0.087 | 0.685 |  |
| semaxanib | BRD-K63504947 | FGFR1, FLT1, KDR, KIT, PDGFRA, PDGFRB, RET | KIT (3 per gene) | 526 | 141 | 15 | 0.500 | 0.444 | 0.652 (0.506 to 0.778) | 0.576 (0.417 to 0.727) | 0.170 vs 0.106 | 0.609 |  |
| BMS-690514 | BRD-K76239644 | EGFR, ERBB2, FLT3, KDR | FLT3 (3 per gene) | 554 | 140 | 14 | 0.500 | 0.345 | 0.380 (0.270 to 0.494) | 0.423 (0.260 to 0.599) | 0.085 vs 0.100 | 0.369 | weak |
| linifanib | BRD-K99749624 | CSF1, CSF1R, FLT1, FLT3, FLT4, KDR, KIT, PDGFRB, RET, TEK | FLT3 (3 per gene) | 481 | 125 | 12 | 0.500 | 0.600 | 0.631 (0.464 to 0.785) | 0.732 (0.546 to 0.884) | 0.177 vs 0.096 | 0.603 | weak |
| pexidartinib | BRD-K54519451 | CSF1R, FLT3, KIT | FLT3 (3 per gene) | 405 | 118 | 19 | 0.500 | 0.610 | 0.631 (0.509 to 0.741) | 0.583 (0.448 to 0.710) | 0.291 vs 0.161 | 0.578 |  |
| tyrphostin-AG-1296 | BRD-K76064317 | FLT3 | FLT3 (selective) | 357 | 101 | 4 | 0.500 | 0.784 | 0.179 (0.000 to 0.361) | 0.432 (0.000 to 0.859) | 0.031 vs 0.040 | 0.384 | weak; underpowered (4) |
| gilteritinib | BRD-K72280606 | FLT3 | FLT3 (selective) | 346 | 91 | 18 | 0.500 | 0.436 | 0.572 (0.432 to 0.699) | 0.496 (0.340 to 0.646) | 0.225 vs 0.198 | 0.566 | weak |
| AVL-292 | BRD-K87782578 | BTK, YES1 | BTK (3 per gene) | 543 | 142 | 14 | 0.500 | 0.366 | 0.546 (0.407 to 0.681) | 0.566 (0.432 to 0.702) | 0.112 vs 0.099 | 0.506 | weak |
| ibrutinib | BRD-K70301465 | BLK, BMX, BTK | BTK (3 per gene) | 545 | 136 | 5 | 0.500 | 0.260 | 0.361 (0.165 to 0.566) | 0.286 (0.044 to 0.521) | 0.031 vs 0.037 | 0.321 | weak |
| acalabrutinib | BRD-K64034691 | BTK | BTK (3 per gene) | 414 | 100 | 11 | 0.500 | 0.392 | 0.387 (0.187 to 0.602) | 0.463 (0.228 to 0.710) | 0.134 vs 0.110 | 0.407 | weak |
| CNX-774 | BRD-K48443249 | BTK | BTK (selective) | 352 | 97 | 11 | 0.500 | 0.561 | 0.597 (0.410 to 0.763) | 0.617 (0.447 to 0.789) | 0.225 vs 0.113 | 0.582 | weak |
| cyt387 | BRD-K87737963 | JAK1, JAK2, JAK3 | JAK1 (3 per gene) | 548 | 138 | 18 | 0.500 | 0.509 | 0.483 (0.349 to 0.613) | 0.418 (0.286 to 0.557) | 0.126 vs 0.130 | 0.436 | weak |
| ruxolitinib | BRD-K53972329 | JAK1, JAK2, JAK3, TYK2 | JAK1 (3 per gene) | 505 | 131 | 9 | 0.500 | 0.568 | 0.547 (0.404 to 0.701) | 0.493 (0.315 to 0.676) | 0.077 vs 0.069 | 0.538 | weak |
| itacitinib | BRD-K67482377 | JAK1 | JAK1 (3 per gene) | 365 | 101 | 14 | 0.500 | 0.474 | 0.546 (0.369 to 0.705) | 0.519 (0.344 to 0.679) | 0.218 vs 0.139 | 0.545 | weak |
| atiprimod | BRD-K38527262 | JAK2, STAT3 | JAK2 (3 per gene) | 563 | 143 | 14 | 0.500 | 0.313 | 0.541 (0.385 to 0.692) | 0.510 (0.351 to 0.665) | 0.120 vs 0.098 | 0.521 | weak |
| TG-02 | BRD-K14560436 | CDK1, CDK2, CDK7, CDK9, FLT3, JAK2 | JAK2 (3 per gene) | 369 | 104 | 11 | 0.500 | 0.432 | 0.469 (0.242 to 0.711) | 0.489 (0.310 to 0.673) | 0.142 vs 0.106 | 0.583 | weak |
| TG-101209 | BRD-K39841531 | JAK2, JAK3 | JAK2 (3 per gene) | 365 | 104 | 14 | 0.500 | 0.552 | 0.409 (0.266 to 0.562) | 0.491 (0.370 to 0.618) | 0.139 vs 0.135 | 0.494 | weak |
| AZ960 | BRD-K64888243 | JAK2 | JAK2 (selective) | 357 | 101 | 10 | 0.500 | 0.642 | 0.613 (0.383 to 0.824) | 0.566 (0.364 to 0.765) | 0.165 vs 0.099 | 0.657 | weak |
| thiram | BRD-K29254801 | JAK2 | JAK2 (selective) | 324 | 97 | 14 | 0.500 | 0.423 | 0.446 (0.302 to 0.587) | 0.543 (0.368 to 0.719) | 0.132 vs 0.144 | 0.431 | weak |
| CEP-33779 | BRD-K37237504 | JAK2 | JAK2 (selective) | 306 | 85 | 12 | 0.500 | 0.620 | 0.433 (0.268 to 0.604) | 0.506 (0.351 to 0.660) | 0.144 vs 0.141 | 0.461 | weak |
| tozasertib | BRD-K59369769 | AURKA, AURKB, AURKC, LCK | AURKA (3 per gene) | 568 | 141 | 25 | 0.500 | 0.503 | 0.604 (0.496 to 0.709) | 0.563 (0.455 to 0.663) | 0.229 vs 0.177 | 0.560 | weak |
| alisertib | BRD-K75295174 | AURKA | AURKA (3 per gene) | 373 | 101 | 9 | 0.500 | 0.450 | 0.472 (0.291 to 0.641) | 0.582 (0.410 to 0.744) | 0.088 vs 0.089 | 0.455 | weak |
| danusertib | BRD-K07881437 | AURKA, AURKB, AURKC, FGFR1, NTRK1, RET, SLK | AURKA (3 per gene) | 366 | 103 | 15 | 0.500 | 0.453 | 0.553 (0.406 to 0.694) | 0.519 (0.364 to 0.665) | 0.176 vs 0.146 | 0.588 | weak |
| aurora-a-inhibitor-i | BRD-K53561341 | AURKA | AURKA (selective) | 360 | 97 | 13 | 0.500 | 0.566 | 0.668 (0.475 to 0.841) | 0.447 (0.259 to 0.637) | 0.314 vs 0.134 | 0.582 | weak |
| MK-8745 | BRD-K25279140 | AURKA | AURKA (selective) | 347 | 97 | 12 | 0.500 | 0.672 | 0.425 (0.303 to 0.540) | 0.428 (0.279 to 0.586) | 0.116 vs 0.124 | 0.371 | weak |
| MLN-8054 | BRD-K83963101 | AURKA | AURKA (selective) | 287 | 81 | 11 | 0.500 | 0.491 | 0.476 (0.278 to 0.679) | 0.512 (0.318 to 0.703) | 0.141 vs 0.136 | 0.496 | weak |
| barasertib | BRD-K31928526 | AURKA, AURKB | AURKB (3 per gene) | 548 | 138 | 17 | 0.500 | 0.531 | 0.583 (0.469 to 0.689) | 0.597 (0.481 to 0.705) | 0.157 vs 0.123 | 0.627 | weak |
| TAK-901 | BRD-K01683783 | AURKB | AURKB (3 per gene) | 371 | 103 | 11 | 0.500 | 0.596 | 0.672 (0.506 to 0.826) | 0.596 (0.396 to 0.799) | 0.205 vs 0.107 | 0.705 |  |
| ZM-447439 | BRD-K72703948 | AURKA, AURKB | AURKB (3 per gene) | 366 | 102 | 17 | 0.500 | 0.612 | 0.528 (0.384 to 0.672) | 0.562 (0.429 to 0.685) | 0.191 vs 0.167 | 0.524 | weak |
| barasertib-HQPA | BRD-K63923597 | AURKB | AURKB (selective) | 350 | 98 | 15 | 0.500 | 0.644 | 0.590 (0.424 to 0.755) | 0.687 (0.517 to 0.850) | 0.243 vs 0.153 | 0.574 | weak |
| hesperadin | BRD-K58122457 | AURKB | AURKB (selective) | 290 | 76 | 13 | 0.500 | 0.621 | 0.582 (0.417 to 0.727) | 0.549 (0.402 to 0.688) | 0.220 vs 0.171 | 0.587 | weak |
| volasertib | BRD-K69776681 | PLK1 | PLK1 (3 per gene) | 561 | 141 | 7 | 0.500 | 0.463 | 0.564 (0.381 to 0.767) | 0.477 (0.275 to 0.683) | 0.060 vs 0.050 | 0.513 | weak |
| rigosertib | BRD-K55187425 | PLK1 | PLK1 (3 per gene) | 533 | 135 | 9 | 0.500 | 0.311 | 0.457 (0.225 to 0.695) | 0.437 (0.207 to 0.670) | 0.073 vs 0.067 | 0.437 | weak |
| HMN-214 | BRD-K70511574 | PLK1 | PLK1 (3 per gene) | 367 | 102 | 11 | 0.500 | 0.585 | 0.488 (0.325 to 0.655) | 0.504 (0.349 to 0.654) | 0.114 vs 0.108 | 0.440 | weak |
| GSK461364 | BRD-K92428232 | PLK1 | PLK1 (selective) | 368 | 99 | 8 | 0.500 | 0.495 | 0.567 (0.333 to 0.783) | 0.600 (0.384 to 0.805) | 0.134 vs 0.081 | 0.583 | weak |
| irinotecan | BRD-K08547377 | TOP1, TOP1MT | TOP1 (3 per gene) | 552 | 141 | 15 | 0.500 | 0.617 | 0.619 (0.508 to 0.719) | 0.613 (0.499 to 0.712) | 0.141 vs 0.106 | 0.539 |  |
| rubitecan | BRD-K79821389 | TOP1 | TOP1 (3 per gene) | 370 | 103 | 16 | 0.500 | 0.373 | 0.544 (0.360 to 0.718) | 0.462 (0.303 to 0.623) | 0.250 vs 0.155 | 0.590 | weak |
| nemorubicin | BRD-K51911221 | TOP1, TOP2A | TOP1 (3 per gene) | 368 | 103 | 12 | 0.500 | 0.499 | 0.477 (0.332 to 0.632) | 0.465 (0.326 to 0.624) | 0.123 vs 0.117 | 0.435 | weak |
| genz-644282 | BRD-K99475619 | TOP1 | TOP1 (selective) | 366 | 103 | 11 | 0.500 | 0.605 | 0.428 (0.280 to 0.591) | 0.487 (0.334 to 0.645) | 0.101 vs 0.107 | 0.450 | weak |
| beta-lapachone | BRD-K28061410 | TOP1 | TOP1 (selective) | 367 | 101 | 8 | 0.500 | 0.591 | 0.360 (0.123 to 0.608) | 0.328 (0.104 to 0.621) | 0.069 vs 0.079 | 0.452 | weak |
| 10-hydroxycamptothecin | BRD-K63784565 | TOP1 | TOP1 (selective) | 359 | 103 | 16 | 0.500 | 0.499 | 0.529 (0.374 to 0.705) | 0.551 (0.395 to 0.718) | 0.261 vs 0.155 | 0.525 | weak |
| TAS-103 | BRD-K09426783 | TOP1 | TOP1 (selective) | 348 | 98 | 10 | 0.500 | 0.753 | 0.514 (0.359 to 0.664) | 0.559 (0.372 to 0.721) | 0.135 vs 0.102 | 0.386 | weak |
| camptothecin | BRD-K37890730 | TOP1 | TOP1 (selective) | 285 | 81 | 7 | 0.500 | 0.455 | 0.637 (0.333 to 0.911) | 0.683 (0.442 to 0.901) | 0.282 vs 0.086 | 0.640 | weak |
| SN-38 | BRD-K89561498 | TOP1 | TOP1 (selective) | 244 | 76 | 14 | 0.500 | 0.634 | 0.566 (0.387 to 0.736) | 0.521 (0.325 to 0.698) | 0.300 vs 0.184 | 0.570 | weak |
| daunorubicin | BRD-K43389675 | TOP2A, TOP2B | TOP2A (3 per gene) | 562 | 142 | 17 | 0.500 | 0.471 | 0.464 (0.329 to 0.597) | 0.572 (0.438 to 0.711) | 0.111 vs 0.120 | 0.485 | weak |
| teniposide | BRD-K10362825 | TOP2A, TOP2B | TOP2A (3 per gene) | 554 | 138 | 17 | 0.500 | 0.533 | 0.462 (0.315 to 0.596) | 0.508 (0.361 to 0.650) | 0.116 vs 0.123 | 0.488 | weak |
| genistein | BRD-K43797669 | CFTR, ESR1, ESR2, ESRRA, ESRRB, ESRRG, NCOA1, NCOA2, PPARG, PTK2B, TOP2A, TRPC5 | TOP2A (3 per gene) | 473 | 120 | 9 | 0.500 | 0.562 | 0.613 (0.496 to 0.729) | 0.661 (0.522 to 0.781) | 0.109 vs 0.075 | 0.459 | weak |
| doxorubicin | BRD-K92093830 | TOP2A | TOP2A (selective) | 362 | 102 | 12 | 0.500 | 0.657 | 0.389 (0.238 to 0.558) | 0.391 (0.237 to 0.539) | 0.122 vs 0.118 | 0.469 | weak |
| valrubicin | BRD-K72951360 | TOP2A | TOP2A (selective) | 360 | 102 | 15 | 0.500 | 0.470 | 0.501 (0.346 to 0.661) | 0.516 (0.383 to 0.645) | 0.166 vs 0.147 | 0.430 | weak |
| norfloxacin | BRD-K11196887 | TOP2A | TOP2A (selective) | 358 | 98 | 11 | 0.500 | 0.596 | 0.551 (0.363 to 0.725) | 0.467 (0.311 to 0.619) | 0.138 vs 0.112 | 0.531 | weak |
| voreloxin | BRD-K23677682 | TOP2A | TOP2A (selective) | 353 | 100 | 13 | 0.500 | 0.760 | 0.639 (0.466 to 0.810) | 0.612 (0.440 to 0.775) | 0.227 vs 0.130 | 0.616 | weak |
| etoposide-phosphate | BRD-K72533376 | TOP2A | TOP2A (selective) | 355 | 97 | 20 | 0.500 | 0.583 | 0.474 (0.338 to 0.611) | 0.469 (0.304 to 0.625) | 0.197 vs 0.206 | 0.435 | weak |
| sparfloxacin | BRD-K07612980 | TOP2A | TOP2A (selective) | 350 | 94 | 10 | 0.500 | 0.552 | 0.588 (0.397 to 0.763) | 0.550 (0.336 to 0.741) | 0.150 vs 0.106 | 0.569 | weak |
| trovafloxacin | BRD-K00494077 | TOP2A | TOP2A (selective) | 333 | 100 | 10 | 0.500 | 0.647 | 0.602 (0.396 to 0.807) | 0.542 (0.369 to 0.728) | 0.233 vs 0.100 | 0.561 | weak |
| mitoxantrone | BRD-K21680192 | TOP2A | TOP2A (selective) | 324 | 97 | 17 | 0.500 | 0.499 | 0.499 (0.362 to 0.656) | 0.455 (0.315 to 0.617) | 0.196 vs 0.175 | 0.453 | weak |
| idarubicin | BRD-K69650333 | TOP2A | TOP2A (selective) | 324 | 97 | 8 | 0.500 | 0.599 | 0.550 (0.300 to 0.761) | 0.550 (0.262 to 0.787) | 0.113 vs 0.082 | 0.553 | weak |
| 2-methoxyestradiol | BRD-K44408410 | COMT, CYP19A1, CYP1A1, CYP1B1, HIF1A, TUBB | TUBB (3 per gene) | 563 | 142 | 13 | 0.500 | 0.568 | 0.575 (0.414 to 0.730) | 0.576 (0.397 to 0.728) | 0.134 vs 0.092 | 0.547 | weak |
| paclitaxel | BRD-K62008436 | BCL2, MAP2, MAP4, MAPT, NR1I2, TLR4, TUBB, TUBB1 | TUBB (3 per gene) | 552 | 141 | 14 | 0.500 | 0.662 | 0.749 (0.619 to 0.865) | 0.630 (0.455 to 0.804) | 0.229 vs 0.099 | 0.675 |  |
| flubendazole | BRD-K86003836 | TUBB | TUBB (3 per gene) | 372 | 104 | 7 | 0.500 | 0.330 | 0.451 (0.255 to 0.659) | 0.464 (0.162 to 0.761) | 0.070 vs 0.067 | 0.350 | weak |
| verubulin | BRD-K42673188 | TUBB | TUBB (selective) | 367 | 102 | 10 | 0.500 | 0.523 | 0.397 (0.239 to 0.568) | 0.583 (0.408 to 0.743) | 0.084 vs 0.098 | 0.420 | weak |
| CYT-997 | BRD-K23363278 | TUBB | TUBB (selective) | 366 | 102 | 12 | 0.500 | 0.381 | 0.408 (0.222 to 0.611) | 0.312 (0.174 to 0.458) | 0.139 vs 0.118 | 0.403 | weak |
| parbendazole | BRD-K02407574 | TUBB | TUBB (selective) | 361 | 102 | 9 | 0.500 | 0.649 | 0.540 (0.309 to 0.759) | 0.557 (0.334 to 0.760) | 0.132 vs 0.088 | 0.566 | weak |
| ABT-751 | BRD-K91623615 | TUBB | TUBB (selective) | 360 | 103 | 8 | 0.500 | 0.630 | 0.532 (0.353 to 0.704) | 0.558 (0.312 to 0.797) | 0.096 vs 0.078 | 0.472 | weak |
| dolastatin-10 | BRD-K78567475 | TUBB | TUBB (selective) | 357 | 102 | 8 | 0.500 | 0.547 | 0.583 (0.366 to 0.786) | 0.622 (0.395 to 0.812) | 0.112 vs 0.078 | 0.601 | weak |
| fenbendazole | BRD-K51318897 | TUBB | TUBB (selective) | 324 | 97 | 8 | 0.500 | 0.650 | 0.567 (0.308 to 0.811) | 0.674 (0.428 to 0.905) | 0.186 vs 0.082 | 0.486 | weak |
| D-64131 | BRD-K26997899 | TUBB | TUBB (selective) | 330 | 88 | 7 | 0.500 | 0.552 | 0.490 (0.234 to 0.761) | 0.525 (0.237 to 0.822) | 0.087 vs 0.080 | 0.496 | weak |
| vorinostat | BRD-K81418486 | HDAC1, HDAC10, HDAC11, HDAC2, HDAC3, HDAC5, HDAC6, HDAC8, HDAC9 | HDAC1 (3 per gene) | 562 | 144 | 10 | 0.500 | 0.608 | 0.488 (0.360 to 0.613) | 0.643 (0.475 to 0.800) | 0.080 vs 0.069 | 0.369 | weak |
| belinostat | BRD-K17743125 | HDAC1, HDAC10, HDAC11, HDAC2, HDAC3, HDAC4, HDAC5, HDAC6, HDAC7, HDAC8, HDAC9 | HDAC1 (3 per gene) | 562 | 142 | 12 | 0.500 | 0.457 | 0.485 (0.333 to 0.631) | 0.504 (0.304 to 0.693) | 0.081 vs 0.085 | 0.431 | weak |
| resminostat | BRD-K28822270 | HDAC1, HDAC3, HDAC6, HDAC8 | HDAC1 (3 per gene) | 556 | 144 | 12 | 0.500 | 0.528 | 0.577 (0.413 to 0.745) | 0.487 (0.335 to 0.661) | 0.132 vs 0.083 | 0.557 | weak |
| tacedinaline | BRD-K52313696 | HDAC1 | HDAC1 (selective) | 511 | 136 | 12 | 0.500 | 0.454 | 0.632 (0.483 to 0.777) | 0.518 (0.374 to 0.670) | 0.136 vs 0.088 | 0.601 | weak |
| AR-42 | BRD-K13167095 | HDAC1 | HDAC1 (selective) | 367 | 100 | 15 | 0.500 | 0.688 | 0.524 (0.363 to 0.685) | 0.435 (0.268 to 0.611) | 0.172 vs 0.150 | 0.504 | weak |
| parthenolide-(-) | BRD-K34851558 | HDAC1 | HDAC1 (selective) | 357 | 99 | 20 | 0.500 | 0.504 | 0.414 (0.288 to 0.552) | 0.386 (0.249 to 0.529) | 0.228 vs 0.202 | 0.429 | weak |
| NSC-3852 | BRD-K13169950 | HDAC1 | HDAC1 (selective) | 342 | 99 | 13 | 0.500 | 0.489 | 0.335 (0.196 to 0.492) | 0.404 (0.256 to 0.566) | 0.176 vs 0.131 | 0.405 | weak |
| pyroxamide | BRD-K11663430 | HDAC1 | HDAC1 (selective) | 337 | 97 | 14 | 0.500 | 0.658 | 0.544 (0.389 to 0.682) | 0.557 (0.390 to 0.713) | 0.171 vs 0.144 | 0.469 | weak |
| carfilzomib | BRD-K15179879 | PSMA1, PSMA2, PSMA3, PSMA4, PSMA5, PSMA6, PSMA7, PSMA8, PSMB1, PSMB10, PSMB11, PSMB2, PSMB3, PSMB4, PSMB5, PSMB6, PSMB7, PSMB8, PSMB9 | PSMB5 (3 per gene) | 559 | 138 | 9 | 0.500 | 0.403 | 0.463 (0.270 to 0.658) | 0.420 (0.207 to 0.636) | 0.063 vs 0.065 | 0.486 | weak |
| bortezomib | BRD-K88510285 | PSMA1, PSMA2, PSMA3, PSMA4, PSMA5, PSMA6, PSMA7, PSMA8, PSMB1, PSMB10, PSMB11, PSMB2, PSMB3, PSMB4, PSMB5, PSMB6, PSMB7, PSMB8, PSMB9, PSMD1, PSMD2, RELA | PSMB5 (3 per gene) | 546 | 140 | 8 | 0.500 | 0.454 | 0.454 (0.221 to 0.692) | 0.606 (0.353 to 0.823) | 0.064 vs 0.057 | 0.500 | weak |
| idasanutlin | BRD-K62627508 | MDM2, TP53 | MDM2 (3 per gene) | 520 | 133 | 16 | 0.500 | 0.577 | 0.752 (0.651 to 0.838) | 0.780 (0.688 to 0.861) | 0.260 vs 0.120 | 0.711 |  |
| RITA | BRD-K00317371 | MDM2 | MDM2 (3 per gene) | 352 | 102 | 18 | 0.500 | 0.517 | 0.604 (0.457 to 0.742) | 0.580 (0.438 to 0.714) | 0.284 vs 0.176 | 0.536 | weak |
| nutlin-3 | BRD-A12230535 | MDM2, TP53 | MDM2 (3 per gene) | 343 | 97 | 14 | 0.500 | 0.771 | 0.655 (0.536 to 0.761) | 0.741 (0.639 to 0.836) | 0.233 vs 0.144 | 0.712 |  |
| AMG-232 | BRD-K64925568 | MDM2 | MDM2 (selective) | 342 | 96 | 17 | 0.500 | 0.773 | 0.776 (0.690 to 0.851) | 0.773 (0.686 to 0.851) | 0.329 vs 0.177 | 0.804 |  |
| CGM097 | BRD-K79584249 | MDM2 | MDM2 (selective) | 329 | 96 | 15 | 0.500 | 0.764 | 0.777 (0.685 to 0.866) | 0.781 (0.670 to 0.881) | 0.312 vs 0.156 | 0.765 |  |
| serdemetan | BRD-K65924316 | MDM2 | MDM2 (selective) | 232 | 75 | 11 | 0.500 | 0.555 | 0.670 (0.463 to 0.864) | 0.648 (0.430 to 0.852) | 0.330 vs 0.147 | 0.614 | weak |
| TW-37 | BRD-K28360340 | BCL2, BCL2L1, MCL1 | BCL2L1 (3 per gene) | 361 | 101 | 9 | 0.500 | 0.426 | 0.623 (0.417 to 0.798) | 0.731 (0.582 to 0.861) | 0.131 vs 0.089 | 0.496 | weak |
| ABT-737 | BRD-K56301217 | BCL2, BCL2L1, BCL2L2 | BCL2L1 (3 per gene) | 356 | 98 | 18 | 0.500 | 0.605 | 0.418 (0.303 to 0.539) | 0.482 (0.350 to 0.599) | 0.166 vs 0.184 | 0.418 | weak |
| 2,3-DCPE | BRD-K61734568 | BCL2L1 | BCL2L1 (3 per gene) | 350 | 98 | 15 | 0.500 | 0.431 | 0.625 (0.502 to 0.746) | 0.641 (0.498 to 0.780) | 0.200 vs 0.153 | 0.546 |  |
| XL-647 | BRD-K03765900 | EGFR, EPHB4, ERBB2, FLT4, KDR | KDR (3 per gene) | 554 | 143 | 16 | 0.500 | 0.472 | 0.536 (0.401 to 0.673) | 0.554 (0.411 to 0.691) | 0.121 vs 0.112 | 0.490 | weak |
| foretinib | BRD-K03449891 | FLT1, FLT4, KDR, MET | KDR (3 per gene) | 546 | 143 | 16 | 0.500 | 0.594 | 0.590 (0.431 to 0.741) | 0.557 (0.400 to 0.719) | 0.155 vs 0.112 | 0.580 | weak |
| lenvatinib | BRD-K39974922 | FLT4, KDR | KDR (3 per gene) | 552 | 137 | 15 | 0.500 | 0.460 | 0.410 (0.303 to 0.539) | 0.328 (0.225 to 0.441) | 0.095 vs 0.109 | 0.395 | weak |
| fruquintinib | BRD-K70504253 | KDR | KDR (selective) | 389 | 93 | 20 | 0.500 | 0.571 | 0.437 (0.315 to 0.554) | 0.450 (0.330 to 0.573) | 0.205 vs 0.215 | 0.415 | weak |
| SU014813 | BRD-K75911534 | KDR | KDR (selective) | 358 | 99 | 12 | 0.500 | 0.497 | 0.486 (0.322 to 0.629) | 0.407 (0.252 to 0.575) | 0.130 vs 0.121 | 0.417 | weak |
| KI-8751 | BRD-K47150025 | KDR | KDR (selective) | 356 | 100 | 13 | 0.500 | 0.434 | 0.492 (0.340 to 0.633) | 0.631 (0.481 to 0.764) | 0.147 vs 0.130 | 0.526 | weak |
| telatinib | BRD-K84564571 | KDR | KDR (selective) | 353 | 100 | 17 | 0.500 | 0.504 | 0.602 (0.472 to 0.744) | 0.551 (0.413 to 0.702) | 0.216 vs 0.170 | 0.533 | weak |
| LY2801653 | BRD-K18961567 | MET | MET (3 per gene) | 555 | 145 | 24 | 0.500 | 0.616 | 0.493 (0.380 to 0.599) | 0.596 (0.491 to 0.690) | 0.169 vs 0.166 | 0.459 | weak |
| tivantinib | BRD-K33379087 | MET | MET (3 per gene) | 544 | 141 | 7 | 0.500 | 0.471 | 0.435 (0.196 to 0.697) | 0.409 (0.262 to 0.569) | 0.062 vs 0.050 | 0.412 | weak |
| golvatinib | BRD-K69001009 | KDR, MET | MET (3 per gene) | 544 | 140 | 14 | 0.500 | 0.483 | 0.439 (0.298 to 0.587) | 0.571 (0.410 to 0.730) | 0.091 vs 0.100 | 0.468 | weak |
| INC-280 | BRD-K81016934 | MET | MET (selective) | 487 | 124 | 11 | 0.500 | 0.497 | 0.593 (0.434 to 0.733) | 0.465 (0.330 to 0.587) | 0.114 vs 0.089 | 0.542 | weak |
| savolitinib | BRD-K98028353 | MET | MET (selective) | 464 | 118 | 7 | 0.500 | 0.564 | 0.538 (0.239 to 0.820) | 0.587 (0.312 to 0.862) | 0.110 vs 0.059 | 0.484 | weak |
| AMG-337 | BRD-K27061362 | MET | MET (selective) | 408 | 109 | 8 | 0.500 | 0.518 | 0.321 (0.179 to 0.463) | 0.397 (0.267 to 0.523) | 0.062 vs 0.073 | 0.371 | weak |
| AMG458 | BRD-K21782625 | MET | MET (selective) | 354 | 99 | 17 | 0.500 | 0.475 | 0.380 (0.254 to 0.519) | 0.480 (0.347 to 0.612) | 0.145 vs 0.172 | 0.389 | weak |
| NVP-BVU972 | BRD-K77943374 | MET | MET (selective) | 351 | 99 | 14 | 0.500 | 0.514 | 0.429 (0.302 to 0.559) | 0.446 (0.302 to 0.596) | 0.127 vs 0.141 | 0.376 | weak |
| PHA-665752 | BRD-K95435023 | MET | MET (selective) | 345 | 98 | 10 | 0.500 | 0.556 | 0.419 (0.238 to 0.622) | 0.458 (0.308 to 0.632) | 0.094 vs 0.102 | 0.453 | weak |
| PF-04217903 | BRD-K73319509 | MET | MET (selective) | 343 | 96 | 14 | 0.500 | 0.538 | 0.617 (0.433 to 0.782) | 0.443 (0.248 to 0.650) | 0.216 vs 0.146 | 0.539 | weak |
| AMG-208 | BRD-K32285926 | MET | MET (selective) | 338 | 89 | 12 | 0.500 | 0.538 | 0.525 (0.325 to 0.708) | 0.519 (0.334 to 0.696) | 0.147 vs 0.135 | 0.538 | weak |
| regorafenib | BRD-K16730910 | ABL1, BRAF, DDR2, EPHA2, FGFR1, FGFR2, FLT1, FLT4, FRK, KDR, KIT, MAPK11, NTRK1, PDGFRA, PDGFRB, RAF1, RET, TEK | RET (3 per gene) | 553 | 141 | 18 | 0.500 | 0.583 | 0.600 (0.467 to 0.706) | 0.659 (0.527 to 0.780) | 0.169 vs 0.128 | 0.467 | weak |
| vandetanib | BRD-K77625799 | EGFR, EPHA1, EPHA10, EPHA2, EPHA3, EPHA4, EPHA5, EPHA6, EPHA7, EPHA8, EPHB1, EPHB2, EPHB3, EPHB4, EPHB6, ERBB2, ERBB3, ERBB4, FLT1, FLT4, KDR, PTK6, RET, SRC, TEK, VEGFA | RET (3 per gene) | 550 | 139 | 21 | 0.500 | 0.515 | 0.636 (0.509 to 0.771) | 0.589 (0.456 to 0.724) | 0.230 vs 0.151 | 0.569 |  |
| imatinib | BRD-K92723993 | ABL1, CSF1R, DDR1, KIT, NTRK1, PDGFRA, PDGFRB, RET | RET (3 per gene) | 508 | 130 | 14 | 0.500 | 0.445 | 0.535 (0.381 to 0.669) | 0.534 (0.364 to 0.701) | 0.129 vs 0.108 | 0.610 | weak |
| sunitinib | BRD-K42828737 | CSF1R, FGFR1, FLT1, FLT3, FLT4, KDR, KIT, PDGFRA, PDGFRB, RET | FGFR1 (3 per gene) | 536 | 142 | 19 | 0.500 | 0.556 | 0.583 (0.449 to 0.708) | 0.670 (0.540 to 0.783) | 0.175 vs 0.134 | 0.568 | weak |
| pazopanib | BRD-K74514084 | CSF1R, FGF1, FGFR1, FGFR3, FLT1, FLT4, ITK, KDR, KIT, PDGFRA, PDGFRB, SH2B3 | FGFR1 (3 per gene) | 531 | 137 | 13 | 0.500 | 0.569 | 0.518 (0.379 to 0.643) | 0.680 (0.526 to 0.805) | 0.131 vs 0.095 | 0.639 | weak |
| MK-2461 | BRD-K56405753 | FGFR1, FGFR2, FGFR3, FLT1, FLT3, FLT4, KDR, MERTK, MET, MST1R, NTRK1, NTRK2, PDGFRB | FGFR1 (3 per gene) | 363 | 96 | 15 | 0.500 | 0.577 | 0.579 (0.444 to 0.715) | 0.491 (0.323 to 0.649) | 0.185 vs 0.156 | 0.546 | weak |

**Which model ships:** the pre-registered switch rule, re-applied for the record, gives the random forest the higher held-out ROC-AUC on 97 of 198 drugs that are not underpowered (it needs more than half), so the rule alone would ship the logistic regression. **By the 2026-11-04 amendment, logistic regression ships for every drug**: the first run's random-forest win (32 of 60) was a tie-sized margin, and the hosted app's size matters (the first run's 60 random forests took 73,143,794 bytes). Random-forest results stay in every table. Underpowered drugs: 4 of 202.

## What this says

Over the 198 drugs that are not underpowered: median held-out ROC-AUC 0.546 (logistic), 0.545 (random forest), 0.516 (1-NN). Logistic regression beats 1-NN on 119 drugs; the random forest beats 1-NN on 114. 171 of 202 shipped models are weak (CI reaches 0.5) and 73 are below 0.5; the highest is 0.860 (selumetinib). Hotspot mutations alone explain little of how a cell line responds to most of these drugs; the models are a weak signal next to the measured responses of the nearest cell lines, not a prediction for a person.

## What changed between runs

First run = commit 5b7d361 (the 60 oncology-list matches with the most lines; random forest shipped by the switch rule). FIX round 1 = commit 71dc695 (up to 3 per oncology gene, first-listed gene; logistic regression ships by amendment). FIX round 2 = this run (3 per gene with the fewest-so-far assignment, plus selective drugs). Same split, seed and model parameters. Medians and beat-1-NN are over drugs that are not underpowered; weak counts all drugs.

| | First run (5b7d361) | FIX round 1 (71dc695) | FIX round 2 (this run) |
|---|---|---|---|
| Drugs | 60 | 86 | 202 |
| Underpowered | 0 | 0 | 4 |
| Median ROC-AUC, majority | 0.500 | 0.500 | 0.500 |
| Median ROC-AUC, 1-NN | 0.507 | 0.518 | 0.516 |
| Median ROC-AUC, logistic regression | 0.549 | 0.545 | 0.546 |
| Median ROC-AUC, random forest | 0.562 | 0.540 | 0.545 |
| Beats 1-NN, logistic regression | 40 | 55 | 119 |
| Beats 1-NN, random forest | 40 | 54 | 114 |
| Weak, logistic regression | 51 | 65 | 171 |
| Weak, random forest | 53 | 73 | 178 |
| Switch rule: RF wins | 32 of 60 | 40 of 86 | 97 of 198 |
| Shipped | random forest | logistic regression | logistic regression |
| Model bytes | 73,143,794 | 675,367 | 1,517,979 |

Models: `models/loop2/<broad_id>.joblib` (git-ignored), logistic regression fit on the training lines, 1,517,979 bytes in total.
