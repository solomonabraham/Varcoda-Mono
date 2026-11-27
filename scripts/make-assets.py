#!/usr/bin/env python3
"""Render the repository images in assets/ from the compiled fonts.

    python scripts/make-assets.py [--refs DIR] [--only NAME ...]

Every picture is made from the real font files in fonts/: PNGs are rasterised
with FreeType (hinted, like a Linux desktop) after HarfBuzz shaping, the SVGs
contain the glyph outlines themselves.  Nothing is mocked up.

--refs DIR   directory with JetBrainsMono-Regular.ttf, FiraCode-Regular.ttf and
             Iosevka-Regular.ttf for assets/comparison.png (see
             docs/COMPARISON.md for how to obtain them).  Without it the
             comparison image is skipped.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from fontsrc import build, params  # noqa: E402
from fontsrc.glyphs_liga import LIGATURES, STYLISTIC_SETS  # noqa: E402
from fontsrc.render import FontRenderer, to_image  # noqa: E402

_spec = importlib.util.spec_from_file_location("specimens", os.path.join(HERE, "make-specimens.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

ASSETS = os.path.join(ROOT, "assets")
STYLES = [w[0] for w in params.WEIGHTS]
W = 1600
MARGIN = 72

DARK = dict(name="dark", bg=(19, 21, 26), panel=(27, 30, 37), rule=(44, 49, 60), fg=(216, 220, 229), muted=(122, 131, 150),
            accent=(95, 208, 196), amber=(242, 182, 112),
            syntax=dict(C_KEYWORD=(242, 134, 152), C_STRING=(166, 214, 132), C_NUMBER=(242, 182, 112), C_FUNC=(120, 182, 252),
                        C_TYPE=(242, 216, 132), C_VAR=(196, 204, 255), C_OP=(140, 204, 222), C_COMMENT=(104, 114, 134),
                        C_TAG=(242, 134, 152), C_ATTR=(242, 216, 132), FG=(216, 220, 229)))
LIGHT = dict(name="light", bg=(247, 245, 240), panel=(237, 234, 227), rule=(214, 210, 200), fg=(27, 30, 37), muted=(112, 114, 122),
             accent=(0, 122, 112), amber=(176, 98, 0),
             syntax=dict(C_KEYWORD=(186, 38, 84), C_STRING=(36, 118, 44), C_NUMBER=(166, 88, 0), C_FUNC=(20, 88, 190),
                         C_TYPE=(134, 96, 0), C_VAR=(84, 70, 172), C_OP=(0, 108, 128), C_COMMENT=(128, 132, 140),
                         C_TAG=(186, 38, 84), C_ATTR=(134, 96, 0), FG=(27, 30, 37)))

HEX = lambda c: "#%02X%02X%02X" % tuple(c)  # noqa: E731

CODE = '''// Debounced search with an abort signal
export async function search(query, { limit = 20, signal } = {}) {
  if (query == null || query.length <= 2) return [];
  const url = `/api/items?q=${encodeURIComponent(query)}&limit=${limit}`;
  const res = await fetch(url, { signal });
  if (res.status !== 200 && res.status !== 304) {
    throw new Error(`HTTP ${res.status}`);
  }
  const { items = [], total = 0 } = await res.json();
  return items.filter((it) => it.score >= 0.5 || it.pinned).map((it, i) => ({ ...it, rank: i + 1 }));
}'''

_fonts = {}


def font_path(style):
    return os.path.join(ROOT, "fonts", "%s-%s.ttf" % (build.PS_FAMILY, style))


def R(style_or_path, px, hinting=True) -> FontRenderer:
    path = style_or_path if os.path.sep in style_or_path else font_path(style_or_path)
    key = (path, px, hinting)
    if key not in _fonts:
        _fonts[key] = FontRenderer(path, px, hinting=hinting)
    return _fonts[key]


class Sheet:
    """a growing canvas with a cursor and a colour theme"""

    def __init__(self, theme, width=W, height=7000):
        self.t = theme
        self.cv = np.empty((height, width, 3), dtype=np.float32)
        self.cv[:] = np.array(theme["bg"], dtype=np.float32)
        self.y = MARGIN
        self.width = width

    def text(self, x, baseline, s, style="Regular", px=28, color=None, features=None, colors=None, hinting=True):
        r = R(style, px, hinting)
        r.draw(self.cv, x, baseline, s, color or self.t["fg"], features if features is not None else {"calt": False}, colors)
        return r

    def line(self, s, style="Regular", px=28, color=None, features=None, colors=None, x=MARGIN, lead=1.42, hinting=True):
        r = R(style, px, hinting)
        lh = round(px * lead)
        base = self.y + (lh - (r.ascent + r.descent)) // 2 + r.ascent
        self.text(x, base, s, style, px, color, features, colors, hinting)
        self.y += lh
        return r

    def gap(self, h):
        self.y += h

    def rule(self):
        self.cv[self.y:self.y + 2, MARGIN:self.width - MARGIN] = np.array(self.t["rule"], dtype=np.float32)
        self.y += 2

    def label(self, s):
        self.gap(44)
        self.line(s.upper(), "Medium", 20, self.t["accent"], lead=1.3)
        self.gap(6)
        self.rule()
        self.gap(22)

    def panel(self, h, pad=22):
        self.cv[self.y:self.y + h + 2 * pad, MARGIN - 28:self.width - MARGIN + 28] = np.array(self.t["panel"], dtype=np.float32)
        self.y += pad

    def code(self, code, lexer, px, style="Regular", features=None, lead=1.5, hinting=True):
        for k, v in self.t["syntax"].items():
            setattr(S, k, v)
        lines = S.colourise(code, lexer)
        self.panel(round(px * lead) * len(lines))
        comment = tuple(self.t["syntax"]["C_COMMENT"])
        feats = features if features is not None else {"calt": True}
        for text, cols in lines:
            # comments are set in the italic of the same weight, everything else upright
            is_c = [tuple(c) == comment for c in cols]
            plain = "".join(" " if c else ch for ch, c in zip(text, is_c))
            ital = "".join(ch if c else " " for ch, c in zip(text, is_c))
            y0 = self.y
            self.line(plain, style, px, colors=cols, features=feats, lead=lead, hinting=hinting)
            if ital.strip():
                self.y = y0
                self.line(ital, params.italic_style(style), px, colors=cols, features=feats, lead=lead, hinting=hinting)
        self.gap(22)

    def save(self, name):
        os.makedirs(ASSETS, exist_ok=True)
        path = os.path.join(ASSETS, name)
        to_image(self.cv[:self.y + MARGIN]).save(path, optimize=True)
        print("  assets/%s  %dx%d" % (name, self.width, self.y + MARGIN))


def family_facts():
    tt = TTFont(font_path("Regular"))
    return len(tt.getGlyphOrder()), len(tt.getBestCmap()), tt


# --------------------------------------------------------------------------
# PNG sheets
# --------------------------------------------------------------------------
def specimen(theme):
    glyphs, chars, _ = family_facts()
    p = Sheet(theme)
    p.line(build.FAMILY, "Bold", 128, lead=1.1)
    p.line("Squared for code.", "Regular", 34, theme["muted"])
    p.gap(8)
    p.line("%d weights with italics · %d glyphs · one 600-unit cell · version %s · SIL OFL 1.1" % (len(STYLES), glyphs, build.VERSION),
           "Regular", 22, theme["muted"])
    p.label("Characters")
    for s in ("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789  ⁰¹²³⁴⁵⁶⁷⁸⁹ ₀₁₂₃₄₅₆₇₈₉",
              "( ) [ ] { } < > . , : ; ' \" ` ! ?", "@ # $ % & * + - = / \\ | _ ~ ^"):
        p.line(s, "Regular", 44, lead=1.36)
    p.label("Characters that must not be confused")
    p.line("0O 1lI| 5S 8B 2Z rn m cl d {( '\"` .,:;", "Regular", 56, lead=1.3)
    p.label("Code at 28 px, ligatures on")
    p.code(CODE.replace("  return items.filter((it) => it.score >= 0.5 || it.pinned).map((it, i) => ({ ...it, rank: i + 1 }));",
                        "  return items.filter((it) => it.score >= 0.5 || it.pinned);"), "javascript", 28)
    p.label("The same code at 13 px and 14 px, pixel for pixel (hinted, greyscale)")
    short = "\n".join(CODE.split("\n")[1:6])
    p.code(short, "javascript", 13)
    p.code(short, "javascript", 14)
    p.label("Weights")
    for st, wc, _stem in params.WEIGHTS:
        p.line("%-8s %d  for (const [key, value] of Object.entries(map)) {}" % (st, wc), st, 34, lead=1.4)
    p.label("Italics: five weights, written rather than slanted")
    p.line("The quick brown fox jumps over a lazy dog. /* fluffy, safe, every day */", "Italic", 34, lead=1.4)
    p.line("abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789", "Italic", 22, theme["muted"], lead=1.6)
    p.label("Box drawing and Powerline")
    for s in ("┌──────────┬──────────┐  ╭────────╮  ░▒▓█▇▆▅▄▃▂▁", "│ build    │ passing  │  │  main │       ",
              "└──────────┴──────────┘  ╰────────╯  ← ↑ → ↓ ↔ ⇒ ✓ ✗"):
        p.line(s, "Regular", 36, lead=1.23)
    p.save("specimen-%s.png" % theme["name"])


def weights():
    p = Sheet(DARK)
    for st, wc, stem in params.WEIGHTS:
        p.line("%s %d" % (st, wc), "Medium", 20, DARK["accent"], lead=1.5)
        p.line("Varcoda Mono  const fn = (a, b) => a !== b && a >= 0;", st, 46, features={"calt": True}, lead=1.3)
        p.line("Varcoda Mono  // every file, safely: a quick fix", params.italic_style(st), 46, features={"calt": True}, lead=1.3)
        p.line("abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789", st, 22, DARK["muted"], lead=1.5)
        p.gap(18)
    p.save("weights.png")


def ligatures():
    _, _, tt = family_facts()
    rev = {v: chr(k) for k, v in tt.getBestCmap().items()}
    p = Sheet(DARK)
    p.line("Ligatures", "Bold", 60, lead=1.2)
    p.line("OpenType feature calt: off / on. Every character keeps its own cell.", "Regular", 24, DARK["muted"])
    p.gap(26)
    seqs = ["".join(rev[g] for g in seq) for _, seq, _ in LIGATURES]
    cols, px = 4, 44
    r = R("Regular", px)
    colw = (W - 2 * MARGIN) // cols
    lh = round(px * 1.5)
    for i, seq in enumerate(seqs):
        x = MARGIN + (i % cols) * colw
        if i % cols == 0 and i:
            p.y += lh
        base = p.y + (lh - (r.ascent + r.descent)) // 2 + r.ascent
        p.text(x, base, seq, "Regular", px, DARK["muted"], {"calt": False})
        p.text(x + 4 * r.cell, base, "→", "Regular", px, DARK["rule"], {"calt": False})
        p.text(x + 6 * r.cell, base, seq, "Regular", px, DARK["fg"], {"calt": True})
    p.y += lh
    p.label("In context")
    p.code("if (a !== b && c >= d || e?.f ?? g) { x += y ** 2; n -= 1; }   // => -> <- <=> ::\n"
           "result := compute(a, b) |> filter(ok) /* walrus, pipe */", "javascript", 30)
    p.label("Alternates")
    for tag, label, subs in [("zero", "Slashed zero", None)] + STYLISTIC_SETS:
        sample = {"zero": "0123 0x00FF 100%", "ss02": "data = alpha.max()", "ss03": "0123 0x00FF 100%",
                  "ss04": "all null: illegal", "ss05": "every key: yes", "ss06": "quick pq queue",
                  "ss07": "maximum memory"}[tag]
        p.line("%s  %s" % (tag, label), "Regular", 30, DARK["accent"], lead=1.5)
        p.y -= round(30 * 1.5)
        p.line(" " * 26 + sample, "Regular", 30, DARK["muted"], lead=1.5)
        p.y -= round(30 * 1.5)
        p.line(" " * 46 + "→ " + sample, "Regular", 30, DARK["fg"], features={tag: True, "calt": False}, lead=1.5)
    p.save("ligatures.png")


def glyph_overview():
    glyphs, chars, tt = family_facts()
    cps = sorted(tt.getBestCmap())
    cps = [c for c in cps if c not in (0x20, 0xA0, 0xAD)]
    p = Sheet(DARK)
    p.line("Glyph overview", "Bold", 60, lead=1.2)
    p.line("%d encoded characters, %d glyphs (Regular)" % (chars, glyphs), "Regular", 24, DARK["muted"])
    p.gap(26)
    px, cols = 38, 30
    r = R("Regular", px)
    step = (W - 2 * MARGIN) // cols
    lh = round(px * 1.5)
    for i, cp in enumerate(cps):
        if i % cols == 0 and i:
            p.y += lh
        base = p.y + (lh - (r.ascent + r.descent)) // 2 + r.ascent
        p.text(MARGIN + (i % cols) * step + (step - r.cell) // 2, base, chr(cp), "Regular", px, DARK["fg"])
    p.y += lh
    p.save("glyph-overview.png")


def comparison(refs):
    names = [("Varcoda Mono", font_path("Regular")), ("JetBrains Mono", os.path.join(refs, "JetBrainsMono-Regular.ttf")),
             ("Fira Code", os.path.join(refs, "FiraCode-Regular.ttf")), ("Iosevka", os.path.join(refs, "Iosevka-Regular.ttf"))]
    missing = [p for _, p in names if not os.path.isfile(p)]
    if missing:
        print("  comparison.png skipped: missing %s" % ", ".join(os.path.basename(m) for m in missing))
        return
    sample = "\n".join(CODE.split("\n")[1:6])
    p = Sheet(DARK)
    p.line("Same code, same size", "Bold", 60, lead=1.2)
    p.line("Regular weights, FreeType hinted greyscale, ligatures off. Reference fonts are rendered from their", "Regular", 22, DARK["muted"])
    p.line("published files for comparison only; they are not part of this project.", "Regular", 22, DARK["muted"])
    for px, zoom, title in ((14, 1, "14 px, pixel for pixel"), (14, 2, "14 px, enlarged 2× (nearest neighbour)"), (26, 1, "26 px")):
        p.label(title)
        for label, path in names:
            p.line(label, "Medium", 18, DARK["accent"], lead=1.6)
            r = R(path, px)
            lh = round(px * 1.45)
            lines = sample.split("\n")
            h, w = lh * len(lines) + 8, r.cell * max(len(l) for l in lines) + 8
            cv = np.empty((h, w, 3), dtype=np.float32)
            cv[:] = np.array(DARK["bg"], dtype=np.float32)
            for i, l in enumerate(lines):
                r.draw(cv, 4, 4 + i * lh + (lh - (r.ascent + r.descent)) // 2 + r.ascent, l, DARK["fg"], {"calt": False, "liga": False})
            img = to_image(cv)
            if zoom != 1:
                img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
            arr = np.asarray(img, dtype=np.float32)[:, :W - 2 * MARGIN]
            p.cv[p.y:p.y + arr.shape[0], MARGIN:MARGIN + arr.shape[1]] = arr
            p.y += arr.shape[0] + 10
    p.save("comparison.png")


TEST_LINES = ["0O0o 1lI|i 5S 8B 2Z rn/m cl/d", "illinois immune millimeter minimum",
              "$variable = $object->method($argument);", "if ($value !== null && $enabled === true) {}",
              "const result = items?.map(item => item ?? fallback);", "{[(<>)]} ; : , . ' \" ` ~ ! @ # $ % ^ & * += -= *= /= %="]
TEST_SIZES = [10, 11, 12, 13, 14, 16, 18]


def test_sheet(theme):
    """the fixed typography test: same lines, sizes, leading and colours every time"""
    p = Sheet(theme)
    p.line("Typography test sheet", "Bold", 44, lead=1.3)
    p.line("Regular with an italic comment, hinted greyscale, pixel for pixel, ligatures on. Regenerate: make-assets.py", "Regular", 18,
           theme["muted"])
    for px in TEST_SIZES:
        p.label("%d px" % px)
        for text in TEST_LINES:
            p.line(text, "Regular", px, features={"calt": True}, lead=1.5)
        p.line("// italic comment: a quick fix for every file, safely (0O 1lI)", "Italic", px, theme["muted"], lead=1.5)
        p.line("ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 ÀÉÎõüçñß ┌─┬─┐ ░▒▓█", "Regular", px, lead=1.5)
    p.save("test-sheet-%s.png" % theme["name"])


# --------------------------------------------------------------------------
# SVG (outlines of the real glyphs) and PNG copies made by headless Chrome
# --------------------------------------------------------------------------
class Outliner:
    def __init__(self, style):
        self.path = font_path(style)
        self.tt = TTFont(self.path)
        self.gs = self.tt.getGlyphSet()
        with open(self.path, "rb") as fh:
            self.hb_font = hb.Font(hb.Face(fh.read()))
        self.upm = self.tt["head"].unitsPerEm

    def text(self, s, x, y, size, fill, features=None):
        """-> (svg <path>, x after the text); y is the baseline"""
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, features or {"calt": False})
        k = size / self.upm
        pen = SVGPathPen(self.gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.hb_font.glyph_to_string(info.codepoint)
            self.gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
            x += pos.x_advance * k
        return '<path fill="%s" d="%s"/>' % (fill, pen.getCommands()), x


def chrome_png(svg_path, png_path, w, h, transparent=False):
    exe = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not exe:
        print("  %s skipped: no Chrome/Chromium to rasterise the SVG" % os.path.basename(png_path))
        return
    args = [exe, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
            "--window-size=%d,%d" % (w, h), "--screenshot=%s" % png_path]
    if transparent:
        args.append("--default-background-color=00000000")
    before = os.path.getmtime(png_path) if os.path.isfile(png_path) else 0
    subprocess.run(args + [pathlib.Path(svg_path).as_uri()], capture_output=True, timeout=120)
    for _ in range(60):             # chrome.exe detaches on Windows and writes the file a moment later
        if os.path.isfile(png_path) and os.path.getmtime(png_path) > before:
            break
        time.sleep(0.5)
    if os.path.isfile(png_path):
        im = Image.open(png_path)
        print("  assets/%s  %dx%d" % (os.path.basename(png_path), im.width, im.height))


def logo():
    bold = Outliner("Bold")
    size = 330
    adv = 0.6 * size
    x0 = (512 - 2 * adv) / 2 + 6
    base = 256 + 0.36 * size
    k, _ = bold.text("V", x0, base, size, HEX(DARK["fg"]))
    bar, _ = bold.text("|", x0 + adv, base, size, HEX(DARK["amber"]))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" '
           'aria-label="Varcoda Mono"><title>Varcoda Mono</title><rect width="512" height="512" rx="104" fill="%s"/>%s%s</svg>\n'
           % (HEX(DARK["bg"]), k, bar))
    path = os.path.join(ASSETS, "logo.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("  assets/logo.svg")
    chrome_png(path, os.path.join(ASSETS, "logo.png"), 512, 512, transparent=True)


def banner():
    bold, reg = Outliner("Bold"), Outliner("Regular")
    t = DARK
    parts = ['<rect width="1280" height="640" fill="%s"/>' % HEX(t["bg"]),
             '<rect x="88" y="150" width="10" height="346" fill="%s"/>' % HEX(t["amber"])]
    parts.append(bold.text(build.FAMILY, 136, 286, 156, HEX(t["fg"]))[0])
    parts.append(reg.text("Squared for code.", 138, 356, 40, HEX(t["muted"]))[0])
    x, y, size = 138, 452, 31
    syn = t["syntax"]
    for seg, col in (("const ", syn["C_KEYWORD"]), ("squared ", syn["FG"]), ("= ", syn["C_OP"]), ("(", syn["C_OP"]), ("bowl", syn["C_VAR"]),
                     (") ", syn["C_OP"]), ("=> ", syn["C_OP"]), ("bowl", syn["FG"]), (".", syn["C_OP"]), ("fill ", syn["FG"]),
                     (">= ", syn["C_OP"]), ("0.89 ", syn["C_NUMBER"]), ("&& ", syn["C_OP"]), ('"code"', syn["C_STRING"]), (";", syn["C_OP"])):
        p, x = reg.text(seg, x, y, size, HEX(col), {"calt": True})
        parts.append(p)
    parts.append(reg.text(" · ".join(STYLES) + "   ·   italics   ·   ligatures   ·   OFL 1.1", 138, 548, 22, HEX(t["muted"]))[0])
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" width="1280" height="640" role="img" '
           'aria-label="Varcoda Mono - Squared for code."><title>Varcoda Mono</title>%s</svg>\n' % "".join(parts))
    path = os.path.join(ASSETS, "banner.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("  assets/banner.svg")
    chrome_png(path, os.path.join(ASSETS, "banner.png"), 1280, 640)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refs", default=os.environ.get("VARCODA_REFS", ""), help="directory with the reference fonts")
    ap.add_argument("--only", nargs="+", default=None)
    args = ap.parse_args()
    os.makedirs(ASSETS, exist_ok=True)
    jobs = {"specimen-dark": lambda: specimen(DARK), "specimen-light": lambda: specimen(LIGHT), "weights": weights,
            "ligatures": ligatures, "glyph-overview": glyph_overview, "logo": logo, "banner": banner,
            "test-sheet-dark": lambda: test_sheet(DARK), "test-sheet-light": lambda: test_sheet(LIGHT)}
    if args.refs:
        jobs["comparison"] = lambda: comparison(args.refs)
    for name, job in jobs.items():
        if args.only and name not in args.only:
            continue
        job()
    if not args.refs and not args.only:
        print("  comparison.png not regenerated (pass --refs DIR)")


if __name__ == "__main__":
    main()
