"""Terminal extras: the Powerline separators and status symbols
(U+E0A0-E0A2, U+E0B0-E0B3) and the superscript / subscript figures
(U+2070, U+2074-2079, U+2080-2089).

The separators fill the character cell exactly like the block elements do
(including the overshoot that hides seams), so prompt segments join without
gaps.  All shapes are original drawings built from the family's own pens.
"""
from __future__ import annotations

from .geom import BIG, Shape, poly, rect, sbox
from .glyphs_box import cell, true_cell
from .glyphs_upper import (L_, N_, eight_, five_, four_, nine_, one_, seven_, six_, three_, two_, zero_ring)
from .kit import dot, g, opath


# -- separators --------------------------------------------------------------
def _solid_right(m) -> Shape:
    ex0, ey0, ex1, ey1, cx, cy = cell(m)[:6]
    x0, y0, x1, y1 = true_cell(m)
    return poly([(ex0, ey0), (x0, ey0), (x1, cy), (x0, ey1), (ex0, ey1)])


def _thin_right(m) -> Shape:
    ex0, ey0, ex1, ey1, cx, cy, light = cell(m)[:7]
    x0, y0, x1, y1 = true_cell(m)
    tri = poly([(x0 - BIG, ey0), (x0, ey0), (x1, cy), (x0, ey1), (x0 - BIG, ey1)])
    # horizontal thickness chosen so the stroke is as heavy as a light box line
    slope = (x1 - x0) / ((ey1 - ey0) / 2)
    d = light * (1 + slope * slope) ** 0.5
    return (tri - tri.move(-d, 0)) & rect(x0, ey0, x1, ey1)


@g("uniE0B0", uni=0xE0B0)
def pl_right_solid_(m):
    return _solid_right(m)


@g("uniE0B1", uni=0xE0B1)
def pl_right_thin_(m):
    return _thin_right(m)


@g("uniE0B2", uni=0xE0B2)
def pl_left_solid_(m):
    return _solid_right(m).flip_x(m.xc)


@g("uniE0B3", uni=0xE0B3)
def pl_left_thin_(m):
    return _thin_right(m).flip_x(m.xc)


# -- status symbols ----------------------------------------------------------
@g("uniE0A0", uni=0xE0A0)
def pl_branch_(m):
    """version-control branch: a trunk with two nodes and a side branch"""
    t = m.sw * 0.92
    r = m.lerp(0.112, 0.128) * m.W
    xt, xb = 0.27 * m.W, 0.73 * m.W
    y_top, y_bot = m.cap - r + m.os, r - m.os
    y_join = 0.36 * m.cap

    def node(cx, cy):
        return dot(m, cx, cy, 2 * r)

    trunk = rect(xt - t / 2, y_bot + r - t / 2, xt + t / 2, y_top - r + t / 2)
    side = opath(m, [(xb, y_top - r + t / 2), (xb, y_join), (xt, y_join)], t, t, (xb - xt) * 0.62, (y_top - y_join) * 0.42)
    return node(xt, y_top) | node(xt, y_bot) | node(xb, y_top) | trunk | side


@g("uniE0A1", uni=0xE0A1)
def pl_line_(m):
    """line number: L over N"""
    f = m.scaled(0.54, stem=m.csw * m.lerp(0.74, 0.64))
    top = L_(f).move(0.03 * m.W - f.UL * 0.55, m.cap + 0.085 * m.cap - f.cap)
    bot = N_(f).move(m.W - f.W - 0.03 * m.W + f.UL * 0.55, -0.085 * m.cap)
    return top | bot


@g("uniE0A2", uni=0xE0A2)
def pl_lock_(m):
    """padlock: read-only"""
    t = m.sw * 0.95
    x0, x1 = 0.135 * m.W, 0.865 * m.W
    yb, yt = -m.os, 0.56 * m.cap
    body = sbox(x0, yb, x1, yt, 0.07 * m.W, 0.07 * m.W, m.k)
    kw, kh = 0.13 * m.W, 0.22 * m.cap
    cy = (yb + yt) / 2
    key = sbox(m.xc - kw / 2, cy - kh / 2, m.xc + kw / 2, cy + kh / 2, kw * 0.46, kw * 0.46, 0.60)
    xl, xr = 0.27 * m.W + t / 2, 0.73 * m.W - t / 2
    top = m.cap + m.os - t / 2
    shackle = opath(m, [(xl, yt - 2), (xl, top), (xr, top), (xr, yt - 2)], t, t, (xr - xl) * 0.5, (top - yt) * 0.62)
    return (body - key) | shackle


# -- superscript and subscript figures -----------------------------------------
def _zero_plain(f):
    return zero_ring(f)[0]


_FIGS = [_zero_plain, one_, two_, three_, four_, five_, six_, seven_, eight_, nine_]


def _small(m, fn, sub):
    f = m.scaled(0.56, stem=m.csw * m.lerp(0.72, 0.64))
    y = -0.19 * m.cap - f.os if sub else m.cap + m.os - f.cap - f.os
    return fn(f).move(m.xc - f.W / 2, y)


def _reg_small_figures():
    for i, fn in enumerate(_FIGS):
        if i not in (1, 2, 3):               # ¹ ² ³ live in Latin-1 (glyphs_symbols)
            g("uni%04X" % (0x2070 + i), uni=0x2070 + i)(lambda m, fn=fn: _small(m, fn, False))
        g("uni%04X" % (0x2080 + i), uni=0x2080 + i)(lambda m, fn=fn: _small(m, fn, True))


_reg_small_figures()
