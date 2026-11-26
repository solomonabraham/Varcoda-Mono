"""Glyph registry and the shared construction helpers ("parts") that give
Varcoda Mono its consistent structure: stems, bars, superelliptic rings,
arches that branch out of stems, bowls, squircle dots."""
from __future__ import annotations

from fontTools.agl import UV2AGL

from .geom import (BIG, K, Shape, Skel, diag, diag_edge, diag_hw, extend_line, finalize, halfplane, pline, poly, rect,
                   round_path, rrect_skel, rrect_skel4, sbox, sbox4, slash, slash_in, slash_pts, stroke, union)

# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
GLYPHS = {}      # name -> dict(func=..., unicodes=[...], kind='outline'|'composite')
ORDER = []


def glyph_name(cp: int) -> str:
    if cp in UV2AGL:
        return UV2AGL[cp]
    return "uni%04X" % cp if cp <= 0xFFFF else "u%05X" % cp


def g(spec, uni=None):
    """Register a glyph drawing function.

    ``spec`` is a single character (name and code point are derived from it)
    or a glyph name; ``uni`` may list extra/explicit code points."""

    def deco(fn):
        if len(spec) == 1:
            cps = [ord(spec)]
            name = glyph_name(cps[0])
        else:
            name = spec
            cps = []
        if uni is not None:
            cps = list(uni) if isinstance(uni, (list, tuple)) else [uni]
        GLYPHS[name] = dict(func=fn, unicodes=cps)
        if name not in ORDER:
            ORDER.append(name)
        return fn

    return deco


class Composite:
    """A glyph made purely of references to other glyphs."""

    def __init__(self, *parts):
        # parts: (glyph name, dx, dy)
        self.parts = [(p, 0, 0) if isinstance(p, str) else p for p in parts]


# --------------------------------------------------------------------------
# parts
# --------------------------------------------------------------------------
def vstem(x0, y0, y1, w) -> Shape:
    return rect(x0, y0, x0 + w, y1)


def hbar(x0, x1, y0, h) -> Shape:
    return rect(x0, y0, x1, y0 + h)


def srad(m, w, h, sw, hw):
    """skeleton corner radii for a bowl whose *outer* size is w × h"""
    rxo, ryo = m.radii(w, h)
    return max(rxo - sw / 2, sw * 0.15), max(ryo - hw / 2, hw * 0.15)


def ring(m, x0, y0, x1, y1, sw, hw, rxo=None, ryo=None) -> Shape:
    """Closed superelliptic ring; (x0,y0,x1,y1) is the outer bounding box."""
    a, b = sw / 2, hw / 2
    if rxo is None:
        rxo, ryo = m.radii(x1 - x0, y1 - y0)
    sk = rrect_skel(x0 + a, y0 + b, x1 - a, y1 - b, max(rxo - a, 1), max(ryo - b, 1), m.k)
    return stroke(sk, a, b, closed=True)


def opath(m, pts, sw, hw, rx, ry, radii=None, **kw) -> Shape:
    """Stroke along an orthogonal polyline with rounded corners (skeleton
    coordinates, skeleton radii)."""
    return stroke(round_path(pts, rx, ry, m.k, radii), sw / 2, hw / 2, **kw)


def stem_side_radii(m, rx, ry, stem_w, e):
    """Corner radii on the side where an arch or bowl leaves its stem.  They
    are chosen so that the visible eased corner has the same width (m.ease)
    in every weight instead of growing with the bowl."""
    rxl = min(rx, m.ease + e + stem_w / 2)
    return rxl, ry * rxl / rx


def arch(m, xL, xR, top, foot, sw, hw, rx=None, ry=None, br=None, flush=True, stem_w=None) -> Shape:
    """The n-arch: springs out of a stem whose outer left edge is xL, runs
    flat along ``top``, turns a round shoulder and comes down as a leg to
    y=foot.  With ``flush`` the top stays level with the end of the stem
    (Varcoda Mono's flat shoulder); the inner corner at the stem is eased."""
    a, b = sw / 2, hw / 2
    stem_w = sw if stem_w is None else stem_w
    br = m.br if br is None else br
    e = br * stem_w
    if rx is None:
        rx, ry = srad(m, xR - xL, 2 * top, sw, hw)
    rxl, ryl = stem_side_radii(m, rx, ry, stem_w, e)
    yt = top - b
    xl, xr = xL + stem_w / 2 - e, xR - a
    sk = round_path([(xl, yt - ryl - 2), (xl, yt), (xr, yt), (xr, foot)], rx, ry, m.k, radii=[(rxl, ryl), (rx, ry)])
    s = stroke(sk, a, b) & rect(xL + stem_w / 2, -BIG, BIG, BIG)
    if flush and xl + rxl > xL + stem_w:
        s = s | rect(xL + stem_w - 2, top - hw, xl + rxl + 2, top)
    return s


def bowl(m, xL, xR, y0, y1, sw, hw, rx=None, ry=None, br=None, flush="both", stem_w=None) -> Shape:
    """A closed bowl attached to the right side of a stem whose outer left
    edge is xL.  flush='bottom' / 'top' / 'both' keeps that side level with
    the metric line (no overshoot there); a free side overshoots."""
    a, b = sw / 2, hw / 2
    stem_w = sw if stem_w is None else stem_w
    br = m.br if br is None else br
    e = br * stem_w
    fb, ft = flush in ("bottom", "both"), flush in ("top", "both")
    yb = y0 + b if fb else y0 - m.os + b
    yt = y1 - b if ft else y1 + m.os - b
    if rx is None:
        rx, ry = srad(m, xR - xL, yt - yb + hw, sw, hw)
    rxl, ryl = stem_side_radii(m, rx, ry, stem_w, e)
    xl = xL + stem_w / 2 - e
    sk = rrect_skel4(xl, yb, xR - a, yt, (rxl, ryl), (rx, ry), (rx, ry), (rxl, ryl), m.k)
    s = stroke(sk, a, b, closed=True) & rect(xL + stem_w / 2, -BIG, BIG, BIG)
    if fb and xl + rxl > xL + stem_w:
        s = s | rect(xL + stem_w - 2, y0, xl + rxl + 2, y0 + hw)
    if ft and xl + rxl > xL + stem_w:
        s = s | rect(xL + stem_w - 2, y1 - hw, xl + rxl + 2, y1)
    return s


def dot(m, cx, cy, size=None) -> Shape:
    """The squircle dot used by i j . : ; ! ? and the dieresis."""
    d = size if size is not None else m.dot
    return sbox(cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2, d * 0.17, d * 0.17, 0.60)


def blade(m, shape, x, w, y, up=True) -> Shape:
    """The family's own detail: the free end of an extender (the stem of
    b d h k t above the x-height, of p q below the baseline) is sliced at an
    angle instead of square.  Top and bottom cuts are parallel; x, w: the
    stem; y: the height of its end."""
    rise = m.blade * w
    s = rise / w
    if up:      # top edge: the left corner drops by `rise`
        tri = poly([(x - 4, y - rise - 4 * s), (x + w + 4, y + 4 * s), (x - 4, y + 4 * s + 4)])
    else:       # bottom edge: the right corner lifts by `rise`
        tri = poly([(x - 4, y - 4 * s), (x + w + 4, y + rise + 4 * s), (x + w + 4, y - 4 * s - 4)])
    return shape - tri


def cut_above(shape, y):
    return shape & rect(-BIG, -BIG, BIG, y)


def cut_below(shape, y):
    return shape & rect(-BIG, y, BIG, BIG)


def cut_left(shape, x):
    return shape & rect(x, -BIG, BIG, BIG)


def cut_right(shape, x):
    return shape & rect(-BIG, -BIG, x, BIG)


def ess(m, L, R, H, sw, hw, cut=0.215, upper_inset=(0.012, 0.018), lower_out=(0.004, 0.004), mid=0.51) -> Shape:
    """The S skeleton: two stacked half-squircles joined by a level spine.
    Terminals are cut horizontally."""
    a, b = sw / 2, hw / 2
    yt, yb = H + m.os - b, -m.os + b
    ym = H * mid
    xl1, xr1 = L + upper_inset[0] * m.W + a, R - upper_inset[1] * m.W - a   # upper bowl
    xl2, xr2 = L - lower_out[0] * m.W + a, R + lower_out[1] * m.W - a       # lower bowl
    ry1, ry2 = (yt - ym) / 2, (ym - yb) / 2
    rx = (xr2 - xl1) * 0.47
    sk = round_path([(xr1, yt - ry1), (xr1, yt), (xl1, yt), (xl1, ym), (xr2, ym), (xr2, yb), (xl2, yb), (xl2, yb + ry2)],
                    rx, ry1, m.k, radii=[(rx, ry1), (rx, ry1), (rx, ry1), (rx, ry2), (rx, ry2), (rx, ry2)])
    s = stroke(sk, a, b)
    s = s - rect(m.xc, ym + b + 1, BIG, H * (1 - cut))
    s = s - rect(-BIG, H * cut, m.xc, ym - b - 1)
    return s


def kay(m, L, sw, top, x_arm, x_leg, ka, kb, yj=0.36, t=0.30) -> Shape:
    """Arm and leg of k / K: the arm leaves the stem's right edge at yj*top,
    the leg leaves the arm at fraction t of its length."""
    pj = (L + sw, top * yj)
    h = ka
    for _ in range(8):
        h = diag_hw((x_arm - h) - pj[0], top - pj[1], ka, kb)
    c1 = (x_arm - h, top)
    slope = (c1[0] - pj[0]) / (c1[1] - pj[1])
    c0 = (pj[0] - slope * 0.3 * top, pj[1] - 0.3 * top)
    arm = diag(c0, c1, ka, kb) & rect(L + sw / 2, -BIG, BIG, BIG)
    j = (pj[0] + (c1[0] - pj[0]) * t, pj[1] + (c1[1] - pj[1]) * t)
    hl = ka
    for _ in range(8):
        hl = diag_hw((x_leg - hl) - j[0], -j[1], ka, kb)
    up = 0.1 * top
    leg = diag((j[0] - (x_leg - hl - j[0]) * (up / j[1]), j[1] + up), (x_leg - hl, 0), ka, kb)
    leg = leg - halfplane((c0[0] - h, c0[1]), (c1[0] - h, c1[1]), +1)
    return arm | leg
