# Evaluation protocol: mutations to drugs (loop 2)

Written 2026-11-04, before any loop-2 data was downloaded or processed. Changing a rule after seeing data needs a
dated note here saying what changed and why. Everything here is about **cell lines, not patients**. The app is a
**research and learning tool, not medical advice**.

## Sources (all CC BY 4.0, file IDs from `docs/data-registry.md` section 3b)
- DepMap 24Q4 Public (Figshare+, doi:10.25452/figshare.plus.27993248): `OmicsSomaticMutationsMatrixHotspot.csv`
  (51065750), `OmicsSomaticMutations.csv` (51065732), `Model.csv` (51065297), `PortalCompounds.csv` (51065762).
- PRISM Repurposing 20Q2 (figshare, doi:10.6084/m9.figshare.20564034): secondary-screen dose-response curve
  parameters (36794595). `scripts/pull_depmap.py` records URL, bytes and SHA-256 of each file in `PULL_INFO.json`.

## Mutation vector
The hotspot matrix, one row per `ModelID`, one column per gene (`SYMBOL (EntrezID)` renamed to `SYMBOL`). Values
0/1/2 become 0/1: 2 only means the summed allele frequency is above 0.95, and the app asks whether a gene is
mutated, not how many copies. All genes are kept in the derived table; the app's input is a list of gene symbols.

## Sensitivity
`auc` of the PRISM dose-response fit (lower = more sensitive). Drop rows with `passed_str_profiling` False (the
cell line's identity check failed) and rows with no `auc`. A compound is the Broad ID without its batch suffix
(`BRD-K12345678`). One value per (cell line, compound): the **median** `auc` over all remaining rows, which pools
the replicate screens (HTS002, MTS005, MTS006, MTS010). Name, SMILES and targets come from the PRISM rows.

## Join
PRISM `depmap_id` = DepMap `ModelID` = hotspot-matrix row ID. Never join on names. Report the overlap.

## Nearest cell lines (a lookup, not a prediction)
Query = 1 for each listed gene that is a matrix column, 0 elsewhere; listed genes not in the matrix are reported
and ignored (none in the matrix is an error). Rank by the number of shared mutated genes (query genes the
line carries), then by Jaccard similarity between the query and the line's 0/1 vector (0 when both are empty),
then by cell line name (amended 2026-11-04, see Changes). Top k = 10. It shows which screened cell lines
carry similar hotspot mutations and what was measured on them. It does not predict anything for a person.

## Evidence shown per nearest cell line
Name, lineage, primary disease (never `Age`, `Sex` or `PatientRace`; they are dropped when `Model.csv` is read and
never written), shared mutated genes, and its 10 most sensitive compounds (lowest `auc`) with name, SMILES and
target genes.

## Per-drug models (later task; rules fixed now)
- Drugs with at least 300 screened cell lines that are also in the hotspot matrix.
- Label: sensitive when `auc` is below the 10th percentile of that drug's `auc` (threshold from training lines only).
- Split: leave-lineage-out by `OncotreeLineage` (same greedy rule as `molscreen.chem.scaffold_split`, lineage as
  the group), so no lineage is in both train and test and a model cannot memorise a lineage.
- Baselines as in `docs/evaluation.md`: majority class (ROC-AUC 0.5) and 1-nearest-neighbour by hotspot Jaccard.
- Metrics: ROC-AUC with a bootstrap 95% CI (headline), PR-AUC of the sensitive class next to its prevalence,
  balanced accuracy; test size and number of sensitive lines always shown. Too few sensitive lines: say so.

## Reporting
Counts and the worked example go to `results/loop2_data.md`, built from one run of `molscreen.depmap`.

## Changes
- 2026-11-04, after the download, before the lookup was first run: nearest cell lines are searched only among
  lines that have at least one PRISM `auc` after QC. Why: only 726 of the 1,929 hotspot-matrix lines are in PRISM,
  so most neighbours would otherwise have no drug evidence to show.
- 2026-11-04, after the first lookup run, decided by Prakhar: nearest cell lines rank by the **number of shared
  mutated genes first**, then Jaccard, then cell line name (was: Jaccard, then name). Each result also carries
  `n_shared`. Why: plain Jaccard rewards lines that carry nothing but the listed genes, so a line with 2 of 3
  listed genes and no other hotspot outranked a line with all 3 plus other hotspots. For KRAS/TP53/STK11, 43
  screened lines tied at Jaccard 0.667 and the top 10 was decided by the name sort. Rejected: plain Jaccard;
  weighting genes by rarity.
