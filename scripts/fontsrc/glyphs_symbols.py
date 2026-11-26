"""Latin-1 symbols, typographic punctuation, currency, superiors, arrows,
mathematical operators and geometric shapes."""
from __future__ import annotations

import math

from .geom import BIG, Shape, Skel, diag, diag_hw, pline, poly, rect, round_path, sbox, slash, slash_pts, stroke
from .glyphs_lower import a_, c_, o_, u_, _lc
from .glyphs_punct import (asterisk_shape, chevron, comma_, comma_tail, eq_gap, exclam_, obar, pdot, question_,
                           small_ring, tilde_shape, _p)
from .glyphs_upper import C_, M_, R_, S_, T_, Y_, one_, two_, three_, four_, zero_ring, _uc, _dg
from .kit import GLYPHS, Composite, dot, ess, g, opath, ring, srad, vstem


# -- .notdef ------------------------------------------------------------------
@g(".notdef")
def notdef_(m):
    t = m.hw * 0.9
    x0, x1 = 0.11 * m.W, 0.89 * m.W
    return rect(x0, 0, x1, m.cap) - rect(x0 + t, t, x1 - t, m.cap - t)


# -- inverted marks -------------------------------------------------------------
@g("exclamdown", uni=0xA1)
def exclamdown_(m):
    return exclam_(m).rot180(m.xc, (m.xh + m.cap * 0.75 - m.cap) / 2 + m.cap * 0.125)


@g("questiondown", uni=0xBF)
def questiondown_(m):
    return question_(m).rot180(m.xc, (m.xh + m.cap * 0.75 - m.cap) / 2 + m.cap * 0.125)


# -- currency -------------------------------------------------------------------
@g("cent", uni=0xA2)
def cent_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    w = sw * 0.90
    ext = 0.15 * m.xh
    x = xc - 0.012 * m.W
    return c_(m) | rect(x - w / 2, m.xh - b, x + w / 2, m.xh + ext) | rect(x - w / 2, -ext, x + w / 2, b)


@g("sterling", uni=0xA3)
def sterling_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    yt = H + m.os - b
    xs = L + 0.115 * m.W + a
    xr = R - 0.01 * m.W - a
    rx, ry = (xr - xs) * 0.52, H * 0.24
    hook = opath(m, [(xr, yt - ry), (xr, yt), (xs, yt), (xs, b)], sw, hw, rx, ry, radii=[(rx * 0.95, ry * 0.85), (rx, ry)])
    hook = hook - rect(xc + 0.03 * m.W, 0.30 * H, BIG, H * 0.755)
    ym = H * 0.44
    return hook | rect(L - 0.012 * m.W, 0, R + 0.012 * m.W, hw) | rect(L - 0.012 * m.W, ym - b, R - 0.09 * m.W, ym + b)


@g("currency", uni=0xA4)
def currency_(m):
    sw, hw, a, b, xc, H = _p(m)
    r = 0.265 * m.W
    cy = m.axis + 0.02 * H
    w, t = sw * 0.84, hw * 0.88
    s = ring(m, xc - r, cy - r, xc + r, cy + r, w, t, r * 0.98, r * 0.98)
    out = s
    for sx in (-1, 1):
        for sy in (-1, 1):
            p0 = (xc + sx * r * 0.62, cy + sy * r * 0.62)
            p1 = (xc + sx * r * 1.42, cy + sy * r * 1.42)
            out = out | pline([p0, p1], t * 0.5, t * 0.5)
    return out


@g("yen", uni=0xA5)
def yen_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    t = hw * 0.86
    x0, x1 = L + 0.045 * m.W, R - 0.045 * m.W
    return Y_(m) | rect(x0, H * 0.36 - t, x1, H * 0.36) | rect(x0, H * 0.36 - t - H * 0.155, x1, H * 0.36 - H * 0.155)


@g("Euro", uni=0x20AC)
def euro_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    t = hw * 0.84
    x0 = L + 0.045 * m.W
    s = ring(m, x0, -m.os, R + m.rnd, H + m.os, sw, hw)
    s = s - rect(xc + 0.03 * m.W, H * 0.25, BIG, H * 0.75)
    xb0, xb1 = L - 0.065 * m.W, xc + 0.115 * m.W
    return s | rect(xb0, H * 0.58, xb1, H * 0.58 + t) | rect(xb0, H * 0.42 - t, xb1 - 0.03 * m.W, H * 0.42)


# -- bars, section, pilcrow -------------------------------------------------------
@g("brokenbar", uni=0xA6)
def brokenbar_(m):
    w = m.sw * 0.98
    c = (m.btop + m.bbot) / 2
    gap = 0.075 * m.cap
    return rect(m.xc - w / 2, m.bbot, m.xc + w / 2, c - gap) | rect(m.xc - w / 2, c + gap, m.xc + w / 2, m.btop)


@g("section", uni=0xA7)
def section_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    sw, hw = sw * m.lerp(0.95, 0.76), m.chw3 * m.lerp(0.97, 0.82)
    a, b = sw / 2, hw / 2
    top, bot = H + m.os, -0.165 * H
    c = (top + bot) / 2
    x0, x1 = L + 0.045 * m.W, R - 0.045 * m.W
    rh = (top - bot) * 0.215                 # half height of the middle ring
    mid = ring(m, x0, c - rh, x1, c + rh, sw, hw, (x1 - x0) * 0.46, rh * 0.92)
    yt = top - b
    xl, xr = x0 + a, x1 - 0.02 * m.W - a
    rx, ry = (xr - xl) * 0.5, (yt - (c + rh - b)) * 0.5
    hook = opath(m, [(xr, yt - ry * 1.1), (xr, yt), (xl, yt), (xl, c + rh * 0.3)], sw, hw, rx, ry * 0.98,
                 radii=[(rx * 0.95, ry * 0.9), (rx, ry * 0.98)])
    hook = hook - rect(xc, c + rh + 1, BIG, top - (top - c - rh) * 0.52)
    return mid | hook | hook.rot180(xc, c)


@g("paragraph", uni=0xB6)
def paragraph_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    w = sw * m.lerp(0.86, 0.74)
    y0 = -0.14 * H
    x1 = xc + 0.035 * m.W
    x2 = R - 0.035 * m.W - w
    bw = sbox(L - 0.02 * m.W, H * 0.44, x1 + w, H, 0.30 * m.W, 0.27 * H, m.k) | rect(xc - 0.05 * m.W, H * 0.44, x1 + w, H)
    return bw | rect(x1, y0, x1 + w, H) | rect(x2, y0, x2 + w, H) | rect(x1, H - hw * 0.9, x2 + w, H)


@g("dagger", uni=0x2020)
def dagger_(m):
    sw, hw, a, b, xc, H = _p(m)
    w, t = sw * 0.92, hw * 0.94
    y = H * 0.68
    return rect(xc - w / 2, -0.14 * H, xc + w / 2, H) | rect(0.19 * m.W, y - t / 2, 0.81 * m.W, y + t / 2)


@g("daggerdbl", uni=0x2021)
def daggerdbl_(m):
    sw, hw, a, b, xc, H = _p(m)
    t = hw * 0.94
    y = H * 0.18
    return dagger_(m) | rect(0.19 * m.W, y - t / 2, 0.81 * m.W, y + t / 2)


# -- circled and raised -----------------------------------------------------------
def big_circle(m):
    w, t = m.sw * m.lerp(0.66, 0.50), m.hw * m.lerp(0.72, 0.56)
    r = 0.47 * m.W
    cy = m.cap * 0.5
    return ring(m, m.xc - r, cy - r, m.xc + r, cy + r, w, t, r * 0.90, r * 0.90), cy, w


def small_cap(m, fn, s, stem_f=0.62):
    """a capital drawn at reduced size with its own (heavier) pen"""
    f = m.scaled(s, stem=m.csw * m.lerp(stem_f, stem_f - 0.10))
    return fn(f), f


@g("copyright", uni=0xA9)
def copyright_(m):
    circ, cy, w = big_circle(m)
    s, f = small_cap(m, C_, 0.50)
    return circ | s.move(m.xc - f.W / 2 + 0.008 * m.W, cy - f.cap / 2)


@g("registered", uni=0xAE)
def registered_(m):
    circ, cy, w = big_circle(m)
    s, f = small_cap(m, R_, 0.50)
    return circ | s.move(m.xc - f.W / 2 + 0.004 * m.W, cy - f.cap / 2)


@g("trademark", uni=0x2122)
def trademark_(m):
    t, f = small_cap(m, T_, 0.46, 0.64)
    mm, f2 = small_cap(m, M_, 0.46, 0.64)
    y = m.cap - f.cap
    return t.move(0.03 * m.W - f.UL * 0.0, y) | mm.move(m.W - f2.W - 0.01 * m.W, y)


def superior(m, fn, s=0.56, stem_f=0.72):
    f = m.scaled(s, stem=m.csw * m.lerp(stem_f, stem_f - 0.08))
    return fn(f).move(m.xc - f.W / 2, m.cap + m.os - f.cap - f.os), f


@g("uni00B9", uni=0xB9)
def onesup_(m):
    return superior(m, one_)[0]


@g("uni00B2", uni=0xB2)
def twosup_(m):
    return superior(m, two_)[0]


@g("uni00B3", uni=0xB3)
def threesup_(m):
    return superior(m, three_)[0]


def ordinal(m, fn):
    f = m.scaled(0.62, stem=m.sw * m.lerp(0.76, 0.66))
    s = fn(f).move(m.xc - f.W / 2, m.cap - f.xh - f.os)
    t = m.hw * 0.78
    yb = m.cap - f.xh - 0.17 * m.cap
    return s | rect(m.xc - 0.19 * m.W, yb, m.xc + 0.19 * m.W, yb + t)


@g("ordfeminine", uni=0xAA)
def ordfeminine_(m):
    return ordinal(m, a_)


@g("ordmasculine", uni=0xBA)
def ordmasculine_(m):
    return ordinal(m, o_)


@g("degree", uni=0xB0)
def degree_(m):
    w, t = m.sw * m.lerp(0.80, 0.56), m.hw * m.lerp(0.84, 0.62)
    r = m.lerp(0.165, 0.18) * m.W
    return ring(m, m.xc - r, m.cap + m.os - 2 * r, m.xc + r, m.cap + m.os, w, t, r * 0.94, r * 0.94)


def fraction(m, num, den):
    f = m.scaled(0.43, stem=m.csw * m.lerp(0.66, 0.54))
    n = num(f).move(0.02 * m.W - f.DL * 0.35, m.cap - f.cap)
    d = den(f).move(m.W - f.W - 0.02 * m.W + f.DL * 0.35, 0)
    bar = slash(0.20 * m.W, -0.03 * m.cap, 0.80 * m.W, 1.03 * m.cap, m.a * m.lerp(0.62, 0.50), m.b * m.lerp(0.62, 0.50))
    return n | d | bar


@g("onequarter", uni=0xBC)
def onequarter_(m):
    return fraction(m, one_, four_)


@g("onehalf", uni=0xBD)
def onehalf_(m):
    return fraction(m, one_, two_)


@g("threequarters", uni=0xBE)
def threequarters_(m):
    return fraction(m, three_, four_)


@g("mu", uni=0xB5)
def mu_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return u_(m) | vstem(L, m.desc, m.xh * 0.4, sw)


# -- guillemets, dashes, quotes ------------------------------------------------
def guil(m, x_tip, x_open):
    return chevron(m, x_tip, x_open, 0.205 * m.cap, m.a * 0.92, m.b * 0.92, cy=m.xh * 0.5)


@g("guilsinglleft", uni=0x2039)
def guilsinglleft_(m):
    return guil(m, 0.25 * m.W, 0.70 * m.W)


@g("guilsinglright", uni=0x203A)
def guilsinglright_(m):
    return guilsinglleft_(m).flip_x(m.xc)


@g("guillemotleft", uni=0xAB)
def guillemotleft_(m):
    return guil(m, 0.06 * m.W, 0.47 * m.W) | guil(m, 0.50 * m.W, 0.91 * m.W)


@g("guillemotright", uni=0xBB)
def guillemotright_(m):
    return guillemotleft_(m).flip_x(m.xc)


@g("endash", uni=0x2013)
def endash_(m):
    return obar(m, m.axis, 0.085 * m.W, 0.915 * m.W)


@g("emdash", uni=0x2014)
def emdash_(m):
    return obar(m, m.axis, 0, m.W)


@g("uni00AD", uni=0xAD)
def softhyphen_(m):
    return obar(m, m.axis, m.OL + 0.02 * m.W, m.W - m.OL - 0.02 * m.W)


def quote_dot(m, double=False):
    """dot size of the curly quotes; the double ones are narrowed to stay apart"""
    return min(m.pdot, (0.235 if double else 0.30) * m.W)


def quote_mark(m, cx, d):
    return pdot(m, cx, 0, d) | comma_tail(m, cx, 0, d)


def raised_comma(m, cx, d):
    return quote_mark(m, cx, d).move(0, m.asc - d)


def _turn(m, shape, d):
    """6-shaped opening quote: the closing quote rotated about its own centre"""
    b = shape.bounds()
    return shape.rot180(m.xc, (b[1] + b[3]) / 2)


@g("quoteright", uni=0x2019)
def quoteright_(m):
    return raised_comma(m, m.xc, quote_dot(m))


@g("quoteleft", uni=0x2018)
def quoteleft_(m):
    return _turn(m, quoteright_(m), quote_dot(m))


@g("quotesinglbase", uni=0x201A)
def quotesinglbase_(m):
    return comma_(m)


@g("quotedblright", uni=0x201D)
def quotedblright_(m):
    d = quote_dot(m, True)
    return raised_comma(m, m.xc - 0.165 * m.W, d) | raised_comma(m, m.xc + 0.165 * m.W, d)


@g("quotedblleft", uni=0x201C)
def quotedblleft_(m):
    return _turn(m, quotedblright_(m), quote_dot(m, True))


@g("quotedblbase", uni=0x201E)
def quotedblbase_(m):
    d = quote_dot(m, True)
    return quote_mark(m, m.xc - 0.165 * m.W, d) | quote_mark(m, m.xc + 0.165 * m.W, d)


@g("bullet", uni=0x2022)
def bullet_(m):
    return dot(m, m.xc, m.axis, 0.34 * m.W)


@g("periodcentered", uni=[0xB7, 0x2219, 0x22C5])
def periodcentered_(m):
    return dot(m, m.xc, m.axis, m.pdot)


@g("ellipsis", uni=0x2026)
def ellipsis_(m):
    d = min(m.pdot * 0.84, 0.215 * m.W)
    return (dot(m, 0.165 * m.W, d / 2, d) | dot(m, 0.5 * m.W, d / 2, d) | dot(m, 0.835 * m.W, d / 2, d))


# -- arithmetic ------------------------------------------------------------------
@g("minus", uni=0x2212)
def minus_(m):
    return obar(m, m.axis)


@g("plusminus", uni=0xB1)
def plusminus_(m):
    v = (m.W - 2 * m.OL) / 2
    w = m.sw * 0.95
    cy = m.axis + 0.10 * m.cap
    return obar(m, cy) | rect(m.xc - w / 2, cy - v * 0.86, m.xc + w / 2, cy + v * 0.86) | obar(m, m.hw * 0.51)


@g("multiply", uni=0xD7)
def multiply_(m):
    r = (m.W - 2 * m.OL) / 2 * 0.80
    t = m.hw * 1.0
    s = pline([(m.xc - r, m.axis - r), (m.xc + r, m.axis + r)], t / 2, t / 2)
    return s | s.flip_x(m.xc)


@g("divide", uni=0xF7)
def divide_(m):
    d = m.pdot * 0.86
    off = 0.235 * m.cap
    return obar(m, m.axis) | dot(m, m.xc, m.axis + off, d) | dot(m, m.xc, m.axis - off, d)


@g("logicalnot", uni=0xAC)
def logicalnot_(m):
    w = m.sw * 0.95
    x1 = m.W - m.OL
    return obar(m, m.axis) | rect(x1 - w, m.axis - 0.235 * m.cap, x1, m.axis)


@g("notequal", uni=0x2260)
def notequal_(m):
    sl = slash(m.xc - 0.16 * m.W, m.axis - 0.335 * m.cap, m.xc + 0.16 * m.W, m.axis + 0.335 * m.cap, m.a * 0.86, m.b * 0.86)
    return obar(m, m.axis + eq_gap(m)) | obar(m, m.axis - eq_gap(m)) | sl


@g("equivalence", uni=0x2261)
def equivalence_(m):
    gp = eq_gap(m) * 1.55
    t = m.hw * m.lerp(1.0, 0.92)
    return obar(m, m.axis, t=t) | obar(m, m.axis + gp, t=t) | obar(m, m.axis - gp, t=t)


@g("approxequal", uni=0x2248)
def approxequal_(m):
    x0, x1 = m.OL - 0.02 * m.W + m.a, m.W - m.OL + 0.02 * m.W - m.a
    amp = 0.07 * m.cap
    gp = 0.135 * m.cap
    return (tilde_shape(m, x0, x1, m.axis + gp, amp, m.a * 0.94, m.b * 0.98)
            | tilde_shape(m, x0, x1, m.axis - gp, amp, m.a * 0.94, m.b * 0.98))


def lesseq(m):
    hh = 0.215 * m.cap
    cy = m.axis + 0.095 * m.cap
    ch = chevron(m, m.OL - 0.01 * m.W, m.W - m.OL - 0.005 * m.W, hh, m.a * 0.94, m.b * 0.94, cy=cy)
    return ch | obar(m, cy - hh - 0.115 * m.cap - m.hw * 0.5)


@g("lessequal", uni=0x2264)
def lessequal_(m):
    return lesseq(m)


@g("greaterequal", uni=0x2265)
def greaterequal_(m):
    return lesseq(m).flip_x(m.xc)


@g("infinity", uni=0x221E)
def infinity_(m):
    w, t = m.sw * m.lerp(0.84, 0.66), m.hw * m.lerp(0.90, 0.76)
    hh = 0.21 * m.cap
    x0 = 0.035 * m.W
    xm = m.xc
    left = small_ring(m, x0, m.axis - hh, xm + w / 2, m.axis + hh, w, t)
    return left | left.flip_x(m.xc)


@g("radical", uni=0x221A)
def radical_(m):
    t = m.hw * 0.92
    top = m.cap + 0.06 * m.cap
    pts = [(0.05 * m.W, 0.40 * m.cap), (0.19 * m.W, 0.40 * m.cap), (0.385 * m.W, 0.03 * m.cap), (0.62 * m.W, top), (0.96 * m.W, top)]
    return pline(pts, t / 2, t / 2, "v", "v") & rect(-BIG, 0, BIG, BIG)


@g("summation", uni=0x2211)
def summation_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    t = hw
    x0, x1 = L + 0.01 * m.W, R - 0.01 * m.W
    top, bot = H, -0.14 * H
    cy = (top + bot) / 2
    s = rect(x0, top - t, x1, top) | rect(x0, bot, x1, bot + t)
    up = slash(xc + 0.06 * m.W, cy, x0, top - t, a * 0.92, b, to_y1=top, to_y0=cy - 30) & rect(x0, cy, BIG, top)
    return s | up | up.flip_y(cy)


@g("product", uni=0x220F)
def product_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    bot = -0.14 * H
    x0, x1 = L + 0.02 * m.W, R - 0.02 * m.W
    return rect(L - 0.03 * m.W, H - hw, R + 0.03 * m.W, H) | rect(x0, bot, x0 + sw, H) | rect(x1 - sw, bot, x1, H)


@g("pi", uni=0x3C0)
def pi_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    x0, x1 = L + 0.045 * m.W, R - 0.045 * m.W
    return rect(L - 0.035 * m.W, m.xh - hw, R + 0.035 * m.W, m.xh) | rect(x0, 0, x0 + sw, m.xh) | rect(x1 - sw, 0, x1, m.xh)


@g("lambda", uni=0x3BB)
def lambda_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    c0, c1, h = slash_pts(R + 0.02 * m.W, 0, L + 0.03 * m.W, m.asc, a, b)
    long = diag(c0, c1, a, b)
    t = 0.50
    j = (c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t)
    xb = L - 0.02 * m.W
    hl = a
    for _ in range(8):
        hl = diag_hw(j[0] - (xb + hl), j[1], a, b)
    return long | diag((xb + hl, 0), (j[0] + 0.0, j[1]), a, b)


@g("Lambda", uni=0x39B)
def Lambda_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    from .geom import diag_edge
    apex = sw * 1.2
    left = diag_edge((L - 0.035 * m.W, 0), (xc - apex / 2, H), a * 0.98, b, +1)
    return left | left.flip_x(xc)


@g("Pi", uni=0x3A0)
def Pi_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    return rect(L - 0.02 * m.W, H - hw, R + 0.02 * m.W, H) | rect(L, 0, L + sw, H) | rect(R - sw, 0, R, H)


@g("Delta", uni=[0x2206, 0x394])
def increment_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    t = hw * 0.5
    x0, x1 = L - 0.03 * m.W, R + 0.03 * m.W
    outer = poly([(x0, 0), (x1, 0), (xc, H + 0.02 * H)])
    # inner triangle: offset by the stroke
    k = (x1 - x0) / 2 / (H * 1.02)
    off_side = sw * 0.92 * math.hypot(1, k)
    ix0 = x0 + off_side + hw * k
    inner = poly([(ix0, hw), (m.W - ix0, hw), (xc, hw + (xc - ix0) / k)])
    return outer - inner


# -- arrows -----------------------------------------------------------------------
def arrow_right(m, x0, x1, double=False, both=False, cy=None):
    """arrow from x0 to tip x1 (head pen like '>'), shaft like '-' or '='"""
    cy = m.axis if cy is None else cy
    hh = 0.215 * m.cap
    a, b = m.a * 0.94, m.b * 0.94
    head_len = 0.36 * m.W
    head = chevron(m, x1, x1 - head_len, hh, a, b, cy=cy)
    # centre-line vertex of the head
    bx = head.bounds()
    off = a
    for _ in range(8):
        vx = x1 - off
        L = math.hypot(head_len - off, hh)
        cos, sin = (head_len - off) / L, hh / L
        off = math.hypot(a * sin, b * cos) / sin
    vx = x1 - off
    out = head
    xs = x0
    if both:
        out = out | chevron(m, x0, x0 + head_len, hh, a, b, cy=cy)
        xs = x0 + off
    if double:
        gp = eq_gap(m)
        xe = vx - (vx - (x1 - head_len)) * (gp / hh)
        xs2 = xs + ((vx - (x1 - head_len)) * (gp / hh) if both else 0)
        out = out | obar(m, cy + gp, xs2, xe) | obar(m, cy - gp, xs2, xe)
    else:
        out = out | obar(m, cy, xs, vx)
    return out


def _rot90(s, m):
    """rotate a quarter turn counter-clockwise about the centre of the arrow"""
    cx, cy = m.xc, m.axis
    return s.transform(0, 1, -1, 0, cx + cy, cy - cx)


@g("arrowright", uni=0x2192)
def arrowright_(m):
    return arrow_right(m, 0.045 * m.W, 0.955 * m.W)


@g("arrowleft", uni=0x2190)
def arrowleft_(m):
    return arrowright_(m).flip_x(m.xc)


@g("arrowup", uni=0x2191)
def arrowup_(m):
    return _rot90(arrowright_(m), m)


@g("arrowdown", uni=0x2193)
def arrowdown_(m):
    return arrowup_(m).flip_y(m.axis)


@g("arrowboth", uni=0x2194)
def arrowboth_(m):
    return arrow_right(m, 0.025 * m.W, 0.975 * m.W, both=True)


@g("arrowupdn", uni=0x2195)
def arrowupdn_(m):
    return _rot90(arrowboth_(m), m)


@g("arrowdblright", uni=0x21D2)
def arrowdblright_(m):
    return arrow_right(m, 0.045 * m.W, 0.955 * m.W, double=True)


@g("arrowdblleft", uni=0x21D0)
def arrowdblleft_(m):
    return arrowdblright_(m).flip_x(m.xc)


@g("arrowdblboth", uni=0x21D4)
def arrowdblboth_(m):
    return arrow_right(m, 0.025 * m.W, 0.975 * m.W, double=True, both=True)


# -- geometric shapes ---------------------------------------------------------------
def _sq(m, f):
    r = f * m.W / 2
    cy = m.cap * 0.5
    return m.xc - r, cy - r, m.xc + r, cy + r


def _hollow(shape_fn, m, f, t):
    x0, y0, x1, y1 = _sq(m, f)
    return shape_fn(x0, y0, x1, y1) - shape_fn(x0 + t, y0 + t, x1 - t, y1 - t)


@g("filledbox", uni=0x25A0)
def filledbox_(m):
    return rect(*_sq(m, 0.86))


@g("H22073", uni=0x25A1)
def whitebox_(m):
    return _hollow(rect, m, 0.86, m.hw * 0.9)


@g("H18543", uni=0x25AA)
def smallfilledbox_(m):
    return rect(*_sq(m, 0.46))


@g("H18551", uni=0x25AB)
def smallwhitebox_(m):
    return _hollow(rect, m, 0.46, m.hw * 0.72)


def _circle(x0, y0, x1, y1):
    return sbox(x0, y0, x1, y1, (x1 - x0) / 2, (y1 - y0) / 2, 0.5523)


@g("H18533", uni=0x25CF)
def blackcircle_(m):
    return _circle(*_sq(m, 0.86))


@g("circle", uni=0x25CB)
def whitecircle_(m):
    return _hollow(_circle, m, 0.86, m.hw * 0.9)


def _tri(m, f, direction):
    x0, y0, x1, y1 = _sq(m, f)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if direction == "up":
        return [(x0, y0), (x1, y0), (cx, y1)]
    if direction == "down":
        return [(x0, y1), (cx, y0), (x1, y1)]
    if direction == "right":
        return [(x0, y0), (x1, cy), (x0, y1)]
    return [(x1, y0), (x1, y1), (x0, cy)]


def _tri_glyph(direction, hollow):
    def draw(m):
        pts = _tri(m, 0.86, direction)
        s = poly(pts)
        if not hollow:
            return s
        t = m.hw * 0.9
        # shrink towards the centroid by the stroke width
        cx = sum(p[0] for p in pts) / 3
        cy = sum(p[1] for p in pts) / 3
        # inradius of the triangle
        a_ = math.dist(pts[0], pts[1])
        b_ = math.dist(pts[1], pts[2])
        c_ = math.dist(pts[2], pts[0])
        sp = (a_ + b_ + c_) / 2
        area = abs((pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[2][0] - pts[0][0]) * (pts[1][1] - pts[0][1])) / 2
        rin = area / sp
        k = (rin - t) / rin
        # incentre
        ix = (b_ * pts[0][0] + c_ * pts[1][0] + a_ * pts[2][0]) / (a_ + b_ + c_)
        iy = (b_ * pts[0][1] + c_ * pts[1][1] + a_ * pts[2][1]) / (a_ + b_ + c_)
        inner = poly([(ix + (p[0] - ix) * k, iy + (p[1] - iy) * k) for p in pts])
        return s - inner

    return draw


for _name, _cp, _dir, _hol in [("triagup", 0x25B2, "up", False), ("uni25B3", 0x25B3, "up", True),
                               ("uni25B6", 0x25B6, "right", False), ("uni25B7", 0x25B7, "right", True),
                               ("triagdn", 0x25BC, "down", False), ("uni25BD", 0x25BD, "down", True),
                               ("uni25C0", 0x25C0, "left", False), ("uni25C1", 0x25C1, "left", True)]:
    g(_name, uni=_cp)(_tri_glyph(_dir, _hol))


def _diamond(x0, y0, x1, y1):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return poly([(cx, y0), (x1, cy), (cx, y1), (x0, cy)])


@g("uni25C6", uni=0x25C6)
def blackdiamond_(m):
    return _diamond(*_sq(m, 0.94))


@g("uni25C7", uni=[0x25C7, 0x25CA])
def whitediamond_(m):
    x0, y0, x1, y1 = _sq(m, 0.94)
    t = m.hw * 0.9 * math.sqrt(2)
    return _diamond(x0, y0, x1, y1) - _diamond(x0 + t, y0 + t, x1 - t, y1 - t)


@g("uni2713", uni=0x2713)
def check_(m):
    t = m.hw * 1.0
    pts = [(0.10 * m.W, 0.36 * m.cap), (0.37 * m.W, 0.06 * m.cap), (0.90 * m.W, 0.86 * m.cap)]
    return pline(pts, t / 2, t / 2) & rect(-BIG, 0, BIG, BIG)


@g("uni2717", uni=0x2717)
def ballotx_(m):
    t = m.hw * 1.0
    r = 0.36 * m.W
    cy = m.cap * 0.47
    s = pline([(m.xc - r, cy - r), (m.xc + r, cy + r)], t / 2, t / 2)
    return s | s.flip_x(m.xc)


@g("uniFFFD", uni=0xFFFD)
def replacement_(m):
    cy = m.cap * 0.5
    r = 0.49 * m.W
    dia = poly([(m.xc, cy - r * 1.28), (m.xc + r, cy), (m.xc, cy + r * 1.28), (m.xc - r, cy)])
    f = m.scaled(0.50, stem=m.csw * 0.60)
    q = question_(f).move(m.xc - f.W / 2, cy - f.cap / 2)
    return dia - q
