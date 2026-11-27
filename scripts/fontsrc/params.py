"""The Varcoda Mono design system: one grid, one pen per weight.

All numbers are font units on a 1000-unit em.  A *master* is fully described
by its vertical stem thickness; everything else (horizontal stroke, side
bearings, cap weight ...) is derived by interpolating between the Light and
Bold extremes, so all styles share one construction and one set of
metrics.
"""
from __future__ import annotations

import copy

UPM = 1000
WIDTH = 600          # advance width of every glyph (0.6 em)

# vertical grid ------------------------------------------------------------
XH = 540             # x-height
CAP = 720            # cap height, figure height
ASC = 772            # ascender of b d f h k l
DESC = -192          # descender of g j p q y
OVERSHOOT = 8        # round shapes exceed flat ones by this much
AXIS = 320           # centre line of operators and arrows
BRACKET_TOP = 800    # ( [ { | / \ span this range, centred on the axis
BRACKET_BOT = -160

# line box: identical in hhea and OS/2 typo (USE_TYPO_METRICS is set), so
# the default line height is 1.23 em on Windows, macOS and Linux.
LINE_ASC = 980
LINE_DESC = -250
# Box drawing and block elements reach slightly beyond their cell so that
# they still join when a renderer rounds the cell size up to whole pixels.
# OS/2 winAscent/winDescent (the Windows clipping box) include this overshoot.
BOX_OVER_X = 20
BOX_OVER_Y = 30
WIN_ASC = LINE_ASC + BOX_OVER_Y
WIN_DESC = -(LINE_DESC - BOX_OVER_Y)

# curve model --------------------------------------------------------------
TENSION = 0.67       # quarter-arc handle length (0.5523 would be a circle)

LIGHT_STEM, BOLD_STEM = 54, 124

#            name      usWeightClass  stem
WEIGHTS = [("Light", 300, 60),
           ("Regular", 400, 84),
           ("Medium", 500, 97),
           ("SemiBold", 600, 110),
           ("Bold", 700, 124)]

ITALIC_ANGLE = 9.5                     # degrees, clockwise


def italic_style(weight_name: str) -> str:
    """file / PostScript style name of the italic of a weight"""
    return "Italic" if weight_name == "Regular" else weight_name + "Italic"


# (style, weight name, usWeightClass, stem)
ITALICS = [(italic_style(w[0]),) + tuple(w) for w in WEIGHTS]



class Master:
    """Every measurement a glyph function may use."""

    def __init__(self, name="Regular", weight_class=400, stem=84, italic=False):
        self.name = name
        self.italic = italic              # glyph functions draw their written form (glyphs_italic.py)
        self.weight_class = weight_class
        t = (stem - LIGHT_STEM) / (BOLD_STEM - LIGHT_STEM)
        self.t = t

        def lerp(lo, hi):
            return lo + (hi - lo) * t

        self.lerp = lerp
        self.s = 1.0                      # scale of this frame (1 = full size)
        self.W = WIDTH
        self.xh, self.cap, self.asc, self.desc = XH, CAP, ASC, DESC
        self.os = OVERSHOOT
        self.axis = AXIS
        self.btop, self.bbot = BRACKET_TOP, BRACKET_BOT
        self.k = TENSION

        # lowercase pen: vertical stems / horizontal strokes
        self.sw = float(stem)
        self.hw = lerp(48, 100)
        # capitals and figures are slightly heavier
        self.csw = round(stem * 1.07)
        self.chw = lerp(51, 106)
        # glyphs with three horizontal strokes stacked (a e s, B E S 3 8 ...)
        # get slightly thinner horizontals in the heavy weights
        self.hw3 = self.hw * lerp(1.0, 0.88)
        self.chw3 = self.chw * lerp(1.0, 0.90)

        # horizontal grid: outer edges of straight-sided letters
        self.L = lerp(96, 68)             # lowercase n, h, u ...
        self.rnd = lerp(8, 10)            # round letters reach this much further
        self.UL = lerp(80, 50)            # capitals H, E, N ...
        self.DL = lerp(92, 70)            # figures
        # corner radii of bowls as a fraction of the bowl's outer size
        self.fx, self.fy = 0.415, 0.375
        self.blade = 0.32                 # rise of the slanted cut on extender ends (× stem width)
        self.br = lerp(0.56, 0.40)        # how far arches reach into a stem (× stem)
        self.ease = lerp(40, 34)          # visible width of the eased corner where an arch leaves a stem
        self.dot = lerp(84, 156)          # diameter of the squircle dot (i j)
        self.pdot = lerp(124, 184)        # punctuation dot ( . : ; ! ? )
        self.OL = lerp(88, 72)            # left end of operator bars ( + - = )

    # -- derived -----------------------------------------------------------
    @property
    def xc(self):
        return self.W / 2

    @property
    def R(self):
        return self.W - self.L

    def with_(self, **kw):
        """copy of the frame with some measurements replaced"""
        m = copy.copy(self)
        for k, v in kw.items():
            setattr(m, k, v)
        return m

    @property
    def UR(self):
        return self.W - self.UL

    @property
    def DR(self):
        return self.W - self.DL

    @property
    def a(self):
        return self.sw / 2

    @property
    def b(self):
        return self.hw / 2

    @property
    def ca(self):
        return self.csw / 2

    @property
    def cb(self):
        return self.chw / 2

    def radii(self, w, h):
        """outer corner radii (rx, ry) for a bowl of outer size w × h"""
        rx = min(self.fx * w, 0.56 * h)
        ry = min(self.fy * h, 0.62 * w)
        return rx, ry

    def scaled(self, s, stem=None, hstem=None):
        """A reduced copy of the frame (superiors, fractions, © ® ...).
        Geometry scales by ``s``; pens are given explicitly so small glyphs
        keep enough weight."""
        m = copy.copy(self)
        m.s = self.s * s
        for attr in ("W", "xh", "cap", "asc", "desc", "os", "axis", "btop", "bbot", "L", "rnd", "UL", "DL", "dot", "pdot", "OL", "ease"):
            setattr(m, attr, getattr(self, attr) * s)
        ratio = self.hw / self.sw
        m.sw = stem if stem is not None else self.sw * s
        m.hw = hstem if hstem is not None else m.sw * ratio
        m.csw, m.chw = m.sw, m.hw
        m.hw3 = m.chw3 = m.hw
        return m


def masters():
    return [Master(n, wc, st) for n, wc, st in WEIGHTS]
