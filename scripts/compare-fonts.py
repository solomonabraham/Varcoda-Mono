#!/usr/bin/env python3
"""Measure Varcoda Mono against reference coding fonts (render/measure only).

    python scripts/compare-fonts.py FONT.ttf [FONT.ttf ...]

Everything is reported in thousandths of the em, so fonts with different
units-per-em compare directly.  Reference fonts are only measured and
rendered; no outline data is copied from them.
"""
import sys

import freetype
import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

PX = 1000


class Probe:
    def __init__(self, path):
        self.path = path
        self.tt = TTFont(path, lazy=True)
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.face = freetype.Face(path)
        self.face.set_pixel_sizes(PX, PX)
        self._bm = {}

    def n(self, v):
        return v * 1000.0 / self.upm

    def bounds(self, ch):
        pen = BoundsPen(self.gs)
        self.gs[self.cmap[ord(ch)]].draw(pen)
        if pen.bounds is None:
            return None
        return tuple(self.n(v) for v in pen.bounds)

    def adv(self, ch="n"):
        return self.n(self.tt["hmtx"][self.cmap[ord(ch)]][0])

    def bitmap(self, ch):
        """(array, left, top) at 1000 px per em: 1 px = 1/1000 em"""
        if ch not in self._bm:
            self.face.load_char(ch, freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
            g = self.face.glyph
            bm = g.bitmap
            buf = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)
            self._bm[ch] = (np.unpackbits(buf, axis=1)[:, :bm.width], g.bitmap_left, g.bitmap_top)
        return self._bm[ch]

    @staticmethod
    def runs(line):
        out, start = [], None
        for i, v in enumerate(list(line) + [0]):
            if v and start is None:
                start = i
            elif not v and start is not None:
                out.append((start, i - start))
                start = None
        return out

    def hruns(self, ch, y):
        """ink runs along the horizontal line at height y (em/1000)"""
        arr, left, top = self.bitmap(ch)
        r = int(round(top - y))
        if r < 0 or r >= arr.shape[0]:
            return []
        return [(left + s, w) for s, w in self.runs(arr[r])]

    def vruns(self, ch, x):
        arr, left, top = self.bitmap(ch)
        c = int(round(x - left))
        if c < 0 or c >= arr.shape[1]:
            return []
        return [(top - s - w, w) for s, w in self.runs(arr[:, c])]


def rhythm(p, text, y):
    """white gaps between consecutive stems of ``text`` on the line at height y:
    (mean gap, coefficient of variation).  Lower CV = more even rhythm."""
    adv = p.adv()
    ink = []
    for i, ch in enumerate(text):
        ink += [(i * adv + s, w) for s, w in p.hruns(ch, y)]
    ink.sort()
    gaps = [b[0] - (a[0] + a[1]) for a, b in zip(ink, ink[1:])]
    gaps = np.array([g for g in gaps if g > 0], dtype=float)
    return gaps.mean(), gaps.std() / gaps.mean()


LC_RHYTHM, UC_RHYTHM = "nihmulnhimun", "HIUHLHIHUH"


def measure(path):
    p = Probe(path)
    m = {}
    adv = p.adv()
    m["advance"] = adv
    xh = p.bounds("x")[3]
    cap = p.bounds("H")[3]
    m["x-height"] = xh
    m["cap height"] = cap
    m["ascender (l)"] = p.bounds("l")[3]
    m["descender (p)"] = p.bounds("p")[1]
    hh = p.tt["hhea"]
    m["line height"] = p.n(hh.ascent - hh.descent + hh.lineGap)
    m["x-height / advance"] = xh / adv * 1000
    r = p.hruns("n", xh * 0.25)
    m["stem n"] = r[0][1] if r else 0
    r = p.hruns("H", cap * 0.25)
    m["stem H"] = r[0][1] if r else 0
    r = p.vruns("z", adv / 2)
    m["bar z"] = r[0][1] if r else 0
    r = p.hruns("n", xh * 0.25)
    m["counter n"] = r[1][0] - (r[0][0] + r[0][1]) if len(r) > 1 else 0
    r = p.hruns("m", xh * 0.25)
    if len(r) >= 3:
        m["counter m"] = r[1][0] - (r[0][0] + r[0][1])
        m["stem m (mid)"] = r[1][1]
    r = p.hruns("o", xh * 0.5)
    m["counter o"] = r[1][0] - (r[0][0] + r[0][1]) if len(r) > 1 else 0
    mean, cv = rhythm(p, LC_RHYTHM, xh * 0.4)
    m["rhythm lc gap"] = mean
    m["rhythm lc CV %"] = cv * 100
    mean, cv = rhythm(p, UC_RHYTHM, cap * 0.3)
    m["rhythm UC gap"] = mean
    m["rhythm UC CV %"] = cv * 100
    for ch in "iljtrfI1!|" + "mwMW@%&" + "nHO0":
        b = p.bounds(ch)
        m["ink w  " + ch] = b[2] - b[0]
        m["lsb/rsb " + ch] = "%d/%d" % (round(b[0]), round(adv - b[2]))
    for ch in ".,:;'\"`^~*-_=+":
        b = p.bounds(ch)
        m["size  " + ch] = "%dx%d" % (round(b[2] - b[0]), round(b[3] - b[1]))
    for ch in "([{|/":
        b = p.bounds(ch)
        m["span  " + ch] = "%d..%d w%d" % (round(b[1]), round(b[3]), round(b[2] - b[0]))
    for ch in "+-=<>*~:|/()[]{}":
        b = p.bounds(ch)
        m["centre " + ch] = (b[1] + b[3]) / 2
    return m


def main(paths):
    cols = [measure(p) for p in paths]
    names = [p.split("/")[-1].replace("-Regular.ttf", "").replace(".ttf", "")[:14] for p in paths]
    print("%-20s" % "" + "".join("%15s" % n for n in names))
    for k in cols[0]:
        row = "%-20s" % k
        for c in cols:
            v = c.get(k, "")
            row += "%15s" % (v if isinstance(v, str) else "%.0f" % v)
        print(row)


if __name__ == "__main__":
    main(sys.argv[1:])
