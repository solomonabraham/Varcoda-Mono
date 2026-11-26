"""Design proofs rendered straight from Shape objects (no font needed).

Used while drawing: lets the build script and the designer look at outlines,
guides and spacing before anything is compiled.
"""
from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw

from .geom import Shape, flatten


def glyph_bitmap(shape: Shape, scale: float, width: float, top: float, bottom: float, ss: int = 4, pad: float = 300):
    """Rasterise one glyph cell (even-odd fill of clean, non-overlapping
    contours) -> 'L' image, anti-aliased by supersampling."""
    w = int(round((width + 2 * pad) * scale * ss))
    h = int(round((top - bottom) * scale * ss))
    acc = Image.new("1", (w, h), 0)
    for poly in flatten(shape, 16):
        pts = [((x + pad) * scale * ss, (top - y) * scale * ss) for x, y in poly]
        if len(pts) < 3:
            continue
        m = Image.new("1", (w, h), 0)
        ImageDraw.Draw(m).polygon(pts, fill=1)
        acc = ImageChops.logical_xor(acc, m)
    return acc.convert("L").resize((max(1, w // ss), max(1, h // ss)), Image.LANCZOS)


def sheet(glyphs, lines, scale=0.2, width=600, top=1000, bottom=-300, guides=(), margin=30,
          fg=(20, 22, 28), bg=(250, 250, 248), guide_color=(215, 80, 80), pad=300, labels=None):
    """Render rows of glyph names.  ``glyphs`` maps name -> Shape."""
    cols = max(len(l) for l in lines)
    cw = width * scale
    lh = (top - bottom) * scale
    W = int(cols * cw + 2 * margin)
    H = int(len(lines) * lh + 2 * margin)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    cache = {}
    for r, line in enumerate(lines):
        y0 = margin + r * lh
        for g in guides:
            y = y0 + (top - g) * scale
            d.line([(margin, y), (W - margin, y)], fill=guide_color, width=1)
        for c, name in enumerate(line):
            if name is None or name not in glyphs:
                continue
            if name not in cache:
                cache[name] = glyph_bitmap(glyphs[name], scale, width, top, bottom, pad=pad)
            bm = cache[name]
            x = int(round(margin + c * cw - pad * scale))
            ink = Image.new("RGB", bm.size, fg)
            img.paste(ink, (x, int(round(y0))), bm)
    if labels:
        for (x, y, text) in labels:
            d.text((x, y), text, fill=(120, 120, 120))
    return img


def text_sheet(glyphs, cmap, text_lines, **kw):
    """Like sheet() but takes strings; cmap maps char -> glyph name."""
    lines = [[cmap.get(ch) for ch in line] for line in text_lines]
    return sheet(glyphs, lines, **kw)
