# Loop 2 data: DepMap 24Q4 hotspot mutations + PRISM 20Q2 sensitivity

Built by `python -m molscreen.depmap` from the files pulled by `scripts/pull_depmap.py` (pulled 2026-11-04). Rules: `docs/evaluation-loop2.md`. Cell lines, not patients. Research and learning tool, not medical advice.

## Counts (from the run)
| What | Count | How |
|---|---|---|
| Cell lines in the hotspot matrix | 1,929 | rows of `OmicsSomaticMutationsMatrixHotspot.csv` |
| Genes in the hotspot matrix | 542 | columns of the same file |
| Hotspot lines with at least one hotspot | 1,506 | row sum > 0 |
| Rows in `Model.csv` | 2,105 | 4 columns read, donor columns never read |
| PRISM rows | 753,778 | all rows of the 20Q2 secondary dose-response file |
| PRISM rows after QC | 742,231 | `passed_str_profiling` TRUE |
| PRISM rows with `auc` and `depmap_id` | 742,231 | rows without a `depmap_id` cannot be joined |
| PRISM cell lines (after QC) | 728 | distinct `depmap_id` |
| PRISM compounds | 1,494 | Broad ID without batch suffix |
| (cell line, compound) values | 677,732 | median `auc` per pair |
| Pairs with more than one row (median taken) | 61,996 | replicate screens |
| PRISM lines also in the hotspot matrix | 726 | `depmap_id` = matrix row ID |
| PRISM lines also in `Model.csv` | 728 | `depmap_id` = `ModelID` |
| Compounds with a SMILES | 1,492 | PRISM `smiles` column |
| Compounds whose SMILES parses in RDKit | 1,491 | `molscreen.chem.canonical_smiles` |
| Compounds with a ChEMBL ID | 117 | via `BRD:` IDs in `PortalCompounds.csv` |
| Compounds with >= 300 lines in the hotspot matrix | 1,457 | candidates for per-drug models |

## Raw files (SHA-256 recorded on download)
| File | Bytes | SHA-256 |
|---|---|---|
| `OmicsSomaticMutationsMatrixHotspot.csv` | 4,210,723 | `6444ce819a28d4228ff7b748e309611c5830c551620d8d2c7f86052e2675e3d8` |
| `OmicsSomaticMutations.csv` | 338,945,382 | `92e86ab6a8457ef99908daf2a2c82d9529320e23cd6c6b7adc128adc1e0f41c8` |
| `Model.csv` | 645,696 | `b7a0c1385e6cef30132b56aff61f1261d11e3f490490b355c430d32ee0dbdcfa` |
| `PortalCompounds.csv` | 692,052 | `8078ad69c27378a8101e90358dc216bfa03156c20f3087b66a260b90a8fad992` |
| `prism-repurposing-20q2-secondary-screen-dose-response-curve-parameters.csv` | 290,170,269 | `2ac69a21f1d681fe7447689262b82ca6e3dc90bfef0bd96eb5479b96f424e43d` |

## Derived tables (`data/depmap/derived/`, git-ignored, not committed)
- `compounds.csv`: 230,640 bytes
- `hotspot_binary.csv`: 2,115,560 bytes
- `models.csv`: 110,197 bytes
- `sensitivity.csv`: 28,901,573 bytes
- Total 31,357,970 bytes: over 5 MB.

## Worked example: nearest cell lines for ['KRAS', 'TP53', 'STK11']
| # | ModelID | Cell line | Lineage | Primary disease | Jaccard | Shared genes |
|---|---|---|---|---|---|---|
| 1 | ACH-001001 | 143B | Bone | Osteosarcoma | 0.6667 | KRAS, TP53 |
| 2 | ACH-000174 | CAL-62 | Thyroid | Anaplastic Thyroid Cancer | 0.6667 | KRAS, TP53 |
| 3 | ACH-000138 | CFPAC-1 | Pancreas | Pancreatic Adenocarcinoma | 0.6667 | KRAS, TP53 |
| 4 | ACH-000803 | COLO 668 | Lung | Lung Neuroendocrine Tumor | 0.6667 | KRAS, TP53 |
| 5 | ACH-000264 | Calu-6 | Lung | Non-Small Cell Lung Cancer | 0.6667 | KRAS, TP53 |
| 6 | ACH-000107 | Capan-2 | Pancreas | Pancreatic Adenocarcinoma | 0.6667 | KRAS, TP53 |
| 7 | ACH-000698 | DMS 53 | Lung | Lung Neuroendocrine Tumor | 0.6667 | STK11, TP53 |
| 8 | ACH-000485 | GSU | Esophagus/Stomach | Esophagogastric Adenocarcinoma | 0.6667 | KRAS, TP53 |
| 9 | ACH-000314 | HCC-2108 | Lung | Non-Small Cell Lung Cancer | 0.6667 | KRAS, TP53 |
| 10 | ACH-000667 | HCC-44 | Lung | Non-Small Cell Lung Cancer | 0.6667 | KRAS, TP53 |

43 screened cell lines have Jaccard 0.6667 (the 10th value), so the order among them is only the tie-break by cell line name (case-sensitive sort).

### Top 10 compounds (lowest `auc`) for ACH-001001 (143B)
| # | Compound | Name | auc | Target | SMILES |
|---|---|---|---|---|---|
| 1 | BRD-K59456551 | methotrexate | 0.220 | DHFR | `CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(cc1)C(=O)N[C@@H](CCC(O)=O)C(O)=O` |
| 2 | BRD-K08547377 | irinotecan | 0.253 | TOP1, TOP1MT | `CCc1c2Cn3c(cc4c(COC(=O)[C@]4(O)CC)c3=O)-c2nc2ccc(OC(=O)N3CCC(CC3)N3CCCCC3)cc12` |
| 3 | BRD-K69776681 | volasertib | 0.345 | PLK1 | `CC[C@H]1N(C(C)C)c2nc(Nc3ccc(cc3OC)C(=O)N[C@H]3CC[C@@H](CC3)N3CCN(CC4CC4)CC3)ncc2N(C)C1=O` |
| 4 | BRD-K82135108 | elesclomol | 0.345 | HSPA1A | `CN(NC(=O)CC(=O)NN(C)C(=S)c1ccccc1)C(=S)c1ccccc1` |
| 5 | BRD-K43389675 | daunorubicin | 0.355 | TOP2A, TOP2B | `COc1cccc2C(=O)c3c(O)c4C[C@](O)(C[C@H](O[C@H]5C[C@H](N)[C@H](O)[C@H](C)O5)c4c(O)c3C(=O)c12)C(C)=O` |
| 6 | BRD-K13662825 | dinaciclib | 0.366 | CDK1, CDK2, CDK5, CDK9 | `CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(nc12)N1CCCC[C@H]1CCO` |
| 7 | BRD-K12184916 | NVP-BEZ235 | 0.389 | ATR, MTOR, PIK3CA, PIK3CD, PIK3CG | `Cn1c2cnc3ccc(cc3c2n(-c2ccc(cc2)C(C)(C)C#N)c1=O)-c1cnc2ccccc2c1` |
| 8 | BRD-K10362825 | teniposide | 0.415 | TOP2A, TOP2B | `COc1cc(cc(OC)c1O)[C@H]1[C@@H]2[C@H](COC2=O)[C@H](O[C@@H]2O[C@@H]3CO[C@H](O[C@H]3[C@H](O)[C@H]2O)c2cccs2)c2cc3OCOc3cc12` |
| 9 | BRD-K59317601 | MLN0128 | 0.419 | MTOR, PIK3CA, PIK3CD, PIK3CG | `CC(C)n1nc(-c2ccc3oc(N)nc3c2)c2c(N)ncnc12` |
| 10 | BRD-K30577245 | docetaxel | 0.425 | BCL2, MAP2, MAP4, MAPT, NR1I2, TUBB, TUBB1 | `CC(=O)O[C@@]12CO[C@@H]1C[C@H](O)[C@]1(C)[C@@H]2[C@H](OC(=O)c2ccccc2)[C@]2(O)C[C@H](OC(=O)[C@H](O)[C@@H](NC(=O)OC(C)(C)C)c3ccccc3)C(C)=C([C@@H](O)C1=O)C2(C)C` |

## Credit lines (for the README)
- **DepMap 24Q4 Public** (hotspot mutations, cell-line annotations, compound map), Broad Institute. Figshare+, doi:10.25452/figshare.plus.27993248. CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- **PRISM Repurposing 20Q2** (secondary-screen dose-response), Broad Institute; DepMap, Corsello S, Kocak M, Golub T. figshare, doi:10.6084/m9.figshare.20564034. CC BY 4.0. Corsello SM, Nagari RT, Spangler RD, et al. Discovering the anticancer potential of non-oncology drugs by systematic viability profiling. *Nat Cancer.* 2020;1(2):235-248. doi:10.1038/s43018-019-0018-6
- Tsherniak A, Vazquez F, Montgomery PG, et al. Defining a Cancer Dependency Map. *Cell.* 2017;170(3):564-576.e16. doi:10.1016/j.cell.2017.06.010
- Mutation data: Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer Cell Line Encyclopedia. *Nature.* 2019;569(7757):503-508. doi:10.1038/s41586-019-1186-3
