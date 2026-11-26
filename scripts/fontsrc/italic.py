"""Italic styles.

The italic is derived from the upright program rather than drawn twice, but
it is more than a slanted roman:

* everything alphabetic is slanted by ITALIC_ANGLE around the middle of the
  x-height, so letters stay centred in their cell;
* three letters change construction, as they do in a written hand:
  ``a`` becomes single-storey, ``y`` becomes the squared, hooked form, and
  ``f`` descends below the baseline;
* everything that has to join or point - box drawing, block elements,
  arrows, geometric shapes, the Powerline symbols - stays upright, so tables
  and prompts look the same in a comment as anywhere else.

Limitation, stated plainly: curves are sheared, not redrawn, so their stroke
weight is not optically corrected (at 9.5 degrees the error is below 3 % of
the stem).
"""
from __future__ import annotations

import math

from . import params
from .geom import Shape
from .glyphs_lower import _lc
from .kit import GLYPHS, Composite, blade, opath
from .geom import rect

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

# letters that take another construction in the italic: name -> glyph whose drawing is used
ITALIC_FORMS = {"a": "a.ss02", "y": "y.ss05"}


def f_descending(m) -> Shape:
    """italic f: the stem runs below the baseline and ends in the blade cut"""
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = xc - 0.06 * m.W
    xe = R + 0.014 * m.W
    foot = m.desc * 0.66
    hook = opath(m, [(xs, foot), (xs, m.asc - b), (xe, m.asc - b)], sw, hw, 0.29 * m.W, 0.27 * m.xh)
    s = blade(m, hook, xs - a, sw, foot, up=False)
    return s | rect(L - 0.004 * m.W, m.xh - hw, R - 0.012 * m.W, m.xh)


ITALIC_DRAW = {"f": f_descending}


def stays_upright(name: str) -> bool:
    if name in UPRIGHT_NAMES:
        return True
    return any(lo <= cp <= hi for cp in GLYPHS[name]["unicodes"] for lo, hi in UPRIGHT_RANGES)


def _rounded(shape: Shape) -> Shape:
    return Shape([[(seg[0],) + tuple((round(p[0]), round(p[1])) for p in seg[1:]) for seg in cont]
                  for cont in shape.contours])


def italicize(m, glyphs: dict) -> dict:
    """upright drawings of one master -> italic drawings (same glyph set)"""
    src = dict(glyphs)
    for name, fn in ITALIC_DRAW.items():
        src[name] = fn(m)
    for name, other in ITALIC_FORMS.items():
        src[name] = glyphs[other]
    out = {}
    for name, res in src.items():
        if isinstance(res, Composite) or stays_upright(name):
            out[name] = res
        else:
            out[name] = _rounded(res.skew(TAN, PIVOT))
    return out
