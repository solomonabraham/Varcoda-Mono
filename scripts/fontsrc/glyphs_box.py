"""Box drawing (U+2500-257F) and block elements (U+2580-259F).

These glyphs fill the whole character cell: 0..600 horizontally and the full
line box (LINE_DESC..LINE_ASC) vertically, plus a small overshoot on every
side that touches the cell boundary, so they join seamlessly when the
application uses the font's own line height - also when it rounds the cell
up to whole pixels."""
from __future__ import annotations

from .geom import BIG, Shape, pline, poly, rect, round_path, stroke
from .kit import g, glyph_name
from .params import BOX_OVER_X, BOX_OVER_Y, LINE_ASC, LINE_DESC


def true_cell(m):
    """the character cell proper: (x0, y0, x1, y1)"""
    return 0, LINE_DESC * m.s, m.W, LINE_ASC * m.s


def cell(m):
    """(x0, y0, x1, y1, cx, cy, light, heavy): the cell *including* the
    overshoot that lets neighbouring cells overlap; the centre is that of the
    true cell"""
    tx0, ty0, tx1, ty1 = true_cell(m)
    t = round(m.lerp(56, 104))
    ox, oy = BOX_OVER_X * m.s, BOX_OVER_Y * m.s
    return tx0 - ox, ty0 - oy, tx1 + ox, ty1 + oy, m.W / 2, (ty0 + ty1) / 2, t, round(t * m.lerp(2.3, 1.9))


# arms: up, right, down, left ; 0 none, 1 light, 2 heavy, 3 double
ARMS = {
    0x2500: "0101", 0x2501: "0202", 0x2502: "1010", 0x2503: "2020",
    0x250C: "0110", 0x250D: "0210", 0x250E: "0120", 0x250F: "0220",
    0x2510: "0011", 0x2511: "0012", 0x2512: "0021", 0x2513: "0022",
    0x2514: "1100", 0x2515: "1200", 0x2516: "2100", 0x2517: "2200",
    0x2518: "1001", 0x2519: "1002", 0x251A: "2001", 0x251B: "2002",
    0x251C: "1110", 0x251D: "1210", 0x251E: "2110", 0x251F: "1120",
    0x2520: "2120", 0x2521: "2210", 0x2522: "1220", 0x2523: "2220",
    0x2524: "1011", 0x2525: "1012", 0x2526: "2011", 0x2527: "1021",
    0x2528: "2021", 0x2529: "2012", 0x252A: "1022", 0x252B: "2022",
    0x252C: "0111", 0x252D: "0112", 0x252E: "0211", 0x252F: "0212",
    0x2530: "0121", 0x2531: "0122", 0x2532: "0221", 0x2533: "0222",
    0x2534: "1101", 0x2535: "1102", 0x2536: "1201", 0x2537: "1202",
    0x2538: "2101", 0x2539: "2102", 0x253A: "2201", 0x253B: "2202",
    0x253C: "1111", 0x253D: "1112", 0x253E: "1211", 0x253F: "1212",
    0x2540: "2111", 0x2541: "1121", 0x2542: "2121", 0x2543: "2112",
    0x2544: "2211", 0x2545: "1122", 0x2546: "1221", 0x2547: "2212",
    0x2548: "1222", 0x2549: "2122", 0x254A: "2221", 0x254B: "2222",
    0x2550: "0303", 0x2551: "3030",
    0x2552: "0310", 0x2553: "0130", 0x2554: "0330",
    0x2555: "0013", 0x2556: "0031", 0x2557: "0033",
    0x2558: "1300", 0x2559: "3100", 0x255A: "3300",
    0x255B: "1003", 0x255C: "3001", 0x255D: "3003",
    0x255E: "1310", 0x255F: "3130", 0x2560: "3330",
    0x2561: "1013", 0x2562: "3031", 0x2563: "3033",
    0x2564: "0313", 0x2565: "0131", 0x2566: "0333",
    0x2567: "1303", 0x2568: "3101", 0x2569: "3303",
    0x256A: "1313", 0x256B: "3131", 0x256C: "3333",
    0x2574: "0001", 0x2575: "1000", 0x2576: "0100", 0x2577: "0010",
    0x2578: "0002", 0x2579: "2000", 0x257A: "0200", 0x257B: "0020",
    0x257C: "0201", 0x257D: "1020", 0x257E: "0102", 0x257F: "2010",
}

# direction vectors and their perpendicular / opposite arm indices
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def junction(m, arms) -> Shape:
    x0, y0, x1, y1, cx, cy, t, T = cell(m)
    s = [int(c) for c in arms]
    width = {0: 0, 1: t, 2: T, 3: 3 * t}

    def arm_rect(i, w, ext):
        dx, dy = DIRS[i]
        if dx:                                   # horizontal arm
            edge = x1 if dx > 0 else x0
            inner = cx - dx * ext
            return rect(min(edge, inner), cy - w / 2, max(edge, inner), cy + w / 2)
        edge = y1 if dy > 0 else y0
        inner = cy - dy * ext
        return rect(cx - w / 2, min(edge, inner), cx + w / 2, max(edge, inner))

    solid_double, hollow, plain = Shape(), Shape(), Shape()
    for i in range(4):
        if not s[i]:
            continue
        perp = [s[(i + 1) % 4], s[(i + 3) % 4]]
        opp = s[(i + 2) % 4]
        perp_w = max(width[p] for p in perp)
        has_perp = any(perp)
        if s[i] == 3:
            ext = perp_w / 2 if has_perp else 0
            solid_double = solid_double | arm_rect(i, 3 * t, ext)
            if opp == 3 or 3 in perp:
                h_ext = t / 2
            elif has_perp:
                h_ext = -perp_w / 2
            else:
                h_ext = 0
            hollow = hollow | arm_rect(i, t, h_ext)
        else:
            w = width[s[i]]
            if perp == [3, 3] and not opp:
                ext = -t / 2                       # stop at the near line of a double through-road
            elif has_perp:
                ext = perp_w / 2
            else:
                ext = 0
            plain = plain | arm_rect(i, w, ext)
    return (solid_double - hollow) | plain


def _reg_junctions():
    for cp, arms in ARMS.items():
        g(glyph_name(cp), uni=cp)(lambda m, arms=arms: junction(m, arms))


_reg_junctions()


# dashes -----------------------------------------------------------------------
def dashes(m, n, heavy, vertical) -> Shape:
    _, _, _, _, cx, cy, t, T = cell(m)
    x0, y0, x1, y1 = true_cell(m)
    w = T if heavy else t
    out = Shape()
    length = (y1 - y0) if vertical else (x1 - x0)
    period = length / n
    dash = period * 0.62
    for i in range(n):
        a = (y0 if vertical else x0) + i * period + (period - dash) / 2
        if vertical:
            out = out | rect(cx - w / 2, a, cx + w / 2, a + dash)
        else:
            out = out | rect(a, cy - w / 2, a + dash, cy + w / 2)
    return out


for _cp, (_n, _heavy, _vert) in {0x2504: (3, 0, 0), 0x2505: (3, 1, 0), 0x2506: (3, 0, 1), 0x2507: (3, 1, 1),
                                 0x2508: (4, 0, 0), 0x2509: (4, 1, 0), 0x250A: (4, 0, 1), 0x250B: (4, 1, 1),
                                 0x254C: (2, 0, 0), 0x254D: (2, 1, 0), 0x254E: (2, 0, 1), 0x254F: (2, 1, 1)}.items():
    g(glyph_name(_cp), uni=_cp)(lambda m, n=_n, h=_heavy, v=_vert: dashes(m, n, h, v))


# rounded corners ----------------------------------------------------------------
def arc_corner(m, right, down) -> Shape:
    x0, y0, x1, y1, cx, cy, t, T = cell(m)
    r = 0.42 * m.W
    ex = x1 + 10 if right else x0 - 10
    ey = y0 - 10 if down else y1 + 10
    sk = round_path([(cx, ey), (cx, cy), (ex, cy)], r, r, 0.5523)
    return stroke(sk, t / 2, t / 2) & rect(x0, y0, x1, y1)


g(glyph_name(0x256D), uni=0x256D)(lambda m: arc_corner(m, True, True))
g(glyph_name(0x256E), uni=0x256E)(lambda m: arc_corner(m, False, True))
g(glyph_name(0x256F), uni=0x256F)(lambda m: arc_corner(m, False, False))
g(glyph_name(0x2570), uni=0x2570)(lambda m: arc_corner(m, True, False))


# diagonals ----------------------------------------------------------------------
def box_diag(m, rising) -> Shape:
    x0, y0, x1, y1, cx, cy, t, T = cell(m)
    dx, dy = (x1 - x0), (y1 - y0)
    p0 = (x0 - dx * 0.2, (y0 if rising else y1) - (dy * 0.2 if rising else -dy * 0.2))
    p1 = (x1 + dx * 0.2, (y1 if rising else y0) + (dy * 0.2 if rising else -dy * 0.2))
    return pline([p0, p1], t / 2, t / 2) & rect(x0, y0, x1, y1)


g(glyph_name(0x2571), uni=0x2571)(lambda m: box_diag(m, True))
g(glyph_name(0x2572), uni=0x2572)(lambda m: box_diag(m, False))
g(glyph_name(0x2573), uni=0x2573)(lambda m: box_diag(m, True) | box_diag(m, False))


# block elements -----------------------------------------------------------------
def block(m, fx0, fy0, fx1, fy1) -> Shape:
    """rectangle given in fractions of the cell (y from the bottom); sides
    lying on the cell boundary get the overshoot"""
    ex0, ey0, ex1, ey1 = cell(m)[:4]
    x0, y0, x1, y1 = true_cell(m)
    ax = ex0 if fx0 <= 0 else x0 + (x1 - x0) * fx0
    bx = ex1 if fx1 >= 1 else x0 + (x1 - x0) * fx1
    ay = ey0 if fy0 <= 0 else y0 + (y1 - y0) * fy0
    by = ey1 if fy1 >= 1 else y0 + (y1 - y0) * fy1
    return rect(ax, ay, bx, by)


BLOCKS = {0x2580: (0, .5, 1, 1), 0x2588: (0, 0, 1, 1), 0x2590: (.5, 0, 1, 1), 0x2594: (0, 7 / 8, 1, 1), 0x2595: (7 / 8, 0, 1, 1)}
for _i in range(1, 8):
    BLOCKS[0x2580 + _i] = (0, 0, 1, _i / 8)            # lower eighths
    BLOCKS[0x2590 - _i] = (0, 0, _i / 8, 1)            # left eighths: 258F = 1/8 ... 2589 = 7/8
for _cp, _f in BLOCKS.items():
    g(glyph_name(_cp), uni=_cp)(lambda m, f=_f: block(m, *f))

QUAD = {"ul": (0, .5, .5, 1), "ur": (.5, .5, 1, 1), "ll": (0, 0, .5, .5), "lr": (.5, 0, 1, .5)}
QUADS = {0x2596: ["ll"], 0x2597: ["lr"], 0x2598: ["ul"], 0x2599: ["ul", "ll", "lr"], 0x259A: ["ul", "lr"],
         0x259B: ["ul", "ur", "ll"], 0x259C: ["ul", "ur", "lr"], 0x259D: ["ur"], 0x259E: ["ur", "ll"],
         0x259F: ["ur", "ll", "lr"]}


def quadrants(m, parts) -> Shape:
    out = Shape()
    for p in parts:
        out = out | block(m, *QUAD[p])
    return out


for _cp, _parts in QUADS.items():
    g(glyph_name(_cp), uni=_cp)(lambda m, parts=_parts: quadrants(m, parts))


def shade(m, level) -> Shape:
    """dither patterns: 1 = light (25 %), 2 = medium (50 %), 3 = dark (75 %)"""
    ex0, ey0, ex1, ey1 = cell(m)[:4]
    x0, y0, x1, y1 = true_cell(m)
    cols, rows = 8, 16
    gw, gh = (x1 - x0) / cols, (y1 - y0) / rows
    ins = 0.0
    conts = []

    def sq(c, r, hole=False, inset=0.0):
        ax, ay = x0 + c * gw + inset, y0 + r * gh + inset
        bx, by = x0 + (c + 1) * gw - inset, y0 + (r + 1) * gh - inset
        pts = [(ax, ay), (bx, ay), (bx, by), (ax, by)]
        if hole:
            pts.reverse()
        return [("M", pts[0])] + [("L", p) for p in pts[1:]]

    def light(c, r):
        return r % 2 == 0 and (c + r // 2) % 2 == 0

    if level == 1:
        conts = [sq(c, r) for r in range(rows) for c in range(cols) if light(c, r)]
    elif level == 2:
        # horizontal runs would merge; use isolated squares on a checkerboard,
        # slightly inset so that corners do not touch
        conts = [sq(c, r, inset=gw * 0.035) for r in range(rows) for c in range(cols) if (c + r) % 2 == 0]
    else:
        conts = [[("M", (ex0, ey0)), ("L", (ex1, ey0)), ("L", (ex1, ey1)), ("L", (ex0, ey1))]]
        conts += [sq(c, r, hole=True, inset=gw * 0.02) for r in range(rows) for c in range(cols)
                  if light(c, r) and 0 < c < cols - 1 and 0 < r < rows - 1]
        # holes on the border are cut with booleans (they open the outline)
        s = Shape(conts)
        for r in range(rows):
            for c in range(cols):
                if light(c, r) and not (0 < c < cols - 1 and 0 < r < rows - 1):
                    s = s - rect(x0 + c * gw - (BIG if c == 0 else 0), y0 + r * gh - (BIG if r == 0 else 0),
                                 x0 + (c + 1) * gw + (BIG if c == cols - 1 else 0),
                                 y0 + (r + 1) * gh + (BIG if r == rows - 1 else 0))
        return s
    return Shape(conts)


for _cp, _lvl in {0x2591: 1, 0x2592: 2, 0x2593: 3}.items():
    g(glyph_name(_cp), uni=_cp)(lambda m, lvl=_lvl: shade(m, lvl))
