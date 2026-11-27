"""ASCII punctuation and programming symbols."""
from __future__ import annotations

import math

from .geom import (BIG, Shape, Skel, diag, diag_edge, diag_hw, extend_line, halfplane, pen_support, pline, poly, rect,
                   round_path, sbox, slash, slash_in, stroke)
from .kit import arch, bowl, dot, ess, g, kay, opath, ring, srad, vstem


def _p(m):
    return m.sw, m.hw, m.a, m.b, m.xc, m.cap


@g("space", uni=[0x20, 0xA0])
def space_(m):
    return Shape()


# -- dots ------------------------------------------------------------------
def pdot(m, cx, y_bottom, d=None):
    d = m.pdot if d is None else d
    return dot(m, cx, y_bottom + d / 2, d)


def comma_tail(m, cx, y_bottom, d=None):
    d = m.pdot if d is None else d
    # a long, sturdy tail: at 12-14 px it is what separates , from . and ; from :
    depth = max(0.235 * m.cap, 1.14 * d) * (d / m.pdot)
    hw_ = max(d * 0.32, 0.058 * m.W * (d / m.pdot))
    return diag((cx + d * 0.5 - hw_, y_bottom + d * 0.3), (cx - d * 0.52, y_bottom - depth), hw_, hw_)


@g(".")
def period_(m):
    return pdot(m, m.xc, 0)


@g(",")
def comma_(m):
    return pdot(m, m.xc, 0) | comma_tail(m, m.xc, 0)


@g(":")
def colon_(m):
    return pdot(m, m.xc, 0) | pdot(m, m.xc, m.xh - m.pdot)


@g(";")
def semicolon_(m):
    return comma_(m) | pdot(m, m.xc, m.xh - m.pdot)


@g("!")
def exclam_(m):
    sw, hw, a, b, xc, H = _p(m)
    w = m.csw * 1.04
    return pdot(m, xc, 0) | rect(xc - w / 2, m.pdot + 0.105 * H, xc + w / 2, H)


@g("?")
def question_(m):
    sw, hw, a, b, xc, H = _p(m)
    sw, hw = m.csw, m.chw
    a, b = sw / 2, hw / 2
    yt = H + m.os - b
    xl, xr = m.DL + 0.05 * m.W + a, m.DR - 0.05 * m.W - a
    xs = xc - 0.006 * m.W                       # centre of the short stem
    ym = H * m.lerp(0.40, 0.475)                # centre line of the hook's return
    y_stem = m.pdot + m.lerp(0.105, 0.08) * H   # heavier weights need the room for the stem
    rx, ry = (xr - xl) * 0.5, H * 0.19
    # hook: terminal at the upper left, over the top, down the right side, then
    # one S-bend back to the middle and down into the short stem
    hx = (xr - xs) / 2
    sk = round_path([(xl, yt - ry * 0.9), (xl, yt), (xr, yt), (xr, ym), (xs, ym), (xs, y_stem)],
                    rx, ry, 0.60, radii=[(rx * 0.95, ry * 0.85), (rx, ry), (hx, H * 0.15), (hx, min(H * 0.15, (ym - y_stem) * 0.9))])
    s = stroke(sk, a, b)
    s = s - rect(-BIG, H * 0.60, xc - 0.05 * m.W, H * 0.765)
    return s | pdot(m, xs, 0)


# -- quotes ----------------------------------------------------------------
def tick(m, cx):
    w = m.sw * 1.12
    return rect(cx - w / 2, m.asc - 0.40 * m.cap, cx + w / 2, m.asc)


@g("'")
def quotesingle_(m):
    return tick(m, m.xc)


@g('"')
def quotedbl_(m):
    return tick(m, m.xc - 0.142 * m.W) | tick(m, m.xc + 0.142 * m.W)


@g("`")
def grave_(m):
    # wide and clearly slanted, so that it cannot be taken for ' at small sizes
    return slash(m.xc + 0.175 * m.W, m.asc - 0.295 * m.cap, m.xc - 0.19 * m.W, m.asc,
                 m.a * m.lerp(1.42, 1.0), m.b * m.lerp(1.28, 1.0))   # heavier in the light weights; Bold must stay clear of '


# -- brackets --------------------------------------------------------------
@g("(")
def parenleft_(m):
    sw, hw, a, b, xc, H = _p(m)
    pa, pb = a * 0.96, b
    c = (m.btop + m.bbot) / 2
    half = (m.btop - m.bbot) / 2
    xl = 0.295 * m.W + pa
    # one continuous, round curve: the bowls of this family are squared, but a
    # squared parenthesis reads as a bracket
    s = half * 0.02
    RX, RY = 0.41 * m.W, (half - s) * 1.07
    k = 0.56
    sk = Skel(xl + RX, c + s + RY)
    sk.arc(xl, c + s, "h", k)
    sk.line(xl, c - s)
    sk.arc(xl + RX, c - s - RY, "v", k)
    return stroke(sk, pa, pb) & rect(-BIG, m.bbot, BIG, m.btop)


@g(")")
def parenright_(m):
    return parenleft_(m).flip_x(m.xc)


@g("[")
def bracketleft_(m):
    sw, hw, a, b, xc, H = _p(m)
    w, t = sw * 0.96, hw * 0.98
    x0, x1 = 0.305 * m.W, 0.705 * m.W
    return rect(x0, m.bbot, x0 + w, m.btop) | rect(x0, m.btop - t, x1, m.btop) | rect(x0, m.bbot, x1, m.bbot + t)


@g("]")
def bracketright_(m):
    return bracketleft_(m).flip_x(m.xc)


@g("{")
def braceleft_(m):
    sw, hw, a, b, xc, H = _p(m)
    w, t = sw * 0.94, hw * 0.98
    c = (m.btop + m.bbot) / 2
    xr, xm, xl = 0.745 * m.W, 0.48 * m.W, 0.185 * m.W
    yt = m.btop - t / 2
    span = m.btop - m.bbot
    top = opath(m, [(xr, yt), (xm, yt), (xm, c), (xl, c)], w, t, 0, 0,
                radii=[((xr - xm) * 0.82, span * 0.13), ((xm - xl) * 0.94, span * 0.085)])
    return top | top.flip_y(c)


@g("}")
def braceright_(m):
    return braceleft_(m).flip_x(m.xc)


def chevron_vx(x_tip, x_open, half_h, a, b):
    """x of the centre-line vertex of a chevron whose outer tip is at x_tip"""
    sgn = 1 if x_open > x_tip else -1
    off = a
    for _ in range(10):
        vx = x_tip + sgn * off
        L = math.hypot(x_open - vx, half_h)
        cos, sin = abs(x_open - vx) / L, half_h / L
        off = math.hypot(a * sin, b * cos) / sin
    return x_tip + sgn * off


def chevron(m, x_tip, x_open, half_h, a, b, cy=None) -> Shape:
    """< shape: sharp outer tip at x_tip, arms end with vertical cuts at x_open"""
    cy = m.axis if cy is None else cy
    vx = chevron_vx(x_tip, x_open, half_h, a, b)
    return pline([(x_open, cy + half_h), (vx, cy), (x_open, cy - half_h)], a, b, "v", "v")


LESS_HH = 0.255          # half height of < > as a fraction of the cap height


def less_geom(m):
    """(x_tip, x_open, half_h, a, b) of the less-than sign"""
    return m.OL - 0.01 * m.W, m.W - m.OL - 0.005 * m.W, LESS_HH * m.cap, m.a * 0.96, m.b * 0.96


@g("<")
def less_(m):
    return chevron(m, *less_geom(m))


@g(">")
def greater_(m):
    return less_(m).flip_x(m.xc)


# -- strokes ---------------------------------------------------------------
@g("/")
def slash_(m):
    return slash(0.135 * m.W, m.bbot, 0.865 * m.W, m.btop, m.a * 0.96, m.b)


@g("\\")
def backslash_(m):
    return slash_(m).flip_x(m.xc)


@g("|")
def bar_(m):
    w = m.sw * 0.98
    return rect(m.xc - w / 2, m.bbot, m.xc + w / 2, m.btop)


@g("_")
def underscore_(m):
    top = -0.105 * m.cap
    return rect(0.09 * m.W, top - m.hw, 0.91 * m.W, top)


# -- operators -------------------------------------------------------------
def obar(m, y, x0=None, x1=None, t=None):
    """horizontal operator bar centred on height y"""
    t = m.hw * 1.02 if t is None else t
    x0 = m.OL if x0 is None else x0
    x1 = m.W - m.OL if x1 is None else x1
    return rect(x0, y - t / 2, x1, y + t / 2)


def eq_gap(m):
    """distance of the two bars of = from the axis"""
    return 0.125 * m.cap + m.lerp(0, 6)


@g("-")
def hyphen_(m):
    return obar(m, m.axis, m.OL + 0.02 * m.W, m.W - m.OL - 0.02 * m.W)


@g("+")
def plus_(m):
    v = (m.W - 2 * m.OL) / 2
    w = m.sw * 0.95
    return obar(m, m.axis) | rect(m.xc - w / 2, m.axis - v, m.xc + w / 2, m.axis + v)


@g("=")
def equal_(m):
    return obar(m, m.axis + eq_gap(m)) | obar(m, m.axis - eq_gap(m))


@g("^")
def asciicircum_(m):
    H = m.cap
    s = pline([(m.xc - 0.265 * m.W, H * 0.55), (m.xc, H), (m.xc + 0.265 * m.W, H * 0.55)], m.a * 0.94, m.b * 0.94, "h", "h")
    return s & rect(-BIG, -BIG, BIG, H + m.os)


def tilde_shape(m, x0, x1, cy, amp, a, b):
    q = (x1 - x0) * 0.27
    xc = (x0 + x1) / 2
    d = (xc - (x0 + q), -amp * 1.9)
    sk = Skel(x0, cy - amp * 0.55)
    sk.arc(x0 + q, cy + amp, "v", 0.60)
    sk.bend(xc, cy, (1, 0), d, 0.58)
    sk.bend(x1 - q, cy - amp, d, (1, 0), 0.58)
    sk.arc(x1, cy + amp * 0.55, "h", 0.60)
    return stroke(sk, a, b)


@g("~")
def asciitilde_(m):
    return tilde_shape(m, m.OL - 0.02 * m.W + m.a, m.W - m.OL + 0.02 * m.W - m.a, m.axis, 0.085 * m.cap, m.a * 0.96, m.b * 1.02)


def asterisk_shape(m, cx, cy, r, t):
    out = None
    for ang in (90, 30, 150):
        dx, dy = r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))
        s = pline([(cx - dx, cy - dy), (cx + dx, cy + dy)], t / 2, t / 2)
        out = s if out is None else out | s
    return out


@g("*")
def asterisk_(m):
    return asterisk_shape(m, m.xc, m.axis + 0.02 * m.cap, 0.365 * m.W, m.hw * 1.06)


@g("#")
def numbersign_(m):
    sw, hw, a, b, xc, H = _p(m)
    w, t = sw * 0.90, hw * 0.94
    dx, dy = 0.155 * m.W, 0.172 * H
    x0, x1 = 0.075 * m.W, 0.925 * m.W
    s = rect(xc - dx - w / 2, 0, xc - dx + w / 2, H) | rect(xc + dx - w / 2, 0, xc + dx + w / 2, H)
    return s | rect(x0, H / 2 + dy - t / 2, x1, H / 2 + dy + t / 2) | rect(x0, H / 2 - dy - t / 2, x1, H / 2 - dy + t / 2)


@g("$")
def dollar_(m):
    """The S is drawn at 94 % of the cap height and the strokes reach 0.15 cap
    heights beyond the cap height and the baseline.  With a full-size S and
    short strokes (until 1.400) $ and S were the closest pair in the font:
    14-16 % of their ink apart, now 30-44 %."""
    sw, hw, a, b, xc, H = _p(m)
    f, ext = 0.94, 0.15 * H
    y0, y1 = H * (1 - f) / 2, H * (1 + f) / 2          # bottom and top of the S
    s = ess(m, m.UL + 0.004 * m.W, m.UR - 0.004 * m.W, H * f, m.csw, m.chw3, cut=0.205).move(0, y0)
    w = m.csw * 0.92
    return s | rect(xc - w / 2, y1 - m.chw3 / 2, xc + w / 2, H + ext) | rect(xc - w / 2, -ext, xc + w / 2, y0 + m.chw3 / 2)


def small_ring(m, x0, y0, x1, y1, sw, hw):
    return ring(m, x0, y0, x1, y1, sw, hw, 0.47 * (x1 - x0), 0.46 * (y1 - y0))


@g("%")
def percent_(m):
    sw, hw, a, b, xc, H = _p(m)
    psw, phw = sw * m.lerp(0.90, 0.66), hw * m.lerp(0.93, 0.72)
    rw, rh = 0.37 * m.W, 0.415 * H
    x0 = 0.045 * m.W
    r1 = small_ring(m, x0, H + m.os * 0.5 - rh, x0 + rw, H + m.os * 0.5, psw, phw)
    r2 = small_ring(m, m.W - x0 - rw, -m.os * 0.5, m.W - x0, rh - m.os * 0.5, psw, phw)
    sl = slash(0.15 * m.W, 0, 0.85 * m.W, H, a * m.lerp(0.88, 0.68), b * 0.8)
    return r1 | r2 | sl


@g("&")
def ampersand_(m):
    sw, hw, a, b, xc, H = _p(m)
    sw, hw = m.csw * m.lerp(0.97, 0.80), m.chw3 * m.lerp(1.0, 0.86)
    a, b = sw / 2, hw / 2
    yt, yb = H + m.os - b, -m.os + b
    # top bowl
    tl, tr = m.lerp(0.215, 0.185) * m.W + a, m.lerp(0.655, 0.675) * m.W - a
    # bottom bowl
    bl, br = 0.085 * m.W + a, 0.745 * m.W - a
    rxt, ryt = (tr - tl) * 0.5, H * 0.135
    rxb, ryb = (br - bl) * 0.46, H * 0.19
    y_tb = H * 0.66                       # lower end of the top bowl's sides
    y_bt = H * 0.40                       # upper end of the bottom bowl's left side
    # 1: leg from the bottom right up into the left side of the top bowl
    foot = (m.UR + 0.035 * m.W - a * 1.25, 0)
    d1 = (tl - foot[0] + 0.02 * m.W, y_tb - foot[1] - 0.08 * H)
    s1 = Skel(*foot)
    s1.line(tl + 0.34 * (foot[0] - tl), y_tb - 0.34 * (y_tb + 0.02 * H))
    s1.bend(tl, y_tb + 0.02 * H, (-(foot[0] - tl), y_tb), (0, 1), 0.62)
    s1.line(tl, yt - ryt)
    s1.arc(tl + rxt, yt, "v", m.k)
    s1.arc(tr, yt - ryt, "h", m.k)
    s1.line(tr, y_tb + 0.02 * H)
    leg = stroke(s1, a, b, ext0=40) & rect(-BIG, 0, BIG, BIG)
    # 2: from the right side of the top bowl down across to the bottom bowl and its arm
    s2 = Skel(tr, y_tb + 0.04 * H)
    dd = (bl - tr, (y_bt - 0.02 * H) - (y_tb))
    mid = ((tr + bl) / 2, (y_tb + y_bt) / 2)
    s2.bend(mid[0], mid[1], (0, -1), dd, 0.62)
    s2.bend(bl, y_bt - 0.02 * H, dd, (0, -1), 0.62)
    s2.line(bl, yb + ryb)
    s2.arc(bl + rxb, yb, "v", m.k)
    s2.line(br - rxb, yb)
    s2.arc(br, yb + ryb, "h", m.k)
    s2.line(br, H * 0.47)
    body = stroke(s2, a, b)
    return leg | body


@g("@")
def at_(m):
    sw, hw, a, b, xc, H = _p(m)
    w, t = sw * m.lerp(0.84, 0.64), hw * m.lerp(0.88, 0.72)
    x0, x1 = 0.055 * m.W, 0.945 * m.W
    y0, y1 = -0.215 * H, H + m.os
    xl, xr = x0 + w / 2, x1 - w / 2
    yb, yt = y0 + t / 2, y1 - t / 2
    il = 0.375 * m.W + w / 2
    ib, it = 0.105 * H + t / 2, 0.70 * H - t / 2
    R = (0.36 * (x1 - x0) - w / 2, 0.20 * (y1 - y0))
    r = ((xr - il) * 0.50, (it - ib) * 0.34)
    sk = round_path([(0.80 * m.W, yb), (xl, yb), (xl, yt), (xr, yt), (xr, ib), (il, ib), (il, it), (xr, it)],
                    R[0], R[1], m.k, radii=[R, R, R, r, r, r])
    return stroke(sk, w / 2, t / 2)
