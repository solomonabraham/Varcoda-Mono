"""Italic lowercase: written forms, not a slanted roman.

Everything here is drawn upright and slanted afterwards (italic.py); the
glyph functions in glyphs_lower.py switch to these drawings when the master is
an italic (kit.ital).  Three gestures carry the hand, and each of them already
exists in the roman:

* the exit stroke - a stem that reaches the baseline leaves to the right, as
  the foot of the roman l and t does (a d h i k m n u);
* the branch - an arch grows out of its stem half-way up and thins there,
  instead of meeting it with a flat shoulder (h m n r, the bowl of b p);
* the return - the same curve turned round: a bowl runs back up into its
  stem (a d g q u y).

Stems that start at the x-height begin with the family's blade cut, the way
a pen sets down.  f descends and ends in a hook.  c e j l o s t v w x z keep
their roman construction: they have no stem standing on the baseline.
Terminals stay orthogonal and corners stay superelliptic, so the italic is
still the same family.
"""
from __future__ import annotations

from .geom import BIG, Skel, rect, stroke
from .kit import blade, dot, kay_arm, opath, srad, vstem

THIN = 0.74          # weight of a stroke where it leaves or joins a stem (× full weight)
LEAN = (0.34, 1.0)   # direction of a branch at the stem
BRANCH = 0.46        # height at which a branch leaves the centre of its stem (× x-height)
TUCK = 0.045         # the right stem moves in by this much (× advance) to make room for the exit stroke
EXIT = 0.150         # how far the exit stroke reaches beyond its stem (× advance)


def _f(m):
    """sw, hw, a, b, left edge, centre of the right stem"""
    return m.sw, m.hw, m.a, m.b, m.L, m.R - TUCK * m.W - m.a


def _exit(sk, m, x, a, b, reach=EXIT):
    """continue a skeleton that comes down at x: round the foot and leave to the right"""
    rx, ry = 0.13 * m.W, 0.19 * m.xh
    sk.line(x, b + ry)
    sk.arc(x + rx, b, "v", m.k)
    sk.line(x + a + reach * m.W, b)
    return sk


def stem_exit(m, x, top, sw=None, hw=None):
    """stem centred on x from `top` down to the baseline, with the exit stroke"""
    sw, hw = sw or m.sw, hw or m.hw
    return stroke(_exit(Skel(x, top), m, x, sw / 2, hw / 2), sw / 2, hw / 2)


def hump(m, xs, xr, top, foot=0.0, exit=None, sw=None, hw=None, branch=BRANCH, lean=LEAN):
    """The italic arch: branches out of a stem (centre xs), turns over at
    `top` and comes down as a leg (centre xr) to `foot` or into an exit stroke."""
    sw, hw = sw or m.sw, hw or m.hw
    a, b = sw / 2, hw / 2
    yt = top + m.os - b
    rx, ry = srad(m, xr - xs + sw, 2 * top, sw, hw)
    rx = min(rx, (xr - xs) * 0.56)
    sk = Skel(xs, branch * top)
    sk.bend(xr - rx, yt, lean, (1, 0), 0.60)
    sk.arc(xr, yt - ry, "h", m.k)
    if exit:
        _exit(sk, m, xr, a, b, exit)
    else:
        sk.line(xr, foot)
    return stroke(sk, a, b, w=[THIN] + [1.0] * (len(sk.nodes) - 1))


def cup(m, xs, xl, top, sw=None, hw=None):
    """The italic bowl, to the left of a stem (centre xs): level with the end
    of the stem at `top`, round the far side (skeleton x = xl) and the bottom,
    then back up into the stem.  Turned by 180 degrees it is the bowl of b and p."""
    sw, hw = sw or m.sw, hw or m.hw
    a, b = sw / 2, hw / 2
    yt, yb = top - b, -m.os + b
    rx, ry = srad(m, xs - xl + sw, top + m.os, sw, hw)
    rx = min(rx, (xs - xl) * 0.56)
    sk = Skel(xs, yt)
    sk.line(xl + rx, yt)
    sk.arc(xl, yt - ry, "h", m.k)
    sk.line(xl, yb + ry)
    sk.arc(xl + rx, yb, "v", m.k)
    sk.bend(xs, top * (1 - BRANCH), (1, 0), LEAN, 0.60)
    return stroke(sk, a, b, w=[1.0] * (len(sk.nodes) - 1) + [THIN])


def _cup_left(m):
    sw, hw, a, b, L, xr = _f(m)
    return cup(m, xr, L - m.rnd + a, m.xh)


def _cup_right(m):
    """bowl of b and p: the cup turned round, on a stem at the left edge"""
    sw, hw, a, b, L, xr = _f(m)
    return cup(m, m.W - L - a, m.W - (m.R + m.rnd - a), m.xh).rot180(m.xc, m.xh / 2)


def a_(m):
    sw, hw, a, b, L, xr = _f(m)
    return _cup_left(m) | stem_exit(m, xr, m.xh)


def b_(m):
    sw, hw, a, b, L, xr = _f(m)
    return blade(m, vstem(L, 0, m.asc, sw) | _cup_right(m), L, sw, m.asc)


def d_(m):
    sw, hw, a, b, L, xr = _f(m)
    return _cup_left(m) | blade(m, stem_exit(m, xr, m.asc), xr - a, sw, m.asc)


def eng_(m):
    sw, hw, a, b, L, xr = _f(m)
    yd = m.desc + b
    hook = opath(m, [(m.R - a, m.xh * 0.5), (m.R - a, yd), (m.xc - 0.045 * m.W, yd)], sw, hw, 0.20 * m.W, 0.22 * m.xh)
    return blade(m, vstem(L, 0, m.xh, sw) | hump(m, L + a, m.R - a, m.xh, m.xh * 0.3) | hook, L, sw, m.xh)


def f_(m):
    """descends, and ends in a hook to the left that answers the one at the top"""
    sw, hw, a, b, L, xr = _f(m)
    xs = m.xc - 0.035 * m.W
    yb = m.desc + b
    s = opath(m, [(m.R + 0.014 * m.W, m.asc - b), (xs, m.asc - b), (xs, yb), (L + 0.035 * m.W, yb)], sw, hw, 0.29 * m.W,
              0.27 * m.xh, radii=[None, (0.20 * m.W, 0.24 * m.xh)])
    return s | rect(L + 0.02 * m.W, m.xh - hw, m.R - 0.012 * m.W, m.xh)


def g_(m):
    sw, hw, a, b, L, xr = _f(m)
    tail = opath(m, [(xr, m.xh), (xr, m.desc + b), (L + 0.04 * m.W, m.desc + b)], sw, hw, 0.27 * m.W, 0.25 * m.xh)
    return _cup_left(m) | tail


def h_(m):
    sw, hw, a, b, L, xr = _f(m)
    return blade(m, vstem(L, 0, m.asc, sw) | hump(m, L + a, xr, m.xh, exit=EXIT), L, sw, m.asc)


def dotless_i(m):
    sw, hw, a, b, L, xr = _f(m)
    xs = m.xc - 0.02 * m.W
    return stem_exit(m, xs, m.xh) | rect(L + 0.06 * m.W, m.xh - hw, xs, m.xh)


def i_(m):
    return dotless_i(m) | dot(m, m.xc - 0.02 * m.W, m.xh * 1.285)


def k_(m):
    """the roman arm; the leg bends into an exit stroke"""
    sw, hw, a, b, L, xr = _f(m)
    ka, kb = a * 0.98, b
    arm, j, above = kay_arm(m, L, sw, m.xh, m.R + 0.012 * m.W, ka, kb)
    foot = (m.R - 0.075 * m.W, kb)                # where the straight leg would meet the baseline
    d = (foot[0] - j[0], foot[1] - j[1])
    sk = Skel(j[0] - 0.2 * d[0], j[1] - 0.2 * d[1])
    sk.line(j[0] + 0.52 * d[0], j[1] + 0.52 * d[1])
    sk.bend(foot[0] + 0.075 * m.W, kb, d, (1, 0), 0.62)
    sk.line(m.R + 0.045 * m.W, kb)
    return blade(m, vstem(L, 0, m.asc, sw) | arm | (stroke(sk, ka, kb) - above), L, sw, m.asc)


def m_(m, full=False):
    """two narrow humps; the middle leg stays short, as in the roman"""
    sw, hw, a, b, L, xr = _f(m)
    msw, mhw = sw * m.lerp(0.95, 0.80), hw * m.lerp(0.97, 0.88)
    ML = L - m.lerp(0.034, 0.046) * m.W
    x1, x3 = ML + msw / 2, m.W - ML - msw / 2 - 0.02 * m.W
    x2 = (x1 + x3) / 2
    kw = dict(sw=msw, hw=mhw, branch=0.60, lean=(0.18, 1.0))        # no room to branch as low as n does
    s = vstem(ML, 0, m.xh, msw) | hump(m, x1, x2, m.xh, 0 if full else m.xh * 0.30, **kw)
    return blade(m, s | hump(m, x2, x3, m.xh, exit=0.085, **kw), ML, msw, m.xh)


def n_(m):
    sw, hw, a, b, L, xr = _f(m)
    return blade(m, vstem(L, 0, m.xh, sw) | hump(m, L + a, xr, m.xh, exit=EXIT), L, sw, m.xh)


def p_(m):
    sw, hw, a, b, L, xr = _f(m)
    return blade(m, blade(m, vstem(L, m.desc, m.xh, sw) | _cup_right(m), L, sw, m.desc, up=False), L, sw, m.xh)


def q_(m, plain=False):
    sw, hw, a, b, L, xr = _f(m)
    if plain:
        return _cup_left(m) | blade(m, vstem(xr - a, m.desc, m.xh, sw), xr - a, sw, m.desc, up=False)
    tail = opath(m, [(xr, m.xh), (xr, m.desc + b), (xr + a + 0.078 * m.W, m.desc + b)], sw, hw, 0.105 * m.W, 0.10 * m.xh)
    return _cup_left(m) | tail


def r_(m):
    sw, hw, a, b, L, xr = _f(m)
    xs = L + m.lerp(0.100, 0.076) * m.W
    arm = hump(m, xs + a, m.R + m.rnd + 0.008 * m.W - a, m.xh, m.xh * 0.4)
    return blade(m, vstem(xs, 0, m.xh, sw) | (arm - rect(xs + sw + 1, -BIG, BIG, m.xh * 0.655)), xs, sw, m.xh)


def thorn_(m):
    sw, hw, a, b, L, xr = _f(m)
    return vstem(L, m.desc, m.asc, sw) | _cup_right(m)


def _u_bowl(m):
    sw, hw, a, b, L, xr = _f(m)
    return blade(m, hump(m, L + a, xr, m.xh).rot180((L + a + xr) / 2, m.xh / 2), L, sw, m.xh)


def u_(m):
    sw, hw, a, b, L, xr = _f(m)
    return _u_bowl(m) | blade(m, stem_exit(m, xr, m.xh), xr - a, sw, m.xh)


def y_(m):
    sw, hw, a, b, L, xr = _f(m)
    tail = opath(m, [(xr, m.xh), (xr, m.desc + b), (L + 0.075 * m.W, m.desc + b)], sw, hw, 0.27 * m.W, 0.25 * m.xh)
    return _u_bowl(m) | blade(m, tail, xr - a, sw, m.xh)
