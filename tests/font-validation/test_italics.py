"""Tests for the italic styles (the upright styles are covered by test_fonts.py)."""
import math
import os
import subprocess
import sys

import freetype
import pytest
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from fontsrc import build, params  # noqa: E402
from fontsrc.italic import PIVOT, TAN  # noqa: E402

PAIRS = [(it[0], it[1], it[2]) for it in params.ITALICS]          # (italic style, weight name, weight class)
IDS = [p[0] for p in PAIRS]
W = params.WIDTH


def path(style, kind="ttf"):
    sub = {"ttf": (), "otf": ("otf",), "woff2": ("webfonts",)}[kind]
    return os.path.join(ROOT, "fonts", *sub, "%s-%s.%s" % (build.PS_FAMILY, style, kind))


_cache = {}


def font(p):
    if p not in _cache:
        _cache[p] = TTFont(p)
    return _cache[p]


def bounds(f, name):
    gs = f.getGlyphSet()
    pen = BoundsPen(gs)
    gs[name].draw(pen)
    return pen.bounds


def shape(p, text, features):
    with open(p, "rb") as fh:
        hbf = hb.Font(hb.Face(fh.read()))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, features)
    return [hbf.glyph_to_string(i.codepoint) for i in buf.glyph_infos], [p_.x_advance for p_ in buf.glyph_positions]


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
@pytest.mark.parametrize("kind", ["ttf", "otf", "woff2"])
def test_files_exist_and_stay_monospaced(style, weight, wclass, kind):
    f = font(path(style, kind))
    assert {adv for adv, _ in f["hmtx"].metrics.values()} == {W}
    assert f["post"].isFixedPitch == 1
    assert f["OS/2"].panose.bProportion == 9


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
def test_italic_metadata(style, weight, wclass):
    f = font(path(style))
    up = font(path(weight))
    os2, name = f["OS/2"], f["name"]
    assert f["post"].italicAngle == -params.ITALIC_ANGLE
    assert f["hhea"].caretSlopeRun > 0 and f["hhea"].caretSlopeRise > 0
    assert abs(f["hhea"].caretSlopeRun / f["hhea"].caretSlopeRise - TAN) < 0.01
    assert os2.fsSelection & 1, "ITALIC bit"
    assert not os2.fsSelection & 0x40, "REGULAR bit must be clear"
    assert bool(os2.fsSelection & 0x20) == (weight == "Bold")
    assert os2.fsSelection & 0x80, "USE_TYPO_METRICS"
    assert f["head"].macStyle & 2 and bool(f["head"].macStyle & 1) == (weight == "Bold")
    assert os2.usWeightClass == wclass == up["OS/2"].usWeightClass
    # style linking: Regular/Italic/Bold/Bold Italic form one group, the other weights one group each
    human = "Italic" if weight == "Regular" else "%s Italic" % weight
    if weight in ("Regular", "Bold"):
        assert name.getDebugName(1) == build.FAMILY and name.getDebugName(2) == human
        assert name.getDebugName(16) is None
    else:
        assert name.getDebugName(1) == "%s %s" % (build.FAMILY, weight) and name.getDebugName(2) == "Italic"
        assert name.getDebugName(16) == build.FAMILY and name.getDebugName(17) == human
    assert name.getDebugName(4) == "%s %s" % (build.FAMILY, human)
    assert name.getDebugName(6) == "%s-%s" % (build.PS_FAMILY, style)
    assert name.getDebugName(5) == "Version %s" % build.VERSION
    # STAT: one weight axis value and the italic axis value, in both members of each pair
    for fnt, ital in ((f, 1.0), (up, 0.0)):
        stat = fnt["STAT"].table
        assert [a.AxisTag for a in stat.DesignAxisRecord.Axis] == ["wght", "ital"]
        vals = {stat.DesignAxisRecord.Axis[v.AxisIndex].AxisTag: v.Value for v in stat.AxisValueArray.AxisValue}
        assert vals == {"wght": float(wclass), "ital": ital}
    # same line box as the upright, so mixing styles never changes the line height
    for table, fields in (("hhea", ("ascent", "descent", "lineGap")),
                          ("OS/2", ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent",
                                    "sxHeight", "sCapHeight"))):
        for field in fields:
            assert getattr(f[table], field) == getattr(up[table], field), field


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
def test_same_characters_and_features_as_the_upright(style, weight, wclass):
    f, up = font(path(style)), font(path(weight))
    assert f.getGlyphOrder() == up.getGlyphOrder()
    assert f.getBestCmap() == up.getBestCmap()
    tags = lambda t: sorted({r.FeatureTag for r in t["GSUB"].table.FeatureList.FeatureRecord})  # noqa: E731
    assert tags(f) == tags(up)
    assert "GPOS" not in f and "kern" not in f


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
def test_letters_are_slanted_and_joining_glyphs_are_not(style, weight, wclass):
    f, up = font(path(style)), font(path(weight))
    cmap = f.getBestCmap()
    # a vertical stem of height h leans by h * tan
    for ch, h in (("H", params.CAP), ("I", params.CAP), ("|", params.BRACKET_TOP - params.BRACKET_BOT)):
        bi, bu = bounds(f, cmap[ord(ch)]), bounds(up, cmap[ord(ch)])
        lean = (bi[2] - bi[0]) - (bu[2] - bu[0])
        assert abs(lean - h * TAN) <= 6, (ch, lean, h * TAN)
    # the slant pivots on the middle of the x-height: x stays centred
    for ch, h in (("o", params.XH), ("H", params.CAP)):     # lowercase stays centred, capitals move 15 units right
        bi, bu = bounds(f, ch), bounds(up, ch)
        shift = (bi[0] + bi[2]) / 2 - (bu[0] + bu[2]) / 2
        assert abs(shift - (h / 2 - PIVOT) * TAN) <= 3, (ch, shift)
    # box drawing, blocks, arrows, shapes and Powerline are identical to the upright
    for cp in (0x2500, 0x2502, 0x253C, 0x256C, 0x2588, 0x2591, 0x2192, 0x25A0, 0x2713, 0xE0A0, 0xE0B0, 0xE0B2):
        assert bounds(f, cmap[cp]) == bounds(up, cmap[cp]), hex(cp)


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
def test_italic_letterforms(style, weight, wclass):
    f, up = font(path(style)), font(path(weight))
    gs_i, gs_u = f["glyf"], up["glyf"]
    # a is single-storey (one counter), the upright a is double-storey with the same outline count but another shape
    assert gs_i["a"].numberOfContours == up["glyf"]["a.ss02"].numberOfContours
    assert bounds(f, "a")[3] == bounds(f, "a.ss02")[3]
    # f descends, the upright f stands on the baseline
    assert bounds(up, "f")[1] == 0 and bounds(f, "f")[1] <= params.DESC * 0.6
    # y is the hooked, squared form
    assert gs_i["y"].numberOfContours == gs_u["y.ss05"].numberOfContours
    assert abs((bounds(f, "y")[2] - bounds(f, "y")[0]) - (bounds(f, "y.ss05")[2] - bounds(f, "y.ss05")[0])) <= 1


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
def test_ink_stays_close_to_the_cell(style, weight, wclass):
    """Slanted tops lean a little over the right cell edge (the widest: V and W,
    52 units in Bold).  Neighbouring italic glyphs lean by the same amount, so nothing
    collides; a terminal that clips every cell may shave about half a pixel.
    The apostrophe-shaped caron of d-caron, l-caron, t-caron sits at the top
    right and leans furthest."""
    carons = {"dcaron", "lcaron", "tcaron", "Lcaron"}
    f = font(path(style))
    cmap = f.getBestCmap()
    over = 0
    for cp, name in cmap.items():
        if 0x2500 <= cp <= 0x259F or 0xE0B0 <= cp <= 0xE0B3:
            continue
        b = bounds(f, name)
        if b is None:
            continue
        assert b[1] >= params.LINE_DESC and b[3] <= params.LINE_ASC, name
        limit = 85 if name in carons else 55
        assert b[0] >= -limit and b[2] <= W + limit, (name, b)
        if name not in carons:
            over = max(over, -b[0], b[2] - W)
    assert over <= 55


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
@pytest.mark.parametrize("kind", ["ttf", "otf"])
def test_ligatures_and_sets_shape_like_the_upright(style, weight, wclass, kind):
    p, pu = path(style, kind), path(weight, kind)
    for text in ("a != b", "x => y", "a?.b ?? c", "n += 1", "i := 0", "==="):
        gi, ai = shape(p, text, {"calt": True})
        gu, _ = shape(pu, text, {"calt": True})
        assert gi == gu and set(ai) == {W}, text
        assert shape(p, text, {"calt": False})[0] != gi
    assert shape(p, "0", {"ss01": True})[0] == ["zero.ss01"]
    assert shape(p, "qm", {"ss06": True, "ss07": True})[0] == ["q.ss06", "m.ss07"]


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
def test_hinted_advances_and_fontconfig(style, weight, wclass):
    face = freetype.Face(path(style))
    for px in (10, 11, 12, 13, 14, 16, 18, 24):
        face.set_pixel_sizes(px, px)
        advs = set()
        for ch in "ailmWf0({=|─":
            face.load_char(ch, freetype.FT_LOAD_DEFAULT)
            advs.add(face.glyph.advance.x)
        assert len(advs) == 1, (px, advs)
    out = subprocess.run(["fc-scan", "--format", "%{family}|%{slant}|%{spacing}|%{weight}", path(style)],
                         capture_output=True, text=True).stdout
    fam, slant, spacing, _w = out.split("|")
    assert build.FAMILY in fam and slant == "100" and spacing == "100"


@pytest.mark.parametrize("style,weight,wclass", PAIRS, ids=IDS)
@pytest.mark.parametrize("kind", ["ttf", "otf"])
def test_opentype_sanitizer(style, weight, wclass, kind):
    ots = pytest.importorskip("ots")
    r = ots.sanitize(path(style, kind), capture_output=True)
    assert r.returncode == 0, r.stderr
