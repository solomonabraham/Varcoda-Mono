#!/usr/bin/env python3
"""Generate the specimen images from the compiled fonts.

    python3 scripts/make-specimens.py

Writes specimens/specimen.png and specimens/code-samples.png.  Everything is
rendered with the TTF files in fonts/ (HarfBuzz shaping + FreeType
rasterising), never from the drawing code, so the images show what the
released fonts really do.  Syntax colours come from Pygments.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from PIL import Image  # noqa: E402

from fontsrc.glyphs_liga import LIGATURES  # noqa: E402
from fontsrc.params import italic_style  # noqa: E402
from fontsrc.render import FontRenderer, to_image  # noqa: E402

# palette -------------------------------------------------------------------
BG = (19, 21, 26)
PANEL = (27, 30, 37)
RULE = (44, 49, 60)
FG = (216, 220, 229)
MUTED = (122, 131, 150)
ACCENT = (95, 208, 196)
C_KEYWORD = (242, 134, 152)
C_STRING = (166, 214, 132)
C_NUMBER = (242, 182, 112)
C_FUNC = (120, 182, 252)
C_TYPE = (242, 216, 132)
C_VAR = (196, 204, 255)
C_OP = (140, 204, 222)
C_COMMENT = (104, 114, 134)
C_TAG = (242, 134, 152)
C_ATTR = (242, 216, 132)

W = 1600
MARGIN = 72


BEFORE = os.path.join(ROOT, "tests", "baseline", "v1.300", "VarcodaMono-Italic.ttf")    # the slanted italic of 1.300


def font_path(style):
    return style if os.path.sep in style else os.path.join(ROOT, "fonts", "VarcodaMono-%s.ttf" % style)


_renderers = {}


def R(style, px, hinting=True) -> FontRenderer:
    key = (style, px, hinting)
    if key not in _renderers:
        _renderers[key] = FontRenderer(font_path(style), px, hinting=hinting)
    return _renderers[key]


class Page:
    """a growing canvas with a cursor"""

    def __init__(self, width=W, height=6000, bg=BG):
        self.cv = np.empty((height, width, 3), dtype=np.float32)
        self.cv[:] = np.array(bg, dtype=np.float32)
        self.y = 0
        self.width = width

    def text(self, x, baseline, s, style="Regular", px=28, color=FG, features=None, colors=None, hinting=True):
        r = R(style, px, hinting)
        r.draw(self.cv, x, baseline, s, color, features if features is not None else {"calt": False}, colors)
        return r

    def line(self, s, style="Regular", px=28, color=FG, features=None, colors=None, x=MARGIN, lead=1.42, hinting=True):
        r = R(style, px, hinting)
        lh = round(px * lead)
        base = self.y + (lh - (r.ascent + r.descent)) // 2 + r.ascent
        self.text(x, base, s, style, px, color, features, colors, hinting)
        self.y += lh
        return r

    def gap(self, h):
        self.y += h

    def rule(self):
        self.cv[self.y:self.y + 2, MARGIN:self.width - MARGIN] = np.array(RULE, dtype=np.float32)
        self.y += 2

    def label(self, s):
        self.gap(46)
        self.line(s.upper(), "Medium", 20, ACCENT, lead=1.3)
        self.gap(6)
        self.rule()
        self.gap(22)

    def panel(self, y0, y1, x0=MARGIN - 28, x1=None, color=PANEL):
        x1 = self.width - MARGIN + 28 if x1 is None else x1
        self.cv[y0:y1, x0:x1] = np.array(color, dtype=np.float32)

    def paste(self, img: Image.Image, x):
        arr = np.asarray(img.convert("RGB"), dtype=np.float32)
        h, w = arr.shape[:2]
        self.cv[self.y:self.y + h, x:x + w] = arr
        self.y += h

    def save(self, path):
        img = to_image(self.cv[:self.y + MARGIN])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path, optimize=True)
        return img.size


# ---------------------------------------------------------------------------
# syntax colouring
# ---------------------------------------------------------------------------
def colourise(code: str, lexer_name: str):
    """-> list of (line, [colour per character])"""
    from pygments import lex
    from pygments.lexers import get_lexer_by_name
    from pygments.token import Token as T

    def colour(tok):
        table = [
            (T.Comment, C_COMMENT), (T.Literal.String.Doc, C_COMMENT), (T.Keyword.Type, C_TYPE), (T.Keyword.Constant, C_NUMBER), (T.Keyword, C_KEYWORD),
            (T.Literal.String.Interpol, C_OP), (T.Literal.String, C_STRING), (T.Literal.Number, C_NUMBER),
            (T.Name.Function, C_FUNC), (T.Name.Class, C_TYPE), (T.Name.Builtin, C_FUNC), (T.Name.Decorator, C_FUNC),
            (T.Name.Tag, C_TAG), (T.Name.Attribute, C_ATTR), (T.Name.Variable, C_VAR), (T.Name.Entity, C_NUMBER),
            (T.Name.Constant, C_NUMBER), (T.Name.Namespace, C_TYPE), (T.Name.Exception, C_TYPE), (T.Name.Property, C_FUNC),
            (T.Operator.Word, C_KEYWORD), (T.Operator, C_OP), (T.Punctuation, C_OP),
        ]
        for ttype, col in table:
            if tok in ttype:
                return col
        return FG

    opts = {"startinline": False} if lexer_name == "php" else {}
    lexer = get_lexer_by_name(lexer_name, stripnl=False, ensurenl=False, **opts)
    lines, cur, cols = [], "", []
    for tok, value in lex(code, lexer):
        col = colour(tok)
        for ch in value:
            if ch == "\n":
                lines.append((cur, cols))
                cur, cols = "", []
            else:
                cur += ch
                cols.append(col)
    lines.append((cur, cols))
    return lines


SAMPLES = [
    ("PHP", "php", """<?php

final class ApplicationService
{
    public function execute(array $options): bool
    {
        $enabled = $options['enabled'] ?? false;

        if ($enabled !== true) {
            return false;
        }

        return true;
    }
}"""),
    ("JavaScript", "javascript", """// Debounced search with an abort signal
const cache = new Map();

export async function search(query, { limit = 20, signal } = {}) {
  if (query.length <= 2 || cache.has(query)) return cache.get(query) ?? [];
  const url = `/api/items?q=${encodeURIComponent(query)}&limit=${limit}`;
  const res = await fetch(url, { signal });
  if (!res.ok && res.status !== 304) throw new Error(`HTTP ${res.status}`);
  const items = (await res.json()).filter((x) => x.score >= 0.5);
  cache.set(query, items);
  return items.map(({ id, title }) => ({ id, label: title ?? "untitled" }));
}"""),
    ("Python", "python", """from dataclasses import dataclass, field

@dataclass(frozen=True)
class Vector:
    x: float = 0.0
    y: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def norm(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

if __name__ == "__main__":
    total = sum((Vector(i, i * 2) for i in range(10)), Vector())
    print(f"{total.norm():.3f}")  # 0O 1lI| 5S 8B"""),
    ("JSON", "json", """{
  "name": "varcoda-mono",
  "version": "1.0.0",
  "private": false,
  "weights": [300, 400, 500, 600, 700],
  "metrics": { "unitsPerEm": 1000, "advance": 600, "xHeight": 540 },
  "features": { "calt": true, "zero": false, "ss02": null }
}"""),
    ("HTML", "html", """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Varcoda Mono &mdash; specimen</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body class="dark">
    <main id="app" data-size="14">
      <h1>Hello, <em>world</em>!</h1>
      <button type="button" disabled>Run &rarr;</button>
    </main>
  </body>
</html>"""),
    ("CSS", "css", """@font-face {
  font-family: "Varcoda Mono";
  src: url("fonts/VarcodaMono-Regular.ttf") format("truetype");
  font-weight: 400;
}

:root { --accent: #5fd0c4; --radius: 6px; }

pre > code, .token.comment:not([hidden]) {
  font: 400 14px/1.5 "Varcoda Mono", monospace;
  font-feature-settings: "calt" 0, "zero" 1;
  color: rgb(214 218 227 / 92%);
  border-left: 2px solid var(--accent);
  border-radius: calc(var(--radius) * 2);
}"""),
    ("TypeScript", "typescript", """type Result<T> = { ok: true; value: T } | { ok: false; error: string };

export function parse<T>(raw: string, guard: (v: unknown) => v is T): Result<T> {
  try {
    const value: unknown = JSON.parse(raw);
    return guard(value) ? { ok: true, value } : { ok: false, error: "shape" };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}
const ids = items?.map((item) => item.id ?? fallback) ?? [];
"""),
    ("Drupal (PHP)", "php", """<?php

declare(strict_types=1);

namespace Drupal\\mymodule\\Hook;

use Drupal\\Core\\Hook\\Attribute\\Hook;
use Drupal\\node\\NodeInterface;
use Psr\\Log\\LoggerInterface;

/**
 * Adds a reading time to article teasers.
 */
final class NodeHooks {

  public function __construct(
    private readonly ConfigFactoryInterface $configFactory,
    private readonly ?LoggerInterface $logger = NULL,
  ) {}

  #[Hook('node_view')]
  public function view(array &$build, NodeInterface $node, string $view_mode): void {
    $wpm = $this->configFactory->get('mymodule.settings')->get('wpm') ?? 220;
    $words = str_word_count($node->get('body')?->value ?? '');
    $build['reading_time'] = [
      '#markup' => $this->t('@min min read', ['@min' => intdiv($words, $wpm) ?: 1]),
      '#weight' => -10,
    ];
    $this->logger?->debug('Viewed @id', ['@id' => $node->id()]);
  }

}
"""),
    ("YAML", "yaml", """services:
  mymodule.importer:
    class: Drupal\\mymodule\\Importer
    arguments: ['@http_client', '@logger.channel.mymodule', '%app.root%']
    tags:
      - { name: event_subscriber, priority: 100 }
retries: 3          # 0 disables
timeout: 12.5
enabled: true
"""),
    ("Bash", "bash", """#!/usr/bin/env bash
set -euo pipefail
for f in "${SRC_DIR:-src}"/*.ttf; do
  name="$(basename "$f" .ttf)"
  [[ -s "$f" && "$name" != *Italic* ]] || continue
  printf '%-24s %6d bytes\\n' "$name" "$(stat -c %s "$f")" | tee -a build.log
done 2>/dev/null || { echo "failed: $?" >&2; exit 1; }
"""),
    ("PowerShell", "powershell", """$fonts = Get-ChildItem -Path "$env:LOCALAPPDATA\\Microsoft\\Windows\\Fonts" -Filter 'Varcoda*.ttf'
foreach ($font in $fonts) {
    if ($font.Length -gt 0 -and $font.Name -notmatch 'Italic') {
        Write-Host ("{0,-28} {1,8:N0} bytes" -f $font.Name, $font.Length)
    }
}
$total = ($fonts | Measure-Object -Property Length -Sum).Sum
"""),
    ("SQL", "sql", """SELECT u.id, u.email, COUNT(o.id) AS orders, SUM(o.total) AS revenue
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id AND o.status <> 'void'
WHERE u.created_at >= '2026-01-01' AND u.email LIKE '%@example.com'
GROUP BY u.id, u.email
HAVING SUM(o.total) > 1000.00
ORDER BY revenue DESC
LIMIT 25;"""),
]


def code_block(page: Page, title, lexer, code, px=27, style="Regular", features=None, note=None):
    lines = colourise(code, lexer)
    r = R(style, px)
    lh = round(px * 1.5)
    page.gap(40)
    head_y = page.y
    page.line(title.upper() + ("   " + note if note else ""), "Medium", 20, ACCENT, lead=1.3)
    page.gap(14)
    y0 = page.y
    y1 = y0 + lh * len(lines) + 44
    page.panel(y0, y1)
    page.gap(22)
    gutter = len(str(len(lines)))
    for i, (text, cols) in enumerate(lines, 1):
        base = page.y + (lh - (r.ascent + r.descent)) // 2 + r.ascent
        page.text(MARGIN, base, str(i).rjust(gutter), style, px, (72, 80, 98))
        # comments and keywords go in the italic, as an editor theme sets them; both passes keep every
        # character in its own cell, so the two styles share one grid
        slanted = [c in (C_COMMENT, C_KEYWORD) for c in cols]
        for flag, st in ((False, style), (True, italic_style(style))):
            run = "".join(ch if sl == flag else " " for ch, sl in zip(text, slanted))
            if run.strip():
                page.text(MARGIN + (gutter + 2) * r.cell, base, run, st, px, FG, features, cols)
        page.y += lh
    page.gap(22)


def build_code_samples(path):
    page = Page(height=12000)
    page.gap(64)
    page.line("Varcoda Mono", "Bold", 76, FG, lead=1.2)
    page.line("Code samples · Regular, comments and keywords in Italic · ligatures off (the default)", "Regular", 26, MUTED)
    for title, lexer, code in SAMPLES:
        code_block(page, title, lexer, code)
    # the same code with the optional features enabled
    js = SAMPLES[1][2].split("\n")
    snippet = "\n".join(js[4:10])
    code_block(page, "JavaScript", "javascript", snippet, features={"calt": True},
               note="with ligatures enabled (calt)")
    code_block(page, "Drupal (PHP)", "php", "<?php\n" + "\n".join(SAMPLES[7][2].split("\n")[20:30]), features={"calt": True},
               note="with ligatures enabled (calt)")
    code_block(page, "PHP", "php", SAMPLES[0][2], style="Bold", note="Bold 700")
    page.gap(30)
    return page.save(path)


# ---------------------------------------------------------------------------
# main specimen
# ---------------------------------------------------------------------------
def family_facts():
    f = TTFont(font_path("Regular"))
    return len(f.getGlyphOrder()), len(f.getBestCmap()), f["name"].getDebugName(5)


def build_specimen(path):
    glyphs, chars, version = family_facts()
    page = Page(height=11000)
    page.gap(70)
    page.line("Varcoda Mono", "Bold", 132, FG, lead=1.12)
    page.gap(6)
    page.line("A geometric, technical typeface for code.", "Regular", 36, MUTED)
    page.line("Five weights from Light to Bold, each with a written italic · %d glyphs · one 600-unit cell" % glyphs,
              "Regular", 26, MUTED)

    page.label("Five weights, each with its italic")
    for style, wc in (("Light", 300), ("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)):
        r = page.line("%-9s%d  fn main() -> Result<(), Error> {}" % (style, wc), style, 32, FG, lead=1.5)
        page.y -= round(32 * 1.5)
        page.line("// quietly, after all", italic_style(style), 32, MUTED, x=MARGIN + 50 * r.cell, lead=1.5)

    page.label("Uppercase")
    page.line("ABCDEFGHIJKLM", "Regular", 86, FG, lead=1.22, hinting=False)
    page.line("NOPQRSTUVWXYZ", "Regular", 86, FG, lead=1.22, hinting=False)
    page.label("Lowercase")
    page.line("abcdefghijklm", "Regular", 86, FG, lead=1.22, hinting=False)
    page.line("nopqrstuvwxyz", "Regular", 86, FG, lead=1.22, hinting=False)
    page.label("Numbers")
    page.line("0123456789", "Regular", 86, FG, lead=1.22, hinting=False)

    page.label("Regular and Italic")
    for st in ("Regular", "Italic"):
        page.line("abcdefghijklmnopqrstuvwxyz", st, 56, FG, lead=1.3, hinting=False)
    page.gap(12)
    page.line("The italic is written, not slanted: stems leave the baseline to the right, arches", "Regular", 26, MUTED)
    page.line("branch out of their stem, bowls run back up into it, and f descends. Capitals,", "Regular", 26, MUTED)
    page.line("figures and signs are sloped by 9.5°; box drawing and arrows stay upright.", "Regular", 26, MUTED)
    page.gap(12)
    for st in ("Regular", "Italic"):
        page.line("handful of quick fixes: adjust, and unify buffering", st, 44, FG, lead=1.45)
    for st in ("Regular", "Italic"):
        page.line("ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 {}[]()<>?!&@", st, 36, MUTED, lead=1.45)

    page.label("Programming punctuation")
    for s in ("{} [] () <> != !== == === => -> && || ??", "++ -- += -= *= /* */ // # @ $ % ^ & * _ ~ ` | \\",
              ": ; , . ? ! ' \" + - = / < > 0xFF 1e-9 a[i] f(x)"):
        page.line(s, "Regular", 44, FG, lead=1.5)

    page.label("Told apart at a glance")
    r = R("Regular", 104, False)
    groups = ["0O", "1lI|", "5S", "8B", "2Z", "g9q"]
    x = MARGIN
    base = page.y + 118
    for gstr in groups:
        page.text(x, base, gstr, "Regular", 104, FG, hinting=False)
        x += (len(gstr)) * r.cell + 46
    page.y += 160
    page.line("dotted zero · hooked l, flagged 1, slab I · open-tail g · flat-top 5", "Regular", 26, MUTED)
    page.line("` ' \"   . , : ;   - _ ~   ( [ { < | > } ] )   rn m  cl d", "Regular", 44, FG, lead=1.5)

    page.label("Regular versus Bold")
    sample = "const total = items.filter(x => x.ok).length;"
    page.line(sample, "Regular", 44, FG, lead=1.5)
    page.line(sample, "Bold", 44, FG, lead=1.5)

    page.label("Optional ligatures — every glyph keeps its cell")
    px = 44
    r = R("Regular", px)
    rev = {v: chr(k) for k, v in TTFont(font_path("Regular")).getBestCmap().items()}
    pairs = ["".join(rev[g] for g in seq) for _, seq, _ in LIGATURES]            # all of them, straight from the feature code
    cols = 6
    colw = (W - 2 * MARGIN) // cols
    lh = round(px * 1.55)
    for i, pr in enumerate(pairs):
        cx = MARGIN + (i % cols) * colw
        base = page.y + (i // cols) * lh + r.ascent + 8
        page.text(cx, base, pr, "Regular", px, MUTED, {"calt": False})
        page.text(cx + (len(pr) + 1) * r.cell, base, pr, "Regular", px, FG, {"calt": True})
    page.y += ((len(pairs) + cols - 1) // cols) * lh + 10
    page.line("grey: feature off (plain glyphs) · white: calt on", "Regular", 26, MUTED)
    page.gap(10)
    page.line("if (a !== b && c >= d) return x ?? y;   // off", "Regular", 40, FG, {"calt": False}, lead=1.5)
    page.line("if (a !== b && c >= d) return x ?? y;   // calt on", "Regular", 40, FG, {"calt": True}, lead=1.5)
    page.line("$name = $node?->getOwner()?->label() ?? 'n/a'; $n *= 2;", "Regular", 40, FG, {"calt": True}, lead=1.5)

    page.label("Alternates")
    page.line("0 a á   default", "Regular", 44, FG, lead=1.45)
    page.line("0 a á   zero slashed zero · ss02 single-storey a", "Regular", 44, FG, {"calt": False, "zero": True, "ss02": True}, lead=1.45)

    page.label("Before and after — the italic of 1.300 (grey) and of %s" % version.replace("Version ", ""))
    if os.path.isfile(BEFORE):
        r = R("Italic", 76, False)
        for row in ("adfhi", "kmnpq", "ruy"):
            base = page.y + 104
            for i, ch in enumerate(row):
                x = MARGIN + i * 6 * r.cell
                page.text(x, base, ch, BEFORE, 76, MUTED, hinting=False)
                page.text(x + 2 * r.cell, base, ch, "Italic", 76, FG, hinting=False)
            page.y += 150
        for st, col in ((BEFORE, MUTED), ("Italic", FG)):
            page.line("// a handful of quick fixes: adjust, then unify buffering", st, 40, col, lead=1.5)
        for st, col in ((BEFORE, MUTED), ("Italic", FG)):
            page.line("// a handful of quick fixes: adjust the minimum, unify buffering (14 px, hinted)", st, 14, col, lead=1.7)
        page.gap(8)
        page.line("n *= 2;  new ligature, drawn like += and -=", "Regular", 40, FG, {"calt": True}, lead=1.5)
        page.line("The upright styles are unchanged, point for point.", "Regular", 26, MUTED)

    page.label("Small sizes — actual pixels, hinted (FreeType)")
    text = "for (let i = 0; i < items.length; i++) { total += items[i].price * 1.07; }  // 0O 1lI| {}[]()"
    for px in (12, 13, 14, 15, 16):
        page.line("%dpx  %s" % (px, text), "Regular", px, FG, lead=1.7)
    page.gap(10)
    for px in (12, 14, 16):
        page.line("%dpx  %s" % (px, text), "Bold", px, FG, lead=1.7)
    for px in (12, 13, 14, 16):
        page.line("%dpx  // %s" % (px, "walk the tree and adjust every heading, quietly; then unify buffering upstream (0O 1lI|)"),
                  "Italic", px, FG, lead=1.7)
    page.gap(18)
    page.line("13px Regular, magnified 4×", "Regular", 20, MUTED)
    page.gap(8)
    strip = Page(width=(W - 2 * MARGIN) // 4, height=40, bg=PANEL)
    strip.gap(4)
    strip.line("if (x !== 0O) { l1I| }  $a->b ?? [c];", "Regular", 13, FG, x=6, lead=1.7)
    img = to_image(strip.cv[:30])
    page.paste(img.resize((img.width * 4, img.height * 4), Image.NEAREST), MARGIN)

    page.label("Terminal — box drawing fills the line box")
    px = 30
    r = R("Regular", px)
    term = ["PS C:\\src\\varcoda-mono> python scripts\\build-fonts.py",
            "┌──────────┬────────┬─────────────┐   ╔═══════════╗   ╭────────╮",
            "│ Style    │ Glyphs │ Status      │   ║ ▁▂▃▄▅▆▇█  ║   │ 100 %  │",
            "├──────────┼────────┼─────────────┤   ║ ░░▒▒▓▓██  ║   │ ✓ done │",
            "│ Regular  │    %d │ ✓ hinted    │   ╚═══════════╝   ╰────────╯" % glyphs,
            "│ Bold     │    %d │ ✓ hinted    │   ← ↑ → ↓  ≠ ≤ ≥  λ π ∑" % glyphs,
            "└──────────┴────────┴─────────────┘"]
    lh = r.ascent + r.descent                      # the font's own line height: boxes must connect
    y0 = page.y
    page.panel(y0, y0 + lh * len(term) + 44)
    page.gap(22)
    for i, s in enumerate(term):
        page.text(MARGIN, page.y + r.ascent, s, "Regular", px, FG if i else C_STRING)
        page.y += lh
    page.gap(22)

    page.label("Languages")
    page.line("Zażółć gęślą jaźń · Příliš žluťoučký kůň · Größe", "Regular", 40, FG, lead=1.5)
    page.line("Ça coûte 12 € · ¿Qué tal? · Ærøskøbing · İstanbul", "Regular", 40, FG, lead=1.5)

    page.gap(46)
    page.rule()
    page.gap(18)
    page.line("%s · %d glyphs · %d characters · SIL Open Font License 1.1" % (version, glyphs, chars), "Regular", 22, MUTED)
    return page.save(path)


def main():
    out = os.path.join(ROOT, "specimens")
    print("specimen.png     ", build_specimen(os.path.join(out, "specimen.png")))
    print("code-samples.png ", build_code_samples(os.path.join(out, "code-samples.png")))


if __name__ == "__main__":
    main()
