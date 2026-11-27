"""Diacritics, accented letters and the special letters of Latin-1 and
Latin Extended-A."""
from __future__ import annotations

import unicodedata

from .geom import BIG, Shape, Skel, diag, diag_hw, pline, rect, round_path, slash, stroke
from .glyphs_lower import (a_, b_, d_, e_, f_, h_, i_, j_, l_, n_, o_, t_, u_, _lc)
from .glyphs_punct import chevron, comma_tail, pdot, tilde_shape
from .glyphs_upper import D_, H_, L_, N_, O_, T_, _bowls, _uc
from . import glyphs_italic as it
from .kit import GLYPHS, ORDER, Composite, arch, bowl, dot, g, glyph_name, ital, kay, opath, ring, srad, vstem

# --------------------------------------------------------------------------
# accent drawing.  lc zone sits above the x-height, the .case zone above caps
# --------------------------------------------------------------------------
def zone(m, case):
    if case:
        y0 = m.cap + 0.065 * m.cap
        return y0, 0.185 * m.cap
    y0 = m.xh + 0.105 * m.xh
    return y0, 0.295 * m.xh


def acc_pen(m, f=0.90):
    return m.a * f, m.b * f


def acute_shape(m, case, cx=None, f=1.0):
    cx = m.xc if cx is None else cx
    y0, h = zone(m, case)
    a, b = acc_pen(m)
    if case:
        return slash(cx - 0.105 * m.W * f, y0, cx + 0.125 * m.W * f, y0 + h, a, b)
    return slash(cx - 0.075 * m.W * f, y0, cx + 0.105 * m.W * f, y0 + h, a, b)


def circumflex_shape(m, case):
    y0, h = zone(m, case)
    a, b = acc_pen(m, 0.84)
    w = 0.185 * m.W
    s = pline([(m.xc - w, y0), (m.xc, y0 + h), (m.xc + w, y0)], a, b, "h", "h")
    return s & rect(-BIG, -BIG, BIG, y0 + h)


def tilde_acc(m, case):
    y0, h = zone(m, case)
    a, b = acc_pen(m, 0.82)
    return tilde_shape(m, m.xc - 0.215 * m.W + a, m.xc + 0.215 * m.W - a, y0 + h * 0.52, h * 0.26, a, b)


def dieresis_shape(m, case):
    y0, h = zone(m, case)
    d = m.dot * m.lerp(0.94, 0.80)
    cy = y0 + d / 2 + (0 if case else h * 0.12)
    return dot(m, m.xc - 0.155 * m.W, cy, d) | dot(m, m.xc + 0.155 * m.W, cy, d)


def dotaccent_shape(m, case):
    y0, h = zone(m, case)
    cy = y0 + m.dot / 2 + (0 if case else h * 0.12)
    return dot(m, m.xc, cy)


def ring_shape(m, case):
    y0, h = zone(m, case)
    hh = h * (1.12 if case else 1.0)
    w = 0.27 * m.W
    sw, hw = m.sw * m.lerp(0.70, 0.56), m.hw * m.lerp(0.74, 0.60)
    return ring(m, m.xc - w / 2, y0, m.xc + w / 2, y0 + hh, sw, hw, w * 0.48, hh * 0.48)


def macron_shape(m, case):
    y0, h = zone(m, case)
    t = m.hw * 0.90
    yb = y0 + h * (0.20 if case else 0.30)
    return rect(m.xc - 0.195 * m.W, yb, m.xc + 0.195 * m.W, yb + t)


def breve_shape(m, case):
    y0, h = zone(m, case)
    sw, hw = m.sw * 0.80, m.hw * 0.84
    w = 0.17 * m.W
    hh = h * (0.80 if case else 0.74)
    s = opath(m, [(m.xc - w, y0 + hh + 20), (m.xc - w, y0 + hw / 2), (m.xc + w, y0 + hw / 2), (m.xc + w, y0 + hh + 20)],
              sw, hw, w * 0.80, hh * 0.72)
    return s & rect(-BIG, -BIG, BIG, y0 + hh)


def hungar_shape(m, case):
    y0, h = zone(m, case)
    a, b = acc_pen(m, 0.84)
    s1 = slash(m.xc - 0.185 * m.W, y0, m.xc - 0.01 * m.W, y0 + h, a, b)
    s2 = slash(m.xc + 0.035 * m.W, y0, m.xc + 0.21 * m.W, y0 + h, a, b)
    return s1 | s2


def cedilla_shape(m, cx=None):
    cx = m.xc if cx is None else cx
    sw, hw = m.sw * 0.66, m.hw * 0.74
    y1 = -0.085 * m.cap
    y2 = min(-0.235 * m.cap, m.desc + hw / 2 - 0.005 * m.cap)
    xr = cx + 0.085 * m.W
    hook = opath(m, [(cx - sw / 2, y1), (xr, y1), (xr, y2), (cx - 0.095 * m.W, y2)], sw, hw, 0.075 * m.W, (y1 - y2) * 0.5)
    return hook | rect(cx - sw / 2, y1, cx + sw / 2, 0.01 * m.cap)


def ogonek_shape(m, cx=None):
    cx = m.xc if cx is None else cx
    sw, hw = m.sw * 0.70, m.hw * 0.78
    yb = m.desc + hw / 2 + 0.004 * m.cap
    return opath(m, [(cx, 0.03 * m.cap), (cx, yb), (cx + 0.135 * m.W, yb)], sw, hw, 0.095 * m.W, 0.14 * m.cap)


def commaaccent_shape(m, cx=None, top=None):
    cx = m.xc if cx is None else cx
    top = -0.085 * m.cap if top is None else top
    d = m.pdot * 0.86
    return diag((cx + d * 0.22, top), (cx - d * 0.20, top - d * 1.02), d * 0.27, d * 0.27)


def caron_alt_shape(m, case):
    """the apostrophe-like caron of ď ľ ť Ľ"""
    w = m.sw * 0.92
    top = m.cap if case else m.asc
    x = m.W * 0.865
    return slash(x - 0.045 * m.W - w / 2, top - 0.27 * m.cap, x + w / 2 + 0.02 * m.W, top, w / 2 * 0.9, w / 2 * 0.9)


ABOVE = {
    "grave": lambda m, c: acute_shape(m, c).flip_x(m.xc),
    "acute": acute_shape,
    "circumflex": circumflex_shape,
    "caron": lambda m, c: circumflex_shape(m, c).flip_y(zone(m, c)[0] + zone(m, c)[1] / 2),
    "tilde": tilde_acc,
    "dieresis": dieresis_shape,
    "dotaccent": dotaccent_shape,
    "ring": ring_shape,
    "macron": macron_shape,
    "breve": breve_shape,
    "hungarumlaut": hungar_shape,
}

# spacing clones in Unicode (lowercase position)
SPACING = {"acute": 0xB4, "circumflex": 0x2C6, "caron": 0x2C7, "tilde": 0x2DC, "dieresis": 0xA8, "dotaccent": 0x2D9,
           "ring": 0x2DA, "macron": 0xAF, "breve": 0x2D8, "hungarumlaut": 0x2DD}


def _mk(name, fn, case):
    def draw(m, fn=fn, case=case):
        return fn(m, case)

    return draw


for _n, _fn in ABOVE.items():
    # component glyphs used by the accented letters
    g(_n + "comb")(_mk(_n, _fn, False))
    g(_n + "comb.case")(_mk(_n, _fn, True))
    if _n in SPACING:
        g(glyph_name(SPACING[_n]), uni=SPACING[_n])(_mk(_n, _fn, False))


@g("cedilla", uni=0xB8)
def cedilla_(m):
    return cedilla_shape(m)


@g("ogonek", uni=0x2DB)
def ogonek_(m):
    return ogonek_shape(m)


@g("commaaccentcomb")
def commaaccent_(m):
    return commaaccent_shape(m)


@g("commaturnedabovecomb")
def commaturned_(m):
    y0, h = zone(m, False)
    return commaaccent_shape(m, m.xc, 0).rot180(m.xc, 0).move(0, y0 - 0.01 * m.xh)


@g("caroncomb.alt")
def caron_alt_(m):
    return caron_alt_shape(m, False)


@g("caroncomb.alt.case")
def caron_alt_case_(m):
    return caron_alt_shape(m, True)


# --------------------------------------------------------------------------
# special letters
# --------------------------------------------------------------------------
@g("dotlessi", uni=0x131)
@ital(it.dotless_i)
def dotlessi_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = xc + 0.012 * m.W - a
    return vstem(xs, 0, m.xh, sw) | rect(L + 0.075 * m.W, m.xh - hw, xs + 2, m.xh) | rect(L + 0.02 * m.W, 0, R - 0.02 * m.W, hw)


@g("uni0237", uni=0x237)
def dotlessj_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xsc = xc + 0.075 * m.W
    hook = opath(m, [(xsc, m.xh), (xsc, m.desc + b), (L + 0.05 * m.W, m.desc + b)], sw, hw, 0.27 * m.W, 0.25 * m.xh)
    return hook | rect(L + 0.10 * m.W, m.xh - hw, xsc, m.xh)


def _narrow(m, f_sw):
    """frame for the two halves of æ œ Æ Œ"""
    sw = m.sw * m.lerp(f_sw, f_sw - 0.12)
    return m.with_(sw=sw, hw=m.hw * m.lerp(0.97, 0.90), hw3=m.hw3 * m.lerp(0.97, 0.92))


@g("ae", uni=0xE6)
def ae_(m):
    n = _narrow(m, 0.90)
    x0, x1 = m.L - 0.04 * m.W, m.R + 0.04 * m.W
    half = (x1 - x0 + n.sw) / 2
    fa = n.with_(L=m.xc - half / 2, rnd=m.rnd * 0.4)
    left = a_.roman(fa).move(x0 - fa.L, 0)       # two-storey in the italic as well: there is no room for an exit stroke
    fe = n.with_(L=m.xc - half / 2 + fa.rnd, rnd=m.rnd * 0.4)
    right = e_(fe).move(x1 - (fe.R + fe.rnd), 0)
    return left | right


@g("oe", uni=0x153)
def oe_(m):
    n = _narrow(m, 0.90)
    x0, x1 = m.L - 0.04 * m.W, m.R + 0.04 * m.W
    half = (x1 - x0 + n.sw) / 2
    fo = n.with_(L=m.xc - half / 2 + m.rnd * 0.4, rnd=m.rnd * 0.4)
    left = o_(fo).move(x0 - (fo.L - fo.rnd), 0)
    right = e_(fo).move(x1 - (fo.R + fo.rnd), 0)
    return left | right


@g("AE", uni=0xC6)
def AE_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    sw2, hw2 = sw * m.lerp(0.90, 0.78), m.chw3 * 0.96
    a2 = sw2 / 2
    x0, x1 = L - 0.05 * m.W, R + 0.04 * m.W
    xs = xc + 0.01 * m.W                         # left edge of the E stem
    # left diagonal of the A leaning onto the E stem
    dg = slash(x0, 0, xs + sw2, H, a2 * 0.96, hw2 / 2)
    ym = H * 0.525
    e_part = vstem(xs, 0, H, sw2) | rect(xs, H - hw2, x1 - 0.01 * m.W, H) | rect(xs, 0, x1, hw2)
    e_part = e_part | rect(xs, ym - hw2 / 2, x1 - 0.035 * m.W, ym + hw2 / 2)
    yb = H * 0.215
    return dg | e_part | (rect(x0, yb, xs + 2, yb + hw2) & _hull_right(x0, xs + sw2, H, a2, hw2))


def _hull_right(x0, x_top, H, a2, hw2):
    """region to the right of the AE diagonal's outer (left) edge"""
    from .geom import poly, slash_pts
    c0, c1, h = slash_pts(x0, 0, x_top, H, a2 * 0.96, hw2 / 2)
    return poly([(c0[0] - h, 0), (BIG, 0), (BIG, H), (c1[0] - h, H)])


@g("OE", uni=0x152)
def OE_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    sw2, hw2 = sw * m.lerp(0.90, 0.78), m.chw3 * 0.96
    x0, x1 = L - 0.05 * m.W, R + 0.04 * m.W
    xs = xc + 0.01 * m.W
    ym = H * 0.525
    # O half: a tall ring whose right side is the E stem
    o = ring(m, x0, -m.os, xs + sw2, H + m.os, sw2, hw2)
    o = (o & rect(-BIG, -BIG, xs + sw2 / 2, BIG))
    e_part = vstem(xs, 0, H, sw2) | rect(xs, H - hw2, x1 - 0.01 * m.W, H) | rect(xs, 0, x1, hw2)
    e_part = e_part | rect(xs, ym - hw2 / 2, x1 - 0.035 * m.W, ym + hw2 / 2)
    return o | e_part


@g("oslash", uni=0xF8)
def oslash_(m):
    sl = slash(m.L - 0.02 * m.W, -0.085 * m.xh, m.R + 0.02 * m.W, m.xh * 1.085, m.a * 0.72, m.b * 0.72)
    return o_(m) | sl


@g("Oslash", uni=0xD8)
def Oslash_(m):
    sl = slash(m.UL - 0.02 * m.W, -0.07 * m.cap, m.UR + 0.02 * m.W, m.cap * 1.07, m.ca * 0.72, m.cb * 0.72)
    return O_(m) | sl


@g("eth", uni=0xF0)
def eth_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    top = m.xh * 0.93
    bw = ring(m, L - m.rnd, -m.os, R + m.rnd, top, sw, hw)
    xr = R + m.rnd - a
    # the ascender: rises from the right side and bends back to the upper left
    arc = opath(m, [(xr, top * 0.5), (xr, m.asc - b), (L + 0.10 * m.W, m.asc - b)], sw, hw, 0.36 * m.W, 0.36 * m.xh)
    bar = slash(xc - 0.07 * m.W, m.asc - 0.30 * m.xh, xc + 0.22 * m.W, m.asc - 0.02 * m.xh, a * 0.70, b * 0.70)
    return bw | arc | bar


@g("Eth", uni=[0xD0, 0x110])
def Eth_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    ym = H * 0.52
    return D_(m) | rect(L - 0.065 * m.W, ym - b, L + sw + 0.115 * m.W, ym + b)


@g("dcroat", uni=0x111)
def dcroat_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    y = m.xh + (m.asc - m.xh) * 0.52
    return d_(m) | rect(R - sw - 0.15 * m.W, y - b * 0.9, R + 0.065 * m.W, y + b * 0.9)


@g("thorn", uni=0xFE)
@ital(it.thorn_)
def thorn_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return vstem(L, m.desc, m.asc, sw) | bowl(m, L, R + m.rnd, 0, m.xh, sw, hw)


@g("Thorn", uni=0xDE)
def Thorn_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    L = L + 0.014 * m.W
    return vstem(L, 0, H, sw) | _bowls(m, L, R, [(H * 0.80 - b, H * 0.22 + b, R + 0.008 * m.W)], sw, hw)


@g("germandbls", uni=0xDF)
def germandbls_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    hw = m.hw3
    b = hw / 2
    yt = m.asc + m.os - b
    ym = m.xh * 0.60 + 0.5 * (m.asc - m.xh) * 0.2
    yb = -m.os + b
    xl = L + a
    xr1, xr2 = R - 0.045 * m.W - a, R + m.rnd - a
    xm = xc - 0.03 * m.W
    ru, rl = (yt - ym) / 2, (ym - yb) / 2
    rx1 = (xr1 - xl) * 0.52
    top = opath(m, [(xl, 0), (xl, yt), (xr1, yt), (xr1, ym), (xm, ym)], sw, hw, rx1, ru * 0.98,
                radii=[(rx1, ru * 0.80), None, None])
    rx2 = (xr2 - xm) * 0.62
    bot = opath(m, [(xm, ym), (xr2, ym), (xr2, yb), (xm - 0.055 * m.W, yb)], sw, hw, rx2, rl * 0.98)
    return top | bot


@g("hbar", uni=0x127)
def hbar_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    y = m.xh + (m.asc - m.xh) * 0.52
    return h_(m) | rect(L - 0.065 * m.W, y - b * 0.9, L + sw + 0.15 * m.W, y + b * 0.9)


@g("Hbar", uni=0x126)
def Hbar_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    y = H * 0.775
    return H_(m) | rect(L - 0.045 * m.W, y - b * 0.85, R + 0.045 * m.W, y + b * 0.85)


@g("lslash", uni=0x142)
def lslash_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xsc = xc - 0.04 * m.W
    cy = m.asc * 0.56
    return l_(m) | slash(xsc - 0.17 * m.W, cy - 0.105 * m.asc, xsc + 0.17 * m.W, cy + 0.105 * m.asc, a * 0.84, b * 0.84)


@g("Lslash", uni=0x141)
def Lslash_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    xsc = L + 0.035 * m.W + a
    cy = H * 0.52
    return L_(m) | slash(xsc - 0.14 * m.W, cy - 0.115 * H, xsc + 0.20 * m.W, cy + 0.115 * H, a * 0.84, b * 0.84)


@g("eng", uni=0x14B)
@ital(it.eng_)
def eng_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    yd = m.desc + b
    s = vstem(L, 0, m.xh, sw) | arch(m, L, R, m.xh, m.xh * 0.3, sw, hw)
    hook = opath(m, [(R - a, m.xh * 0.5), (R - a, yd), (xc - 0.045 * m.W, yd)], sw, hw, 0.20 * m.W, 0.22 * m.xh)
    return s | hook


@g("Eng", uni=0x14A)
def Eng_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    nsw = sw * m.lerp(0.98, 0.92)
    yd = -0.21 * H + b
    hook = opath(m, [(R - nsw / 2, H), (R - nsw / 2, yd), (xc - 0.02 * m.W, yd)], nsw, hw, 0.20 * m.W, 0.20 * H)
    s = vstem(L, 0, H, nsw) | hook
    return s | slash(L, H, R, 0, a * m.lerp(0.95, 0.82), b)


@g("tbar", uni=0x167)
def tbar_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xsc = xc - 0.07 * m.W
    y = m.xh * 0.46
    return t_(m) | rect(xsc - 0.17 * m.W, y - b * 0.85, xsc + 0.20 * m.W, y + b * 0.85)


@g("Tbar", uni=0x166)
def Tbar_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    y = H * 0.46
    return T_(m) | rect(xc - 0.20 * m.W, y - b * 0.85, xc + 0.20 * m.W, y + b * 0.85)


@g("kgreenlandic", uni=0x138)
def kra_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return vstem(L, 0, m.xh, sw) | kay(m, L, sw, m.xh, R + 0.012 * m.W, R + 0.022 * m.W, a * 0.98, b)


@g("longs", uni=0x17F)
def longs_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = xc - 0.06 * m.W
    hook = opath(m, [(xs, 0), (xs, m.asc - b), (R + 0.014 * m.W, m.asc - b)], sw, hw, 0.29 * m.W, 0.27 * m.xh)
    return hook | rect(L - 0.004 * m.W, m.xh - hw, xs, m.xh)


@g("napostrophe", uni=0x149)
def napostrophe_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    w = sw * 0.9
    x = L - 0.03 * m.W
    tick = slash(x - 0.02 * m.W, m.asc - 0.27 * m.cap, x + w + 0.03 * m.W, m.asc, w / 2 * 0.9, w / 2 * 0.9)
    return n_(m) | tick


@g("Ldot", uni=0x13F)
def Ldot_(m):
    return L_(m) | dot(m, m.UR - 0.11 * m.W, m.cap * 0.52, m.pdot * 0.92)


@g("ldot", uni=0x140)
def ldot_(m):
    return l_(m) | dot(m, m.R - 0.03 * m.W, m.xh * 0.62, m.pdot * 0.80)


@g("IJ", uni=0x132)
def IJ_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    sw2 = sw * m.lerp(0.94, 0.84)
    xi = L - 0.01 * m.W
    xr = R + 0.004 * m.W - sw2 / 2
    yb = -m.os + b
    hook = opath(m, [(xr, H), (xr, yb), (xc - 0.085 * m.W, yb), (xc - 0.085 * m.W, yb + 0.16 * H)], sw2, hw, 0.16 * m.W, 0.17 * H)
    hook = hook - rect(-BIG, H * 0.19, xr - sw2, BIG)
    return vstem(xi, 0, H, sw2) | hook


@g("ij", uni=0x133)
def ij_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    sw2 = sw * m.lerp(0.96, 0.86)
    xi = L + 0.015 * m.W
    xj = R - 0.005 * m.W - sw2 / 2
    hook = opath(m, [(xj, m.xh), (xj, m.desc + b), (xc - 0.06 * m.W, m.desc + b)], sw2, hw, 0.18 * m.W, 0.22 * m.xh)
    d = m.dot * 0.96
    return vstem(xi, 0, m.xh, sw2) | hook | dot(m, xi + sw2 / 2, m.xh * 1.255, d) | dot(m, xj, m.xh * 1.255, d)


@g("dcaron", uni=0x10F)
def dcaron_(m):
    """narrowed d that leaves room for the apostrophe-shaped caron"""
    inset = 0.08 * m.W
    d = d_(m.with_(L=m.L + inset / 2)).move(-inset / 2 - 0.014 * m.W, 0)
    xl = m.R - inset - 0.014 * m.W + 0.028 * m.W
    t = m.sw * 0.72
    return d | slash(xl, m.asc - 0.26 * m.cap, 0.992 * m.W, m.asc, t / 2, t / 2)


# --------------------------------------------------------------------------
# accented letters, generated from Unicode decompositions
# --------------------------------------------------------------------------
MARKS = {0x300: "grave", 0x301: "acute", 0x302: "circumflex", 0x303: "tilde", 0x304: "macron", 0x306: "breve",
         0x307: "dotaccent", 0x308: "dieresis", 0x30A: "ring", 0x30B: "hungarumlaut", 0x30C: "caron",
         0x327: "cedilla", 0x328: "ogonek", 0x326: "commaaccent"}

COMMA_BELOW = set("ĢĶĻŅŖķļņŗȘșȚț")      # drawn with a comma below
ALT_CARON = set("ľťĽ")

# where an attached mark hangs: fraction of the advance width (default: centre)
CEDILLA_X = {"c": 0.515, "C": 0.52, "s": 0.50, "S": 0.50, "t": 0.585, "T": 0.50}
OGONEK_X = {"a": None, "e": 0.545, "i": 0.545, "u": None, "A": None, "E": 0.72, "I": 0.52, "U": 0.55}


def _base_name(ch):
    if ch == "i":
        return "dotlessi"
    if ch == "j":
        return "uni0237"
    return glyph_name(ord(ch))


def _attach_x(m, ch, table):
    f = table.get(ch, 0.5)
    if f is not None:
        return f * m.W
    if ch in "au":
        return m.R - m.a * 0.55
    if ch == "A":
        return m.UR + 0.035 * m.W - m.ca * 2.1
    return m.xc


def _make_accented(cp, base, mark):
    ch = chr(cp)
    upper = base.isupper()
    bname = _base_name(base) if mark not in ("cedilla", "ogonek", "commaaccent") else glyph_name(ord(base))

    if ch == "ģ":                      # g takes a turned comma above instead
        return lambda m: Composite("g", "commaturnedabovecomb")
    if ch in COMMA_BELOW or mark == "commaaccent":
        return lambda m: Composite(glyph_name(ord(base)), "commaaccentcomb")
    if ch in ALT_CARON:
        acc = "caroncomb.alt.case" if upper else "caroncomb.alt"
        dx = {"ľ": -0.08, "ť": -0.02, "Ľ": -0.10}[ch]
        return lambda m: Composite(bname, (acc, round(dx * m.W), 0))
    if mark == "cedilla":
        def draw(m):
            return GLYPHS[bname]["func"](m) | cedilla_shape(m, _attach_x(m, base, CEDILLA_X))
        return draw
    if mark == "ogonek":
        def draw(m):
            return GLYPHS[bname]["func"](m) | ogonek_shape(m, _attach_x(m, base, OGONEK_X))
        return draw
    acc = mark + ("comb.case" if upper else "comb")
    # ascender letters (b d h k l) take the capital accents, raised
    if not upper and base in "bdhklf":
        return lambda m: Composite(bname, (mark + "comb.case", 0, round(m.asc - m.cap)))
    return lambda m: Composite(bname, acc)


def register_accented():
    ranges = list(range(0xC0, 0x180)) + [0x218, 0x219, 0x21A, 0x21B]
    for cp in ranges:
        name = glyph_name(cp)
        if name in GLYPHS or any(cp in v["unicodes"] for v in GLYPHS.values()):
            continue
        dec = unicodedata.decomposition(chr(cp)).split()
        if len(dec) != 2 or dec[0].startswith("<"):
            continue
        base, mark = chr(int(dec[0], 16)), MARKS.get(int(dec[1], 16))
        if mark is None or not base.isascii():
            continue
        g(name, uni=cp)(_make_accented(cp, base, mark))


register_accented()
