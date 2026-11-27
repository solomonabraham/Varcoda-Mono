"""Uppercase A-Z and the figures 0-9."""
from __future__ import annotations

from .geom import (BIG, Skel, diag, diag_edge, diag_hw, extend_line, halfplane, poly, rect, sbox, sbox4, slash, slash_in,
                   stroke)
from .kit import arch, bowl, dot, ess, g, kay, opath, ring, srad, vstem


def _uc(m):
    return m.csw, m.chw, m.ca, m.cb, m.UL, m.UR, m.xc, m.cap


def _dg(m):
    return m.csw, m.chw, m.ca, m.cb, m.DL, m.DR, m.xc, m.cap


# --------------------------------------------------------------------------
# capitals
# --------------------------------------------------------------------------
@g("A")
def A_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    xo = L - 0.035 * m.W
    apex = sw * 1.2
    left = diag_edge((xo, 0), (xc - apex / 2, H), a * 0.98, b, +1)
    tri = poly([(xo, 0), (m.W - xo, 0), (xc + apex / 2, H), (xc - apex / 2, H)])
    yb = H * 0.215
    return left | left.flip_x(xc) | (rect(0, yb, m.W, yb + hw) & tri)


def _bowls(m, L, x_right, levels, sw, hw):
    """D-shaped bowls stacked on a stem (B, P, R): levels = centre lines"""
    a, b = sw / 2, hw / 2
    x0 = L + a
    out = None
    for (y_top, y_bot, xr) in levels:
        r = (y_top - y_bot) / 2
        s = opath(m, [(x0, y_top), (xr - a, y_top), (xr - a, y_bot), (x0, y_bot)], sw, hw, (xr - a - x0) * 0.56, r * 0.98)
        out = s if out is None else out | s
    return out


@g("B")
def B_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    hw = m.chw3
    b = hw / 2
    L = L + 0.006 * m.W
    ym = H * 0.535
    bw = _bowls(m, L, R, [(H - b, ym, R - 0.036 * m.W), (ym, b, R + 0.008 * m.W)], sw, hw)
    return vstem(L, 0, H, sw) | bw


@g("C")
def C_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    s = ring(m, L - m.rnd, -m.os, R + m.rnd - 0.012 * m.W, H + m.os, sw, hw)
    return s - rect(xc, H * 0.265, BIG, H * 0.735)


@g("D")
def D_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    # tighter corners than O (and no overshoot) keep D and O apart, also in Bold
    xr = R + m.rnd * 0.5 - a
    w = R + m.rnd * 0.5 - L
    rx, ry = max(0.31 * w - a, sw * 0.2), max(0.235 * H - b, hw * 0.2)
    s = opath(m, [(L + a, H - b), (xr, H - b), (xr, b), (L + a, b)], sw, hw, rx, ry)
    return vstem(L, 0, H, sw) | s


@g("E")
def E_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    hw = m.chw3
    L = L + 0.014 * m.W
    ym = H * 0.525
    s = vstem(L, 0, H, sw) | rect(L, H - hw, R - 0.012 * m.W, H) | rect(L, 0, R - 0.004 * m.W, hw)
    return s | rect(L, ym - hw / 2, R - 0.05 * m.W, ym + hw / 2)


@g("F")
def F_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    L = L + 0.024 * m.W
    ym = H * 0.495
    s = vstem(L, 0, H, sw) | rect(L, H - hw, R - 0.002 * m.W, H)
    return s | rect(L, ym - hw / 2, R - 0.045 * m.W, ym + hw / 2)


@g("G")
def G_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    x1 = R + m.rnd - 0.006 * m.W
    s = ring(m, L - m.rnd, -m.os, x1, H + m.os, sw, hw)
    # the bar sits just above the middle and reaches past the centre, and the upper arm is
    # shorter than that of C: what separates G from C at 12-14 px (until 1.400: bar at 0.47
    # of the cap height, starting right of the centre, arm as long as that of C)
    yb = H * 0.51
    s = s - rect(xc, yb, BIG, H * 0.78)
    return s | rect(xc - 0.06 * m.W, yb - b, x1, yb + b)


@g("H")
def H_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    ym = H * 0.52
    return vstem(L, 0, H, sw) | vstem(R - sw, 0, H, sw) | rect(L, ym - b, R, ym + b)


@g("I")
def I_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    x0, x1 = L + 0.07 * m.W, R - 0.07 * m.W
    return vstem(xc - a, 0, H, sw) | rect(x0, H - hw, x1, H) | rect(x0, 0, x1, hw)


@g("J")
def J_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    xr = R - 0.04 * m.W - a
    xl = L + 0.024 * m.W + a
    yb = -m.os + b
    rx, ry = srad(m, xr - xl + sw, H, sw, hw)
    hook = opath(m, [(xr, H), (xr, yb), (xl, yb), (xl, yb + ry)], sw, hw, rx, ry * 0.8)
    hook = hook - rect(-BIG, H * 0.265, xc, BIG)
    return hook | rect(L + 0.12 * m.W, H - hw, xr, H)


@g("K")
def K_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    L = L + 0.004 * m.W
    return vstem(L, 0, H, sw) | kay(m, L, sw, H, R + 0.026 * m.W, R + 0.034 * m.W, a * 0.98, b, yj=0.38, t=0.30)


@g("L")
def L_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    L = L + 0.035 * m.W
    return vstem(L, 0, H, sw) | rect(L, 0, R - 0.004 * m.W, hw)


@g("M")
def M_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    msw = sw * m.lerp(0.96, 0.86)
    ML = L - 0.022 * m.W
    da, db = a * m.lerp(0.88, 0.72), b * m.lerp(0.95, 0.85)
    apex = 2 * da * 1.1
    s = vstem(ML, 0, H, msw) | diag_edge((ML, H), (xc - apex / 2, H * 0.36), da, db, +1)
    return s | s.flip_x(xc)


@g("N")
def N_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    nsw = sw * m.lerp(0.98, 0.92)
    s = vstem(L, 0, H, nsw) | vstem(R - nsw, 0, H, nsw)
    return s | slash(L, H, R, 0, a * m.lerp(0.95, 0.82), b)


@g("O")
def O_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    return ring(m, L - m.rnd, -m.os, R + m.rnd, H + m.os, sw, hw)


@g("P")
def P_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    L = L + 0.014 * m.W
    return vstem(L, 0, H, sw) | _bowls(m, L, R, [(H - b, H * 0.43, R + 0.008 * m.W)], sw, hw)


@g("Q")
def Q_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    tail = diag((xc + 0.02 * m.W, b), (R - 0.055 * m.W, -H * 0.20), a * 0.92, b)
    return O_(m) | tail


@g("R")
def R_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    L = L + 0.008 * m.W
    ym = H * 0.455
    s = vstem(L, 0, H, sw) | _bowls(m, L, R, [(H - b, ym, R - 0.004 * m.W)], sw, hw)
    xj, xb = xc - 0.01 * m.W, R + 0.022 * m.W
    h = a
    for _ in range(8):
        h = diag_hw((xb - h) - xj, -ym, a, b)
    return s | diag((xj, ym), (xb - h, 0), a, b)


@g("S")
def S_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    return ess(m, L - 0.004 * m.W, R + 0.004 * m.W, H, sw, m.chw3, cut=0.205)


@g("T")
def T_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    return rect(L - 0.02 * m.W, H - hw, R + 0.02 * m.W, H) | vstem(xc - a, 0, H, sw)


@g("U")
def U_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    rx, ry = srad(m, R - L, H, sw, hw)
    return opath(m, [(L + a, H), (L + a, -m.os + b), (R - a, -m.os + b), (R - a, H)], sw, hw, rx, ry)


@g("V")
def V_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    apex = sw * 1.15
    left = diag_edge((L - 0.035 * m.W, H), (xc - apex / 2, 0), a, b, +1)
    return left | left.flip_x(xc)


@g("W")
def W_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    wa, wb = a * m.lerp(0.88, 0.72), b * m.lerp(0.94, 0.84)
    xo = L - 0.045 * m.W
    x1 = xc - (xc - xo) * 0.50
    apex = 2 * wa * 1.12
    s1 = diag_edge((xo, H), (x1 - apex / 2, 0), wa, wb, +1)
    s2 = slash_in(x1 + apex / 2, 0, xc - apex / 2, H * 0.70, wa, wb)
    half = s1 | s2
    return half | half.flip_x(xc)


@g("X")
def X_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    s1 = slash(L - 0.024 * m.W, 0, R + 0.010 * m.W, H, a, b)
    return s1 | s1.flip_x(xc)


@g("Y")
def Y_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    xo = L - 0.035 * m.W
    yj = H * 0.40
    ya = a * 0.98
    h = diag_hw(xc - a - xo, yj - H, ya, b)
    c_top, c_bot = extend_line((xo + h, H), (xc - a + h, yj), None, yj - 0.1 * H)
    arm = diag(c_top, c_bot, ya, b)
    # keep the arm inside the outer edge of its mirror image
    arm = arm - halfplane((xc + a, yj), (m.W - xo, H), -1)
    return arm | arm.flip_x(xc) | vstem(xc - a, 0, yj + 0.04 * H, sw)


@g("Z")
def Z_(m):
    sw, hw, a, b, L, R, xc, H = _uc(m)
    x0, x1 = L - 0.004 * m.W, R + 0.008 * m.W
    x2, x3 = L + 0.012 * m.W, R - 0.008 * m.W
    dg = slash(x0, hw, x3, H - hw, a * 1.04, b, to_y0=0, to_y1=H) & rect(x0, 0, x3, H)
    return rect(x2, H - hw, x3, H) | rect(x0, 0, x1, hw) | dg


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def zero_ring(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    x0, x1 = L - m.rnd * 0.4, R + m.rnd * 0.4
    return ring(m, x0, -m.os, x1, H + m.os, sw, hw), x0, x1


def zero_dot(m):
    """the dot of the default zero: a pill as wide as a stem.  (A slash is too
    close to the letter Ø; the slashed zero is the 'zero' feature.)"""
    sw, hw, a, b, L, R, xc, H = _dg(m)
    w, h = sw * 1.02, 0.27 * H
    return sbox(xc - w / 2, H / 2 - h / 2, xc + w / 2, H / 2 + h / 2, w * 0.42, w * 0.42, 0.60)


def zero_slash(m):
    """the slash of the slashed zero: runs from side to side of the counter
    and dies in the ring"""
    sw, hw, a, b, L, R, xc, H = _dg(m)
    ring_, x0, x1 = zero_ring(m)
    outer = sbox(x0, -m.os, x1, H + m.os, *m.radii(x1 - x0, H + 2 * m.os), m.k)
    f = m.lerp(1.0, 0.74)                       # the slash must survive at 12 px, also in Light
    sl = slash(x0 + sw * 0.5, H * 0.24, x1 - sw * 0.5, H * 0.76, a * f, b * f, to_y0=H * 0.1, to_y1=H * 0.9)
    return sl & outer


@g("0")
def zero_(m):
    return zero_ring(m)[0] | zero_dot(m)


@g("1")
def one_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    xs = xc + 0.035 * m.W
    s = vstem(xs - a, 0, H, sw) | rect(L + 0.035 * m.W, 0, R - 0.012 * m.W, hw)
    return s | slash(L + 0.055 * m.W, H * 0.735, xs + a, H, a * 0.92, b)


@g("2")
def two_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    yt = H + m.os - b
    xl, xr = L + 0.016 * m.W + a, R - 0.004 * m.W - a
    rx, ry = srad(m, R - L, H * 0.80, sw, hw)
    xbl = L - 0.004 * m.W
    # where the side would meet the diagonal: at the waist of 3 and 8, so the head is as tall as
    # their upper bowls and the diagonal runs at 44 degrees (until 1.400: 0.49, a 40-degree diagonal)
    ix = (xr, H * 0.545)
    h = a
    for _ in range(8):
        e = (xbl + h, hw)
        h = diag_hw(e[0] - ix[0], e[1] - ix[1], a, b)
    e = (xbl + h, hw)
    dx, dy = e[0] - ix[0], e[1] - ix[1]
    dl = (dx * dx + dy * dy) ** 0.5
    d = (dx / dl, dy / dl)
    rn = 0.19 * H
    sk = Skel(xl, yt - ry * 0.85)
    sk.arc(xl + rx * 0.92, yt, "v", m.k)
    sk.line(xr - rx, yt)
    sk.arc(xr, yt - ry, "h", m.k)
    sk.line(xr, ix[1] + rn)
    sk.bend(ix[0] + d[0] * rn, ix[1] + d[1] * rn, (0, -1), d, 0.60)
    sk.line(e[0] + d[0] * 60, e[1] + d[1] * 60)
    s = stroke(sk, a, b) & rect(xbl, 0, BIG, BIG)
    s = s - rect(-BIG, H * 0.52, xc - 0.08 * m.W, H * 0.735)
    return s | rect(xbl, 0, R + 0.01 * m.W, hw)


@g("3")
def three_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    hw = m.chw3
    b = hw / 2
    yt, yb = H + m.os - b, -m.os + b
    ym = H * 0.535
    xr1, xr2 = R - 0.026 * m.W - a, R + 0.002 * m.W - a
    xl1, xl2 = L + 0.03 * m.W + a, L + 0.002 * m.W + a
    xm = xc - 0.07 * m.W
    ru, rl = (yt - ym) / 2, (ym - yb) / 2
    rx1, rx2 = (xr1 - xl1) * 0.50, (xr2 - xl2) * 0.50
    top = opath(m, [(xl1, yt - ru * 0.9), (xl1, yt), (xr1, yt), (xr1, ym), (xm, ym)], sw, hw, rx1, ru * 0.98,
                radii=[(rx1 * 0.9, ru * 0.85), None, None])
    bot = opath(m, [(xm, ym), (xr2, ym), (xr2, yb), (xl2, yb), (xl2, yb + rl * 0.9)], sw, hw, rx2, rl * 0.98,
                radii=[None, None, (rx2 * 0.9, rl * 0.85)])
    top = top - rect(-BIG, ym + b + 1, xc, H * 0.765)
    bot = bot - rect(-BIG, H * 0.235, xc, ym - b - 1)
    return top | bot


@g("4")
def four_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    xs = R - 0.10 * m.W - sw
    yb = H * 0.215
    xbl = L - 0.022 * m.W
    s = vstem(xs, 0, H, sw) | rect(xbl, yb, R + 0.022 * m.W, yb + hw)
    dg = slash(xbl, yb + hw, xs + sw, H, a * 0.95, b, to_y0=yb) & rect(xbl, yb, BIG, BIG)
    return s | dg


@g("5")
def five_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    xlo = L + 0.036 * m.W
    ybt = H * 0.60
    yb = -m.os + b
    xr = R + 0.006 * m.W - a
    xl2 = L + 0.004 * m.W + a
    rx, ry = (xr - xlo - a) * 0.54, (ybt - yb) * 0.47
    bw = opath(m, [(xlo + a, ybt), (xr, ybt), (xr, yb), (xl2, yb), (xl2, yb + ry)], sw, hw, rx, ry,
               radii=[None, None, (rx * 0.9, ry * 0.8)])
    bw = bw - rect(-BIG, H * 0.225, xc, ybt - b - 1)
    return bw | rect(xlo, ybt - b, xlo + sw, H) | rect(xlo, H - hw, R - 0.02 * m.W, H)


@g("6")
def six_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    yt = H + m.os - b
    ybt = H * 0.61
    rxo, ryo = 0.46 * (R - L), 0.46 * (ybt + m.os)
    # bowl: round outside; inside, the corner at the stem is only slightly eased
    outer = sbox(L, -m.os, R, ybt, rxo, ryo, m.k)
    ri = (max(rxo - sw, 1), max(ryo - hw, 1))
    ease = (min(ri[0], m.ease * 1.2), min(ri[1], m.ease * 1.2 * ri[1] / ri[0]))
    inner = sbox4(L + sw, -m.os + hw, R - sw, ybt - hw, ri, ri, ri, ease, m.k)
    rx, ry = srad(m, R - L, H * 0.9, sw, hw)
    xr = R - 0.024 * m.W - a
    arm = opath(m, [(L + a, ybt * 0.5), (L + a, yt), (xr, yt), (xr, yt - ry)], sw, hw, rx, ry,
                radii=[None, (rx * 0.9, ry * 0.8)])
    arm = arm - rect(xc, -BIG, BIG, H * 0.755)
    return (outer - inner) | arm | rect(L + sw - 2, ybt - hw, L + rxo + 2, ybt)


@g("7")
def seven_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    xr = R + 0.008 * m.W
    dg = slash(xc - 0.13 * m.W, 0, xr, H - hw, a, b, to_y1=H) & rect(-BIG, 0, xr, H)
    return rect(L - 0.006 * m.W, H - hw, xr, H) | dg


@g("8")
def eight_(m):
    sw, hw, a, b, L, R, xc, H = _dg(m)
    hw = m.chw3
    b = hw / 2
    ym = H * 0.535
    xu0, xu1 = L + 0.044 * m.W, R - 0.044 * m.W          # a clear waist keeps 8 apart from B
    x0, x1 = L - 0.006 * m.W, R + 0.006 * m.W
    up = ring(m, xu0, ym - b, xu1, H + m.os, sw, hw, 0.47 * (xu1 - xu0), 0.47 * (H + m.os - ym + b))
    lo = ring(m, x0, -m.os, x1, ym + b, sw, hw, 0.47 * (x1 - x0), 0.47 * (ym + b + m.os))
    return up | lo


@g("9")
def nine_(m):
    return six_(m).rot180(m.xc, m.cap / 2)
