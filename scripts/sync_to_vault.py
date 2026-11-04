#!/usr/bin/env python3
"""Mirror a project's working files into an Obsidian vault, so the vault holds a full copy.

    python scripts/sync_to_vault.py --vault "C:/Users/you/Documents/claude brain" --name my-project
    python scripts/sync_to_vault.py --src ../other-repo --vault "..." --name other-repo --dry-run

The copy goes to <vault>/Projects/<name>/repo/. It includes every file git tracks plus
every file git would track (so it follows .gitignore: data, virtual environments and
.env files stay out). If the folder is not a git repo it walks the tree and skips the
usual junk. It also skips:
  - files over --max-mb (default 5), listed in the manifest
  - files whose names or contents look like secrets (keys, tokens), listed in the manifest
It never deletes anything in the vault. Files that disappeared from the project are listed
as "stale" in the manifest so you can decide. The vault path can also come from the
CLAUDE_VAULT environment variable.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

JUNK_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache",
    ".mypy_cache", ".ipynb_checkpoints", ".idea", ".vscode", "dist", "build",
}
SECRET_NAMES = re.compile(
    r"(^|/)(\.env(\..*)?|[^/]*\.(pem|key|p12|pfx)|id_rsa[^/]*|kaggle\.json"
    r"|credentials(\.json|\.ya?ml)?|secrets?\.(json|ya?ml|toml|env|txt)|\.?tokens?(\.txt|\.json)?)$",
    re.IGNORECASE,
)
SECRET_ALLOW = re.compile(r"\.(example|sample|template)$|\.md$", re.IGNORECASE)
SECRET_CONTENT = re.compile(
    r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|hf_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_\-]{30,}"
    r"|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9\-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:api[_-]?key|secret|token|password)\s*[=:]\s*['\"][A-Za-z0-9_\-\.]{20,}['\"])"
)
TEXT_SCAN_LIMIT = 2 * 1024 * 1024


def list_files(src: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(src), "ls-files", "-co", "--exclude-standard", "-z"],
            capture_output=True, check=True,
        ).stdout.decode("utf-8", "surrogateescape")
        files = [f for f in out.split("\0") if f]
        return [f for f in files if (src / f).is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    files = []
    for root, dirs, names in os.walk(src):
        dirs[:] = [d for d in dirs if d not in JUNK_DIRS]
        for name in names:
            path = Path(root) / name
            files.append(path.relative_to(src).as_posix())
    return files


def skip_reason(src: Path, rel: str, max_bytes: int) -> str | None:
    parts = rel.split("/")
    if any(p in JUNK_DIRS for p in parts):
        return "junk folder"
    path = src / rel
    if SECRET_NAMES.search(rel) and not SECRET_ALLOW.search(rel):
        return "name looks like a secret"
    size = path.stat().st_size
    if size > max_bytes:
        return f"over size limit ({size / 1e6:.1f} MB)"
    if size <= TEXT_SCAN_LIMIT:
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            return None
        if SECRET_CONTENT.search(text):
            return "content looks like a secret"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--src", type=Path, default=Path.cwd(), help="project folder (default: current folder)")
    parser.add_argument("--vault", type=Path, default=os.environ.get("CLAUDE_VAULT"), help="vault folder")
    parser.add_argument("--name", help="folder name under Projects/ (default: the project folder's name)")
    parser.add_argument("--max-mb", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.vault:
        print("Give --vault or set CLAUDE_VAULT.", file=sys.stderr)
        return 2
    src = args.src.resolve()
    name = args.name or src.name
    vault = Path(args.vault)
    dest = vault / "Projects" / name / "repo"
    max_bytes = int(args.max_mb * 1e6)

    copied, unchanged, skipped = [], [], []
    wanted = set()
    for rel in sorted(list_files(src)):
        reason = skip_reason(src, rel, max_bytes)
        if reason:
            skipped.append((rel, reason))
            continue
        wanted.add(rel)
        source, target = src / rel, dest / rel
        if target.exists() and target.stat().st_size == source.stat().st_size and target.read_bytes() == source.read_bytes():
            unchanged.append(rel)
            continue
        copied.append(rel)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    stale = []
    if dest.exists():
        for path in dest.rglob("*"):
            if path.is_file():
                rel = path.relative_to(dest).as_posix()
                if rel != "_MANIFEST.md" and rel not in wanted:
                    stale.append(rel)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Repo mirror: {name}",
        "",
        f"Last synced {stamp} from `{src}`. Back to [[Projects/{name}/context|{name}]].",
        "",
        f"- Files in the mirror: {len(wanted)} ({len(copied)} new or changed this run, {len(unchanged)} unchanged)",
        f"- Skipped: {len(skipped)}",
        f"- Stale (in the mirror, no longer in the project): {len(stale)}",
        "",
        "The mirror follows .gitignore, so data, virtual environments and .env files are not here.",
        "Nothing is ever deleted from this folder by the sync.",
        "",
    ]
    if skipped:
        lines += ["## Skipped", ""] + [f"- `{rel}`: {why}" for rel, why in skipped] + [""]
    if stale:
        lines += ["## Stale", ""] + [f"- `{rel}`" for rel in stale] + [""]
    lines += ["## Files", ""] + [f"- `{rel}`" for rel in sorted(wanted)] + [""]

    if args.dry_run:
        print(f"[dry run] would copy {len(copied)}, {len(unchanged)} unchanged, {len(skipped)} skipped, {len(stale)} stale")
    else:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"copied {len(copied)}, {len(unchanged)} unchanged, {len(skipped)} skipped, {len(stale)} stale -> {dest}")
    for rel, why in skipped[:20]:
        print(f"  skipped {rel}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
