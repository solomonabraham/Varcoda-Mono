"""Build pipeline: parametric drawing -> UFO sources -> TTF / OTF.

    draw_master()      Python glyph programs  ->  outlines
    make_ufo()         outlines               ->  sources/VarcodaMono-<Style>.ufo
    compile_ttf()      UFO                    ->  fonts/VarcodaMono-<Style>.ttf (hinted)
    compile_otf()      UFO                    ->  fonts/otf/VarcodaMono-<Style>.otf

The UFOs are complete, ordinary sources: they can be opened and edited in
Glyphs, FontForge, RoboFont or FontLab, and compiled again with
``build-fonts.py --from-ufo`` without re-running the generator.
"""
from __future__ import annotations

import datetime
import os
import shutil
import tempfile

import struct

import ufoLib2
from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._h_m_t_x import table__h_m_t_x

from . import params
from .draw import draw_master
from .geom import Shape
from .glyphs_liga import feature_code
from .kit import GLYPHS, ORDER, Composite

FAMILY = "Varcoda Mono"
PS_FAMILY = "VarcodaMono"
VERSION_MAJOR, VERSION_MINOR = 1, 400
VERSION = "%d.%03d" % (VERSION_MAJOR, VERSION_MINOR)   # OpenType version
RELEASE = "1.4.0"                                           # release tag (v1.4.0)
COPYRIGHT = "Copyright 2026 The Varcoda Mono Project Authors"
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"
DESCRIPTION = ("Varcoda Mono is a monospaced typeface for programming: geometric, technical and built for long "
               "coding sessions. Dotted zero, clearly separated 1 l I, written italics, optional cell-preserving ligatures.")
DESIGNER = "The Varcoda Mono Project Authors"

PANOSE_WEIGHT = {300: 3, 400: 5, 500: 6, 600: 7, 700: 8}

# fixed timestamp base so that two builds of the same sources are identical
# (override with SOURCE_DATE_EPOCH)
BUILD_EPOCH = int(datetime.datetime(2026, 11, 25, tzinfo=datetime.timezone.utc).timestamp())


# --------------------------------------------------------------------------
# glyph order
# --------------------------------------------------------------------------
def glyph_order(names):
    enc, unenc = [], []
    for n in names:
        cps = GLYPHS[n]["unicodes"]
        if n in (".notdef", "space"):
            continue
        (enc if cps else unenc).append(n)
    enc.sort(key=lambda n: min(GLYPHS[n]["unicodes"]))
    unenc.sort()
    return [".notdef", "space"] + enc + unenc


# --------------------------------------------------------------------------
# UFO
# --------------------------------------------------------------------------
def _draw_shape(shape: Shape, pen):
    for cont in shape.contours:
        pen.moveTo(cont[0][1])
        for seg in cont[1:]:
            if seg[0] == "L":
                pen.lineTo(seg[1])
            else:
                pen.curveTo(seg[1], seg[2], seg[3])
        pen.closePath()


def set_info(font, m):
    info = font.info
    weight = m.name
    italic = bool(getattr(m, "italic", False))
    style = weight if not italic else ("Italic" if weight == "Regular" else weight + " Italic")
    ribbi = weight in ("Regular", "Bold")
    info.familyName = FAMILY
    info.styleName = style
    info.styleMapFamilyName = FAMILY if ribbi else "%s %s" % (FAMILY, weight)
    info.styleMapStyleName = (("bold italic" if italic else "bold") if weight == "Bold"
                              else ("italic" if italic else "regular"))
    info.versionMajor, info.versionMinor = VERSION_MAJOR, VERSION_MINOR
    info.copyright = COPYRIGHT
    info.unitsPerEm = params.UPM
    info.ascender, info.descender = params.ASC, params.DESC
    info.xHeight, info.capHeight = params.XH, params.CAP
    info.italicAngle = -params.ITALIC_ANGLE if italic else 0

    info.openTypeHheaAscender = info.openTypeOS2TypoAscender = params.LINE_ASC
    info.openTypeHheaDescender = info.openTypeOS2TypoDescender = params.LINE_DESC
    info.openTypeHheaLineGap = info.openTypeOS2TypoLineGap = 0
    info.openTypeOS2WinAscent = params.WIN_ASC          # clipping box: includes box-drawing overshoot
    info.openTypeOS2WinDescent = params.WIN_DESC
    info.openTypeOS2Selection = [7]                     # USE_TYPO_METRICS
    info.openTypeOS2WeightClass = m.weight_class
    info.openTypeOS2WidthClass = 5
    info.openTypeOS2Type = []                           # installable embedding
    info.openTypeOS2VendorID = "NONE"                   # no registered vendor tag
    info.openTypeOS2Panose = [2, 11, PANOSE_WEIGHT[m.weight_class], 9, 2, 2, 2, 2, 2, 4]
    info.openTypeOS2StrikeoutSize = round(m.hw)
    info.openTypeOS2StrikeoutPosition = round(params.XH * 0.5 + m.hw / 2)
    info.openTypeGaspRangeRecords = [{"rangeMaxPPEM": 65535, "rangeGaspBehavior": [0, 1, 2, 3]}]
    info.openTypeHeadCreated = datetime.datetime.fromtimestamp(
        int(os.environ.get("SOURCE_DATE_EPOCH", BUILD_EPOCH)), datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S")

    info.openTypeNameDesigner = DESIGNER
    info.openTypeNameManufacturer = DESIGNER
    info.openTypeNameLicense = LICENSE
    info.openTypeNameLicenseURL = LICENSE_URL
    info.openTypeNameDescription = DESCRIPTION
    info.openTypeNameVersion = "Version %s" % VERSION
    if not ribbi:
        info.openTypeNamePreferredFamilyName = FAMILY
        info.openTypeNamePreferredSubfamilyName = style

    info.postscriptFontName = "%s-%s" % (PS_FAMILY, style.replace(" ", ""))
    info.postscriptFullName = "%s %s" % (FAMILY, style)
    info.postscriptIsFixedPitch = True
    info.postscriptUnderlineThickness = 66          # one value for the whole family
    info.postscriptUnderlinePosition = -90
    info.postscriptWeightName = style
    os_ = params.OVERSHOOT
    info.postscriptBlueValues = [-os_, 0, params.XH, params.XH + os_, params.CAP, params.CAP + os_,
                                 params.ASC, params.ASC + os_]
    info.postscriptOtherBlues = [params.DESC - os_, params.DESC]
    info.postscriptStemSnapH = sorted({round(m.hw), round(m.chw)})
    info.postscriptStemSnapV = sorted({round(m.sw), round(m.csw)})
    info.postscriptBlueScale = 0.039625
    info.postscriptBlueFuzz = 0


def make_ufo(m, glyphs=None) -> ufoLib2.Font:
    """outlines of one master -> UFO font object"""
    glyphs = glyphs if glyphs is not None else draw_master(m)
    font = ufoLib2.Font()
    set_info(font, m)
    order = glyph_order(list(glyphs))
    for name in order:
        res = glyphs[name]
        gl = font.newGlyph(name)
        gl.width = params.WIDTH
        gl.unicodes = list(GLYPHS[name]["unicodes"])
        if isinstance(res, Composite):
            pen = gl.getPen()
            for part, dx, dy in res.parts:
                pen.addComponent(part, (1, 0, 0, 1, dx, dy))
        else:
            _draw_shape(res, gl.getPen())
    font.lib["public.glyphOrder"] = order
    font.features.text = feature_code()
    return font


def ufo_path(root, style):
    return os.path.join(root, "sources", "%s-%s.ufo" % (PS_FAMILY, style))


def write_ufo(font, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        shutil.rmtree(path)
    font.save(path, overwrite=True)


# --------------------------------------------------------------------------
# compile
# --------------------------------------------------------------------------
AUTOHINT_OPTIONS = dict(
    hinting_range_min=6,
    hinting_range_max=48,
    hinting_limit=160,
    increase_x_height=14,
    fallback_script="none",        # box drawing, arrows ... stay unhinted (they must tile)
    no_info=True,                  # keep name table clean and builds reproducible
)


def _epoch():
    return int(os.environ.get("SOURCE_DATE_EPOCH", BUILD_EPOCH))


class _MonoHmtx(table__h_m_t_x):
    """hmtx writer for monospaced fonts.  fontTools would store a single
    advance (numberOfHMetrics = 1); the OpenType recommendations ask for 3 in
    monospaced fonts because some legacy Windows software relies on it."""

    def compile(self, ttFont):
        order = ttFont.getGlyphOrder()
        n = min(3, len(order))
        ttFont["hhea"].numberOfHMetrics = n
        data = b"".join(struct.pack(">Hh", otRound(self.metrics[g][0]), otRound(self.metrics[g][1])) for g in order[:n])
        return data + b"".join(struct.pack(">h", otRound(self.metrics[g][1])) for g in order[n:])


def _add_stat(tt):
    """STAT table: tells applications how the static styles relate (weight and
    italic axes), which Windows and macOS use to group the family correctly"""
    from fontTools.otlLib.builder import buildStatTable
    wclass = tt["OS/2"].usWeightClass
    italic = bool(tt["OS/2"].fsSelection & 1)
    weight = dict(value=wclass, name={w[1]: w[0] for w in params.WEIGHTS}[wclass])
    if wclass == 400:
        weight.update(flags=0x2, linkedValue=700)               # "Regular" is elided from names, links to Bold
    slope = dict(value=1, name="Italic") if italic else dict(value=0, name="Roman", flags=0x2, linkedValue=1)
    buildStatTable(tt, [dict(tag="wght", name="Weight", values=[weight]),
                        dict(tag="ital", name="Italic", values=[slope])], elidedFallbackName=2, macNames=False)


def _finish(tt: TTFont, hinted=False):
    """table fixes shared by TTF and OTF"""
    _add_stat(tt)
    from fontTools.misc.timeTools import epoch_diff
    stamp = _epoch() - epoch_diff
    tt["head"].created = tt["head"].modified = stamp
    tt["post"].isFixedPitch = 1
    tt["OS/2"].xAvgCharWidth = params.WIDTH
    tt["OS/2"].achVendID = "NONE"
    # all glyphs share one advance: advertise it
    tt["hhea"].advanceWidthMax = params.WIDTH
    hmtx = _MonoHmtx("hmtx")
    hmtx.metrics = dict(tt["hmtx"].metrics)
    tt["hmtx"] = hmtx
    if hinted:
        tt["head"].flags |= 1 << 3              # hinted: ppem is forced to integers


def compile_ttf(ufo, out_path, hint=True):
    import ufo2ft

    tt = ufo2ft.compileTTF(ufo, removeOverlaps=False, reverseDirection=True, cubicConversionError=0.0008,
                           rememberCurveType=True)
    tt.recalcTimestamp = False
    _finish(tt)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if not hint:
        tt.save(out_path, reorderTables=True)
        return "unhinted"
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.ttf")
        tt.save(raw, reorderTables=True)
        try:
            import ttfautohint
            epoch = _epoch()
            ttfautohint.ttfautohint(in_file=raw, out_file=out_path, epoch=epoch, **AUTOHINT_OPTIONS)
            status = "ttfautohint"
        except Exception as exc:  # pragma: no cover - depends on the platform
            shutil.copy(raw, out_path)
            status = "unhinted (ttfautohint unavailable: %s)" % exc
    # normalise after hinting
    tt2 = TTFont(out_path, recalcTimestamp=False)
    _finish(tt2, hinted=status == "ttfautohint")
    tt2.save(out_path, reorderTables=True)
    return status


def component_only_glyphs(ufo):
    """Unencoded glyphs that exist only as building blocks of composites.
    TrueType needs them; CFF has no composites, so the OTFs leave them out."""
    import re
    used_in_features = set(re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", ufo.features.text or ""))
    referenced = {c.baseGlyph for g in ufo for c in g.components}
    return sorted(n for n in referenced if not ufo[n].unicodes and n not in used_in_features)


def compile_otf(ufo, out_path, hint=True):
    """UFO -> OpenType/CFF.  If the AFDKO autohinter (``otfautohint``) is
    installed the glyphs get PostScript stem hints; otherwise the font is
    written unhinted (alignment zones and standard stems are set either way)."""
    import ufo2ft

    tt = ufo2ft.compileOTF(ufo, removeOverlaps=False, roundTolerance=0.5,
                           skipExportGlyphs=component_only_glyphs(ufo))
    tt.recalcTimestamp = False
    _finish(tt)
    tt["CFF "].cff.topDictIndex[0].isFixedPitch = 1
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    status = "unhinted"
    exe = shutil.which("otfautohint") if hint else None
    if exe:
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            raw, hinted = os.path.join(tmp, "raw.otf"), os.path.join(tmp, "hinted.otf")
            tt.save(raw, reorderTables=True)
            res = subprocess.run([exe, raw, "-o", hinted], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(hinted):
                tt = TTFont(hinted, recalcTimestamp=False)
                try:
                    import cffsubr
                    cffsubr.subroutinize(tt)
                except Exception:  # pragma: no cover - size optimisation only
                    pass
                _finish(tt)
                tt["CFF "].cff.topDictIndex[0].isFixedPitch = 1
                status = "otfautohint"
    tt.save(out_path, reorderTables=True)
    return status


def compile_woff2(ttf_path: str, out_path: str) -> str:
    """WOFF2 web font: the finished (hinted) TTF, recompressed.  Needs brotli."""
    try:
        import brotli  # noqa: F401
    except ImportError:
        return "skipped (brotli not installed)"
    from fontTools.ttLib import TTFont
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tt = TTFont(ttf_path, recalcTimestamp=False)
    tt.flavor = "woff2"
    tt.save(out_path, reorderTables=None)
    return "ok"


def write_webfont_css(root: str, weights) -> str:
    """fonts/webfonts/<family>.css: @font-face rules for the WOFF2 files"""
    rules = ["/* %s %s - SIL Open Font License 1.1 */" % (FAMILY, VERSION)]
    for name, wclass, _stem in weights:
        for slope, file_style in (("normal", name), ("italic", params.italic_style(name))):
            rules.append('@font-face {\n  font-family: "%s";\n  font-style: %s;\n  font-weight: %d;\n  font-display: swap;\n'
                         '  src: url("%s-%s.woff2") format("woff2");\n}' % (FAMILY, slope, wclass, PS_FAMILY, file_style))
    path = os.path.join(root, "fonts", "webfonts", FAMILY.lower().replace(" ", "-") + ".css")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n\n".join(rules) + "\n")
    return path
