"""Rasterise text with the *compiled* fonts: HarfBuzz for shaping (so OpenType
features can be switched on and off) and FreeType for hinted rasterisation.

Glyphs are placed on an integer cell grid exactly like a terminal emulator
does, which makes this a realistic small-size rendering test.  Used by the
specimen generator and by tests/rendering-tests.
"""
from __future__ import annotations

import freetype
import numpy as np
import uharfbuzz as hb
from PIL import Image


class FontRenderer:
    def __init__(self, path: str, px: int, hinting: bool = True, cell_width: int | None = None):
        self.path, self.px = path, px
        self.face = freetype.Face(path)
        self.face.set_pixel_sizes(0, px)
        with open(path, "rb") as fh:
            data = fh.read()
        self.hb_face = hb.Face(data)
        self.hb_font = hb.Font(self.hb_face)
        self.upem = self.hb_face.upem
        adv = self.face.get_advance(self.face.get_char_index(ord("M")), freetype.FT_LOAD_NO_SCALE) / self.upem * px
        self.advance = adv
        self.cell = cell_width if cell_width is not None else max(1, round(adv))
        m = self.face.size
        self.ascent = round(m.ascender / 64)
        self.descent = round(-m.descender / 64)
        self.flags = freetype.FT_LOAD_RENDER | (freetype.FT_LOAD_TARGET_NORMAL if hinting else freetype.FT_LOAD_NO_HINTING)
        self._cache = {}

    # -- shaping -----------------------------------------------------------
    def shape(self, text: str, features: dict | None = None):
        """-> list of (glyph id, cluster)"""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, features or {})
        return [(i.codepoint, i.cluster) for i in buf.glyph_infos]

    def glyph_names(self, text: str, features: dict | None = None):
        return [self.hb_font.glyph_to_string(g) for g, _ in self.shape(text, features)]

    # -- rasterising -------------------------------------------------------
    def bitmap(self, gid: int):
        if gid not in self._cache:
            self.face.load_glyph(gid, self.flags)
            g = self.face.glyph
            bm = g.bitmap
            arr = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)[:, :bm.width] if bm.rows else np.zeros((0, 0), np.uint8)
            self._cache[gid] = (arr.astype(np.float32) / 255.0, g.bitmap_left, g.bitmap_top)
        return self._cache[gid]

    def draw(self, canvas: np.ndarray, x: int, baseline: int, text: str, color=(255, 255, 255),
             features: dict | None = None, colors: list | None = None):
        """Draw one line.  canvas: float32 H×W×3 (0..255).  colors: optional
        per-character colours (same length as text)."""
        H, W, _ = canvas.shape
        for i, (gid, cluster) in enumerate(self.shape(text, features)):
            cov, left, top = self.bitmap(gid)
            if cov.size == 0:
                continue
            col = np.array(colors[cluster] if colors else color, dtype=np.float32)
            gx, gy = x + i * self.cell + left, baseline - top
            h, w = cov.shape
            x0, y0, x1, y1 = max(gx, 0), max(gy, 0), min(gx + w, W), min(gy + h, H)
            if x1 <= x0 or y1 <= y0:
                continue
            c = cov[y0 - gy:y1 - gy, x0 - gx:x1 - gx, None]
            region = canvas[y0:y1, x0:x1]
            canvas[y0:y1, x0:x1] = region * (1 - c) + col * c
        return canvas


def new_canvas(w: int, h: int, bg=(24, 26, 31)) -> np.ndarray:
    c = np.empty((h, w, 3), dtype=np.float32)
    c[:] = np.array(bg, dtype=np.float32)
    return c


def to_image(canvas: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(canvas + 0.5, 0, 255).astype(np.uint8), "RGB")


def render_lines(path, px, lines, features=None, fg=(212, 216, 224), bg=(24, 26, 31), pad=12, line_height=None,
                 zoom=1, hinting=True) -> Image.Image:
    r = FontRenderer(path, px, hinting=hinting)
    lh = line_height or round(px * 1.4)
    w = pad * 2 + r.cell * max((len(l) for l in lines), default=1)
    h = pad * 2 + lh * len(lines)
    cv = new_canvas(w, h, bg)
    for i, line in enumerate(lines):
        base = pad + i * lh + (lh - (r.ascent + r.descent)) // 2 + r.ascent
        r.draw(cv, pad, base, line, fg, features)
    img = to_image(cv)
    if zoom != 1:
        img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
    return img
