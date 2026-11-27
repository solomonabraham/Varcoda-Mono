"""Italic styles.

The italic comes from the same program as the upright, in two steps:

* the lowercase is drawn in its written form (glyphs_italic.py: exit strokes,
  branching arches, bowls that run back into their stem, a descending f) -
  the glyph functions pick that form when ``Master.italic`` is set;
* everything alphabetic is then slanted by ITALIC_ANGLE around the middle of
  the x-height, so letters stay centred in their cell.

Everything that has to join or point - box drawing, block elements, arrows,
geometric shapes, the Powerline symbols - stays upright, so tables and
prompts look the same in a comment as anywhere else.

Limitation, stated plainly: the slant is a shear, so the weight of curves is
not optically corrected (at 9.5 degrees the error is below 3 % of the stem).
"""
from __future__ import annotations

import math

from . import params
from .geom import Shape
from .kit import GLYPHS, Composite

TAN = math.tan(math.radians(params.ITALIC_ANGLE))
PIVOT = params.XH / 2

# code points that stay upright
UPRIGHT_RANGES = [(0x2190, 0x21FF),     # arrows
                  (0x221A, 0x221A),     # radical: its long bar would lean far out of the cell
                  (0x2500, 0x25FF),     # box drawing, block elements, geometric shapes
                  (0x2713, 0x2717),     # check marks
                  (0xE0A0, 0xE0B3),     # Powerline
                  (0xFFFD, 0xFFFD)]
UPRIGHT_NAMES = {".notdef", "LIG"}


def stays_upright(name: str) -> bool:
    if name in UPRIGHT_NAMES:
        return True
    return any(lo <= cp <= hi for cp in GLYPHS[name]["unicodes"] for lo, hi in UPRIGHT_RANGES)


def _rounded(shape: Shape) -> Shape:
    return Shape([[(seg[0],) + tuple((round(p[0]), round(p[1])) for p in seg[1:]) for seg in cont]
                  for cont in shape.contours])


def italicize(m, glyphs: dict) -> dict:
    """upright drawings of one master -> italic drawings (same glyph set)"""
    out = {}
    for name, res in glyphs.items():
        if isinstance(res, Composite) or stays_upright(name):
            out[name] = res
        else:
            out[name] = _rounded(res.skew(TAN, PIVOT))
    return out
