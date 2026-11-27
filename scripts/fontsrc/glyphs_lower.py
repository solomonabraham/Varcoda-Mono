"""Lowercase a-z."""
from __future__ import annotations

from .geom import BIG, diag, diag_edge, diag_hw, halfplane, rect, round_path, slash, slash_in, stroke
from . import glyphs_italic as it
from .kit import arch, bowl, dot, ess, g, ital, kay, opath, ring, srad, vstem, blade, cut_below


def _lc(m):
    return m.sw, m.hw, m.a, m.b, m.L, m.R, m.xc


@g("a")
@ital(it.a_)
def a_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    hw, b = m.hw3, m.hw3 / 2
    xr = R - a
    rx, ry = srad(m, R - L, 2 * m.xh, sw, hw)
    yt = m.xh + m.os - b
    xtl = L + 0.03 * m.W + a
    arm = opath(m, [(xr, 0), (xr, yt), (xtl, yt), (xtl, yt - ry)], sw, hw, rx, ry,
                radii=[(rx, ry * 0.86), (rx * 0.86, ry * 0.80)])
    arm = arm - rect(-BIG, -BIG, xc, m.xh * 0.735)
    top = m.xh * m.lerp(0.585, 0.60)
    bw = bowl(m, m.W - R, m.W - (L - m.rnd * 0.6), 0, top, sw, hw).flip_x(xc)
    return arm | bw


@g("b")
@ital(it.b_)
def b_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return blade(m, _b_plain(m), L, sw, m.asc)


def _b_plain(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return vstem(L, 0, m.asc, sw) | bowl(m, L, R + m.rnd, 0, m.xh, sw, hw)


@g("c")
def c_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    s = ring(m, L - m.rnd, -m.os, R + m.rnd - 0.01 * m.W, m.xh + m.os, sw, hw)
    return s - rect(xc, m.xh * 0.265, BIG, m.xh * 0.735)


@g("d")
@ital(it.d_)
def d_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return blade(m, _b_plain(m).flip_x(m.xc), m.W - L - sw, sw, m.asc)


@g("e")
def e_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    hw, b = m.hw3, m.hw3 / 2
    x0, x1 = L - m.rnd, R + m.rnd
    ybar = m.xh * 0.5 + 0.008 * m.xh
    s = ring(m, x0, -m.os, x1, m.xh + m.os, sw, hw)
    s = s - rect(xc, m.xh * 0.20, BIG, ybar)
    return s | rect(x0 + a, ybar - b, x1, ybar + b)


@g("f")
@ital(it.f_)
def f_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = xc - 0.045 * m.W
    xe = R + 0.014 * m.W
    hook = opath(m, [(xs, 0), (xs, m.asc - b), (xe, m.asc - b)], sw, hw, 0.29 * m.W, 0.27 * m.xh)
    return hook | rect(L - 0.004 * m.W, m.xh - hw, R - 0.012 * m.W, m.xh)


@g("g")
@ital(it.g_)
def g_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    bw = bowl(m, m.W - R, m.W - (L - m.rnd), 0, m.xh, sw, hw).flip_x(xc)
    xr = R - a
    tail = opath(m, [(xr, m.xh), (xr, m.desc + b), (L + 0.04 * m.W, m.desc + b)], sw, hw, 0.27 * m.W, 0.25 * m.xh)
    return bw | tail


@g("h")
@ital(it.h_)
def h_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return blade(m, vstem(L, 0, m.asc, sw) | arch(m, L, R, m.xh, 0, sw, hw), L, sw, m.asc)


@g("i")
@ital(it.i_)
def i_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = xc + 0.012 * m.W - a
    s = vstem(xs, 0, m.xh, sw) | rect(L + 0.055 * m.W, m.xh - hw, xs + 2, m.xh) | rect(L + 0.02 * m.W, 0, R - 0.02 * m.W, hw)
    # the dot of i and j sits high enough to leave an empty pixel row above the stem at 11-16 px in
    # every weight (tests/rendering-tests: test_dots_stay_clear_of_their_stems)
    return s | dot(m, xs + a, m.xh * 1.285)


@g("j")
def j_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xsc = xc + 0.10 * m.W
    hook = opath(m, [(xsc, m.xh), (xsc, m.desc + b), (L + 0.025 * m.W, m.desc + b)], sw, hw, 0.27 * m.W, 0.25 * m.xh)
    return hook | rect(L + 0.11 * m.W, m.xh - hw, xsc, m.xh) | dot(m, xsc, m.xh * 1.285)


@g("k")
@ital(it.k_)
def k_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return blade(m, vstem(L, 0, m.asc, sw) | kay(m, L, sw, m.xh, R + 0.012 * m.W, R + 0.022 * m.W, a * 0.98, b), L, sw, m.asc)


@g("l")
def l_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xsc = xc - 0.04 * m.W
    r = 0.28 * m.W
    s = opath(m, [(xsc, m.asc), (xsc, b), (R + 0.02 * m.W, b)], sw, hw, r, r * 0.92)
    return s | rect(L + 0.03 * m.W, m.asc - hw, xsc, m.asc)


@ital(lambda m: it.m_(m, full=True))
def m_full_(m):
    """m with all three legs on the baseline (m.ss07)"""
    sw, hw, a, b, L, R, xc = _lc(m)
    msw, mhw = sw * m.lerp(0.95, 0.80), hw * m.lerp(0.97, 0.88)
    ML = L - m.lerp(0.034, 0.046) * m.W
    MR = m.W - ML
    cl = xc - msw / 2
    rx, ry = srad(m, (cl + msw) - ML, 2 * m.xh, msw, mhw)
    s = vstem(ML, 0, m.xh, msw)
    s = s | arch(m, ML, cl + msw, m.xh, 0, msw, mhw, rx, ry)
    s = s | arch(m, cl, MR, m.xh, 0, msw, mhw, rx, ry)
    # one level top: the valley above the middle stem is filled
    return s | rect(cl - rx, m.xh - mhw, cl + msw, m.xh)


@g("m")
@ital(it.m_)
def m_(m):
    """the middle leg stops short of the baseline: more air in the most
    crowded letter of a fixed-width alphabet"""
    sw, hw, a, b, L, R, xc = _lc(m)
    msw = sw * m.lerp(0.95, 0.80)
    cl = xc - msw / 2
    return m_full_(m) - rect(cl - 2, -BIG, cl + msw + 2, m.xh * 0.30)


@g("q")
@ital(it.q_)
def q_(m):
    """a short tail turns right at the foot, so that q is not the mirror
    image of p"""
    sw, hw, a, b, L, R, xc = _lc(m)
    xr = m.W - L - a
    top = cut_below(_p_plain(m).flip_x(m.xc), m.desc * 0.45)
    tail = opath(m, [(xr, 0), (xr, m.desc + b), (m.W - L + 0.078 * m.W, m.desc + b)], sw, hw, 0.105 * m.W, 0.10 * m.xh)
    return top | tail


@g("n")
@ital(it.n_)
def n_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return vstem(L, 0, m.xh, sw) | arch(m, L, R, m.xh, 0, sw, hw)


@g("o")
def o_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return ring(m, L - m.rnd, -m.os, R + m.rnd, m.xh + m.os, sw, hw)


@g("p")
@ital(it.p_)
def p_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return blade(m, _p_plain(m), L, sw, m.desc, up=False)


def _p_plain(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return vstem(L, m.desc, m.xh, sw) | bowl(m, L, R + m.rnd, 0, m.xh, sw, hw)


@ital(lambda m: it.q_(m, plain=True))
def q_plain_(m):
    """the mirror image of p, with the blade cut at the foot (q.ss06)"""
    sw, hw, a, b, L, R, xc = _lc(m)
    return blade(m, _p_plain(m).flip_x(m.xc), m.W - L - sw, sw, m.desc, up=False)


@g("r")
@ital(it.r_)
def r_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = L + m.lerp(0.100, 0.076) * m.W
    xe = R + m.rnd + 0.008 * m.W
    s = vstem(xs, 0, m.xh, sw) | arch(m, xs, xe, m.xh, -0.1 * m.xh, sw, hw)
    return s - rect(xs + sw + 1, -BIG, BIG, m.xh * 0.655)


@g("s")
def s_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return ess(m, L, R, m.xh, sw, m.hw3)


@g("t")
def t_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xsc = xc - 0.07 * m.W
    r = 0.28 * m.W
    s = opath(m, [(xsc, m.xh * 1.27), (xsc, b), (R + 0.02 * m.W, b)], sw, hw, r, r * 0.92)
    return blade(m, s, xsc - a, sw, m.xh * 1.27) | rect(L - 0.016 * m.W, m.xh - hw, R - 0.02 * m.W, m.xh)


@g("u")
@ital(it.u_)
def u_(m):
    return n_(m).rot180(m.xc, m.xh / 2)


@g("v")
def v_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xo = L - 0.03 * m.W
    apex = sw * 1.12
    left = diag_edge((xo, m.xh), (xc - apex / 2, 0), a, b, +1)
    return left | left.flip_x(xc)


@g("w")
def w_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    wa, wb = a * m.lerp(0.90, 0.74), b * m.lerp(0.94, 0.84)
    xo = L - 0.055 * m.W
    x1 = xc - (xc - xo) * 0.50
    apex = 2 * wa * 1.12
    ym = m.xh * 0.76
    s1 = diag_edge((xo, m.xh), (x1 - apex / 2, 0), wa, wb, +1)
    s2 = slash_in(x1 + apex / 2, 0, xc - apex / 2, ym, wa, wb)
    half = s1 | s2
    return half | half.flip_x(xc)


@g("x")
def x_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    s1 = slash(L - 0.016 * m.W, 0, R - 0.004 * m.W, m.xh, a, b)
    return s1 | s1.flip_x(xc)


@ital(it.y_)
def y_squared_(m):
    """u with a descending, hooked right stem (y.ss05).  It suits the squared
    bowls, but at 12-14 px it sits too close to g and u to be the default:
    see QUALITY_REPORT.md."""
    sw, hw, a, b, L, R, xc = _lc(m)
    xr = R - a
    tail = opath(m, [(xr, m.xh * 0.5), (xr, m.desc + b), (L + 0.075 * m.W, m.desc + b)], sw, hw, 0.27 * m.W, 0.25 * m.xh)
    return u_(m) | tail


@g("y")
@ital(it.y_)
def y_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    xo = L - 0.03 * m.W
    x_tail = L + 0.07 * m.W
    x_top = m.W - xo
    h = a
    for _ in range(8):
        h = diag_hw((x_top - h) - (x_tail + h), m.xh - m.desc, a, b)
    long = diag((x_tail + h, m.desc), (x_top - h, m.xh), a, b)
    t = ((x_top - h) - (x_tail + h)) / (m.xh - m.desc)
    yj = (xo - x_tail + t * (m.xh + m.desc)) / (2 * t)
    xj = xo + (m.xh - yj) * t
    left = diag((xo + h, m.xh), (xj + h, yj), a, b)
    return long | left


@g("z")
def z_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    x0, x1 = L - 0.004 * m.W, R + 0.008 * m.W          # bottom bar
    x2, x3 = L + 0.012 * m.W, R - 0.008 * m.W          # top bar
    top = rect(x2, m.xh - hw, x3, m.xh)
    bot = rect(x0, 0, x1, hw)
    dg = slash(x0, hw, x3, m.xh - hw, a * 1.04, b, to_y0=0, to_y1=m.xh) & rect(x0, 0, x3, m.xh)
    return top | bot | dg
