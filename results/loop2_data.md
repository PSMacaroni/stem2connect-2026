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
Ranked by the number of shared mutated genes, then Jaccard, then cell line name (rule amended 2026-11-04, see the protocol's Changes).

| # | ModelID | Cell line | Lineage | Primary disease | Shared | Jaccard | Shared genes |
|---|---|---|---|---|---|---|---|
| 1 | ACH-000916 | NCI-H1573 | Lung | Non-Small Cell Lung Cancer | 3 | 0.5 | KRAS, STK11, TP53 |
| 2 | ACH-001001 | 143B | Bone | Osteosarcoma | 2 | 0.6667 | KRAS, TP53 |
| 3 | ACH-000174 | CAL-62 | Thyroid | Anaplastic Thyroid Cancer | 2 | 0.6667 | KRAS, TP53 |
| 4 | ACH-000138 | CFPAC-1 | Pancreas | Pancreatic Adenocarcinoma | 2 | 0.6667 | KRAS, TP53 |
| 5 | ACH-000803 | COLO 668 | Lung | Lung Neuroendocrine Tumor | 2 | 0.6667 | KRAS, TP53 |
| 6 | ACH-000264 | Calu-6 | Lung | Non-Small Cell Lung Cancer | 2 | 0.6667 | KRAS, TP53 |
| 7 | ACH-000107 | Capan-2 | Pancreas | Pancreatic Adenocarcinoma | 2 | 0.6667 | KRAS, TP53 |
| 8 | ACH-000698 | DMS 53 | Lung | Lung Neuroendocrine Tumor | 2 | 0.6667 | STK11, TP53 |
| 9 | ACH-000485 | GSU | Esophagus/Stomach | Esophagogastric Adenocarcinoma | 2 | 0.6667 | KRAS, TP53 |
| 10 | ACH-000314 | HCC-2108 | Lung | Non-Small Cell Lung Cancer | 2 | 0.6667 | KRAS, TP53 |

43 screened cell lines share 2 genes with Jaccard 0.6667 (the 10th row), so the order among them is only the tie-break by cell line name (case-sensitive sort).

### Top 10 compounds (lowest `auc`) for ACH-000916 (NCI-H1573)
| # | Compound | Name | auc | Target | SMILES |
|---|---|---|---|---|---|
| 1 | BRD-A64064900 | sangivamycin | 0.019 |  | `NC(=O)c1cn(C2OC(CO)[C@H](O)[C@@H]2O)c2ncnc(N)c12` |
| 2 | BRD-K39484304 | triptolide | 0.024 | RELA | `CC(C)[C@]12O[C@H]1[C@@H]1O[C@]11[C@]3(O[C@H]3C[C@H]3C4=C(CC[C@]13C)C(=O)OC4)[C@@H]2O` |
| 3 | BRD-K52762805 | epothilone-d | 0.126 | TUBA1A, TUBA1B, TUBA1C, TUBA3C, TUBA4A, TUBA8, TUBB, TUBB1, TUBB3, TUBB4A, TUBB4B | `C[C@H]1CCC\C(C)=C/C[C@H](OC(=O)C[C@H](O)C(C)(C)C(=O)[C@H](C)[C@H]1O)C(\C)=C\c1csc(C)n1` |
| 4 | BRD-K78567475 | dolastatin-10 | 0.149 | TUBB | `CC[C@H](C)[C@@H]([C@@H](CC(=O)N1CCC[C@H]1[C@H](OC)[C@@H](C)C(=O)N[C@@H](Cc1ccccc1)c1nccs1)OC)N(C)C(=O)[C@@H](NC(=O)[C@H](C(C)C)N(C)C)C(C)C` |
| 5 | BRD-K61397605 | romidepsin | 0.187 | HDAC1, HDAC2, HDAC3, HDAC4, HDAC5, HDAC6, HDAC7, HDAC8, HDAC9 | `C\C=C1/NC(=O)[C@H]2CSSCC\C=C\[C@H](CC(=O)N[C@H](C(C)C)C(=O)N2)OC(=O)[C@@H](NC1=O)C(C)C` |
| 6 | BRD-K37890730 | camptothecin | 0.198 | TOP1 | `CC[C@@]1(O)C(=O)OCc2c1cc1-c3nc4ccccc4cc3Cn1c2=O` |
| 7 | BRD-K60025295 | crystal-violet | 0.200 |  | `CN(C)c1ccc(cc1)C(c1ccc(cc1)N(C)C)=C1C=CC(C=C1)=[N+](C)C` |
| 8 | BRD-K68164687 | epothilone-b | 0.203 | TUBA1A, TUBA1B, TUBA1C, TUBA3C, TUBA4A, TUBA8, TUBB, TUBB1, TUBB3, TUBB4A, TUBB4B | `C[C@H]1CCC[C@@]2(C)O[C@H]2C[C@@H](OC(=O)C[C@@H](O)C(C)(C)C(=O)[C@H](C)[C@H]1O)C(\C)=C\c1csc(C)n1` |
| 9 | BRD-K06858286 | cabazitaxel | 0.205 | TUBA4A, TUBB, TUBB1 | `CO[C@@H]1C[C@H]2OC[C@@]2(OC(C)=O)[C@H]2[C@@H](OC(=O)c3ccccc3)[C@@]3(O)C[C@H](OC(=O)[C@H](O)[C@@H](NC(=O)OC(C)(C)C)c4ccccc4)C(C)=C([C@@H](OC)C(=O)[C@]12C)C3(C)C` |
| 10 | BRD-K99475619 | genz-644282 | 0.256 | TOP1 | `CNCCn1c2c(cnc3cc4OCOc4cc23)c2cc(OC)c(OC)cc2c1=O` |

## Credit lines (for the README)
- **DepMap 24Q4 Public** (hotspot mutations, cell-line annotations, compound map), Broad Institute. Figshare+, doi:10.25452/figshare.plus.27993248. CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- **PRISM Repurposing 20Q2** (secondary-screen dose-response), Broad Institute; DepMap, Corsello S, Kocak M, Golub T. figshare, doi:10.6084/m9.figshare.20564034. CC BY 4.0. Corsello SM, Nagari RT, Spangler RD, et al. Discovering the anticancer potential of non-oncology drugs by systematic viability profiling. *Nat Cancer.* 2020;1(2):235-248. doi:10.1038/s43018-019-0018-6
- Tsherniak A, Vazquez F, Montgomery PG, et al. Defining a Cancer Dependency Map. *Cell.* 2017;170(3):564-576.e16. doi:10.1016/j.cell.2017.06.010
- Mutation data: Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer Cell Line Encyclopedia. *Nature.* 2019;569(7757):503-508. doi:10.1038/s41586-019-1186-3
