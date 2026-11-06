"""Re-derive every published figure from the results files and check the docs still say it.

Usage: uv run python scripts/check_numbers.py            (exit 0 if every figure matches, 1 otherwise)
       uv run python scripts/check_numbers.py --strict   (also fail if any figure had no source to check)

CI runs the plain form, because `models/`, `data/` and `dist/` are git-ignored and five figures have no source
there; it prints which ones it skipped. Run `--strict` on a full checkout before submitting, so a figure cannot
pass by being unverifiable.

Each check recomputes a figure from `results/*.json`, the bundle manifest or the repo itself, formats it the way
the docs write it, and then asserts that string is present in every document that claims it. So it catches drift
in both directions: a results file that changes under a document, and a document edited away from its source.
It replaces reading a figure off a prose summary, which can itself be the error.

Figures this script cannot own, because they are not in any file: wall-clock timings ("about 15 minutes to
train"), which depend on the machine, and the commit-trailer counts in the AI disclosure, which change with every
commit and are therefore pinned to a named commit in the text instead.
"""

import json
import pathlib
import re
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
README, WRITEUP, VIDEO = "README.md", "docs/submission.md", "docs/video.md"


def load(name: str) -> dict:
    return json.loads((ROOT / "results" / f"{name}.json").read_text(encoding="utf-8"))


A, L, T = load("activity_models"), load("loop2_models"), load("tox21_models")
GENES, DRUGS, TASKS = A["genes"], L["drugs"], T["tasks"]
POWERED = {k: v for k, v in DRUGS.items() if not v["underpowered"]}

checks: list[tuple[str, str, tuple[str, ...]]] = []
skipped: list[tuple[str, str]] = []


def claim(label: str, text: str, *docs: str) -> None:
    """`text` is built from the data; every doc named must contain it verbatim."""
    checks.append((label, text, docs))


def present(rel: str, what: str) -> bool:
    """True if a git-ignored source is in this checkout; otherwise record what cannot be checked and why."""
    if (ROOT / rel).exists():
        return True
    skipped.append((what, rel))
    return False


def best(d: dict, key, hi: bool):
    k = (max if hi else min)(d, key=lambda k: key(d[k]))
    return k, key(d[k])


# ---- loop 1: activity -------------------------------------------------------
claim("activity targets", f"{len(GENES)} cancer protein targets", README)
for model, name in (("rf", "random forest"), ("nn1", "1-NN")):
    for hi in (False, True):
        gene, v = best(GENES, lambda g, m=model: g[m]["roc_auc"], hi)
        claim(f"activity {name} roc_auc {'max' if hi else 'min'}", f"{v:.3f} ({gene})", README)
claim("activity rf beats 1-NN on roc_auc",
      f"{sum(GENES[g]['rf']['roc_auc'] > GENES[g]['nn1']['roc_auc'] for g in GENES)} of {len(GENES)}", README)
claim("activity rf below 1-NN on balanced accuracy",
      f"{sum(GENES[g]['rf']['balanced_acc'] < GENES[g]['nn1']['balanced_acc'] for g in GENES)} of {len(GENES)}",
      README)
fr = [g["test_active_frac"] for g in GENES.values()]
claim("random active-class PR-AUC range", f"{min(fr):.2f} to {max(fr):.2f}", README)
for gene in ("BRAF", "EGFR", "ALK"):
    d = GENES[gene]["dataset"]
    pct = 100 * d["rows_mutant_dropped"] / (d["rows_kept"] + d["rows_mutant_dropped"])
    claim(f"{gene} variant rows dropped", f"{pct:.1f}%", README)
sv = A["split_variance"]["genes"]
gene, spread = best(sv, lambda g: max(g["nn1"]) - min(g["nn1"]), True)
claim("split moves roc_auc by up to (1-NN)", f"{spread:.4f} ({gene}", README)
gene, spread = best(sv, lambda g: max(g["rf"]) - min(g["rf"]), True)
# The Analogs tab prints this figure in prose to justify calling its own ranking flat, so the tab is checked too.
claim("split moves roc_auc by up to (random forest)", f"{spread:.3f}", VIDEO, "src/molscreen/ui_analogs.py")
for gene in ("ABL1", "BCL2"):
    lead = GENES[gene]["rf"]["roc_auc"] - GENES[gene]["nn1"]["roc_auc"]
    claim(f"{gene} seed-0 lead over 1-NN", f"+{lead:.4f}", README)
cdk6 = GENES["CDK6"]
claim("CDK6 roc_auc (spoken)", f"{cdk6['rf']['roc_auc']:.3f}", VIDEO)
lo, hi = cdk6["rf"]["roc_auc_ci95"]
claim("CDK6 roc_auc CI (spoken)", f"{lo:.3f} to {hi:.3f}", VIDEO)

# ---- loop 2: drug response --------------------------------------------------
claim("drugs screened", f"{len(DRUGS)} drugs", README)
claim("drugs not underpowered", f"{len(POWERED)} drugs that are not underpowered", README)
for model in ("logreg", "nn1"):
    claim(f"median roc_auc {model} over the powered drugs",
          f"{st.median(v[model]['roc_auc'] for v in POWERED.values()):.3f}", README)
# "weak" is defined in results/loop2_models.md: the shipped model's CI lower bound is at or below 0.5.
weak = sum(v["logreg"]["roc_auc_ci95"][0] <= 0.5 for v in DRUGS.values())
claim("weak shipped models", f"{weak} of {len(DRUGS)}", README)
below = sum(v["logreg"]["roc_auc"] < 0.5 for v in POWERED.values())
claim("models below 0.5 among the powered drugs",  # the phrase, not a bare number that could match anything
      f"{below} below 0.5 over the {len(POWERED)} drugs that are not underpowered", README)
if present("data/depmap/derived/hotspot_binary.csv", "hotspot genes"):  # one column is the cell-line id
    with (ROOT / "data" / "depmap" / "derived" / "hotspot_binary.csv").open(encoding="utf-8") as fh:
        n_genes = len(fh.readline().rstrip("\n").split(",")) - 1
    claim("hotspot genes", f"{n_genes} genes", README)
sp = L["split"]
claim("leave-lineage-out test set",
      f"{sp['n_test_lines']} test cell lines in {len(sp['test_lineages'])} lineages", README)
claim("sensitive threshold", f"{L['sensitive_percentile']}th percentile", README)

# ---- loop 3: Tox21 ----------------------------------------------------------
claim("Tox21 assays", f"{len(TASKS)} Tox21", README, VIDEO)
for hi in (False, True):
    assay, v = best(TASKS, lambda t: t["rf"]["roc_auc"], hi)
    claim(f"Tox21 rf roc_auc {'max' if hi else 'min'}", f"{v:.3f} ({assay})", README)
claim("Tox21 rf beats 1-NN on roc_auc",
      f"{sum(TASKS[t]['rf']['roc_auc'] > TASKS[t]['nn1']['roc_auc'] for t in TASKS)} of {len(TASKS)}", README)
claim("Tox21 rf below 1-NN on balanced accuracy",
      f"{sum(TASKS[t]['rf']['balanced_acc'] < TASKS[t]['nn1']['balanced_acc'] for t in TASKS)} of {len(TASKS)}",
      README)

# ---- loop 4: analogs --------------------------------------------------------
src = (ROOT / "src" / "molscreen" / "analogs.py").read_text(encoding="utf-8")
n_transforms = len(re.findall(r'^\s{4}"[^"]+": "', src, re.MULTILINE))
SPOKEN = {8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}  # the script spells what is said aloud
claim("analog transforms", f"list of {SPOKEN[n_transforms]}", VIDEO)
floor = float(re.search(r"^FLAT_SPREAD = ([\d.]+)", (ROOT / "src" / "molscreen" / "ui_analogs.py")
                        .read_text(encoding="utf-8"), re.MULTILINE).group(1))
rf_move = max(max(g["rf"]) - min(g["rf"]) for g in sv.values())
assert floor >= rf_move, f"FLAT_SPREAD {floor} must cover the {rf_move:.4f} the forests move across seeds"

# ---- the models bundle ------------------------------------------------------
# models/, data/ and dist/ are git-ignored, so these have no source in CI or in a fresh clone. Each one is
# recorded as skipped rather than quietly dropped, and --strict turns a skip into a failure for the run that
# matters: the one on a full checkout before submitting.
have_manifest = present("models/MANIFEST.json", "models in the bundle")
have_tables = present("data/depmap/derived", "DepMap tables in the bundle")
files: list = []
if have_manifest:
    man = json.loads((ROOT / "models" / "MANIFEST.json").read_text(encoding="utf-8"))
    files = man["files"] if isinstance(man, dict) and "files" in man else man
    claim("models in the bundle", f"{len(files)} models", README)
if have_tables:
    tables = sorted((ROOT / "data" / "depmap" / "derived").glob("*.csv"))
    claim("DepMap tables in the bundle", f"{len(tables)} DepMap tables", README)
if have_manifest and have_tables:  # the download count is the two together, plus PULL_INFO.json
    claim("files verified on download", f"{len(files) + len(tables) + 1} files verified", README)
else:
    skipped.append(("files verified on download", "models/MANIFEST.json and data/depmap/derived"))
if present("dist/models-v2.zip", "bundle size"):
    claim("bundle size", f"{(ROOT / 'dist' / 'models-v2.zip').stat().st_size / 1e6:.0f} MB zip", README)

# ---- the repo itself --------------------------------------------------------
n_tests = sum(len(re.findall(r"^def test_", p.read_text(encoding="utf-8"), re.MULTILINE))
              for p in sorted((ROOT / "tests").glob("test_*.py")))
claim("tests in the suite", f"{n_tests} tests", README)

# The video script states its own narration length, which is the figure that keeps it under the 6:00 limit.
narration = [ln[2:] for ln in (ROOT / VIDEO).read_text(encoding="utf-8").splitlines() if ln.startswith("> ")]
words = len(" ".join(narration).replace("**(cut first)**", "").split())
claim("narration words in the script", f"{words} words", VIDEO)


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    bad = 0
    for label, text, docs in checks:
        for doc in docs:
            body = (ROOT / doc).read_text(encoding="utf-8")
            ok = text in body
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'}  {doc:27s}  {label:48s}  {text!r}")
    for what, rel in skipped:
        print(f"skip  {'(no source here)':27s}  {what:48s}  needs {rel}")
    print(f"\n{len(checks)} figures checked, {bad} mismatch(es), {len(skipped)} skipped for want of a source.")
    if skipped:
        print("Those sources are git-ignored, so this run cannot have checked them. Re-run with --strict on a "
              "checkout that has the models and the DepMap tables before submitting.")
    return 1 if bad or (strict and skipped) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
