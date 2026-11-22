#!/usr/bin/env python3
"""Build the distributable .skill / .zip package for ai-brief-podcast.

Why a custom builder instead of skill-creator's package_skill.py:
  The package must carry the five platform-required frontmatter fields
  (version / display_name / display_name_en / description_zh / description_en)
  in SKILL.md. skill-creator's local quick_validate rejects those as
  "unexpected key", so its packager cannot be used. We build the zip with
  the standard library instead. The format is identical: a .skill file is
  just a zip whose top-level entry is the skill directory.

Packaging recipe (keep in sync with docs/RELEASE.md):
  INCLUDE:  SKILL.md, assets/, references/, scripts/
  EXCLUDE:  evals/ (evaluation assets), listing/ (marketplace copy),
            README.md, .gitignore, this builder and any __pycache__/venv.
  TOP-LEVEL DIR INSIDE ARCHIVE: ai-brief-podcast-skill/

Usage:
  python scripts/build_skill.py
  python scripts/build_skill.py --out dist
"""

import argparse
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPLEVEL = "ai-brief-podcast-skill"
INCLUDE_FILES = ["SKILL.md"]
INCLUDE_DIRS = ["assets", "references", "scripts"]
EXCLUDE_PARTS = {"__pycache__", ".git", ".venv", "evals", "listing"}


def read_version() -> str:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^version:\s*[\"']?([^\s\"']+)", text, re.M)
    if not m:
        raise SystemExit("ERROR: no 'version:' field found in SKILL.md frontmatter")
    return m.group(1).strip()


def collect() -> list[Path]:
    files: list[Path] = []
    for name in INCLUDE_FILES:
        p = ROOT / name
        if p.is_file():
            files.append(p)
    for d in INCLUDE_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if (
                p.is_file()
                and p.name != "build_skill.py"  # the builder itself is not shipped
                and not (set(p.relative_to(base).parts) & EXCLUDE_PARTS)
            ):
                files.append(p)
    return files


def build(out_dir: Path, version: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{TOPLEVEL}-v{version}"
    targets = [out_dir / f"{stem}.skill", out_dir / f"{stem}.zip"]
    files = collect()
    # Normalize text files to LF so the archive is byte-stable across
    # Windows (CRLF checkout) and Linux/Mac, and matches the published base.
    text_suffixes = {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".html"}
    for target in targets:
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files:
                arcname = f"{TOPLEVEL}/{p.relative_to(ROOT).as_posix()}"
                if p.suffix.lower() in text_suffixes:
                    data = p.read_bytes().replace(b"\r\n", b"\n")
                    z.writestr(arcname, data)
                else:
                    z.write(p, arcname)
        print(f"built: {target} ({target.stat().st_size} bytes)")
    print(f"contained files ({len(files)}):")
    for p in files:
        print(f"  {TOPLEVEL}/{p.relative_to(ROOT).as_posix()}")
    return targets[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist", help="output directory (default: dist)")
    args = ap.parse_args()
    version = read_version()
    print(f"version: {version}")
    build(ROOT / args.out, version)


if __name__ == "__main__":
    main()
