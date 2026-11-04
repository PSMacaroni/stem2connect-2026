# Data, model and library registry

The single source of truth for every dataset, model and library this project uses. Every licence was read from the
official page on **2026-11-04**, before anything was downloaded. Nothing in this file was downloaded to check it:
facts come from the official pages, `HEAD` requests (sizes) and small counted API queries (`limit=1`).

If a source changes its terms, update this file first, then the README credits.

Legend for "OK for a public GitHub repo?": **yes** = code and data can both be public; **code yes, data no** = the
repo can be public but the raw files must not be committed (a download script fetches them); **unclear** = see
Blockers.

---

## 1. ChEMBL (bioactivity: loop 1)

| Field | Value |
|---|---|
| Name | ChEMBL |
| URL | https://www.ebi.ac.uk/chembl/ |
| Release | **ChEMBL_37**, released 2026-05-01 (`https://www.ebi.ac.uk/chembl/api/data/status.json` returns `"chembl_db_version": "ChEMBL_37", "chembl_release_date": "2026-05-01"`; the FTP README says `Release: chembl_37, Date: 01/05/2026`) |
| Licence | **Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)**. Licence file: https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/LICENSE . Stated on https://chembl.gitbook.io/chembl-interface-documentation/about ("The ChEMBL data is made available on a Creative Commons Attribution-Share Alike 3.0 Unported License"). Attribution rules: https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/REQUIRED.ATTRIBUTION . Web and API use also fall under the EMBL-EBI terms of use: https://www.ebi.ac.uk/about/terms-of-use |
| OK for a public GitHub repo? | **Yes**, with two duties. (1) Attribution: the README, and the app (it is a web resource), must show the ChEMBL URL and the release, e.g. "ChEMBL data is from http://www.ebi.ac.uk/chembl - the version of ChEMBL is chembl_37", and keep ChEMBL IDs in any data we ship. (2) Share-alike: any ChEMBL-derived data file we publish (cached activity tables, nearest-actives tables) must itself be released under CC BY-SA 3.0, separately from the code licence. Treating trained models as adaptations under the same terms is the safe reading (inferred, not stated by ChEMBL). |
| Citation | Mendez D, Gaulton A, Bento AP, et al. ChEMBL: towards direct deposition of bioassay data. *Nucleic Acids Res.* 2019;47(D1):D930-D940. doi:10.1093/nar/gky1075 (the "primary current citation" in REQUIRED.ATTRIBUTION; DOI checked on Crossref) |
| How we download | REST API, paged: `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=<ID>&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1000&offset=<n>` (follow `page_meta.next`). Or Python `chembl_webresource_client` 0.10.9: `new_client.activity.filter(target_chembl_id=ID, pchembl_value__isnull=False, standard_type__in=["IC50", "Ki", "EC50"])`. No account or key. The full dump is not needed (`chembl_37_sqlite.tar.gz` is 5,764,252,857 bytes by HEAD). |
| Size | 57,045 activity rows in total for the 9 targets (sum of the IC50/Ki/EC50 column below). These are rows, not unique molecules. |
| Fields we use | `molecule_chembl_id`, `canonical_smiles`, `standard_type`, `standard_relation`, `standard_value`, `standard_units`, `pchembl_value`, `assay_chembl_id`, `assay_type`, `data_validity_comment`, `document_chembl_id`, `target_organism` (all confirmed present in a `limit=1` response). `assay_variant_mutation` also exists and can flag assays on mutant proteins. |

### The 9 targets (Homo sapiens, SINGLE PROTEIN)

Counted 2026-11-04 against ChEMBL_37. Target IDs were found with
`https://www.ebi.ac.uk/chembl/api/data/target.json?target_components__target_component_synonyms__component_synonym__iexact=<GENE>&target_type=SINGLE%20PROTEIN&organism=Homo%20sapiens`
(each gene returned exactly one target; UniProt accession shown). Counts are `page_meta.total_count` from the query
URL in the last column (`limit=1`, so only one row was fetched). "Any pChEMBL" is the same URL without
`&standard_type__in=IC50,Ki,EC50`.

| Gene | ChEMBL target ID | UniProt | Activities with pChEMBL, IC50/Ki/EC50 | Any pChEMBL | Query (IC50/Ki/EC50 count) |
|---|---|---|---|---|---|
| EGFR | CHEMBL203 | P00533 | 20,384 | 21,342 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL203&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| BRAF | CHEMBL5145 | P15056 | 9,268 | 9,836 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL5145&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| ERBB2 (HER2) | CHEMBL1824 | P04626 | 3,481 | 3,565 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL1824&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| CDK4 | CHEMBL331 | P11802 | 1,675 | 1,730 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL331&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| CDK6 | CHEMBL2508 | Q00534 | 1,026 | 1,053 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL2508&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| ALK | CHEMBL4247 | Q9UM73 | 4,201 | 4,294 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL4247&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| ABL1 | CHEMBL1862 | P00519 | 5,350 | 6,314 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL1862&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| PARP1 | CHEMBL3105 | P09874 | 5,787 | 5,935 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL3105&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |
| BCL2 | CHEMBL4860 | P10415 | 5,873 | 5,939 | `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL4860&pchembl_value__isnull=false&standard_type__in=IC50,Ki,EC50&limit=1` |

CDK6 (1,026 rows) is the smallest set. Unique molecules after de-duplication will be fewer, so check the count
before promising a CDK6 model.

---

## 2. Tox21 via MoleculeNet / DeepChem (safety flags: loop 3)

| Field | Value |
|---|---|
| Name | Tox21 (12 assays), MoleculeNet copy |
| URL | Data: https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz . Loader that defines it: https://github.com/deepchem/deepchem/blob/master/deepchem/molnet/load_function/tox21_datasets.py . Original challenge: https://tripod.nih.gov/tox21/challenge/data.jsp |
| Version | The S3 file has `Last-Modified: Fri, 10 Jul 2020` and ETag `2882d69e70bba0fec14995f26787cc25` (HEAD). It is the 2014 Tox21 Data Challenge set; the loader docstring says "8k compounds on 12 different targets". |
| Licence | **No licence is stated** by MoleculeNet/DeepChem for the data file, or by NCATS on the challenge data page (the only "Public Domain" heading on https://tripod.nih.gov/tox21/challenge/data.jsp labels their code, not the data). Tox21 is a US federal programme (NCATS, NTP/NIEHS, EPA, FDA), so the data is probably US-government public domain (inferred, not stated anywhere I found). DeepChem's own code is MIT: https://github.com/deepchem/deepchem/blob/master/LICENSE |
| OK for a public GitHub repo? | **Code yes; raw data unclear, so do not commit it.** Download it at run time with the script and cite both papers. Low risk, but not verified. |
| Citation | Wu Z, Ramsundar B, Feinberg EN, et al. MoleculeNet: a benchmark for molecular machine learning. *Chem. Sci.* 2018;9(2):513-530. doi:10.1039/C7SC02664A. And: Huang R, Xia M, et al. Tox21Challenge to build predictive models of nuclear receptor and stress response pathways as mediated by exposure to environmental chemicals and drugs. *Front. Environ. Sci.* 2016;3:85. doi:10.3389/fenvs.2015.00085 (both DOIs checked on Crossref) |
| How we download | `curl -O https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz` (no account). We do not need the `deepchem` package (2.8.0 requires Python < 3.12). |
| Size | 122,925 bytes gzipped (HEAD `Content-Length`) |
| Fields we use | `smiles` plus the 12 task columns `NR-AR`, `NR-AR-LBD`, `NR-AhR`, `NR-Aromatase`, `NR-ER`, `NR-ER-LBD`, `NR-PPAR-gamma`, `SR-ARE`, `SR-ATAD5`, `SR-HSE`, `SR-MMP`, `SR-p53` (from `TOX21_TASKS` in the loader). Labels are 0/1 with blanks for untested. Any extra id column is confirmed on first download. |

---

## 3. GDSC drug sensitivity (loop 2)

**Important change:** `https://www.cancerrxgene.org/` (and `/downloads/bulk_download`) now returns **HTTP 410 Gone**
with a notice that the GDSC "datasets and features have now been integrated into the Sanger DepMap" and to "Download
the GDSC1 & GDSC2 datasets from the Cell Model Passports". The files below are the ones linked from
https://cellmodelpassports.sanger.ac.uk/downloads (Drug Sensitivity Data section, read 2026-11-04).

| Field | Value |
|---|---|
| Name | Genomics of Drug Sensitivity in Cancer (GDSC1 and GDSC2), fitted dose response |
| URL | https://cellmodelpassports.sanger.ac.uk/downloads ; docs: https://depmap.sanger.ac.uk/documentation/datasets/drug-sensitivity/ |
| Version | Release 8.5 files dated **27 Oct 2023** (`screened_compounds_rel_8.5.csv` sits next to them). GDSC1: 970 cell models, 403 compounds, Resazurin or Syto60, 72 h. GDSC2: 969 cell models, 297 compounds, CellTiter-Glo, 72 h (dataset table on the docs page). |
| Licence | **Sanger DepMap Data Usage Policy** (custom, non-commercial): https://depmap.sanger.ac.uk/documentation/data-usage-policy/ . It grants "a non-exclusive, non-transferable right to use data files for internal proprietary research and educational purposes", and excludes use "for resale ... or for provision of commercial services". It also says "Direct use of the API in third party websites without prior permission is not permitted" and that commercial use needs prior consent (contact depmap@sanger.ac.uk). Site terms: https://www.sanger.ac.uk/legal/ |
| OK for a public GitHub repo? | **Code yes, data no; app display unclear.** The rights are non-transferable, so raw GDSC files must not be committed. Whether a public app may show GDSC values, and whether models trained on GDSC may be published, is **unclear** (the use is educational and non-commercial, but it passes the data to third parties). See Blockers. Never call the DepMap API from the hosted app. |
| Citation | Yang W, Soares J, Greninger P, et al. Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells. *Nucleic Acids Res.* 2013;41(D1):D955-D961. doi:10.1093/nar/gks1111. And: Iorio F, Knijnenburg TA, Vis DJ, et al. A landscape of pharmacogenomic interactions in cancer. *Cell* 2016;166(3):740-754. doi:10.1016/j.cell.2016.06.017 (the GDSC1 paper named on the docs page; DOIs checked on Crossref) |
| How we download | `https://cmp.cog.sanger.ac.uk/download/GDSC1_fitted_dose_response_27Oct23.xlsx` and `https://cmp.cog.sanger.ac.uk/download/GDSC2_fitted_dose_response_27Oct23.xlsx`; compound annotations `https://cog.sanger.ac.uk/cmp/download/screened_compounds_rel_8.5.csv`. No account. The raw plate data (`GDSC*_public_raw_data_27Oct23.zip`) is not needed. |
| Size | GDSC1 xlsx 30,348,857 bytes; GDSC2 xlsx 22,112,537 bytes; screened compounds 46,414 bytes (HEAD). Caveat: an older copy with the same file name, `https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/GDSC2_fitted_dose_response_27Oct23.xlsx`, is 21,330,376 bytes (Last-Modified 2023-10-30), so the two copies differ. Use the Cell Model Passports link and record a SHA-256 on download. |
| Fields we use | From the docs' field table: `DATASET`, `CELL_LINE_NAME`, `SANGER_MODEL_ID`, `CANCER_TYPE`, `DRUG_ID`, `DRUG_NAME`, `PUTATIVE_TARGET`, `PATHWAY_NAME`, `MIN_CONC`, `MAX_CONC` (micromolar), `LN_IC50` (natural log of the fitted IC50), `AUC` (fraction of the area between the highest and lowest screening concentration), `RMSE` (curves with RMSE > 0.3 are already excluded), `Z_SCORE`. The same compound can have several `DRUG_ID`s (docs, "Compounds with Multiple Entries"). |

---

## 4. Cell Model Passports mutation data (loop 2)

| Field | Value |
|---|---|
| Name | Cell Model Passports (Wellcome Sanger Institute): mutations and model list |
| URL | https://cellmodelpassports.sanger.ac.uk/downloads ; docs: https://depmap.sanger.ac.uk/documentation/datasets/mutation/ |
| Version | Site footer on 2026-11-04: Data Version 2.21.0, API Version 1.25.0. Mutation files dated 2026-07-24; model list dated 2026-10-13. |
| Licence | The same **Sanger DepMap Data Usage Policy** as GDSC: https://depmap.sanger.ac.uk/documentation/data-usage-policy/ (non-exclusive, non-transferable, internal research and educational use; no resale or commercial services; API not to be used in third-party websites without permission). The site's "Terms & Conditions" link goes to https://www.sanger.ac.uk/legal/ |
| OK for a public GitHub repo? | **Code yes, data no; app display unclear** (same reasons as GDSC). Do not commit raw files. |
| Citation | van der Meer D, Barthorpe S, Yang W, et al. Cell Model Passports - a hub for clinical, genetic and functional datasets of preclinical cancer models. *Nucleic Acids Res.* 2019;47(D1):D923-D929. doi:10.1093/nar/gky872 (DOI checked on Crossref) |
| How we download | Driver mutations (what loop 2 needs): `https://cog.sanger.ac.uk/cmp/download/mutations_summary_20260724.zip`. All mutations (only if needed): `https://cog.sanger.ac.uk/cmp/download/mutations_all_20260724.zip`. Model list with external IDs: `https://cog.sanger.ac.uk/cmp/download/model_list_20261013.csv`. Driver gene list: `https://cog.sanger.ac.uk/cmp/download/driver_genes_20241212.csv`. Rolling `*_latest.csv.gz` links exist, but pin the dated files. No account. |
| Format and size | Zipped CSV / CSV. `mutations_summary_20260724.zip` 584,662 bytes; `mutations_all_20260724.zip` 305,104,654 bytes; `model_list_20261013.csv` 953,924 bytes; `driver_genes_20241212.csv` 41,433 bytes (HEAD). |
| How IDs join to GDSC | Every model has a Sanger model ID (`SIDM...`, "Sanger IDentifier Model" in the glossary: https://depmap.sanger.ac.uk/documentation/cell-models/glossary-terms/). The GDSC fitted files carry `SANGER_MODEL_ID`, so the join is GDSC `SANGER_MODEL_ID` = Cell Model Passports model ID. The model list also maps to COSMIC, Cellosaurus (RRID) and Broad (CCLE) IDs (FAQ: https://depmap.sanger.ac.uk/documentation/frequently-asked-questions/). Join on the ID, never on the cell-line name. |
| Fields we use | Model ID, gene symbol, protein change and the driver flag (`DRV` in the docs), plus tissue and cancer type from the model list. Exact column names are **not verified** (seeing them needs a download); confirm on first download and update this row. |

---

## 3b. Broad DepMap and PRISM (candidate replacement for loop 2)

Researched 2026-11-04 as a drop-in for sections 3 and 4. Nothing was downloaded: facts come from the Figshare API
(`https://api.figshare.com/v2/articles/<id>`), the small README files of each release (5 to 43 KB), byte-range peeks
at the first ~1.2 KB of each data file (to read the header row), the DepMap forum's public JSON
(`https://forum.depmap.org/t/<id>.json`) and Internet Archive copies of the terms page.

**Short answer: the current DepMap portal releases are no longer CC BY 4.0, but the last DepMap and PRISM releases
deposited on Figshare are, and they are enough for loop 2.**

**1. Two licences, depending on where and when the file comes from.**
- **Current portal terms (not open).** `https://depmap.org/portal/terms/`, "Last Revised: April 2nd, 2026" (read from
  the Internet Archive copy of 2026-05-02,
  `https://web.archive.org/web/20260502220113/https://depmap.org/portal/terms/`; the same wording was already in the
  copy of 2025-12-16, "Last Revised: May 20th, 2025"). Exact wording:
  > "The data made available on this website were generated for research purposes and are not intended for clinical
  > or commercial uses, including direct sale, incorporation into a product, or the use of the data to train,
  > develop, or enhance machine learning or AI models other than for internal research use (each a "Commercial
  > Use"). For clarity, machine learning and AI models are permitted to be utilized with or on the Data for your own
  > internal use, or shared for non-profit research purposes, including for process optimization and analysis."

  and, on rehosting:
  > "Any rehosting of the Data on Your website requires that You both adhere to, and require any third party users
  > to adhere to, these terms and conditions. You agree to repost these terms and conditions in full if you elect to
  > rehost the Data."

  The terms also require acknowledging the Broad Institute and keep a confidentiality clause for "identifiable Data
  Subjects".
- **Figshare deposits (CC BY 4.0).** Every DepMap/PRISM Figshare record checked shows
  `"license": {"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}` in the Figshare API on
  2026-11-04 (records in the table below). CC BY 4.0 Section 2(a)(1) grants "a worldwide, royalty-free,
  non-sublicensable, non-exclusive, irrevocable license" to "reproduce and Share the Licensed Material, in whole or
  in part; and produce, reproduce, and Share Adapted Material"
  (https://creativecommons.org/licenses/by/4.0/legalcode). Attribution is the condition that matters here. **The
  permission to put these files (or tables derived from them) in a public repo and show them in a public app comes
  from this licence text, not from any Broad statement.**
- **Why both exist (DepMap staff on the forum; no formal Broad statement beyond forum posts).** These posts only
  support "older Figshare deposits were released under CC BY 4.0; only newer data has the new terms". Phil
  Montgomery (`pmontgom`), 2026-09-25, https://forum.depmap.org/t/ccle-depmap-license-clarification/4686 : "We used
  to deposit data into figshare under a CC4.0 license, but stopped doing when DepMap switched to terms of use which
  were not compatible with the CC4.0 license." Phil Montgomery (`pmontgom`), 2026-07-28,
  https://forum.depmap.org/t/provide-an-open-endpoint-for-latest-version-retrieval/4652 : "Yes, older data has been
  released on those platforms. However, for newly generated data, the DepMap data terms and conditions have
  changed." In the 2026-09-25 post he also says a Zenodo mirror of newer files claiming a CC4.0 license "is not
  valid": use only Broad's own Figshare records.
- **Sanger GDSC on the DepMap portal.** The portal also hosts "Sanger GDSC1 and GDSC2" (Release 8.1, Oct 2019,
  reprocessed) and "Sanger Drug Combinations 2022" (forum list of portal datasets, Samantha Stokes
  (`Samantha_Stokes`), 2024-10-24, https://forum.depmap.org/t/depmap-portal-datasets/3695). The portal's per-file licence for these could not be read
  (captcha, see 4.), so it is **not verified**; the source data is under the Sanger DepMap Data Usage Policy
  (sections 3 and 4), so the portal copy is no way around Blocker 2. `PortalCompounds.csv` (DepMap 24Q4) maps
  compounds to `GDSC1:`/`GDSC2:` IDs, which confirms GDSC data is mixed into the portal.

**2. Releases.** The newest release is **DepMap Public 26Q3**, announced 2026-10-05
(https://forum.depmap.org/t/announcing-the-26q3-release/4692). Since 2026 there are two releases a year (26Q1 and
26Q3; https://forum.depmap.org/t/depmap-26q2-release/4569, 2026-01-29). 25Q2 and later exist only on the portal,
under the new terms (Phil Montgomery (`pmontgom`), 2025-08-18,
https://forum.depmap.org/t/availability-of-depmap-25q2-on-figshare/4424 : "the plan
moving forward is to release DepMap data directly on the DepMap portal without hosting it on figshare").
**The newest CC BY 4.0 release is DepMap 24Q4 Public on Figshare+** (no 25Qx record was found on Figshare).

| Record (Figshare, CC BY 4.0) | DOI / URL | Published | What loop 2 uses |
|---|---|---|---|
| DepMap 24Q4 Public | 10.25452/figshare.plus.27993248.v1 ; https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248 | 2024-12-10 | mutations, model metadata, compound map |
| PRISM Repurposing 20Q2 Dataset | 10.6084/m9.figshare.20564034.v1 ; https://figshare.com/articles/dataset/PRISM_Repurposing_20Q2_Dataset/20564034 | 2022-08-23 | secondary-screen dose-response (AUC, IC50, SMILES) |
| PRISM Repurposing 19Q4 Dataset | 10.6084/m9.figshare.9393293.v4 ; https://figshare.com/articles/dataset/PRISM_Repurposing_19Q3_Primary_Screen/9393293 | 2019-12-17 | the version analysed in Corsello 2020 (fallback) |
| Repurposing Public 24Q2 | 10.6084/m9.figshare.25917643.v1 ; https://figshare.com/articles/dataset/Repurposing_Public_24Q2/25917643 | 2024-05-31 | newest PRISM Repurposing release found; single dose only |

DepMap 24Q4 files (sizes from the Figshare API):

| File | Bytes | Format and key columns (header row read 2026-11-04) |
|---|---|---|
| `OmicsSomaticMutations.csv` | 338,945,382 | One row per somatic variant (Mutect2, hg38). Columns include `HugoSymbol`, `ProteinChange` (e.g. `p.V600E`), `VariantInfo`, `VepImpact`, `LikelyLoF`, `OncogeneHighImpact`, `TumorSuppressorHighImpact`, `HessDriver`, `Hotspot`, `AMClass`/`AMPathogenicity` (AlphaMissense), `CivicID`, `EntrezGeneID` and **`ModelID`** (`ACH-...`). The real header also has `Exon`, `Intron` and `RescueReason`, which the README leaves out. |
| `OmicsSomaticMutationsMatrixHotspot.csv` | 4,210,723 | Cell line x gene matrix; columns are `SYMBOL (EntrezID)` (e.g. `NRAS (4893)`), rows are `ACH-...` IDs. README: 0 = no hotspot mutation, else 1 or 2 by summed allele frequency (2 if > 0.95); "hot spot" = Hess et al. 2019, OncoKB hotspot or COSMIC mutation significance tier 1. **This is the ready-made mutation vector.** |
| `OmicsSomaticMutationsMatrixDamaging.csv` | 147,655,356 | Same shape, for damaging (`LikelyLoF == True`) mutations, i.e. tumour-suppressor loss. |
| `Model.csv` | 645,696 | `ModelID`, `CellLineName`, `StrippedCellLineName`, `OncotreeLineage`, `OncotreePrimaryDisease`, `OncotreeSubtype`, `OncotreeCode`, `RRID` (Cellosaurus), `CCLEName`, **`SangerModelID`** (`SIDM...`) and `COSMICID`. Also the donor's `Age`, `Sex` and `PatientRace`: drop these, never show them. |
| `PortalCompounds.csv` | 692,052 | `CompoundID` (`DPC-...`), `CompoundName`, `GeneSymbolOfTargets`, `SampleIDs` (e.g. `BRD:BRD-K37890730-001-15-1;GDSC2:1003`), `ChEMBLID`, `SMILES`, `InChIKey`, `PubChemCID`. The first rows have empty `SMILES`/`InChIKey`; how many are filled is **not verified**. |
| `README.txt` | 43,103 | Column docs. Mutation pipeline PDF: https://storage.googleapis.com/shared-portal-files/Tools/24Q4_Mutation_Pipeline_Documentation.pdf |

**3. Drug sensitivity (PRISM).** PRISM pools DNA-barcoded cell lines and reads viability with Luminex beads.
- **Secondary screen (dose-response, what loop 2 needs).**
  `prism-repurposing-20q2-secondary-screen-dose-response-curve-parameters.csv` (290,170,269 bytes; the 19Q4 file
  `secondary-screen-dose-response-curve-parameters.csv` is 264,340,589 bytes). 1,448 compounds x 489 cell lines,
  8 doses, 4-fold dilution from 10 uM, 5 days; plus screen `MTS010`: 192 oncology compounds x 770 cell lines (the
  README recommends `MTS010` where available). Header: `broad_id`, `depmap_id`, `ccle_name`, `screen_id`,
  `upper_limit`, `lower_limit`, `slope`, `r2`, `auc`, `ec50`, `ic50`, `passed_str_profiling`, `row_name`, `name`,
  `moa`, `target`, `disease.area`, `indication`, **`smiles`**, `phase`. Measures: **`auc`** (area under a
  four-parameter log-logistic curve fitted with the drc R package) and `ic50`/`ec50` in uM. Structures: a `smiles`
  column on every row, and a Broad ID (`BRD-K...-001-01-1`, "drug-batch combinations"). No InChIKey column.
- **Primary screen.** 4,518 compounds (19Q4) / 5,274 (20Q2) at 2.5 uM against 578 or 562 cell lines; the measure
  is log2 fold change (`primary-screen-replicate-collapsed-logfold-change.csv`).
- **Repurposing Public 24Q2 (newest PRISM release found).** 1,514 compounds (1,280 REP1M + 234 REP300) at a
  single dose of 2.5 uM, 5 days, 906 cell lines (859 passed QC). The measure is log2 fold change only
  (`Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv`, 72,456,953 bytes: rows = treatments, columns =
  `ACH-...`). Its compound list (`Repurposing_Public_24Q2_Extended_Primary_Compound_List.csv`: `screen`, `dose`,
  `repurposing_target`, `MOA`, `IDs` = `BRD:BRD-...`, `Drug.Name`, `Synonyms`) has **no SMILES**; map Broad IDs
  through `PortalCompounds.csv`. No dose-response, so it fits loop 2 less well than the 20Q2 secondary screen. A
  newer PRISM release under the new portal terms may exist but was **not verified** (captcha).

**4. Download mechanics.**
- **depmap.org sits behind a Cloudflare Turnstile check.** On 2026-11-04 every `https://depmap.org/portal/...` URL
  tried (terms, data page, `/portal/api/download/files`, and even `/portal/api/no-captcha/download/files`, which
  Phil Montgomery announced as live on 2026-07-28 in thread 4652) returned a 4.8 KB "DepMap — Verification" page to `curl`, with the note
  "please don't scrape the portal". So the portal cannot be scripted and its per-file licence dialog was not read.
  The check was not bypassed.
- **Figshare works without an account.** `https://ndownloader.figshare.com/files/<file_id>` answers HTTP 302 to a
  signed S3 URL, and range requests work. File IDs: `OmicsSomaticMutationsMatrixHotspot.csv` 51065750,
  `OmicsSomaticMutationsMatrixDamaging.csv` 51065747, `OmicsSomaticMutations.csv` 51065732, `Model.csv` 51065297,
  `PortalCompounds.csv` 51065762, 24Q4 `README.txt` 51065795; 20Q2 secondary dose-response 36794595 and its readme
  36794613; 24Q2 Extended Primary matrix 46630984 and compound list 46630981. Pin these IDs and record a SHA-256 on
  download.

**5. Citations** (journal DOIs checked on Crossref; Figshare DOIs resolve at doi.org; 2026-11-04).
- DepMap, Broad (2024). DepMap 24Q4 Public. Figshare+. Dataset. doi:10.25452/figshare.plus.27993248.v1
- DepMap, Broad; Corsello S; Kocak M; Golub T (2022). PRISM Repurposing 20Q2 Dataset. figshare. Dataset.
  doi:10.6084/m9.figshare.20564034.v1
- Corsello SM, Nagari RT, Spangler RD, et al. Discovering the anticancer potential of non-oncology drugs by
  systematic viability profiling. *Nat Cancer.* 2020;1(2):235-248. doi:10.1038/s43018-019-0018-6 (verified)
- Tsherniak A, Vazquez F, Montgomery PG, et al. Defining a Cancer Dependency Map. *Cell.* 2017;170(3):564-576.e16.
  doi:10.1016/j.cell.2017.06.010
- Mutation data: Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer Cell
  Line Encyclopedia. *Nature.* 2019;569(7757):503-508. doi:10.1038/s41586-019-1186-3
- DepMap's own "how to cite" wording is on the portal and was **not read** (captcha).

**6. Verdict.**

| Source | OK for a public GitHub repo? | OK to display in a public app? | Why |
|---|---|---|---|
| Figshare snapshots: DepMap 24Q4 Public + PRISM Repurposing 20Q2 (or 19Q4) + Repurposing Public 24Q2 | **Yes**, with attribution. Commit only small derived tables (e.g. the hotspot matrix cut to loop-2 genes, the AUC table); fetch the large raw files with a script. | **Yes**, with attribution | Each record carries CC BY 4.0, whose licence text (https://creativecommons.org/licenses/by/4.0/legalcode, Section 2(a)(1)) grants an irrevocable right to reproduce and share the material and adapted material, so redistribution, public display and publishing models trained on it are allowed with attribution. DepMap staff forum posts (2026-07-28, 2026-09-25) only confirm that older Figshare deposits were released under CC BY 4.0 and that only newer data has the new terms; no formal Broad statement beyond forum posts. |
| Current portal releases (25Q2, 26Q1, 26Q3) | **No** | **Unclear, avoid** | Portal terms: ML use only internal or "shared for non-profit research purposes"; rehosting binds every visitor to the terms. Also captcha-gated, so no reproducible download script. |
| GDSC via the DepMap portal | **No** (same as section 3) | **Unclear** | Sanger DepMap Data Usage Policy; the portal's licence text was not verified. |

**What loop 2 looks like on this data.**
1. Mutation vector: `OmicsSomaticMutationsMatrixHotspot.csv` (24Q4), one row per `ACH-...` cell line, one 0/1/2
   column per gene; optionally add `OmicsSomaticMutationsMatrixDamaging.csv` for tumour suppressors. The protein
   change to display (e.g. `BRAF p.V600E`) comes from `OmicsSomaticMutations.csv` (`HugoSymbol`, `ProteinChange`,
   `ModelID`).
2. Drug sensitivity: `auc` (lower = more sensitive) from the 20Q2 secondary dose-response file, preferring
   `screen_id == "MTS010"` and `passed_str_profiling == TRUE`; `smiles` links each drug to loops 1, 3 and 4.
3. Join: PRISM `depmap_id` = DepMap `ModelID` = 24Q4 matrix row ID (`ACH-...`). Names and lineage come from
   `Model.csv`. Never join on cell-line names.
4. Bonus: `Model.csv` has `SangerModelID`, so a GDSC comparison stays possible if Sanger ever says yes.

**Not verified:** the portal's per-file licence dialog and "how to cite" text, the licence shown for the portal's
GDSC copy, any PRISM release newer than Repurposing Public 24Q2, the column names in the 26Q3 release, how many
`PortalCompounds.csv` rows have SMILES, the overlap between 24Q4 mutation lines and PRISM lines, and the licences
of the third-party sources behind some annotation columns (OncoKB/COSMIC hotspot lists, CIViC, AlphaMissense, Drug
Repurposing Hub `moa`/`target`). Confirm the counts on first download.

---

## 5. Open chemistry encoders on Hugging Face (ChemBERTa comparison)

All three repos are **not gated** (`"gated": false` from `https://huggingface.co/api/models/<id>`), so no account or
token is needed to download them. "Params" is inferred as weight-file bytes / 4 (float32). CPU feasibility is
inferred from size, not measured.

| Field | ChemBERTa-2 77M-MLM | ChemBERTa 100M-MLM | MoLFormer-XL-both-10pct |
|---|---|---|---|
| Model id | `DeepChem/ChemBERTa-77M-MLM` (also `DeepChem/ChemBERTa-77M-MTR`) | `DeepChem/ChemBERTa-100M-MLM` | `ibm-research/MoLFormer-XL-both-10pct` (`ibm/...` redirects here) |
| URL | https://huggingface.co/DeepChem/ChemBERTa-77M-MLM | https://huggingface.co/DeepChem/ChemBERTa-100M-MLM | https://huggingface.co/ibm-research/MoLFormer-XL-both-10pct |
| Version | last modified 2022-01-20; pin a commit hash when used | last modified 2025-08-18; pin a commit hash | last modified 2026-07-23; card says tested with transformers v5.12.1 (`revision="compat-v4"` for v4) |
| Licence on the model card | **None.** The repo has no README/model card and no licence tag (files: config, tokenizer, `pytorch_model.bin`). The ChemBERTa code repo is MIT (https://github.com/seyonechithrananda/bert-loves-chemistry/blob/master/LICENSE), but that does not cover these weights. | **MIT** (card front matter `license: mit`, https://huggingface.co/DeepChem/ChemBERTa-100M-MLM/blob/main/README.md) | **Apache-2.0** (card front matter `license: apache-2.0`, https://huggingface.co/ibm-research/MoLFormer-XL-both-10pct/blob/main/README.md); code repo also Apache-2.0: https://github.com/IBM/molformer/blob/main/LICENSE |
| OK for a public GitHub repo? | **Unclear** (no licence = no stated permission). Do not ship it or its embeddings. | **Yes** | **Yes**, but it needs `trust_remote_code=True`, which runs Python from the model repo; pin the revision and read that code first. |
| Size | `pytorch_model.bin` 13,734,116 bytes (~3.4M params); 3 layers, hidden 384 | `model.safetensors` 368,569,864 bytes (~92M params); 12 layers, hidden 768 | `model.safetensors` 187,248,784 bytes (~47M params); 12 layers, hidden 768, max 202 tokens |
| CPU inference realistic? | Yes, tiny | Yes for a few hundred molecules at a time; embed the training set once, offline | Yes; embed the training set once, offline |
| Citation | Ahmad W, Simon E, Chithrananda S, Grand G, Ramsundar B. ChemBERTa-2: Towards Chemical Foundation Models. arXiv:2209.01712 (2022) | Same family: cite ChemBERTa-2 and the model page | Ross J, Belgodere B, Chenthamarakshan V, et al. Large-scale chemical language representations capture molecular structure and properties. *Nat. Mach. Intell.* 2022;4:1256-1264. doi:10.1038/s42256-022-00580-7 |
| How we download | `transformers.AutoModel.from_pretrained(id, revision=<hash>)` (cached by `huggingface_hub`) | same | same, plus `trust_remote_code=True` |
| What we use | Pooled embedding of the SMILES, fed to a small head (the ChemBERTa comparison in PLAN.md) | same | `pooler_output` |

No non-commercial (NC) licence was found on any of these. The only licence problem is the missing licence on the
77M models.

---

## 6. Libraries and hosting

Versions are the latest on PyPI on 2026-11-04 (`https://pypi.org/pypi/<name>/json`), with their release dates.
Pin them in `pyproject.toml` / `uv.lock`. numpy 2.5.4 needs Python >= 3.12, so the project should use Python 3.12.
Install with `uv add <name>==<version>`. Sizes are not tracked (installed packages, not shipped data).

| Library | Pin | Released | Licence (link) | Public repo OK? | Citation / credit | What we use |
|---|---|---|---|---|---|---|
| RDKit | `rdkit==2026.9.1` | 2026-10-09 | BSD-3-Clause, https://github.com/rdkit/rdkit/blob/master/license.txt | Yes | RDKit: Open-source cheminformatics, https://www.rdkit.org | SMILES parsing, Morgan fingerprints, scaffolds, Tanimoto, analog transforms. cp312 manylinux wheels exist. |
| scikit-learn | `scikit-learn==1.9.1` | 2026-09-10 | BSD-3-Clause, https://github.com/scikit-learn/scikit-learn/blob/main/COPYING | Yes | Pedregosa et al., JMLR 12, 2011 | baselines, metrics, random forest |
| LightGBM | `lightgbm==4.7.0` | 2026-07-18 | MIT, https://github.com/lightgbm-org/LightGBM/blob/main/LICENSE (github.com/microsoft/LightGBM now redirects to lightgbm-org) | Yes | Ke et al., NeurIPS 2017 | per-target activity models |
| Streamlit | `streamlit==1.66.1` | 2026-10-21 | Apache-2.0, https://github.com/streamlit/streamlit/blob/develop/LICENSE | Yes | https://streamlit.io | the app |
| pandas | `pandas==3.1.0` | 2026-10-22 | BSD-3-Clause, https://github.com/pandas-dev/pandas/blob/main/LICENSE | Yes | https://pandas.pydata.org | tables |
| joblib | `joblib==1.6.0` | 2026-08-31 | BSD-3-Clause, https://github.com/joblib/joblib/blob/main/LICENSE.txt (page opens, checked 2026-11-04; PyPI `license_expression` BSD-3-Clause) | Yes | https://joblib.readthedocs.io | saving and loading the trained models |
| numpy | `numpy==2.5.4` | 2026-10-10 | BSD-3-Clause (bundled parts: 0BSD, MIT, Zlib, CC0-1.0), https://github.com/numpy/numpy/blob/main/LICENSE.txt | Yes | Harris et al., Nature 585, 2020 | arrays |
| pytest | `pytest==9.2.0` | 2026-10-27 | MIT, https://github.com/pytest-dev/pytest/blob/main/LICENSE | Yes | https://pytest.org | tests (dev only) |
| ruff | `ruff==0.17.3` | 2026-10-27 | MIT, https://github.com/astral-sh/ruff/blob/main/LICENSE | Yes | https://docs.astral.sh/ruff | lint (dev only) |
| uv | `uv 0.13.7` (a tool, not a dependency) | 2026-11-03 | MIT OR Apache-2.0, https://github.com/astral-sh/uv/blob/main/LICENSE-APACHE | Yes | https://docs.astral.sh/uv | environment and lock file |
| chembl_webresource_client | `chembl_webresource_client==0.10.9` | 2024-02-26 | Apache-2.0, https://github.com/chembl/chembl_webresource_client/blob/master/LICENSE | Yes | https://github.com/chembl/chembl_webresource_client | optional ChEMBL client (plain HTTP also works) |
| transformers | `transformers==5.22.1` | 2026-10-30 | Apache-2.0, https://github.com/huggingface/transformers/blob/main/LICENSE | Yes | Wolf et al., EMNLP 2020 (demos) | encoders (ChemBERTa comparison only) |
| torch | `torch==2.15.0` | 2026-10-28 | BSD-3-Clause style, https://github.com/pytorch/pytorch/blob/main/LICENSE | Yes | Paszke et al., NeurIPS 2019 | encoders (ChemBERTa comparison only) |

pandas 3.1.0, pytest 9.2.0, ruff 0.17.3, transformers 5.22.1, torch 2.15.0 and uv 0.13.7 are under two weeks old.
If one breaks, drop to the previous release and note it here.

### Hosting

| Field | Hugging Face Spaces | Streamlit Community Cloud (fallback) |
|---|---|---|
| URL | https://huggingface.co/docs/hub/spaces-overview | https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app |
| Free hardware | CPU Basic: 2 vCPU, 16 GB RAM, 50 GB disk that is not persistent, $0/hour | "as of February 2024": CPU 0.078 to 2 cores, memory 690 MB min to 2.7 GB max, storage up to 50 GB |
| Sleep policy | Free hardware sleeps after 48 hours without use (https://huggingface.co/docs/hub/spaces-gpus); a visitor wakes it | "All apps without traffic for 12 hours go to sleep"; a visitor wakes it |
| Streamlit supported? | **Not on a free account any more.** The built-in Streamlit SDK "is deprecated"; Streamlit now needs the Docker SDK plus the Streamlit template (https://huggingface.co/docs/hub/spaces-sdks-streamlit). And "Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts". Only Static Spaces are free for everyone; free personal accounts can host up to 2 Gradio Spaces on ZeroGPU. This text entered the docs on 2026-07-21 (hub-docs commit "Update Spaces docs: paid plan required for compute Spaces, ZeroGPU free tier (#2624)"). | Yes, free, deploys from a GitHub repo |
| Account needed | Hugging Face account (and PRO for a Docker Space) | Streamlit Community Cloud account linked to GitHub |

---

## Blockers

1. **Hugging Face Spaces cannot host the Streamlit app for $0.** Streamlit on Spaces now needs a Docker Space, and
   Docker Spaces need a paid PRO plan (https://huggingface.co/docs/hub/spaces-overview and
   https://huggingface.co/docs/hub/spaces-sdks-streamlit, read 2026-11-04). This conflicts with PLAN.md ("Streamlit on
   Hugging Face Spaces") and the $0 cap. Options for Prakhar to choose from: Streamlit Community Cloud (already the
   fallback; 2.7 GB memory ceiling, sleeps after 12 h), a Gradio UI on a free ZeroGPU Space, or paying for PRO.
2. **GDSC and Cell Model Passports use a custom non-commercial, non-transferable licence**
   (https://depmap.sanger.ac.uk/documentation/data-usage-policy/). Raw files must not be committed to the public repo
   (download script only). **Unclear:** whether a public app may show GDSC sensitivities and CMP mutations to
   visitors, and whether models trained on them may be published. Suggested fix: Prakhar emails depmap@sanger.ac.uk,
   describes the free, educational, non-commercial hackathon app and asks (an outward action, so his call). Until
   then, keep loop-2 data and models out of git.
   **Alternative found (2026-11-04, section 3b):** Broad's last Figshare deposits are CC BY 4.0 and need no email:
   DepMap 24Q4 Public (mutations, `Model.csv`) + PRISM Repurposing 20Q2 secondary screen (dose-response `auc` with
   `smiles`), joined on `ModelID` = `depmap_id` (`ACH-...`). Both may go in a public repo and app with attribution.
   Do **not** use newer DepMap releases (25Q2, 26Q1, 26Q3): since 2025 the portal terms limit ML use to internal use
   or non-profit research sharing and make rehosting bind every visitor, and the portal is captcha-gated. **Still
   unclear:** Broad has no formal written statement that the old CC BY copies stay usable for new ML work (only
   forum posts by DepMap staff plus the irrevocable CC BY text); the licences of third-party lists behind some
   annotation columns (OncoKB/COSMIC hotspots, CIViC, AlphaMissense, Drug Repurposing Hub); and the cell-line overlap
   and counts (need a download). Choosing GDSC (ask Sanger) or DepMap/PRISM (switch now) is Prakhar's call.
3. **cancerrxgene.org is gone (HTTP 410).** GDSC downloads now come from Cell Model Passports. Two different files
   named `GDSC2_fitted_dose_response_27Oct23.xlsx` exist (22,112,537 vs 21,330,376 bytes); use the CMP link and
   record its SHA-256.
4. **ChemBERTa-2 77M weights have no licence** (`DeepChem/ChemBERTa-77M-MLM` and `-MTR`: no model card, no licence
   tag). Use `DeepChem/ChemBERTa-100M-MLM` (MIT) or `ibm-research/MoLFormer-XL-both-10pct` (Apache-2.0) instead.
5. **Tox21 data has no stated licence** (MoleculeNet file and NCATS page). Probably US-government public domain, not
   verified. Do not commit the raw file; download it and cite.
6. **ChEMBL is share-alike (CC BY-SA 3.0).** Not a blocker, but any ChEMBL-derived data published in the repo or the
   app must carry CC BY-SA 3.0 and show "chembl_37" plus the ChEMBL URL. Say so next to the code licence in the
   README.
7. **MoLFormer needs `trust_remote_code=True`.** Pin the revision and review the remote code before running it.
8. **Accounts:** none needed for any data or model download (all checked without logging in). Hosting needs a
   Streamlit Community Cloud account (GitHub sign-in) or a Hugging Face account; Prakhar creates these himself.
9. **Not verified here:** the Cell Model Passports mutation column names (they need a download). Confirm on first
   pull.

No NC-only licence was found on any model. No other blockers were found.

---

## README credit lines

Paste into the README under "Credits" (trim the list to what the shipped code actually uses).

```markdown
### Data
- **ChEMBL** (bioactivity data). ChEMBL data is from http://www.ebi.ac.uk/chembl - the version of ChEMBL is chembl_37.
  Licensed under CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/). Any ChEMBL-derived data in this
  repository is shared under the same licence. Mendez D, et al. ChEMBL: towards direct deposition of bioassay data.
  Nucleic Acids Res. 2019;47(D1):D930-D940. doi:10.1093/nar/gky1075
- **Tox21** (12 toxicity assays) as distributed by MoleculeNet/DeepChem
  (https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz). Wu Z, et al. MoleculeNet: a benchmark for
  molecular machine learning. Chem. Sci. 2018;9:513-530. doi:10.1039/C7SC02664A. Huang R, et al. Tox21Challenge to
  build predictive models of nuclear receptor and stress response pathways as mediated by exposure to environmental
  chemicals and drugs. Front. Environ. Sci. 2016;3:85. doi:10.3389/fenvs.2015.00085
- **DepMap 24Q4 Public** (hotspot mutations, cell-line annotations, compound map), Broad Institute. Figshare+,
  doi:10.25452/figshare.plus.27993248. CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- **PRISM Repurposing 20Q2** (secondary-screen dose-response), Broad Institute; DepMap, Corsello S, Kocak M, Golub T.
  figshare, doi:10.6084/m9.figshare.20564034. CC BY 4.0. Corsello SM, Nagari RT, Spangler RD, et al. Discovering
  the anticancer potential of non-oncology drugs by systematic viability profiling. *Nat Cancer.*
  2020;1(2):235-248. doi:10.1038/s43018-019-0018-6
- Tsherniak A, Vazquez F, Montgomery PG, et al. Defining a Cancer Dependency Map. *Cell.* 2017;170(3):564-576.e16.
  doi:10.1016/j.cell.2017.06.010
- Mutation data: Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer Cell
  Line Encyclopedia. *Nature.* 2019;569(7757):503-508. doi:10.1038/s41586-019-1186-3
- Not used: Sanger GDSC and Cell Model Passports (non-transferable policy; see Blockers 2), so no credit line.

### Models
- **ChemBERTa-100M-MLM** (DeepChem, MIT), https://huggingface.co/DeepChem/ChemBERTa-100M-MLM. Ahmad W, et al.
  ChemBERTa-2: Towards Chemical Foundation Models. arXiv:2209.01712
- **MoLFormer-XL-both-10pct** (IBM Research, Apache-2.0), https://huggingface.co/ibm-research/MoLFormer-XL-both-10pct.
  Ross J, et al. Nat. Mach. Intell. 2022;4:1256-1264. doi:10.1038/s42256-022-00580-7

### Libraries
RDKit (BSD-3-Clause), scikit-learn (BSD-3-Clause), LightGBM (MIT), Streamlit (Apache-2.0), pandas (BSD-3-Clause),
NumPy (BSD-3-Clause), joblib (BSD-3-Clause), PyTorch (BSD-3-Clause), Hugging Face Transformers (Apache-2.0), chembl_webresource_client
(Apache-2.0), pytest (MIT), ruff (MIT), uv (MIT or Apache-2.0).
```
