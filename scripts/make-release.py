#!/usr/bin/env python3
"""Build releases/VarcodaMono-<release>.zip.

    python3 scripts/make-release.py              # the font package for end users
    python3 scripts/make-release.py --project    # additionally a ZIP of the whole project

The font package holds what somebody needs to install and use the family:
the font files (TTF, OTF, WOFF2), the license, the documentation, a specimen
and the self-contained browser test page.  Archives are deterministic
(sorted entries, fixed timestamps).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from fontsrc import build  # noqa: E402

STYLES = ["Light", "Regular", "Medium", "SemiBold", "Bold",
          "LightItalic", "Italic", "MediumItalic", "SemiBoldItalic", "BoldItalic"]
PACKAGE = "VarcodaMono-%s.zip" % build.RELEASE
PROJECT = "varcoda-mono-%s-project.zip" % build.RELEASE


def _stamp():
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", build.BUILD_EPOCH))
    return time.gmtime(epoch)[:6]


def _add(zf, src, arcname):
    info = zipfile.ZipInfo(arcname, date_time=_stamp())
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    with open(src, "rb") as fh:
        zf.writestr(info, fh.read(), compresslevel=9)


def package_files():
    files = [("README.md", "README.md"), ("LICENSE", "OFL.txt"), ("CHANGELOG.md", "CHANGELOG.md"),
             ("QUALITY_REPORT.md", "QUALITY_REPORT.md"),
             ("assets/specimen-dark.png", "specimen.png"),
             ("tests/rendering-tests/index.html", "rendering-test.html"),
             ("fonts/webfonts/varcoda-mono.css", "fonts/webfonts/varcoda-mono.css")]
    for s in STYLES:
        files.append(("fonts/VarcodaMono-%s.ttf" % s, "fonts/VarcodaMono-%s.ttf" % s))
        files.append(("fonts/otf/VarcodaMono-%s.otf" % s, "fonts/otf/VarcodaMono-%s.otf" % s))
        files.append(("fonts/webfonts/VarcodaMono-%s.woff2" % s, "fonts/webfonts/VarcodaMono-%s.woff2" % s))
    return files


def make_package(root):
    missing = [src for src, _ in package_files() if not os.path.isfile(os.path.join(root, src))]
    if missing:
        sys.exit("cannot build the package, missing: %s\n(run build-fonts.py, make-specimens.py and the tests first)"
                 % ", ".join(missing))
    out = os.path.join(root, "releases", PACKAGE)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    top = "VarcodaMono-%s" % build.RELEASE
    with zipfile.ZipFile(out, "w") as zf:
        for src, arc in sorted(package_files(), key=lambda t: t[1]):
            _add(zf, os.path.join(root, src), "%s/%s" % (top, arc))
    return out


SKIP_DIRS = {"__pycache__", ".pytest_cache", "build", ".git", "node_modules"}


def make_project(root, out):
    """the whole project tree (sources, scripts, tests, fonts, release package)"""
    entries = []
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            full = os.path.join(base, f)
            rel = os.path.relpath(full, root)
            if f.endswith(".pyc") or os.path.abspath(full) == os.path.abspath(out):
                continue
            entries.append((full, rel))
    with zipfile.ZipFile(out, "w") as zf:
        for full, rel in entries:
            _add(zf, full, "varcoda-mono/" + rel.replace(os.sep, "/"))
    return out, len(entries)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--project", nargs="?", const=os.path.join(os.path.dirname(ROOT), PROJECT), default=None,
                    metavar="PATH", help="also write a ZIP of the complete project (default: next to the project folder)")
    args = ap.parse_args(argv)
    pkg = make_package(args.root)
    with zipfile.ZipFile(pkg) as zf:
        names = zf.namelist()
    print("%s  %.0f kB  %d files" % (os.path.relpath(pkg, args.root), os.path.getsize(pkg) / 1024, len(names)))
    if args.project:
        out, n = make_project(args.root, args.project)
        print("%s  %.0f kB  %d files" % (out, os.path.getsize(out) / 1024, n))


if __name__ == "__main__":
    main()
