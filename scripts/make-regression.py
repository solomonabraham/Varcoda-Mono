#!/usr/bin/env python3
"""Before/after rendering comparisons: against the 1.000 baseline and against the previous release.

    python scripts/make-regression.py [--refs DIR]

Writes tests/visual-regression/before-after-{dark,light}.png: the same text
set in the archived 1.000 Regular (tests/baseline/v1.000) and in the current
Regular at 10, 11, 12, 13, 14, 16 and 18 px - once pixel for pixel, once
enlarged 3x - and tests/visual-regression/density.md with the measured ink
density (average coverage of the text area) of both, plus the reference
fonts when --refs is given.

Also writes compare-previous-{dark,light}.png: the previous release (tests/baseline/v1.400)
against the current fonts.  Look-alike characters and operators at 10-20 px, the three code
samples of the 1.5.0 brief at 12, 14 and 16 px, and one line in all ten styles.
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
AFTER = os.path.join(ROOT, "fonts", "ttf", "%s-Regular.ttf" % build.PS_FAMILY)
OUT = os.path.join(ROOT, "tests", "visual-regression")
PREVIOUS = ("1.4.0", os.path.join(ROOT, "tests", "baseline", "v1.400", "%s-%%s.ttf" % build.PS_FAMILY))
CURRENT = (build.RELEASE, os.path.join(ROOT, "fonts", "ttf", "%s-%%s.ttf" % build.PS_FAMILY))
ON, OFF = {"calt": True}, {"calt": False, "liga": False}
PAIRS = "Il1 | O0 | pqpq | $S$S | B8B8 | GCGC"
OPERATORS = "!= !== == === <= >= => -> <-> :: :="
CODE = """<?php

class VarcodaExample {
    public function calculateTotal(
        int $quantity,
        float $price
    ): float {
        return $quantity * $price;
    }
}

const result = items?.map(item => ({
    id: item.id,
    value: item.value ?? 0,
}));

def calculate_total(items):
    return sum(
        item["price"] * item["quantity"]
        for item in items
    )""".splitlines()
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


def text_block(path, px, lines, bg, fg, zoom=1):
    """lines: [(text, features)] -> canvas"""
    r = FontRenderer(path, px)
    lh = round(px * 1.4)
    cv = np.empty((lh * len(lines) + 6, r.cell * max(len(t) for t, _ in lines) + 8, 3), dtype=np.float32)
    cv[:] = np.array(bg, dtype=np.float32)
    for i, (t, feats) in enumerate(lines):
        r.draw(cv, 4, 3 + i * lh + (lh - (r.ascent + r.descent)) // 2 + r.ascent, t, fg, feats)
    if zoom != 1:
        cv = np.asarray(to_image(cv).resize((cv.shape[1] * zoom, cv.shape[0] * zoom), Image.NEAREST), dtype=np.float32)
    return cv


def comparison(theme):
    """previous release against the current fonts -> compare-previous-<theme>.png"""
    bg, fg, muted = THEMES[theme]
    both = (PREVIOUS, CURRENT)
    glyphs = [(PAIRS, OFF), (OPERATORS, OFF), (OPERATORS, ON)]
    sizes, code, styles = [], [], []                            # sections of (label, [left canvas, right canvas])
    for px in SIZES + [20]:
        for ver, path in both:
            sizes.append(("%2d px  %s" % (px, ver), [text_block(path % "Regular", px, glyphs, bg, fg, z) for z in (1, 3)]))
    for px in (12, 14, 16):
        code.append(("%2d px  %s | %s" % (px, PREVIOUS[0], CURRENT[0]),
                     [text_block(path % "Regular", px, [(t, ON) for t in CODE], bg, fg) for _, path in both]))
    line = [(PAIRS + "  " + OPERATORS, ON)]
    for style in [w[0] for w in build.params.WEIGHTS] + [i[0] for i in build.params.ITALICS]:
        for ver, path in both:
            if os.path.isfile(path % style):                    # the baseline holds Regular, Italic and Bold
                styles.append(("%-14s %s" % (style, ver), [text_block(path % style, px, line, bg, fg) for px in (14, 20)]))
    # the right column starts where the widest left canvas of its own section ends
    rows = [(tag, left, right, max(c[0].shape[1] for _, c in sec)) for sec in (sizes, code, styles) for tag, (left, right) in sec]
    label = FontRenderer(AFTER, 15)
    x0 = 40 + label.cell * max(len(r[0]) for r in rows) + 24
    cv = np.empty((60 + sum(max(l.shape[0], r.shape[0]) + 12 for _, l, r, _ in rows),
                   x0 + max(w + 30 + r.shape[1] for _, _, r, w in rows) + 40, 3), dtype=np.float32)
    cv[:] = np.array(bg, dtype=np.float32)
    y = 30
    for tag, left, right, w in rows:
        label.draw(cv, 40, y + 20, tag, muted, OFF)
        cv[y:y + left.shape[0], x0:x0 + left.shape[1]] = left
        cv[y:y + right.shape[0], x0 + w + 30:x0 + w + 30 + right.shape[1]] = right
        y += max(left.shape[0], right.shape[0]) + 12
    name = "compare-previous-%s.png" % theme
    to_image(cv).save(os.path.join(OUT, name), optimize=True)
    print("  tests/visual-regression/%s  %dx%d" % (name, cv.shape[1], cv.shape[0]))


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
        comparison(theme)
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
    with open(os.path.join(OUT, "density.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[5:]))


if __name__ == "__main__":
    main()
