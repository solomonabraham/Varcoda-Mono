#!/usr/bin/env python3
"""Nerd Font builds of Varcoda Mono: a separate distribution, made with the official patcher.

    python scripts/make-nerd-fonts.py [--only Regular Bold] [--no-zip]

Needs Docker; the image nerdfonts/patcher carries FontForge and the icon sets.  The fonts in
fonts/ttf/ are copied first and never changed.  Two variants per style, named as the Nerd Fonts
project names them:

    build/nerd/VarcodaMonoNerdFont-<Style>.ttf       icons may be wider than one cell
    build/nerd/VarcodaMonoNerdFontMono-<Style>.ttf   every icon inside one cell

``--careful`` makes the patcher keep every glyph Varcoda Mono already has (its own Powerline
symbols, box drawing, arrows).  Every result is checked against its source before it is
accepted; the accepted files are zipped into releases/VarcodaMonoNerdFont-<version>.zip.
The output is not byte-reproducible: FontForge writes the time of the run.
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

from fontsrc import build, params  # noqa: E402

IMAGE = "nerdfonts/patcher"
VARIANTS = [("NerdFont", []), ("NerdFontMono", ["--mono"])]
# one code point from each icon set that must be there afterwards
ICONS = {0xE0B4: "Powerline Extra", 0xE5FA: "Seti-UI", 0xE702: "Devicons", 0xF002: "Font Awesome", 0xF401: "Octicons",
         0xF303: "Font Logos", 0xE30D: "Weather", 0xEA60: "Codicons", 0xF0001: "Material Design"}


def bounds(font):
    gs, out = font.getGlyphSet(), {}
    for cp, name in font.getBestCmap().items():
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        out[cp] = (pen.bounds, gs[name].width)
    return out


def check(src_path, out_path, mono):
    """-> list of problems (empty: the patched font kept everything the tests promise for the original)"""
    import uharfbuzz as hb
    src, out = TTFont(src_path), TTFont(out_path)
    bad = []
    a, b = bounds(src), bounds(out)
    moved = [cp for cp in a if cp not in b or b[cp][1] != params.WIDTH
             or (a[cp][0] is None) != (b[cp][0] is None)
             or (a[cp][0] and max(abs(x - y) for x, y in zip(a[cp][0], b[cp][0])) > 1)]
    if moved:
        bad.append("%d original glyphs changed, e.g. %s" % (len(moved), ", ".join("U+%04X" % c for c in moved[:6])))
    missing = [name for cp, name in ICONS.items() if cp not in b]
    if missing:
        bad.append("icon sets missing: " + ", ".join(missing))
    if mono:
        wide = sorted({w for _, w in b.values()} - {params.WIDTH})
        if wide or not out["post"].isFixedPitch:
            bad.append("not strictly monospaced: advances %s, isFixedPitch %d" % (wide[:5], out["post"].isFixedPitch))
    for tag, attr in (("hhea", "ascent"), ("hhea", "descent"), ("hhea", "lineGap"), ("OS/2", "sTypoAscender"),
                      ("OS/2", "sTypoDescender"), ("OS/2", "sTypoLineGap"), ("OS/2", "usWeightClass"), ("head", "unitsPerEm")):
        if getattr(src[tag], attr) != getattr(out[tag], attr):
            bad.append("%s.%s %s -> %s" % (tag, attr, getattr(src[tag], attr), getattr(out[tag], attr)))
    with open(out_path, "rb") as fh:
        fnt = hb.Font(hb.Face(fh.read()))
    buf = hb.Buffer()
    buf.add_str("a!=b")
    buf.guess_segment_properties()
    hb.shape(fnt, buf, {"calt": True})
    names = [fnt.glyph_to_string(i.codepoint) for i in buf.glyph_infos]
    if names != ["a", "LIG", "exclam_equal.liga", "b"] or {p.x_advance for p in buf.glyph_positions} != {params.WIDTH}:
        bad.append("ligatures broken: %s" % names)
    family = out["name"].getBestFamilyName()
    if "Nerd Font" not in family:
        bad.append("family is still %r" % family)
    if "fpgm" in src and "fpgm" not in out:
        bad.append("TrueType hinting lost")
    return bad, family, len(b) - len(a)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", help="styles, e.g. Regular BoldItalic (default: all ten)")
    ap.add_argument("--no-zip", action="store_true")
    args = ap.parse_args()
    if not shutil.which("docker"):
        sys.exit("docker not found: the Nerd Fonts patcher needs FontForge, which its Docker image provides")
    styles = args.only or [w[0] for w in params.WEIGHTS] + [i[0] for i in params.ITALICS]
    sources = [os.path.join(ROOT, "fonts", "ttf", "%s-%s.ttf" % (build.PS_FAMILY, s)) for s in styles]
    out_dir = os.path.join(ROOT, "build", "nerd")
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    failed = False
    with tempfile.TemporaryDirectory() as tmp:
        src_dir = os.path.join(tmp, "in")            # a copy: the patcher wants to write next to its input
        os.makedirs(src_dir)
        for p in sources:
            shutil.copy(p, src_dir)
        for suffix, extra in VARIANTS:
            cmd = ["docker", "run", "--rm", "-v", "%s:/in" % src_dir.replace("\\", "/"),
                   "-v", "%s:/out" % out_dir.replace("\\", "/"), IMAGE, "--complete", "--careful"] + extra
            print("  " + " ".join(cmd[-4:]), flush=True)
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res.returncode:
                sys.exit("patcher failed:\n" + res.stderr[-2000:])
            for style, src in zip(styles, sources):
                out = os.path.join(out_dir, "%s%s-%s.ttf" % (build.PS_FAMILY, suffix, style))
                if not os.path.isfile(out):
                    print("  MISSING %s" % os.path.basename(out))
                    failed = True
                    continue
                bad, family, added = check(src, out, mono=bool(extra))
                print("  %-44s %-28s +%d icons  %s" % (os.path.basename(out), family, added, "; ".join(bad) or "ok"))
                failed = failed or bool(bad)
    if failed:
        sys.exit("some patched fonts did not pass; nothing was zipped")
    if not args.no_zip and not args.only:
        zpath = os.path.join(ROOT, "releases", "%sNerdFont-%s.zip" % (build.PS_FAMILY, build.RELEASE))
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for p in sorted(glob.glob(os.path.join(out_dir, "*.ttf"))):
                z.write(p, os.path.basename(p))
            z.write(os.path.join(ROOT, "LICENSE"), "LICENSE")
            z.write(os.path.join(ROOT, "docs", "NERD-FONTS.md"), "NERD-FONTS.md")
        print("  %s  %.1f MB" % (os.path.relpath(zpath, ROOT), os.path.getsize(zpath) / 1e6))


if __name__ == "__main__":
    main()
