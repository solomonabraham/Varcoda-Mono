"""Outline geometry kit for Varcoda Mono.

Everything a glyph is made of is produced here:

* ``Shape``      closed cubic outlines + boolean algebra (union ``|``,
                 intersection ``&``, difference ``-``) backed by skia-pathops.
* ``Skel``       a skeleton (centre-line) made of lines and cubic arcs.
* ``stroke``     expands a smooth skeleton with an *elliptical pen*
                 (half-width ``a`` for vertical stems, half-height ``b`` for
                 horizontal strokes).  Offsets are fitted as single cubics that
                 keep the skeleton's node structure, so on-curve points stay on
                 horizontal/vertical extremes like in hand-drawn outlines.
* ``pline``      mitred polygon stroke for straight strokes and diagonals with
                 horizontal / vertical terminal cuts.

Coordinates are font units (1000 UPM), y up.
"""
from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

import pathops
from fontTools.pens.recordingPen import RecordingPen
from pathops import Path, PathOp

Pt = Tuple[float, float]
BIG = 5000.0
K = 0.62  # default tension of a superelliptic quarter arc (0.5523 = circle)


# --------------------------------------------------------------------------
# Shape
# --------------------------------------------------------------------------
class Shape:
    """A set of closed contours.  contour = [('M', p), ('L', p) | ('C', c1, c2, p), ...]"""

    __slots__ = ("contours",)

    def __init__(self, contours=None):
        self.contours = contours or []

    # -- conversion -------------------------------------------------------
    def to_skia(self) -> Path:
        p = Path()
        for c in self.contours:
            for seg in c:
                if seg[0] == "M":
                    p.moveTo(*seg[1])
                elif seg[0] == "L":
                    p.lineTo(*seg[1])
                else:
                    p.cubicTo(*seg[1], *seg[2], *seg[3])
            p.close()
        return p

    @classmethod
    def from_skia(cls, path: Path) -> "Shape":
        rec = RecordingPen()
        path.draw(rec)
        contours, cur, last = [], None, None
        for op, args in rec.value:
            if op == "moveTo":
                cur = [("M", args[0])]
                last = args[0]
            elif op == "lineTo":
                cur.append(("L", args[0]))
                last = args[0]
            elif op == "curveTo":
                cur.append(("C", args[0], args[1], args[2]))
                last = args[2]
            elif op == "qCurveTo":
                pts = list(args)
                on_pts = []
                # expand implied on-curve points, then elevate each quad
                for i in range(len(pts) - 1):
                    off = pts[i]
                    if i < len(pts) - 2:
                        nxt = pts[i + 1]
                        on = ((off[0] + nxt[0]) / 2, (off[1] + nxt[1]) / 2)
                    else:
                        on = pts[-1]
                    on_pts.append((off, on))
                for off, on in on_pts:
                    c1 = (last[0] + 2 / 3 * (off[0] - last[0]), last[1] + 2 / 3 * (off[1] - last[1]))
                    c2 = (on[0] + 2 / 3 * (off[0] - on[0]), on[1] + 2 / 3 * (off[1] - on[1]))
                    cur.append(("C", c1, c2, on))
                    last = on
            elif op in ("closePath", "endPath"):
                if cur and len(cur) > 2:
                    contours.append(cur)
                cur = None
        return cls(contours)

    # -- boolean algebra ---------------------------------------------------
    def _op(self, other: "Shape", operator) -> "Shape":
        if not other.contours:
            return self if operator != PathOp.INTERSECTION else Shape()
        if not self.contours:
            return other if operator == PathOp.UNION else Shape()
        res = pathops.op(self.to_skia(), other.to_skia(), operator, fix_winding=True, keep_starting_points=False)
        return Shape.from_skia(res)

    def __or__(self, other):
        return self._op(other, PathOp.UNION)

    def __and__(self, other):
        return self._op(other, PathOp.INTERSECTION)

    def __sub__(self, other):
        return self._op(other, PathOp.DIFFERENCE)

    # -- transforms --------------------------------------------------------
    def transform(self, a, b, c, d, e, f) -> "Shape":
        """x' = a*x + c*y + e ; y' = b*x + d*y + f"""

        def t(p):
            return (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)

        out = []
        for cont in self.contours:
            out.append([(seg[0],) + tuple(t(p) for p in seg[1:]) for seg in cont])
        return Shape(out)

    def move(self, dx=0.0, dy=0.0):
        return self.transform(1, 0, 0, 1, dx, dy)

    def flip_x(self, cx):
        """mirror left-right about the vertical line x = cx"""
        return self.transform(-1, 0, 0, 1, 2 * cx, 0)

    def flip_y(self, cy):
        return self.transform(1, 0, 0, -1, 0, 2 * cy)

    def rot180(self, cx, cy):
        return self.transform(-1, 0, 0, -1, 2 * cx, 2 * cy)

    def scale(self, sx, sy=None, cx=0.0, cy=0.0):
        sy = sx if sy is None else sy
        return self.transform(sx, 0, 0, sy, cx - sx * cx, cy - sy * cy)

    def skew(self, tan, cy=0.0):
        """horizontal shear: x' = x + tan*(y-cy)"""
        return self.transform(1, 0, tan, 1, -tan * cy, 0)

    # -- queries -----------------------------------------------------------
    def points(self):
        for cont in self.contours:
            for seg in cont:
                for p in seg[1:]:
                    yield p

    def bounds(self):
        b = self.to_skia().bounds
        return b  # (xmin, ymin, xmax, ymax)

    def is_empty(self):
        return not self.contours


def union(*shapes: Shape) -> Shape:
    out = Shape()
    for s in shapes:
        if s is None:
            continue
        out = out | s
    return out


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------
def poly(pts: Sequence[Pt]) -> Shape:
    return Shape([[("M", pts[0])] + [("L", p) for p in pts[1:]]])


def rect(x0, y0, x1, y1) -> Shape:
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def sbox(x0, y0, x1, y1, rx, ry=None, k=K) -> Shape:
    """Filled superelliptic rounded rectangle (used for dots)."""
    ry = rx if ry is None else ry
    rx = min(rx, (x1 - x0) / 2)
    ry = min(ry, (y1 - y0) / 2)
    hx, hy = rx * (1 - k), ry * (1 - k)
    c = [("M", (x0 + rx, y0))]
    if x1 - rx > x0 + rx:
        c.append(("L", (x1 - rx, y0)))
    c.append(("C", (x1 - hx, y0), (x1, y0 + hy), (x1, y0 + ry)))
    if y1 - ry > y0 + ry:
        c.append(("L", (x1, y1 - ry)))
    c.append(("C", (x1, y1 - hy), (x1 - hx, y1), (x1 - rx, y1)))
    if x1 - rx > x0 + rx:
        c.append(("L", (x0 + rx, y1)))
    c.append(("C", (x0 + hx, y1), (x0, y1 - hy), (x0, y1 - ry)))
    if y1 - ry > y0 + ry:
        c.append(("L", (x0, y0 + ry)))
    c.append(("C", (x0, y0 + hy), (x0 + hx, y0), (x0 + rx, y0)))
    return Shape([c])


# --------------------------------------------------------------------------
# Elliptical pen
# --------------------------------------------------------------------------
def _unit(dx, dy):
    d = math.hypot(dx, dy)
    return (dx / d, dy / d) if d > 1e-12 else (0.0, 0.0)


def pen_support(a, b, tx, ty) -> Pt:
    """Offset of the *left* edge of a stroke running in direction (tx,ty)
    drawn with an ellipse of semi-axes (a, b)."""
    nx, ny = -ty, tx
    d = math.hypot(a * nx, b * ny)
    if d < 1e-12:
        return (0.0, 0.0)
    return (a * a * nx / d, b * b * ny / d)


def _line_x(p: Pt, d: Pt, q: Pt, e: Pt):
    """intersection of line p + t*d with line q + u*e (None if parallel)"""
    det = d[0] * e[1] - d[1] * e[0]
    if abs(det) < 1e-9:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / det
    return (p[0] + t * d[0], p[1] + t * d[1])


# --------------------------------------------------------------------------
# Polyline strokes (straight strokes, diagonals)
# --------------------------------------------------------------------------
def pline(pts: Sequence[Pt], a, b, cap0="butt", cap1="butt", closed=False) -> Shape:
    """Stroke a polyline with the elliptical pen and mitred joins.

    caps: 'butt' (pen-conjugate cut), 'h' (horizontal cut through the end
    point), 'v' (vertical cut through the end point).
    """
    n = len(pts)
    segs = []
    count = n if closed else n - 1
    for i in range(count):
        p0, p1 = pts[i], pts[(i + 1) % n]
        t = _unit(p1[0] - p0[0], p1[1] - p0[1])
        o = pen_support(a, b, *t)
        segs.append((p0, p1, t, o))

    def side(sign):
        out = []
        m = len(segs)
        for i, (p0, p1, t, o) in enumerate(segs):
            base = (p0[0] + sign * o[0], p0[1] + sign * o[1])
            if i == 0 and not closed:
                out.append(_cap_point(p0, base, t, cap0))
            else:
                pp0, pp1, pt, po = segs[(i - 1) % m]
                pbase = (pp0[0] + sign * po[0], pp0[1] + sign * po[1])
                x = _line_x(pbase, pt, base, t)
                out.append(x if x is not None else base)
        if not closed:
            p0, p1, t, o = segs[-1]
            base = (p1[0] + sign * o[0], p1[1] + sign * o[1])
            out.append(_cap_point(p1, base, t, cap1))
        return out

    left, right = side(+1), side(-1)
    if closed:
        return Shape([[("M", left[0])] + [("L", p) for p in left[1:]],
                      [("M", right[-1])] + [("L", p) for p in reversed(right[:-1])]])
    return poly(left + right[::-1])


def _cap_point(p: Pt, base: Pt, t: Pt, cap: str) -> Pt:
    if cap == "h" and abs(t[1]) > 1e-9:
        x = _line_x(base, t, p, (1.0, 0.0))
        return x
    if cap == "v" and abs(t[0]) > 1e-9:
        x = _line_x(base, t, p, (0.0, 1.0))
        return x
    return base


def diag(p0: Pt, p1: Pt, a, b) -> Shape:
    """Straight stroke whose two ends are cut horizontally."""
    return pline([p0, p1], a, b, "h", "h")


def slash_pts(x0, y0, x1, y1, a, b):
    """centre line (c0, c1) and horizontal half-width h of slash()"""
    sgn = 1 if x1 >= x0 else -1
    h = a
    for _ in range(8):
        dx = (x1 - sgn * h) - (x0 + sgn * h)
        h = diag_hw(dx, y1 - y0, a, b)
    return (x0 + sgn * h, y0), (x1 - sgn * h, y1), h


def slash(x0, y0, x1, y1, a, b, to_y0=None, to_y1=None) -> Shape:
    """Diagonal with horizontal cuts that exactly fills the box between the
    outer x-extremes: x0 is the outermost x at height y0, x1 the outermost x
    (on the other side) at height y1.  to_y0 / to_y1 lengthen the stroke
    along its own direction to another height (for hidden overlaps)."""
    c0, c1, h = slash_pts(x0, y0, x1, y1, a, b)
    return diag(*extend_line(c0, c1, to_y0, to_y1), a, b)


def extend_line(c0, c1, to_y0=None, to_y1=None):
    """move the end points of the line c0->c1 along the line to new heights"""
    sl = (c1[0] - c0[0]) / (c1[1] - c0[1])
    n0 = c0 if to_y0 is None else (c0[0] + (to_y0 - c0[1]) * sl, to_y0)
    n1 = c1 if to_y1 is None else (c1[0] + (to_y1 - c1[1]) * sl, to_y1)
    return n0, n1


def slash_in(xa, y0, xb, y1, a, b) -> Shape:
    """Diagonal with horizontal cuts given by its two *inner* corners: at y0
    it extends from xa towards xb, at y1 it extends from xb towards xa
    (the short diagonal of the parallelogram runs xa -> xb)."""
    sgn = 1 if xb >= xa else -1
    h = a
    for _ in range(8):
        dx = (xb + sgn * h) - (xa - sgn * h)
        h = diag_hw(dx, y1 - y0, a, b)
    return diag((xa - sgn * h, y0), (xb + sgn * h, y1), a, b)


def diag_edge(p0: Pt, p1: Pt, a, b, side) -> Shape:
    """Diagonal with horizontal cuts given by one of its edges (p0 -> p1).
    side=+1: the stroke lies to the right (+x) of that edge, -1: to the left."""
    h = diag_hw(p1[0] - p0[0], p1[1] - p0[1], a, b)
    return diag((p0[0] + side * h, p0[1]), (p1[0] + side * h, p1[1]), a, b)


def halfplane(p0: Pt, p1: Pt, side) -> Shape:
    """Huge polygon on one side of the line p0->p1 (side=+1: left of the
    direction of travel, -1: right)."""
    t = _unit(p1[0] - p0[0], p1[1] - p0[1])
    n = (-t[1] * side, t[0] * side)
    a0 = (p0[0] - t[0] * BIG, p0[1] - t[1] * BIG)
    a1 = (p0[0] + t[0] * BIG, p0[1] + t[1] * BIG)
    return poly([a0, a1, (a1[0] + n[0] * BIG, a1[1] + n[1] * BIG), (a0[0] + n[0] * BIG, a0[1] + n[1] * BIG)])


def diag_hw(dx, dy, a, b) -> float:
    """Horizontal half-width of a straight stroke running along (dx,dy)."""
    t = _unit(dx, dy)
    o = pen_support(a, b, *t)
    if abs(t[1]) < 1e-9:
        return 0.0
    return abs(o[0] - o[1] * t[0] / t[1])


# --------------------------------------------------------------------------
# Skeletons
# --------------------------------------------------------------------------
class Skel:
    """Centre-line path: lines and cubic segments between nodes."""

    def __init__(self, x, y):
        self.nodes: List[Pt] = [(float(x), float(y))]
        self.segs: List[tuple] = []  # ('L',) or ('C', c1, c2)

    @property
    def cur(self) -> Pt:
        return self.nodes[-1]

    def line(self, x, y):
        if abs(x - self.cur[0]) < 1e-6 and abs(y - self.cur[1]) < 1e-6:
            return self
        self.segs.append(("L",))
        self.nodes.append((float(x), float(y)))
        return self

    def hline(self, x):
        return self.line(x, self.cur[1])

    def vline(self, y):
        return self.line(self.cur[0], y)

    def curve(self, c1, c2, p):
        self.segs.append(("C", tuple(map(float, c1)), tuple(map(float, c2))))
        self.nodes.append((float(p[0]), float(p[1])))
        return self

    def arc(self, x, y, start, k=K, k2=None):
        """Superelliptic quarter arc.  start='h': leaves horizontally and
        arrives vertically; start='v': leaves vertically, arrives horizontally."""
        k2 = k if k2 is None else k2
        x0, y0 = self.cur
        if start == "h":
            c1 = (x0 + k * (x - x0), y0)
            c2 = (x, y - k2 * (y - y0))
        else:
            c1 = (x0, y0 + k * (y - y0))
            c2 = (x - k2 * (x - x0), y)
        return self.curve(c1, c2, (x, y))

    def bend(self, x, y, d0, d1, k=K, k2=None):
        """Curve to (x,y) leaving along d0 and arriving along d1 (vectors).
        Handles are k × the distance to the intersection of both tangents."""
        k2 = k if k2 is None else k2
        p0 = self.cur
        p3 = (float(x), float(y))
        d0, d1 = _unit(*d0), _unit(*d1)
        ix = _line_x(p0, d0, p3, d1)
        if ix is None:  # parallel tangents: S-curve, use third of chord
            L = math.hypot(p3[0] - p0[0], p3[1] - p0[1]) / 3
            c1 = (p0[0] + d0[0] * L, p0[1] + d0[1] * L)
            c2 = (p3[0] - d1[0] * L, p3[1] - d1[1] * L)
        else:
            c1 = (p0[0] + k * (ix[0] - p0[0]), p0[1] + k * (ix[1] - p0[1]))
            c2 = (p3[0] + k2 * (ix[0] - p3[0]), p3[1] + k2 * (ix[1] - p3[1]))
        return self.curve(c1, c2, p3)

    # -- helpers -----------------------------------------------------------
    def iter_segments(self, closed=False):
        n = len(self.segs)
        for i, s in enumerate(self.segs):
            p0, p1 = self.nodes[i], self.nodes[i + 1]
            yield (s, p0, p1)

    def transformed(self, fn) -> "Skel":
        out = Skel(*fn(self.nodes[0]))
        for i, s in enumerate(self.segs):
            p = fn(self.nodes[i + 1])
            if s[0] == "L":
                out.segs.append(("L",))
                out.nodes.append(p)
            else:
                out.segs.append(("C", fn(s[1]), fn(s[2])))
                out.nodes.append(p)
        return out


def round_path(pts: Sequence[Pt], rx, ry, k=K, radii=None) -> Skel:
    """Skeleton following an orthogonal polyline with superelliptic corners.

    ``pts`` alternate horizontal and vertical moves.  ``radii`` may give
    per-corner (rx, ry) overrides (list aligned with the interior points,
    ``None`` = default).  Radii are clamped to the available segment lengths.
    """
    n = len(pts)
    horiz = [abs(pts[i + 1][1] - pts[i][1]) < 1e-6 for i in range(n - 1)]
    length = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(n - 1)]
    r_in, r_out = [0.0] * n, [0.0] * n
    for i in range(1, n - 1):
        crx, cry = (rx, ry) if radii is None or radii[i - 1] is None else radii[i - 1]
        r_in[i] = crx if horiz[i - 1] else cry
        r_out[i] = crx if horiz[i] else cry
    for j in range(n - 1):
        used = r_out[j] + r_in[j + 1]
        if used > length[j] and used > 0:
            f = length[j] / used
            r_out[j] *= f
            r_in[j + 1] *= f
    sk = Skel(*pts[0])
    for i in range(1, n - 1):
        p_prev, p, p_next = pts[i - 1], pts[i], pts[i + 1]
        ti = _unit(p[0] - p_prev[0], p[1] - p_prev[1])
        to = _unit(p_next[0] - p[0], p_next[1] - p[1])
        a0 = (p[0] - ti[0] * r_in[i], p[1] - ti[1] * r_in[i])
        a1 = (p[0] + to[0] * r_out[i], p[1] + to[1] * r_out[i])
        sk.line(*a0)
        if r_in[i] > 1e-6 and r_out[i] > 1e-6:
            sk.arc(a1[0], a1[1], "h" if horiz[i - 1] else "v", k)
        else:
            sk.line(*a1)
    sk.line(*pts[-1])
    return sk


def rrect_skel(x0, y0, x1, y1, rx, ry, k=K) -> Skel:
    """Closed rounded-rectangle skeleton, counter-clockwise from bottom-left."""
    rx = min(rx, (x1 - x0) / 2)
    ry = min(ry, (y1 - y0) / 2)
    sk = Skel(x0 + rx, y0)
    sk.line(x1 - rx, y0)
    sk.arc(x1, y0 + ry, "h", k)
    sk.line(x1, y1 - ry)
    sk.arc(x1 - rx, y1, "v", k)
    sk.line(x0 + rx, y1)
    sk.arc(x0, y1 - ry, "h", k)
    sk.line(x0, y0 + ry)
    sk.arc(x0 + rx, y0, "v", k)
    return sk


def rrect_skel4(x0, y0, x1, y1, bl, br, tr, tl, k=K) -> Skel:
    """Closed rounded-rectangle skeleton with one (rx, ry) pair per corner
    (bottom-left, bottom-right, top-right, top-left), counter-clockwise."""
    w, h = x1 - x0, y1 - y0

    def fit(p, q, size, idx):
        tot = p[idx] + q[idx]
        if tot > size and tot > 0:
            f = size / tot
            p[idx] *= f
            q[idx] *= f

    bl, br, tr, tl = list(bl), list(br), list(tr), list(tl)
    fit(bl, br, w, 0)
    fit(tl, tr, w, 0)
    fit(bl, tl, h, 1)
    fit(br, tr, h, 1)
    sk = Skel(x0 + bl[0], y0)
    sk.line(x1 - br[0], y0)
    sk.arc(x1, y0 + br[1], "h", k)
    sk.line(x1, y1 - tr[1])
    sk.arc(x1 - tr[0], y1, "v", k)
    sk.line(x0 + tl[0], y1)
    sk.arc(x0, y1 - tl[1], "h", k)
    sk.line(x0, y0 + bl[1])
    sk.arc(x0 + bl[0], y0, "v", k)
    return sk


def sbox4(x0, y0, x1, y1, bl, br, tr, tl, k=K) -> Shape:
    """Filled rounded rectangle with one (rx, ry) pair per corner."""
    sk = rrect_skel4(x0, y0, x1, y1, bl, br, tr, tl, k)
    c = [("M", sk.nodes[0])]
    for i, seg in enumerate(sk.segs):
        if seg[0] == "L":
            c.append(("L", sk.nodes[i + 1]))
        else:
            c.append(("C", seg[1], seg[2], sk.nodes[i + 1]))
    return Shape([_trim(c)])


# --------------------------------------------------------------------------
# Stroke expansion
# --------------------------------------------------------------------------
def _cubic_pt(p0, p1, p2, p3, t):
    mt = 1 - t
    x = mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0]
    y = mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]
    return (x, y)


def _cubic_tan(p0, p1, p2, p3, t):
    mt = 1 - t
    dx = 3 * mt * mt * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    dy = 3 * mt * mt * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    return _unit(dx, dy)


def _split_cubic(p0, p1, p2, p3, t=0.5):
    def lerp(u, v):
        return (u[0] + (v[0] - u[0]) * t, u[1] + (v[1] - u[1]) * t)

    a = lerp(p0, p1)
    b = lerp(p1, p2)
    c = lerp(p2, p3)
    d = lerp(a, b)
    e = lerp(b, c)
    f = lerp(d, e)
    return (p0, a, d, f), (f, e, c, p3)


def _end_tangents(p0, p1, p2, p3):
    t0 = _unit(p1[0] - p0[0], p1[1] - p0[1])
    if t0 == (0.0, 0.0):
        t0 = _unit(p2[0] - p0[0], p2[1] - p0[1])
    if t0 == (0.0, 0.0):
        t0 = _unit(p3[0] - p0[0], p3[1] - p0[1])
    t3 = _unit(p3[0] - p2[0], p3[1] - p2[1])
    if t3 == (0.0, 0.0):
        t3 = _unit(p3[0] - p1[0], p3[1] - p1[1])
    if t3 == (0.0, 0.0):
        t3 = _unit(p3[0] - p0[0], p3[1] - p0[1])
    return t0, t3


def _offset_cubic(p0, p1, p2, p3, a, b, sign, w0=1.0, w1=1.0):
    """One cubic approximating the elliptical-pen offset of a cubic.
    End points/tangents are exact, the middle of the curve is matched."""
    t0, t3 = _end_tangents(p0, p1, p2, p3)
    s0 = pen_support(a * w0, b * w0, *t0)
    s3 = pen_support(a * w1, b * w1, *t3)
    q0 = (p0[0] + sign * s0[0], p0[1] + sign * s0[1])
    q3 = (p3[0] + sign * s3[0], p3[1] + sign * s3[1])
    m = _cubic_pt(p0, p1, p2, p3, 0.5)
    tm = _cubic_tan(p0, p1, p2, p3, 0.5)
    wm = (w0 + w1) / 2
    sm = pen_support(a * wm, b * wm, *tm)
    mq = (m[0] + sign * sm[0], m[1] + sign * sm[1])
    vx = 8 / 3 * (mq[0] - (q0[0] + q3[0]) / 2)
    vy = 8 / 3 * (mq[1] - (q0[1] + q3[1]) / 2)
    det = -t0[0] * t3[1] + t3[0] * t0[1]
    alpha = beta = None
    if abs(det) > 1e-6:
        alpha = (-vx * t3[1] + t3[0] * vy) / det
        beta = (t0[0] * vy - t0[1] * vx) / det
    if alpha is None or alpha < 0 or beta < 0:
        chord = math.hypot(p3[0] - p0[0], p3[1] - p0[1])
        r = math.hypot(q3[0] - q0[0], q3[1] - q0[1]) / chord if chord > 1e-9 else 1.0
        alpha = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * r
        beta = math.hypot(p3[0] - p2[0], p3[1] - p2[1]) * r
    alpha = max(alpha, 0.01)
    beta = max(beta, 0.01)
    q1 = (q0[0] + alpha * t0[0], q0[1] + alpha * t0[1])
    q2 = (q3[0] - beta * t3[0], q3[1] - beta * t3[1])
    return q0, q1, q2, q3


def stroke(sk: Skel, a, b, closed=False, w=None, ext0=0.0, ext1=0.0, subdiv=0) -> Shape:
    """Expand a smooth skeleton with the elliptical pen (a, b).

    w      optional per-node width factors (tapering)
    ext0/1 lengthen the first/last segment tangentially (hidden overlaps)
    subdiv split every cubic 2**subdiv times before offsetting (accuracy)
    """
    nodes = list(sk.nodes)
    segs = list(sk.segs)
    wl = list(w) if w is not None else [1.0] * len(nodes)

    # tangential extensions
    def seg_points(i):
        s = segs[i]
        p0, p3 = nodes[i], nodes[i + 1]
        if s[0] == "L":
            return (p0, p3)
        return (p0, s[1], s[2], p3)

    if ext0 and not closed:
        pts = seg_points(0)
        t = _unit(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]) if len(pts) == 2 else _end_tangents(*pts)[0]
        nodes.insert(0, (nodes[0][0] - t[0] * ext0, nodes[0][1] - t[1] * ext0))
        segs.insert(0, ("L",))
        wl.insert(0, wl[0])
    if ext1 and not closed:
        pts = seg_points(len(segs) - 1)
        t = _unit(pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]) if len(pts) == 2 else _end_tangents(*pts)[1]
        nodes.append((nodes[-1][0] + t[0] * ext1, nodes[-1][1] + t[1] * ext1))
        segs.append(("L",))
        wl.append(wl[-1])

    # build list of primitive pieces (with widths)
    pieces = []  # (pts tuple, w0, w1)
    for i, s in enumerate(segs):
        p0, p3 = nodes[i], nodes[i + 1]
        w0, w1 = wl[i], wl[i + 1]
        if s[0] == "L":
            pieces.append(((p0, p3), w0, w1))
        else:
            cubs = [((p0, s[1], s[2], p3), w0, w1)]
            for _ in range(subdiv):
                nxt = []
                for c, cw0, cw1 in cubs:
                    c1, c2 = _split_cubic(*c)
                    cm = (cw0 + cw1) / 2
                    nxt += [(c1, cw0, cm), (c2, cm, cw1)]
                cubs = nxt
            pieces += cubs

    def offset_side(sign):
        out = []  # list of segments: ('L', p0, p1) / ('C', p0, c1, c2, p1)
        for pts, w0, w1 in pieces:
            if len(pts) == 2:
                p0, p1 = pts
                t = _unit(p1[0] - p0[0], p1[1] - p0[1])
                s0 = pen_support(a * w0, b * w0, *t)
                s1 = pen_support(a * w1, b * w1, *t)
                out.append(("L", (p0[0] + sign * s0[0], p0[1] + sign * s0[1]),
                            (p1[0] + sign * s1[0], p1[1] + sign * s1[1])))
            else:
                q0, q1, q2, q3 = _offset_cubic(*pts, a, b, sign, w0, w1)
                out.append(("C", q0, q1, q2, q3))
        return out

    def emit_forward(side, contour):
        for s in side:
            start = s[1]
            if contour and _dist(_last(contour), start) > 0.01:
                contour.append(("L", start))
            if s[0] == "L":
                contour.append(("L", s[2]))
            else:
                contour.append(("C", s[2], s[3], s[4]))

    def emit_backward(side, contour):
        for s in reversed(side):
            start = s[-1]
            if contour and _dist(_last(contour), start) > 0.01:
                contour.append(("L", start))
            if s[0] == "L":
                contour.append(("L", s[1]))
            else:
                contour.append(("C", s[3], s[2], s[1]))

    left, right = offset_side(+1), offset_side(-1)
    if closed:
        c1 = [("M", left[0][1])]
        emit_forward(left, c1)
        c2 = [("M", right[-1][-1])]
        emit_backward(right, c2)
        return Shape([_trim(c1), _trim(c2)])
    c = [("M", left[0][1])]
    emit_forward(left, c)
    c.append(("L", right[-1][-1]))
    emit_backward(right, c)
    return Shape([_trim(c)])


def _last(contour):
    return contour[-1][-1]


def _dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def _trim(contour):
    """drop a closing segment that returns to the start point as a line"""
    if len(contour) > 2 and contour[-1][0] == "L" and _dist(contour[-1][1], contour[0][1]) < 0.01:
        contour = contour[:-1]
    return contour


# --------------------------------------------------------------------------
# Final clean-up of a glyph outline
# --------------------------------------------------------------------------
def _is_straight(p0, c1, c2, p3, tol=0.35):
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 1e-9:
        return True
    for c in (c1, c2):
        dist = abs((c[0] - p0[0]) * dy - (c[1] - p0[1]) * dx) / L
        if dist > tol:
            return False
        # control point must project inside the chord
        proj = ((c[0] - p0[0]) * dx + (c[1] - p0[1]) * dy) / (L * L)
        if proj < -0.01 or proj > 1.01:
            return False
    return True


MIN_CONTOUR_AREA = 60.0     # smaller contours are boolean-operation debris
MIN_SEGMENT = 2.6           # shorter segments are merged into their neighbours


def finalize(shape: Shape, grid=1.0) -> Shape:
    """Resolve overlaps, fix winding (outer contours counter-clockwise),
    round to the unit grid and remove redundant points, slivers and
    micro-segments left behind by the boolean operations."""
    if shape.is_empty():
        return shape
    p = shape.to_skia()
    p.simplify(fix_winding=True, keep_starting_points=False, clockwise=False)
    s = Shape.from_skia(p)

    def rnd(pt):
        return (round(pt[0] / grid) * grid, round(pt[1] / grid) * grid)

    out = []
    for cont in s.contours:
        if abs(_contour_area(cont)) < MIN_CONTOUR_AREA:
            continue
        start = rnd(cont[0][1])
        segs = []
        last = start
        for seg in cont[1:]:
            if seg[0] == "L":
                p1 = rnd(seg[1])
                if _dist(p1, last) < MIN_SEGMENT:
                    continue
                segs.append(("L", p1))
                last = p1
            else:
                c1, c2, p3 = seg[1], seg[2], rnd(seg[3])
                if _dist(p3, last) < MIN_SEGMENT and _dist(c1, last) < 2 * MIN_SEGMENT and _dist(c2, last) < 2 * MIN_SEGMENT:
                    continue
                if _is_straight(last, c1, c2, p3):
                    segs.append(("L", p3))
                else:
                    segs.append(("C", rnd(c1), rnd(c2), p3))
                last = p3
        if not segs:
            continue
        # the contour must end where it starts: if the tail was dropped as a
        # micro-segment, let the last kept segment land on the start point
        if last != start:
            if _dist(last, start) < MIN_SEGMENT:
                tail = segs[-1]
                segs[-1] = (tail[0],) + tuple(tail[1:-1]) + (start,)
            # otherwise the closing line is implicit
        pts = [("M", start)] + segs
        if len(pts) > 1 and pts[-1][0] == "L" and pts[-1][1] == pts[0][1]:
            pts.pop()
        pts = _merge_collinear(pts)
        if len(pts) >= 3 or any(sg[0] == "C" for sg in pts):
            if abs(_contour_area(pts)) >= MIN_CONTOUR_AREA:
                out.append(pts)
    return Shape(out)


def _merge_collinear(pts):
    """Remove on-curve points that lie on a straight run between two lines."""
    start = pts[0][1]
    segs = [s for s in pts[1:]]
    if not segs:
        return pts
    if segs[-1][-1] != start:
        segs.append(("L", start))  # explicit closing line
    changed = True
    while changed and len(segs) > 2:
        changed = False
        n = len(segs)
        for i in range(n):
            cur, nxt = segs[i], segs[(i + 1) % n]
            if cur[0] != "L" or nxt[0] != "L":
                continue
            p_prev = segs[i - 1][-1]
            p_cur, p_next = cur[-1], nxt[-1]
            ux, uy = p_cur[0] - p_prev[0], p_cur[1] - p_prev[1]
            vx, vy = p_next[0] - p_cur[0], p_next[1] - p_cur[1]
            if abs(ux * vy - uy * vx) < 1e-6 and ux * vx + uy * vy > 0:
                del segs[i]
                changed = True
                break
    new_start = segs[-1][-1]
    out = [("M", new_start)] + segs
    if out[-1][0] == "L":
        out.pop()  # implicit closing line
    return out


def _flatten_contour(cont, steps=12):
    out = [cont[0][1]]
    last = cont[0][1]
    for seg in cont[1:]:
        if seg[0] == "L":
            out.append(seg[1])
            last = seg[1]
        else:
            for i in range(1, steps + 1):
                out.append(_cubic_pt(last, seg[1], seg[2], seg[3], i / steps))
            last = seg[3]
    return out


def _contour_area(cont):
    pts = _flatten_contour(cont, 8)
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        s += x0 * y1 - x1 * y0
    return s / 2


def flatten(shape: Shape, steps=14):
    return [_flatten_contour(c, steps) for c in shape.contours]
