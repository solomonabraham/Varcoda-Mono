"""Automated validation of the compiled Varcoda Mono fonts.

Run from the project root:

    python3 -m pytest tests/font-validation -q

Every test runs against all styles (and, where it makes sense, against
the OTF builds as well).
"""
from __future__ import annotations

import hashlib
import os
import random
import subprocess
import sys

import pytest
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from fontsrc import build as build_mod, params  # noqa: E402
from fontsrc.glyphs_liga import LIGATURES  # noqa: E402

STYLES = [w[0] for w in params.WEIGHTS]
WEIGHT_CLASS = {w[0]: w[1] for w in params.WEIGHTS}
WIDTH = params.WIDTH


def ttf_path(style):
    return os.path.join(ROOT, "fonts", "VarcodaMono-%s.ttf" % style)


def otf_path(style):
    return os.path.join(ROOT, "fonts", "otf", "VarcodaMono-%s.otf" % style)


_cache = {}


def font(path) -> TTFont:
    if path not in _cache:
        _cache[path] = TTFont(path)
    return _cache[path]


ALL_FILES = [ttf_path(s) for s in STYLES] + [otf_path(s) for s in STYLES]
TTFS = [ttf_path(s) for s in STYLES]


def ids(paths):
    return [os.path.basename(p) for p in paths]


# --------------------------------------------------------------------------
# files and tables
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_file_exists_and_opens(path):
    assert os.path.isfile(path), "missing font file"
    f = font(path)
    for table in ("cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post", "GSUB"):
        assert table in f, "table %s missing" % table
    assert ("glyf" in f) != ("CFF " in f)


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_truetype_hinting_present(path):
    f = font(path)
    for table in ("fpgm", "prep", "cvt ", "gasp"):
        assert table in f, "hinting table %s missing" % table
    assert f["head"].flags & (1 << 3), "hinted fonts must force integer ppem"
    glyf = f["glyf"]
    hinted = sum(1 for n in ("n", "o", "H", "zero", "a", "e") if glyf[n].program.getBytecode())
    assert hinted == 6, "core glyphs carry no instructions"
    assert f["gasp"].gaspRange == {65535: 15}


# --------------------------------------------------------------------------
# monospacing
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_every_advance_width_is_one_cell(path):
    f = font(path)
    widths = {name: adv for name, (adv, lsb) in f["hmtx"].metrics.items()}
    wrong = {n: w for n, w in widths.items() if w != WIDTH}
    assert not wrong, "glyphs with a different advance: %s" % sorted(wrong.items())[:10]
    assert f["hhea"].advanceWidthMax == WIDTH
    assert f["OS/2"].xAvgCharWidth == WIDTH
    assert f["post"].isFixedPitch == 1
    assert f["OS/2"].panose.bProportion == 9          # monospaced
    assert f["hhea"].numberOfHMetrics == 3            # OpenType recommendation for monospaced fonts
    assert f["head"].unitsPerEm == params.UPM
    if "CFF " in f:
        assert f["CFF "].cff.topDictIndex[0].isFixedPitch == 1


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_no_kerning_or_positioning_that_breaks_the_grid(path):
    f = font(path)
    assert "kern" not in f
    if "GPOS" in f:
        feats = {fr.FeatureTag for fr in f["GPOS"].table.FeatureList.FeatureRecord}
        assert not feats & {"kern", "dist", "cpsp"}


# --------------------------------------------------------------------------
# vertical metrics
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_vertical_metrics(path):
    f = font(path)
    os2, hhea = f["OS/2"], f["hhea"]
    assert (hhea.ascent, hhea.descent, hhea.lineGap) == (params.LINE_ASC, params.LINE_DESC, 0)
    assert (os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (params.LINE_ASC, params.LINE_DESC, 0)
    # the Windows clipping box additionally holds the overshoot of the box-drawing glyphs
    assert (os2.usWinAscent, os2.usWinDescent) == (params.WIN_ASC, params.WIN_DESC)
    assert os2.fsSelection & (1 << 7), "USE_TYPO_METRICS not set"
    assert os2.sxHeight == params.XH and os2.sCapHeight == params.CAP
    # nothing may be clipped by Windows (win metrics are a hard clipping box)
    assert f["head"].yMax <= os2.usWinAscent and f["head"].yMin >= -os2.usWinDescent


def _bounds(f, name):
    gs = f.getGlyphSet()
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    return bp.bounds


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_alignment_zones(path):
    """flat letters sit exactly on the grid, round ones overshoot slightly"""
    f = font(path)
    os_ = params.OVERSHOOT
    for name, y0, y1 in [("x", 0, params.XH), ("H", 0, params.CAP), ("n", 0, params.XH), ("l", 0, params.ASC),
                         ("p", params.DESC, params.XH), ("o", -os_, params.XH + os_), ("O", -os_, params.CAP + os_),
                         ("zero", -os_, params.CAP + os_), ("seven", 0, params.CAP)]:
        b = _bounds(f, name)
        assert (b[1], b[3]) == (y0, y1), "%s spans %s..%s, expected %s..%s" % (name, b[1], b[3], y0, y1)


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_glyphs_stay_inside_their_cells(path):
    f = font(path)
    lig_cells = {lig: len(seq) for lig, seq, _ in LIGATURES}
    cmap = f.getBestCmap()
    # box drawing, blocks and the Powerline separators overshoot on purpose so that they join
    box = {cmap[cp] for cp in list(range(0x2500, 0x25A0)) + list(range(0xE0B0, 0xE0B4))}
    bad = []
    for name in f.getGlyphOrder():
        b = _bounds(f, name)
        if b is None:
            continue
        cells = lig_cells.get(name, 1)
        ox, oy = (params.BOX_OVER_X, params.BOX_OVER_Y) if name in box else (0, 0)
        if (b[0] < -(cells - 1) * WIDTH - ox - 0.5 or b[2] > WIDTH + ox + 0.5
                or b[1] < params.LINE_DESC - oy - 0.5 or b[3] > params.LINE_ASC + oy + 0.5):
            bad.append((name, b))
    assert not bad, bad[:10]


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_box_drawing_joins_across_cells(path):
    """lines that leave a cell reach past its edge on that side (and only there)"""
    f = font(path)
    cmap = f.getBestCmap()
    ox, oy = params.BOX_OVER_X, params.BOX_OVER_Y
    expect = {0x2500: (-ox, None, WIDTH + ox, None),                       # horizontal line
              0x2502: (None, params.LINE_DESC - oy, None, params.LINE_ASC + oy),   # vertical line
              0x253C: (-ox, params.LINE_DESC - oy, WIDTH + ox, params.LINE_ASC + oy),
              0x2550: (-ox, None, WIDTH + ox, None), 0x2551: (None, params.LINE_DESC - oy, None, params.LINE_ASC + oy),
              0x2588: (-ox, params.LINE_DESC - oy, WIDTH + ox, params.LINE_ASC + oy)}
    for cp, exp in expect.items():
        b = _bounds(f, cmap[cp])
        for got, want in zip(b, exp):
            assert want is None or got == want, "U+%04X bounds %s" % (cp, b)
    # a corner only reaches the two sides it connects to
    b = _bounds(f, cmap[0x250C])          # down and right
    assert b[2] == WIDTH + ox and b[1] == params.LINE_DESC - oy and b[0] > 0 and b[3] < params.LINE_ASC


# --------------------------------------------------------------------------
# character set
# --------------------------------------------------------------------------
REQUIRED_RANGES = {
    "Basic Latin": range(0x20, 0x7F),
    "Latin-1 Supplement": range(0xA0, 0x100),
    "Latin Extended-A": range(0x100, 0x180),
    "Box Drawing": range(0x2500, 0x2580),
    "Block Elements": range(0x2580, 0x25A0),
}
REQUIRED_EXTRA = "ȘșȚț–—‘’‚“”„†‡•…‹›€™←↑→↓↔↕⇐⇒⇔−∙√∞≈≠≡≤≥∆∏∑πλ■□▲▼▶◀◆●○✓✗�"


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_unicode_coverage(path):
    cmap = font(path).getBestCmap()
    for block, rng in REQUIRED_RANGES.items():
        missing = [hex(cp) for cp in rng if cp not in cmap]
        assert not missing, "%s incomplete: %s" % (block, missing)
    missing = [ch for ch in REQUIRED_EXTRA if ord(ch) not in cmap]
    assert not missing, missing


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_cmap_uses_standard_glyph_names(path):
    from fontTools.agl import UV2AGL
    cmap = font(path).getBestCmap()
    for cp, name in cmap.items():
        if cp in (0xA0, 0x2219, 0x22C5, 0x394, 0x25CA, 0x110):     # second code point of a shared glyph
            continue
        expected = UV2AGL.get(cp, "uni%04X" % cp)
        assert name == expected, "U+%04X is mapped to %r, expected %r" % (cp, name, expected)


def test_all_styles_have_the_same_glyphs_and_cmap():
    ref = font(ttf_path("Regular"))
    glyf = ref["glyf"]
    # accents that only exist as components of composites are not needed in CFF
    component_only = {c.glyphName for n in ref.getGlyphOrder() if glyf[n].isComposite() for c in glyf[n].components}
    component_only = {n for n in component_only if "comb" in n}
    assert len(component_only) == 26
    for path in ALL_FILES:
        f = font(path)
        assert f.getBestCmap() == ref.getBestCmap(), path
        if "glyf" in f:
            assert f.getGlyphOrder() == ref.getGlyphOrder(), path
        else:
            assert f.getGlyphOrder() == [n for n in ref.getGlyphOrder() if n not in component_only], path


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_every_glyph_is_reachable(path):
    """each glyph is encoded, produced by a feature, or used as a component"""
    f = font(path)
    reachable = set(f.getBestCmap().values()) | {".notdef"}
    gsub = f["GSUB"].table
    for lookup in gsub.LookupList.Lookup:
        for st in lookup.SubTable:
            if hasattr(st, "mapping"):
                reachable |= set(st.mapping.values())
    if "glyf" in f:
        glyf = f["glyf"]
        for n in list(reachable):
            if glyf[n].isComposite():
                reachable |= {c.glyphName for c in glyf[n].components}
    unreachable = set(f.getGlyphOrder()) - reachable
    assert not unreachable, sorted(unreachable)


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_no_empty_or_placeholder_glyphs(path):
    f = font(path)
    cmap = f.getBestCmap()
    blank_ok = {"space", "LIG"}
    areas = {}
    for name in f.getGlyphOrder():
        b = _bounds(f, name)
        if name in blank_ok:
            assert b is None, "%s should be empty" % name
            continue
        assert b is not None, "glyph %s has no outline" % name
        assert (b[2] - b[0]) > 20 and (b[3] - b[1]) > 20, "glyph %s is degenerate: %s" % (name, b)
    # letters and figures must all be different drawings
    gs = f.getGlyphSet()
    seen = {}
    for ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        pen = DecomposingRecordingPen(gs)
        gs[cmap[ord(ch)]].draw(pen)
        key = repr(pen.value)
        assert key not in seen, "%r and %r share one outline" % (ch, seen.get(key))
        seen[key] = ch


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_composites_resolve(path):
    f = font(path)
    glyf = f["glyf"]
    names = set(f.getGlyphOrder())
    for name in names:
        g = glyf[name]
        if g.isComposite():
            for comp in g.components:
                assert comp.glyphName in names
                assert not glyf[comp.glyphName].isComposite(), "nested composite in %s" % name


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_contour_direction(path):
    """filled area must be positive in the format's own winding convention"""
    f = font(path)
    gs = f.getGlyphSet()
    sign = -1 if "glyf" in f else 1          # TrueType: clockwise outer contours
    for name in ("o", "H", "ampersand", "at", "eight", "B", "g"):
        pen = AreaPen(gs)
        gs[name].draw(pen)
        assert pen.value * sign > 1000, "%s has inverted contours" % name


# --------------------------------------------------------------------------
# names and style linking
# --------------------------------------------------------------------------
@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("kind", ["ttf", "otf"])
def test_names_and_style_linking(style, kind):
    f = font(ttf_path(style) if kind == "ttf" else otf_path(style))
    name, os2, head = f["name"], f["OS/2"], f["head"]

    def n(i):
        rec = name.getName(i, 3, 1, 0x409)
        return rec.toUnicode() if rec else None

    ribbi = style in ("Regular", "Bold")
    assert n(1) == ("Varcoda Mono" if ribbi else "Varcoda Mono " + style)
    assert n(2) == ("Bold" if style == "Bold" else "Regular")
    assert n(4) == "Varcoda Mono " + style
    assert n(6) == "VarcodaMono-" + style
    if ribbi:
        assert n(16) is None and n(17) is None
    else:
        assert (n(16), n(17)) == ("Varcoda Mono", style)
    assert n(5) == "Version %s" % build_mod.VERSION
    assert "Open Font License" in n(13) and n(14) == "https://openfontlicense.org"
    assert os2.usWeightClass == WEIGHT_CLASS[style]
    assert os2.usWidthClass == 5
    assert os2.fsType == 0, "font must be freely embeddable/installable"
    bold = style == "Bold"
    assert bool(os2.fsSelection & (1 << 5)) == bold           # BOLD
    assert bool(os2.fsSelection & (1 << 6)) == (not bold)     # REGULAR
    assert not os2.fsSelection & 1                            # not italic
    assert bool(head.macStyle & 1) == bold
    assert f["post"].italicAngle == 0


def test_contour_counts_match_across_weights():
    """a glyph has the same number of contours in every weight - a difference
    means that parts merged or fell apart in one of them"""
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    def count(f, name):
        gs = f.getGlyphSet()
        pen = DecomposingRecordingPen(gs)
        gs[name].draw(pen)
        return sum(1 for op, _ in pen.value if op == "moveTo")

    fonts = [font(ttf_path(s)) for s in STYLES]
    bad = []
    for name in fonts[0].getGlyphOrder():
        counts = [count(f, name) for f in fonts]
        if len(set(counts)) != 1:
            bad.append((name, counts))
    assert not bad, bad


def test_weights_are_ordered():
    """ink grows monotonically from Light to Bold"""
    def ink(style, glyph):
        f = font(ttf_path(style))
        gs = f.getGlyphSet()
        pen = AreaPen(gs)
        gs[glyph].draw(pen)
        return abs(pen.value)

    for glyph in ("n", "H", "zero", "at", "equal"):
        vals = [ink(s, glyph) for s in STYLES]
        assert vals == sorted(vals) and len(set(vals)) == len(STYLES), (glyph, vals)


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_powerline_separators_fill_the_cell(path):
    """U+E0B0-E0B3 span the whole line box (plus the overshoot that hides
    seams) and touch the cell edge they point away from, like block elements"""
    f = font(path)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()

    def bounds(cp):
        pen = BoundsPen(gs)
        gs[cmap[cp]].draw(pen)
        return pen.bounds

    top, bot = params.LINE_ASC + params.BOX_OVER_Y, params.LINE_DESC - params.BOX_OVER_Y
    for cp in (0xE0B0, 0xE0B1, 0xE0B2, 0xE0B3):
        x0, y0, x1, y1 = bounds(cp)
        assert (y0, y1) == (bot, top), (hex(cp), y0, y1)
    assert bounds(0xE0B0)[0] == -params.BOX_OVER_X and bounds(0xE0B0)[2] == WIDTH       # base overlaps, tip at the edge
    assert bounds(0xE0B2)[2] == WIDTH + params.BOX_OVER_X and bounds(0xE0B2)[0] == 0
    assert bounds(0xE0B1)[:1] == (0,) and bounds(0xE0B3)[2] == WIDTH
    for cp in (0xE0A0, 0xE0A1, 0xE0A2):
        x0, y0, x1, y1 = bounds(cp)
        assert 0 <= x0 and x1 <= WIDTH and params.LINE_DESC <= y0 and y1 <= params.LINE_ASC


@pytest.mark.parametrize("style", STYLES)
def test_webfont_matches_the_ttf(style):
    """the WOFF2 is the hinted TTF, recompressed: same tables, same glyphs"""
    woff = TTFont(os.path.join(ROOT, "fonts", "webfonts", "VarcodaMono-%s.woff2" % style))
    ttf = font(ttf_path(style))
    assert woff.flavor == "woff2"
    assert woff.getGlyphOrder() == ttf.getGlyphOrder() and woff.getBestCmap() == ttf.getBestCmap()
    assert sorted(woff.keys()) == sorted(ttf.keys())
    assert woff["hmtx"].metrics == ttf["hmtx"].metrics


# --------------------------------------------------------------------------
# operators and brackets share one axis
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_operators_and_brackets_are_centred_on_the_axis(path):
    f = font(path)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()

    def centre(ch):
        pen = BoundsPen(gs)
        gs[cmap[ord(ch)]].draw(pen)
        return (pen.bounds[1] + pen.bounds[3]) / 2, (pen.bounds[0] + pen.bounds[2]) / 2

    for ch in "+-=<>~|/\\()[]{}":
        cy, cx = centre(ch)
        assert abs(cy - params.AXIS) <= 2, "%r is centred at y=%.1f, the axis is %d" % (ch, cy, params.AXIS)
    assert abs(centre("*")[0] - params.AXIS) <= 20          # optically a little above the axis
    for ch in "+-=~|*:.!":          # ; and , lean on their tails
        assert abs(centre(ch)[1] - WIDTH / 2) <= 2, "%r is not centred in its cell" % ch
    # paired brackets are mirror images
    for a, b in ("()", "[]", "{}", "<>"):
        assert abs(centre(a)[1] + centre(b)[1] - WIDTH) <= 1


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_punctuation_is_not_undersized(path):
    """1.200 enlarged the punctuation after measuring it against other coding
    fonts; keep it from shrinking again: sizes relative to the vertical stem."""
    f = font(path)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()

    def size(ch):
        pen = BoundsPen(gs)
        gs[cmap[ord(ch)]].draw(pen)
        return pen.bounds[2] - pen.bounds[0], pen.bounds[3] - pen.bounds[1]

    dot = size(".")[0]
    assert dot >= 0.19 * WIDTH, "period is %d units wide" % dot
    assert size("'")[1] >= 0.36 * params.CAP
    assert size("*")[0] >= 0.62 * WIDTH and size("(")[0] >= 0.38 * WIDTH and size("{")[0] >= 0.52 * WIDTH


# --------------------------------------------------------------------------
# legibility: look-alike characters must really differ
# --------------------------------------------------------------------------
def _raster(path, ch, px=48):
    import freetype
    import numpy as np
    face = freetype.Face(path)
    face.set_pixel_sizes(0, px)
    face.load_char(ch, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
    bm = face.glyph.bitmap
    canvas = np.zeros((px * 2, px), dtype=float)
    arr = np.array(bm.buffer, dtype=float).reshape(bm.rows, bm.pitch)[:, :bm.width] / 255 if bm.rows else np.zeros((0, 0))
    top = int(px * 1.4) - face.glyph.bitmap_top
    left = max(face.glyph.bitmap_left, 0)
    h, w = arr.shape
    canvas[top:top + h, left:left + w] = arr[:canvas.shape[0] - top, :canvas.shape[1] - left]
    return canvas


LOOKALIKES = [("0", "O"), ("0", "o"), ("0", "8"), ("1", "l"), ("1", "I"), ("l", "I"), ("l", "|"), ("I", "|"), ("1", "|"),
              ("1", "7"), ("5", "S"), ("8", "B"), ("2", "Z"), ("6", "b"), ("g", "9"), ("g", "q"), ("c", "e"), ("u", "v"),
              ("`", "'"), (".", ","), (":", ";"), ("-", "_"), ("{", "("), ("[", "("), ("D", "O"),
              ("y", "g"), ("y", "v"), ("b", "h"), ("o", "a")]


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
@pytest.mark.parametrize("pair", LOOKALIKES, ids=["%s~%s" % p for p in LOOKALIKES])
def test_lookalikes_differ(path, pair):
    import numpy as np
    a, b = pair

    def img(s):
        return np.hstack([_raster(path, c) for c in s])

    ia, ib = img(a), img(b)
    diff = np.abs(ia - ib).sum()
    ink = (ia.sum() + ib.sum()) / 2
    # near-identical drawings score below 0.08; the closest legitimate pairs here are
    # Bold D~O (0.18, square vs round left side) and g~q (0.20, hooked vs straight tail)
    assert diff / ink > 0.15, "%r and %r differ by only %.0f %% of their ink" % (a, b, 100 * diff / ink)


# --------------------------------------------------------------------------
# OpenType features (shaped with HarfBuzz)
# --------------------------------------------------------------------------
def shape(path, text, features):
    import uharfbuzz as hb
    with open(path, "rb") as fh:
        face = hb.Face(fh.read())
    fnt = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(fnt, buf, features)
    names = [fnt.glyph_to_string(i.codepoint) for i in buf.glyph_infos]
    adv = [p.x_advance for p in buf.glyph_positions]
    return names, adv


AGL = {"=": "equal", "!": "exclam", "<": "less", ">": "greater", "-": "hyphen", "&": "ampersand", "|": "bar",
       "?": "question", "+": "plus", ":": "colon", "/": "slash", "*": "asterisk"}
INV = {v: k for k, v in AGL.items()}
INV.setdefault("period", ".")


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_feature_list(path):
    gsub = font(path)["GSUB"].table
    tags = {fr.FeatureTag for fr in gsub.FeatureList.FeatureRecord}
    assert tags == {"calt", "ss01", "ss02", "ss03", "ss04", "ss05"}
    # ligatures must be switchable: nothing may hide in always-on features
    assert not tags & {"ccmp", "rlig", "locl", "liga"}


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_ligatures_are_optional(path):
    """with calt off every operator stays a plain glyph"""
    for lig, seq, _ in LIGATURES:
        text = "a" + "".join(INV[g] for g in seq) + "b"
        names, adv = shape(path, text, {"calt": False})
        assert names == ["a"] + seq + ["b"], (text, names)
        assert adv == [WIDTH] * len(text)


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_ligatures_substitute_and_keep_the_grid(path):
    for lig, seq, _ in LIGATURES:
        text = "a" + "".join(INV[g] for g in seq) + "b"
        names, adv = shape(path, text, {"calt": True})
        assert names == ["a"] + ["LIG"] * (len(seq) - 1) + [lig, "b"], (text, names)
        assert adv == [WIDTH] * len(text), "ligature %s changes the advance" % lig


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_long_runs_are_left_alone(path):
    for text in ["====", "=====", "----", "---", "////", "///", "||||", "|||", "&&&", ":::", "+++", "???",
                 "<<=", ">>=", "-->", "<--", "==>", "<==", "!===", "/*/", "===>", "<===", ">==="]:
        names, adv = shape(path, text, {"calt": True})
        assert names == [AGL[c] for c in text], (text, names)


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_random_operator_strings_never_change_cell_count(path):
    rnd = random.Random(20261125)
    alphabet = "=!<>-&|?+:/* ab"
    for _ in range(400):
        text = "".join(rnd.choice(alphabet) for _ in range(rnd.randint(1, 14)))
        names, adv = shape(path, text, {"calt": True})
        assert len(names) == len(text), (text, names)
        assert adv == [WIDTH] * len(text), text
        # every spacer must be followed by a spacer or a ligature
        for i, n in enumerate(names):
            if n == "LIG":
                assert names[i + 1] == "LIG" or names[i + 1].endswith(".liga"), (text, names)


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_stylistic_sets(path):
    assert shape(path, "0a", {})[0] == ["zero", "a"]
    assert shape(path, "0a", {"ss01": True})[0] == ["zero.ss01", "a"]
    assert shape(path, "0aá", {"ss02": True})[0] == ["zero", "a.ss02", "aacute.ss02"]
    assert shape(path, "0Ol", {"ss03": True})[0] == ["zero.ss03", "O", "l"]
    assert shape(path, "0l1", {"ss04": True})[0] == ["zero", "l.ss04", "one"]
    assert shape(path, "vyý", {"ss05": True})[0] == ["v", "y.ss05", "yacute.ss05"]
    assert shape(path, "0al", {})[0] == ["zero", "a", "l"]          # nothing is on by default


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_feature_names(path):
    f = font(path)
    gsub = f["GSUB"].table
    labels = {}
    for fr in gsub.FeatureList.FeatureRecord:
        prm = fr.Feature.FeatureParams
        if prm is not None and hasattr(prm, "UINameID"):
            labels[fr.FeatureTag] = f["name"].getDebugName(prm.UINameID)
    assert labels == {"ss01": "Dotted zero", "ss02": "Single-storey a", "ss03": "Plain zero", "ss04": "Flat-foot l", "ss05": "Squared y"}


# --------------------------------------------------------------------------
# third-party validators and rasterisers
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_opentype_sanitizer(path):
    """OTS is the validator browsers (and therefore Electron apps) run on web fonts"""
    ots = pytest.importorskip("ots")
    res = ots.sanitize(path, capture_output=True)
    assert res.returncode == 0, res.stderr.decode()[:500]


@pytest.mark.parametrize("path", ALL_FILES, ids=ids(ALL_FILES))
def test_freetype_renders_every_glyph_at_small_sizes(path):
    freetype = pytest.importorskip("freetype")
    face = freetype.Face(path)
    f = font(path)
    blank = {"space", "LIG", "nbspace"}
    order = f.getGlyphOrder()
    for px in (12, 13, 14, 15, 16):
        face.set_pixel_sizes(0, px)
        for gid, name in enumerate(order):
            face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
            adv = face.glyph.advance.x / 64
            assert abs(adv - round(WIDTH / 1000 * px)) <= 1, (name, px, adv)
            if name not in blank:
                assert face.glyph.bitmap.rows > 0 and sum(face.glyph.bitmap.buffer) > 0, "%s is invisible at %d px" % (name, px)


@pytest.mark.parametrize("path", TTFS, ids=ids(TTFS))
def test_hinted_advances_are_identical_for_all_glyphs(path):
    """the grid must hold with hinting on: one advance per size, for every glyph"""
    freetype = pytest.importorskip("freetype")
    face = freetype.Face(path)
    n = len(font(path).getGlyphOrder())
    for px in range(8, 33):
        face.set_pixel_sizes(0, px)
        advs = set()
        for gid in range(n):
            face.load_glyph(gid, freetype.FT_LOAD_TARGET_NORMAL)
            advs.add(face.glyph.advance.x)
        assert len(advs) == 1, "advances differ at %d px: %s" % (px, sorted(advs))


def test_fontconfig_reports_monospace():
    import shutil
    if not shutil.which("fc-scan"):
        pytest.skip("fontconfig not installed")
    for style in STYLES:
        out = subprocess.run(["fc-scan", "--format", "%{spacing}|%{family}|%{style}|%{weight}", ttf_path(style)],
                             capture_output=True, text=True, check=True).stdout
        spacing, family, st, weight = out.split("|")
        assert spacing == "100", "fontconfig does not see %s as monospaced (spacing=%s)" % (style, spacing)
        assert "Varcoda Mono" in family


# --------------------------------------------------------------------------
# sources and reproducibility
# --------------------------------------------------------------------------
@pytest.mark.parametrize("style", STYLES)
def test_ufo_sources_match_fonts(style):
    import ufoLib2
    ufo = ufoLib2.Font.open(os.path.join(ROOT, "sources", "VarcodaMono-%s.ufo" % style))
    f = font(ttf_path(style))
    assert list(ufo.lib["public.glyphOrder"]) == f.getGlyphOrder()
    assert all(g.width == WIDTH for g in ufo)
    assert ufo.info.familyName == "Varcoda Mono" and ufo.info.styleName == style
    assert "feature calt" in ufo.features.text


@pytest.mark.parametrize("style", STYLES)
def test_sources_have_no_outline_debris(style):
    """no sliver contours and no micro-segments (left-overs of boolean operations)"""
    import math
    import ufoLib2
    from fontTools.pens.areaPen import AreaPen as AP
    ufo = ufoLib2.Font.open(os.path.join(ROOT, "sources", "VarcodaMono-%s.ufo" % style))
    for glyph in ufo:
        for contour in glyph.contours:
            pen = AP()
            contour.draw(pen)
            assert abs(pen.value) >= 60, "%s contains a sliver contour (area %.1f)" % (glyph.name, pen.value)
            on = [(p.x, p.y) for p in contour.points if p.type is not None]
            for i, p in enumerate(on):
                q = on[(i + 1) % len(on)]
                assert math.dist(p, q) >= 2.6 or p == q, "%s has a micro-segment at %s" % (glyph.name, p)
            for p in contour.points:
                assert float(p.x).is_integer() and float(p.y).is_integer(), "%s has off-grid points" % glyph.name


def test_build_is_reproducible(tmp_path):
    """generating everything again from the Python sources gives identical fonts"""
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build-fonts.py"), "--root", str(tmp_path),
                    "-w", "Regular", "Bold"], check=True, capture_output=True)
    for style in ("Regular", "Bold"):
        for rel in ("fonts/VarcodaMono-%s.ttf" % style, "fonts/otf/VarcodaMono-%s.otf" % style,
                    "fonts/webfonts/VarcodaMono-%s.woff2" % style):
            a = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
            b = hashlib.sha256(open(os.path.join(str(tmp_path), rel), "rb").read()).hexdigest()
            assert a == b, "%s is not reproducible" % rel
