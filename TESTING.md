# Testing Varcoda Mono

## Run everything

```sh
pip install -r requirements-dev.txt
python -m pytest tests                       # 570 tests, about 20 s
python tests/font-validation/validate.py     # + fontbakery and ufolint, writes tests/font-validation/REPORT.md
```

Optional tools: `fontbakery` and `ufolint` (for `validate.py`), `fontconfig` (`fc-scan`) and Chrome or Chromium
(tests that need them are skipped when they are missing).

## What is checked

| File | Scope |
| --- | --- |
| `tests/font-validation/test_fonts.py` | upright fonts: tables, advance widths, vertical metrics, alignment zones, cell bounds, box-drawing joins, Unicode coverage, glyph names, duplicate and unreachable glyphs, contour direction, outline debris, names and style linking, weight order, look-alike outlines, operator alignment, punctuation size, every ligature on and off, long runs, random operator strings, stylistic sets, web fonts, OpenType Sanitizer, hinted advances 8–32 ppem, fontconfig, UFO sources vs binaries, reproducible build |
| `tests/font-validation/test_italics.py` | italic fonts: monospacing, italic angle, caret slope, style bits, style linking, STAT, same line box and character set as the upright, slant applied to letters and not to box drawing / arrows / Powerline, the italic `a` `f` `y`, cell overflow limits, ligatures and sets, hinted advances, fontconfig slant, OpenType Sanitizer |
| `tests/rendering-tests/test_rendering.py` | FreeType hinted bitmaps at 12–16 px: grid alignment, baseline and x-height consistency, look-alike pairs, `rn`/`cl` not fusing, ligatures inside their cells, box-drawing seams; headless Chromium with the web fonts and with the installed fonts |

## Visual test material (all rendered from the compiled fonts)

| File | Use |
| --- | --- |
| `assets/test-sheet-dark.png`, `-light.png` | the fixed sheet: `0O0o 1lI\|i 5S 8B 2Z rn/m cl/d`, `illinois immune millimeter minimum`, the PHP and JavaScript lines, brackets, punctuation and operators, an italic comment, alphabets, accents and box drawing at 10, 11, 12, 13, 14, 16 and 18 px. Same text, leading and colours every time |
| `specimens/code-samples.png` | PHP, Drupal PHP, JavaScript, TypeScript, Python, JSON, YAML, HTML, CSS, SQL, Bash, PowerShell |
| `tests/visual-regression/before-after-*.png` | current Regular against the archived 1.000 at the same seven sizes |
| `tests/rendering-tests/index.html` | self-contained page (fonts embedded) for a real browser: waterfalls, look-alikes, feature toggles |
| `assets/comparison.png` | next to JetBrains Mono, Fira Code and Iosevka (`docs/COMPARISON.md`) |

Rendering conditions for the PNGs: HarfBuzz shaping, FreeType greyscale with the fonts' own hinting, integer
pixel sizes, no subpixel positioning. They show what a Linux desktop shows.

## Testing on your own machine

This is the part automation here could not do. On Windows:

1. Install the ten `.ttf` files from `fonts/` and restart the application.
2. Open `tests/rendering-tests/index.html` in Edge or Chrome.
3. In VS Code and Windows Terminal, at 12, 13 and 14 px, light and dark theme, check: `0O 1lI|`, the dots of
   `. , : ;`, backtick against apostrophe, box-drawing joins, an italic comment, and Bold.
4. Compare with `assets/test-sheet-dark.png`. If something differs for the worse, open a *Rendering issue*
   with a screenshot at 100 % zoom.

## Known gaps

No automated or manual run on Windows or macOS; no editor was driven; the CI workflows in `.github/` have not
run; Nerd Font builds and a variable font do not exist, so there is nothing to test for them.
