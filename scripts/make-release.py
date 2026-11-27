#!/usr/bin/env python3
"""Build the release archives in releases/.

    python scripts/make-release.py              # the archives people download
    python scripts/make-release.py --project    # additionally a ZIP of the whole project

    VarcodaMono-<release>.zip       the recommended download: ttf/, otf/, webfonts/, OFL.txt, INSTALL.txt
    VarcodaMono-<release>-web.zip   only the WOFF2 files and the stylesheet, for websites
    SHA256SUMS                      checksums of every archive of this release found in releases/
                                    (the Nerd Font archive too, when make-nerd-fonts.py ran first)

The archives hold what somebody needs to install and use the family and nothing
else.  They are deterministic (sorted entries, fixed timestamps).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
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
TOP = "%s-%s" % (build.PS_FAMILY, build.RELEASE)
SLUG = build.FAMILY.lower().replace(" ", "-")
CSS = SLUG + ".css"
PROJECT = "%s-%s-project.zip" % (SLUG, build.RELEASE)

INSTALL = """\
{family} {release}
{url}

INSTALL

  Windows   Open the ttf folder, select all ten files, right-click, Install.
  macOS     Open the ttf folder, select all ten files, double-click, Install Font.
  Linux     mkdir -p ~/.local/share/fonts/{slug}
            cp ttf/*.ttf ~/.local/share/fonts/{slug}/ && fc-cache -f

  Install all ten files, not only Regular: applications then use the real
  Bold and Italic instead of faking them.  Restart the application afterwards.

USE

  The font family is called:  {family}

  VS Code, settings.json:
      "editor.fontFamily": "'{family}', monospace",
      "editor.fontLigatures": true

  Other editors and terminals, ligatures, stylistic sets, troubleshooting:
  {url}/blob/main/docs/INSTALLATION.md

IN THIS ARCHIVE

  ttf/        TrueType, hinted.  The files to install, on every system.
  otf/        The same fonts with PostScript outlines.  Install ttf or otf, not both.
  webfonts/   WOFF2 files and {css} for websites.
  OFL.txt     SIL Open Font License 1.1: free for personal and commercial use.

  Icons for terminal prompts (Nerd Fonts) are a separate download from the same
  page: {ps}NerdFont-{release}.zip
"""


def _stamp():
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", build.BUILD_EPOCH))
    return time.gmtime(epoch)[:6]


def _add(zf, arcname, data):
    info = zipfile.ZipInfo(arcname, date_time=_stamp())
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data, compresslevel=9)


def install_text():
    return INSTALL.format(family=build.FAMILY, release=build.RELEASE, url=build.URL, ps=build.PS_FAMILY, css=CSS, slug=SLUG)


def _fonts(kind, folder):
    return [("fonts/%s/%s-%s.%s" % (folder, build.PS_FAMILY, s, kind), "%s-%s.%s" % (build.PS_FAMILY, s, kind)) for s in STYLES]


def web_files():
    """(source, name in the archive): the WOFF2 files and their stylesheet, side by side as the CSS expects"""
    return [("LICENSE", "OFL.txt"), ("fonts/webfonts/" + CSS, CSS)] + _fonts("woff2", "webfonts")


def desktop_files():
    return ([("LICENSE", "OFL.txt")]
            + [(src, "ttf/" + name) for src, name in _fonts("ttf", "ttf")]
            + [(src, "otf/" + name) for src, name in _fonts("otf", "otf")]
            + [(src, "webfonts/" + name) for src, name in web_files()[1:]])


def _write(root, out, top, files, extra=()):
    missing = [src for src, _ in files if not os.path.isfile(os.path.join(root, src))]
    if missing:
        sys.exit("cannot build %s, missing: %s\n(run scripts/build-fonts.py first)" % (os.path.basename(out), ", ".join(missing)))
    entries = list(extra)
    for src, arc in files:
        with open(os.path.join(root, src), "rb") as fh:
            entries.append((arc, fh.read()))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, "w") as zf:
        for arc, data in sorted(entries):
            _add(zf, "%s/%s" % (top, arc), data)
    return out


def make_packages(root, out_dir=None):
    """-> paths of the desktop archive and the web archive"""
    out_dir = out_dir or os.path.join(root, "releases")
    return [_write(root, os.path.join(out_dir, TOP + ".zip"), TOP, desktop_files(), [("INSTALL.txt", install_text().encode("utf-8"))]),
            _write(root, os.path.join(out_dir, TOP + "-web.zip"), TOP + "-web", web_files())]


def write_checksums(out_dir):
    """SHA256SUMS for every archive of this release in out_dir, in the format `sha256sum -c` reads"""
    lines = []
    for path in sorted(glob.glob(os.path.join(out_dir, "%s*-%s*.zip" % (build.PS_FAMILY, build.RELEASE)))):
        with open(path, "rb") as fh:
            lines.append("%s  %s\n" % (hashlib.sha256(fh.read()).hexdigest(), os.path.basename(path)))
    path = os.path.join(out_dir, "SHA256SUMS")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.writelines(lines)
    return path, lines


SKIP_DIRS = {"__pycache__", ".pytest_cache", "build", ".git", "node_modules"}


def make_project(root, out):
    """the whole project tree (sources, scripts, tests, fonts, release archives)"""
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
            with open(full, "rb") as fh:
                _add(zf, "%s/%s" % (SLUG, rel.replace(os.sep, "/")), fh.read())
    return out, len(entries)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--project", nargs="?", const=os.path.join(os.path.dirname(ROOT), PROJECT), default=None,
                    metavar="PATH", help="also write a ZIP of the complete project (default: next to the project folder)")
    args = ap.parse_args(argv)
    for pkg in make_packages(args.root):
        with zipfile.ZipFile(pkg) as zf:
            print("%s  %.0f kB  %d files" % (os.path.relpath(pkg, args.root), os.path.getsize(pkg) / 1024, len(zf.namelist())))
    sums, lines = write_checksums(os.path.join(args.root, "releases"))
    print("%s  %d archives" % (os.path.relpath(sums, args.root), len(lines)))
    if args.project:
        out, n = make_project(args.root, args.project)
        print("%s  %.0f kB  %d files" % (out, os.path.getsize(out) / 1024, n))


if __name__ == "__main__":
    main()
