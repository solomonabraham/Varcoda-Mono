#!/usr/bin/env python3
"""Rename the family everywhere in the project.

    python scripts/rename-family.py "New Name" [--dry-run]

The family name appears in the font name tables, file names, tests and
documentation.  This script rewrites all of them consistently:

    Varcoda Mono  ->  New Name        (display name, name IDs 1/4/16)
    VarcodaMono   ->  NewName         (PostScript name, file names)
    varcoda-mono  ->  new-name        (repository / package slug)

and renames sources/*.ufo.  Afterwards rebuild and test:

    python scripts/build-fonts.py && python -m pytest tests

Compiled fonts and generated images under the old name are left in place;
delete them once the rebuild has passed.  tests/baseline/ is never touched.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from fontsrc import build  # noqa: E402

TEXT_EXT = {".py", ".md", ".txt", ".yml", ".yaml", ".toml", ".json", ".css", ".html", ".fea", ".cfg", ".svg", ""}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "baseline", "fonts", "releases", "sources", "proofs"}
TEXT_NAMES = {"LICENSE", ".gitignore", ".editorconfig", ".gitattributes"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help='new family name, e.g. "Vector Mono"')
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    new = " ".join(args.name.split())
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*( [A-Za-z0-9]+)*", new):
        sys.exit("use letters, digits and single spaces only")
    old = build.FAMILY
    pairs = [(old, new), (old.replace(" ", ""), new.replace(" ", "")),
             (old.lower().replace(" ", "-"), new.lower().replace(" ", "-"))]
    if old == new:
        sys.exit("the family is already called %r" % new)
    changed = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1]
            if f not in TEXT_NAMES and (ext not in TEXT_EXT or ext == "" and f not in TEXT_NAMES):
                continue
            path = os.path.join(base, f)
            try:
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            out = text
            for a, b in pairs:
                out = out.replace(a, b)
            if out != text:
                changed += 1
                print("  rewrite %s" % os.path.relpath(path, ROOT))
                if not args.dry_run:
                    with open(path, "w", encoding="utf-8", newline="") as fh:
                        fh.write(out)
    src = os.path.join(ROOT, "sources")
    for d in sorted(os.listdir(src)) if os.path.isdir(src) else []:
        if d.startswith(pairs[1][0] + "-") and d.endswith(".ufo"):
            target = d.replace(pairs[1][0], pairs[1][1], 1)
            print("  rename  sources/%s -> sources/%s" % (d, target))
            if not args.dry_run:
                os.rename(os.path.join(src, d), os.path.join(src, target))
    print("%s%d files rewritten: %r -> %r.  Now rebuild: python scripts/build-fonts.py" % (
        "(dry run) " if args.dry_run else "", changed, old, new))


if __name__ == "__main__":
    main()
