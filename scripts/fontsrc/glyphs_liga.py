"""Optional programming ligatures and stylistic alternates.

Every ligature glyph keeps the normal 600-unit advance and is drawn
*backwards* over the preceding cells; the characters before it are replaced
by the empty spacer glyph ``LIG``.  A three-character ligature therefore
still occupies exactly three cells and the text grid never shifts."""
from __future__ import annotations

from .geom import Shape, diag, rect, slash
from .glyphs_lower import _lc
from .glyphs_marks import cedilla_shape, ogonek_shape
from .glyphs_punct import (ampersand_, asterisk_, bar_, chevron, chevron_vx, colon_, eq_gap, greater_, less_, less_geom,
                           obar, question_, slash_, equal_, hyphen_, period_, plus_)
from .glyphs_lower import l_, m_full_, q_plain_, y_squared_
from .geom import rect as _rect
from .glyphs_upper import zero_ring, zero_slash
from . import glyphs_italic as it
from .kit import GLYPHS, Composite, bowl, g, ital, vstem

# (ligature glyph, input glyph sequence, extra ignore contexts)
LIGATURES = [
    ("equal_equal_equal.liga", ["equal", "equal", "equal"], ["exclam equal' equal equal", "less equal' equal equal",
                                                             "greater equal' equal equal", "equal' equal equal greater"]),
    ("exclam_equal_equal.liga", ["exclam", "equal", "equal"], ["exclam' equal equal equal"]),
    ("less_equal_greater.liga", ["less", "equal", "greater"], ["less less' equal greater", "less' equal greater greater"]),
    ("less_hyphen_greater.liga", ["less", "hyphen", "greater"], ["less less' hyphen greater", "less' hyphen greater greater"]),
    ("exclam_equal.liga", ["exclam", "equal"], ["exclam exclam' equal", "exclam' equal equal"]),
    ("equal_equal.liga", ["equal", "equal"], ["less equal' equal", "greater equal' equal", "exclam equal' equal",
                                              "equal' equal greater"]),
    ("equal_greater.liga", ["equal", "greater"], ["equal equal' greater", "equal' greater greater", "less equal' greater"]),
    ("hyphen_greater.liga", ["hyphen", "greater"], ["hyphen hyphen' greater", "hyphen' greater greater", "less hyphen' greater"]),
    ("less_hyphen.liga", ["less", "hyphen"], ["less less' hyphen", "less' hyphen hyphen", "less' hyphen greater"]),
    ("less_equal.liga", ["less", "equal"], ["less less' equal", "less' equal equal", "less' equal greater"]),
    ("greater_equal.liga", ["greater", "equal"], ["greater greater' equal", "greater' equal equal", "equal greater' equal",
                                                  "hyphen greater' equal"]),
    ("ampersand_ampersand.liga", ["ampersand", "ampersand"], []),
    ("bar_bar.liga", ["bar", "bar"], []),
    ("question_question.liga", ["question", "question"], []),
    ("plus_plus.liga", ["plus", "plus"], []),
    ("hyphen_hyphen.liga", ["hyphen", "hyphen"], ["less hyphen' hyphen", "hyphen' hyphen greater"]),
    ("colon_colon.liga", ["colon", "colon"], []),
    ("slash_slash.liga", ["slash", "slash"], []),
    ("slash_asterisk.liga", ["slash", "asterisk"], ["slash slash' asterisk", "slash' asterisk slash"]),
    ("asterisk_slash.liga", ["asterisk", "slash"], ["slash asterisk' slash", "asterisk' slash slash"]),
    ("bar_greater.liga", ["bar", "greater"], ["bar bar' greater", "bar' greater greater"]),
    ("less_bar.liga", ["less", "bar"], ["less less' bar", "less' bar bar"]),
    # added in 1.200
    ("colon_equal.liga", ["colon", "equal"], []),
    ("asterisk_asterisk.liga", ["asterisk", "asterisk"], ["slash asterisk' asterisk", "asterisk' asterisk slash"]),
    ("question_period.liga", ["question", "period"], []),
    ("plus_equal.liga", ["plus", "equal"], []),
    ("hyphen_equal.liga", ["hyphen", "equal"], ["less hyphen' equal"]),
    # added in 1.400.  It comes after ** and /*, so **= and /*= keep those and a plain =
    ("asterisk_equal.liga", ["asterisk", "equal"], []),
]


@g("LIG")
def lig_spacer_(m):
    return Shape()


def cellx(m, s, n):
    """place a normal glyph n cells to the left of the last cell"""
    return s.move(-m.W * n, 0)


def _greater_vertex(m):
    x_tip, x_open, hh, a, b = less_geom(m)
    vx = chevron_vx(x_tip, x_open, hh, a, b)
    return m.W - vx, m.W - x_open, hh        # vertex x, open-end x, half height of '>'


def _bar_end_on_arm(m, gp):
    """x where a bar at ±gp from the axis disappears into an arm of '>'"""
    vx, xo, hh = _greater_vertex(m)
    return vx - (vx - xo) * (gp / hh)


@g("hyphen_greater.liga")
def lig_arrow_(m):
    vx, xo, hh = _greater_vertex(m)
    return greater_(m) | obar(m, m.axis, -m.W + m.OL + 0.02 * m.W, vx)


@g("less_hyphen.liga")
def lig_arrow_left_(m):
    vx, xo, hh = _greater_vertex(m)
    return cellx(m, less_(m), 1) | obar(m, m.axis, -vx, m.W - m.OL - 0.02 * m.W)


@g("less_hyphen_greater.liga")
def lig_arrow_both_(m):
    vx, xo, hh = _greater_vertex(m)
    return cellx(m, less_(m), 2) | greater_(m) | obar(m, m.axis, -m.W - vx, vx)


@g("equal_greater.liga")
def lig_fat_arrow_(m):
    gp = eq_gap(m)
    xe = _bar_end_on_arm(m, gp)
    return greater_(m) | obar(m, m.axis + gp, -m.W + m.OL, xe) | obar(m, m.axis - gp, -m.W + m.OL, xe)


@g("less_equal_greater.liga")
def lig_spaceship_(m):
    gp = eq_gap(m)
    xe = _bar_end_on_arm(m, gp)
    xs = -m.W - xe
    return cellx(m, less_(m), 2) | greater_(m) | obar(m, m.axis + gp, xs, xe) | obar(m, m.axis - gp, xs, xe)


@g("equal_equal.liga")
def lig_eq2_(m):
    gp = eq_gap(m)
    return obar(m, m.axis + gp, -m.W + m.OL, m.W - m.OL) | obar(m, m.axis - gp, -m.W + m.OL, m.W - m.OL)


def _triple(m, x0, x1):
    gp = eq_gap(m) * 1.55
    t = m.hw * m.lerp(1.0, 0.92)
    return obar(m, m.axis, x0, x1, t) | obar(m, m.axis + gp, x0, x1, t) | obar(m, m.axis - gp, x0, x1, t)


@g("equal_equal_equal.liga")
def lig_eq3_(m):
    return _triple(m, -2 * m.W + m.OL, m.W - m.OL)


def _not_slash(m, cx, f=1.0):
    return slash(cx - 0.17 * m.W, m.axis - 0.365 * m.cap * f, cx + 0.17 * m.W, m.axis + 0.365 * m.cap * f, m.a * 0.88, m.b * 0.88)


@g("exclam_equal.liga")
def lig_neq_(m):
    return lig_eq2_(m) | _not_slash(m, 0)


@g("exclam_equal_equal.liga")
def lig_neq3_(m):
    return _triple(m, -2 * m.W + m.OL, m.W - m.OL) | _not_slash(m, -m.W / 2, 1.12)


LE_HALF_W = 0.60         # half width of <= and >= as a fraction of the advance


def _wide_less_equal(m):
    """<= as one sign, centred on the border between its two cells.  It is not
    stretched to fill them (until 1.300 it reached ±0.82): a chevron that flat
    stops reading as '<', so the sign stays compact and gets white space instead."""
    hh, gap = 0.245 * m.cap, 0.12 * m.cap          # half height of the chevron, its distance from the bar
    cy = m.axis + (gap + m.hw / 2) / 2             # chevron and bar together are centred on the operator axis
    x = LE_HALF_W * m.W
    return chevron(m, -x, x, hh, m.a * 0.94, m.b * 0.96, cy=cy) | obar(m, cy - hh - gap - m.hw * 0.5, -x, x)


@g("less_equal.liga")
def lig_le_(m):
    return _wide_less_equal(m)


@g("greater_equal.liga")
def lig_ge_(m):
    return _wide_less_equal(m).flip_x(0)


def _pair(m, s, d, s2=None):
    """two glyphs pulled together by d (fraction of the advance) each"""
    s2 = s if s2 is None else s2
    return s.move(-m.W + d * m.W, 0) | s2.move(-d * m.W, 0)


@g("ampersand_ampersand.liga")
def lig_and_(m):
    return _pair(m, ampersand_(m), 0.13)


@g("bar_bar.liga")
def lig_or_(m):
    return _pair(m, bar_(m), 0.19)


@g("question_question.liga")
def lig_qq_(m):
    return _pair(m, question_(m), 0.09)


@g("plus_plus.liga")
def lig_inc_(m):
    v = (m.W - 2 * m.OL) / 2
    w = m.sw * 0.95
    d = 0.055 * m.W
    s = obar(m, m.axis, -m.W + m.OL, m.W - m.OL)
    for cx in (-m.W / 2 + d, m.W / 2 - d):
        s = s | rect(cx - w / 2, m.axis - v, cx + w / 2, m.axis + v)
    return s


@g("hyphen_hyphen.liga")
def lig_dec_(m):
    gap = 0.075 * m.W
    return obar(m, m.axis, -m.W + m.OL + 0.02 * m.W, -gap / 2) | obar(m, m.axis, gap / 2, m.W - m.OL - 0.02 * m.W)


@g("colon_colon.liga")
def lig_scope_(m):
    return _pair(m, colon_(m), 0.11)


@g("slash_slash.liga")
def lig_comment_(m):
    return _pair(m, slash_(m), 0.085)


@g("slash_asterisk.liga")
def lig_comment_open_(m):
    return _pair(m, slash_(m), 0.065, asterisk_(m))


@g("asterisk_slash.liga")
def lig_comment_close_(m):
    return _pair(m, asterisk_(m), 0.065, slash_(m))


@g("bar_greater.liga")
def lig_pipe_(m):
    return _pair(m, bar_(m), 0.11, greater_(m))


@g("less_bar.liga")
def lig_pipe_back_(m):
    return _pair(m, less_(m), 0.11, bar_(m))


@g("colon_equal.liga")
def lig_assign_(m):
    # the colon is lifted onto the operator axis so that its dots sit level with the two bars
    return colon_(m).move(-m.W + 0.07 * m.W, m.axis - m.xh / 2) | equal_(m)


@g("asterisk_asterisk.liga")
def lig_power_(m):
    return _pair(m, asterisk_(m), 0.07)


@g("question_period.liga")
def lig_optional_(m):
    return _pair(m, question_(m), 0.075, period_(m))


@g("plus_equal.liga")
def lig_plus_equal_(m):
    return _pair(m, plus_(m), 0.065, equal_(m))


@g("hyphen_equal.liga")
def lig_minus_equal_(m):
    return _pair(m, hyphen_(m), 0.065, equal_(m))


@g("asterisk_equal.liga")
def lig_times_equal_(m):
    return _pair(m, asterisk_(m), 0.065, equal_(m))


# --------------------------------------------------------------------------
# stylistic alternates
# --------------------------------------------------------------------------
@g("zero.ss03")
def zero_plain_(m):
    return zero_ring(m)[0]


@g("l.ss04")
def l_flat_(m):
    """l with a flat foot (the construction of i at ascender height)"""
    sw, hw, a, b, L, R, xc = _lc(m)
    xs = xc + 0.012 * m.W - a
    return vstem(xs, 0, m.asc, sw) | _rect(L + 0.075 * m.W, m.asc - hw, xs + 2, m.asc) | _rect(L + 0.02 * m.W, 0, R - 0.02 * m.W, hw)


@g("zero.zero")
def zero_slashed_(m):
    return zero_ring(m)[0] | zero_slash(m)


@g("a.ss02")
@ital(it.a_)
def a_single_(m):
    sw, hw, a, b, L, R, xc = _lc(m)
    return vstem(R - sw, 0, m.xh, sw) | bowl(m, m.W - R, m.W - (L - m.rnd), 0, m.xh, sw, hw).flip_x(xc)


A_ACCENTED = ["agrave", "aacute", "acircumflex", "atilde", "adieresis", "aring", "amacron", "abreve"]


def _reg_a_alternates():
    for name in A_ACCENTED:
        mark = name[1:]
        g(name + ".ss02")(lambda m, mark=mark: Composite("a.ss02", mark + "comb"))

    @g("aogonek.ss02")
    def aogonek_alt_(m):
        return a_single_(m) | ogonek_shape(m, m.R - m.a * 0.55)


_reg_a_alternates()

SS02 = [("a", "a.ss02")] + [(n, n + ".ss02") for n in A_ACCENTED] + [("aogonek", "aogonek.ss02")]
@g("y.ss05")
def y_squared_alt_(m):
    return y_squared_(m)


Y_ACCENTED = ["yacute", "ydieresis", "ycircumflex"]
for _name in Y_ACCENTED:
    g(_name + ".ss05")(lambda m, mark=_name[1:]: Composite("y.ss05", mark + "comb"))

SS03 = [("zero", "zero.ss03")]
SS05 = [("y", "y.ss05")] + [(n, n + ".ss05") for n in Y_ACCENTED]
SS04 = [("l", "l.ss04")]

g("q.ss06")(lambda m: q_plain_(m))
g("m.ss07")(lambda m: m_full_(m))
SS06 = [("q", "q.ss06")]
SS07 = [("m", "m.ss07")]

# tag, name shown by applications, substitutions.  Numbers are never reused: ss01 was the
# dotted zero until it became the default in 1.300; the slashed zero is the 'zero' feature.
STYLISTIC_SETS = [("ss02", "Single-storey a", SS02),
                  ("ss03", "Plain zero", SS03),
                  ("ss04", "Flat-foot l", SS04),
                  ("ss05", "Squared y", SS05),
                  ("ss06", "Plain q", SS06),
                  ("ss07", "Long-leg m", SS07)]


# --------------------------------------------------------------------------
# feature code
# --------------------------------------------------------------------------
def feature_code() -> str:
    out = ["# Varcoda Mono OpenType features (generated by scripts/fontsrc/glyphs_liga.py)", "",
           "languagesystem DFLT dflt;", "languagesystem latn dflt;", ""]
    out.append("# Programming ligatures.  They live in 'calt' so the usual editor switches")
    out.append("# (VS Code editor.fontLigatures, JetBrains 'Enable ligatures', terminal")
    out.append("# font features) turn them on and off.  All glyphs keep one cell per character.")
    out.append("feature calt {")
    for lig, seq, ignores in LIGATURES:
        n = len(seq)
        name = lig.replace(".liga", "").replace("_", "")[:28]
        name = "lig_" + lig.replace(".liga", "")
        out.append("    lookup %s {" % name)
        # never touch longer runs of the same character
        out.append("        ignore sub %s %s' %s;" % (seq[0], seq[0], " ".join(seq[1:])))
        out.append("        ignore sub %s' %s %s;" % (seq[0], " ".join(seq[1:]), seq[-1]))
        for ig in ignores:
            out.append("        ignore sub %s;" % ig)
        for i in range(n - 1, 0, -1):
            before = " ".join(["LIG"] * i)
            after = " ".join(seq[i + 1:])
            target = lig if i == n - 1 else "LIG"
            out.append("        sub %s %s'%s by %s;" % (before, seq[i], (" " + after) if after else "", target))
        out.append("        sub %s' %s by LIG;" % (seq[0], " ".join(seq[1:])))
        out.append("    } %s;" % name)
    out.append("} calt;")
    out.append("")
    out.append("# Slashed zero: the registered feature for it (CSS font-variant-numeric: slashed-zero).")
    out.append("feature zero {")
    out.append("    sub zero by zero.zero;")
    out.append("} zero;")
    out.append("")
    for tag, label, subs in STYLISTIC_SETS:
        out.append("feature %s {" % tag)
        out.append('    featureNames { name "%s"; };' % label)
        for a, b in subs:
            out.append("    sub %s by %s;" % (a, b))
        out.append("} %s;" % tag)
        out.append("")
    return "\n".join(out)
