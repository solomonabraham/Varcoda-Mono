#!/usr/bin/env python3
"""Before/after rendering comparison against the 1.000 baseline.

    python scripts/make-regression.py [--refs DIR]

Writes tests/visual-regression/before-after-{dark,light}.png: the same text
set in the archived 1.000 Regular (tests/baseline/v1.000) and in the current
Regular at 10, 11, 12, 13, 14, 16 and 18 px - once pixel for pixel, once
enlarged 3x - and tests/visual-regression/density.md with the measured ink
density (average coverage of the text area) of both, plus the reference
fonts when --refs is given.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from fontsrc import build  # noqa: E402
from fontsrc.render import FontRenderer, to_image  # noqa: E402

SIZES = [10, 11, 12, 13, 14, 16, 18]
TEXT = ["if (x != arr[i]) { return fn(a, b) * 0.5; }", "0O 1lI| 5S 8B 2Z rn m cl d {( '\"` .,:; @#$%&"]
BEFORE = os.path.join(ROOT, "tests", "baseline", "v1.000", "VectorMono-Regular.ttf")
AFTER = os.path.join(ROOT, "fonts", "%s-Regular.ttf" % build.PS_FAMILY)
OUT = os.path.join(ROOT, "tests", "visual-regression")
THEMES = {"dark": ((19, 21, 26), (216, 220, 229), (122, 131, 150)), "light": ((247, 245, 240), (27, 30, 37), (112, 114, 122))}


def block(path, px, bg, fg):
    r = FontRenderer(path, px)
    lh = round(px * 1.4)
    w = r.cell * max(len(t) for t in TEXT) + 8
    cv = np.empty((lh * len(TEXT) + 6, w, 3), dtype=np.float32)
    cv[:] = np.array(bg, dtype=np.float32)
    for i, t in enumerate(TEXT):
        r.draw(cv, 4, 3 + i * lh + (lh - (r.ascent + r.descent)) // 2 + r.ascent, t, fg, {"calt": False, "liga": False})
    return cv


def density(path, px):
    """average coverage (0..1) inside the cells of the text, white on black"""
    r = FontRenderer(path, px)
    lh = r.ascent + r.descent
    total = area = 0.0
    for t in TEXT:
        cv = np.zeros((lh + 4, r.cell * len(t) + 4, 3), dtype=np.float32)
        r.draw(cv, 2, 2 + r.ascent, t, (255, 255, 255), {"calt": False, "liga": False})
        total += cv[:, :, 0].sum() / 255.0
        area += r.cell * len(t) * px
    return total / area


def sheet(theme):
    bg, fg, muted = THEMES[theme]
    label = FontRenderer(AFTER, 15)
    rows = []
    for px in SIZES:
        for tag, path in (("%2d px  before (1.000)" % px, BEFORE), ("%2d px  after  (%s)" % (px, build.VERSION), AFTER)):
            b = block(path, px, bg, fg)
            big = np.asarray(to_image(b).resize((b.shape[1] * 3, b.shape[0] * 3), Image.NEAREST), dtype=np.float32)
            rows.append((tag, b, big))
    width = 40 + 230 + max(r[1].shape[1] for r in rows) + 30 + max(r[2].shape[1] for r in rows) + 40
    height = 40 + sum(r[2].shape[0] + 10 for r in rows) + 14 * len(SIZES) + 30
    cv = np.empty((height, width, 3), dtype=np.float32)
    cv[:] = np.array(bg, dtype=np.float32)
    y = 40
    x1 = 40 + 230
    x2 = x1 + max(r[1].shape[1] for r in rows) + 30
    for i, (tag, small, big) in enumerate(rows):
        label.draw(cv, 40, y + 24, tag, muted, {"calt": False})
        cv[y:y + small.shape[0], x1:x1 + small.shape[1]] = small
        cv[y:y + big.shape[0], x2:x2 + big.shape[1]] = big
        y += big.shape[0] + 10 + (14 if i % 2 else 0)
    os.makedirs(OUT, exist_ok=True)
    name = "before-after-%s.png" % theme
    to_image(cv[:y + 30]).save(os.path.join(OUT, name), optimize=True)
    print("  tests/visual-regression/%s  %dx%d" % (name, width, y + 30))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refs", default=os.environ.get("VARCODA_REFS", ""))
    args = ap.parse_args()
    for theme in THEMES:
        sheet(theme)
    fonts = [("1.000 Regular (baseline)", BEFORE), ("%s Regular" % build.VERSION, AFTER),
             ("%s Medium" % build.VERSION, AFTER.replace("Regular", "Medium"))]
    if args.refs:
        for label, fn in (("JetBrains Mono Regular", "JetBrainsMono-Regular.ttf"), ("Fira Code Regular", "FiraCode-Regular.ttf"),
                          ("Iosevka Regular", "Iosevka-Regular.ttf")):
            p = os.path.join(args.refs, fn)
            if os.path.isfile(p):
                fonts.append((label, p))
    lines = ["# Ink density", "",
             "Average coverage of the text area (per cent), FreeType hinted greyscale, text of `scripts/make-regression.py`.",
             "Generated file - do not edit.", "",
             "| Font | " + " | ".join("%d px" % s for s in SIZES) + " |", "| --- | " + " | ".join("---:" for _ in SIZES) + " |"]
    for label, path in fonts:
        lines.append("| %s | %s |" % (label, " | ".join("%.1f" % (100 * density(path, s)) for s in SIZES)))
    with open(os.path.join(OUT, "density.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[5:]))


if __name__ == "__main__":
    main()
