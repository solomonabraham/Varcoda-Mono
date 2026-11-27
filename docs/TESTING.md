# Testing Varcoda Mono

## Run everything

```sh
pip install -r requirements-dev.txt afdko==5.0.1
python -m pytest tests                       # 605 tests, under a minute
python tests/font-validation/validate.py     # + fontbakery and ufolint, writes tests/font-validation/REPORT.md
```

`validate.py` needs `pip install fontbakery==1.1.0 ufolint`. Tests that need `fontconfig` (`fc-scan`) or a Chrome
that returns its page to the console are skipped where those are missing: on Ubuntu, as in CI, none is skipped; on
Windows 8 are, because `chrome.exe` detaches from the console. Open `tests/rendering-tests/index.html`
there instead.

## What is checked

| File | Scope |
| --- | --- |
| `tests/font-validation/test_fonts.py` | upright fonts: tables, advance widths, vertical metrics, alignment zones, cell bounds, box-drawing joins, Unicode coverage, glyph names, duplicate and unreachable glyphs, contour direction, outline debris, names and style linking, weight order, look-alike outlines, operator alignment, punctuation size, every ligature on and off, long runs, random operator strings, stylistic sets, web fonts, OpenType Sanitizer, hinted advances 8–32 ppem, fontconfig, UFO sources vs binaries, reproducible build |
| `tests/font-validation/test_italics.py` | italic fonts: monospacing, italic angle, caret slope, style bits, style linking, STAT, same line box and character set as the upright, slant applied to letters and not to box drawing / arrows / Powerline, the written letterforms (exit strokes, the descending `f`, alternates equal to the defaults), clean and consistent outlines in all five weights, cell overflow limits, ligatures and sets, hinted advances, fontconfig slant, OpenType Sanitizer |
| `tests/rendering-tests/test_rendering.py` | FreeType hinted bitmaps at 12–16 px: grid alignment, baseline and x-height consistency, look-alike pairs, `rn`/`cl` not fusing, ligatures inside their cells, box-drawing seams; headless Chromium with the web fonts and with the fonts installed into a scratch directory |
| `tests/test_project.py` | the repository around the fonts: every link, heading anchor and file name in the documentation resolves; JSON, JSONC and TOML examples parse and spell the family name correctly; the release archives contain exactly what the README lists, their stylesheet finds its files, and they are deterministic |

## In CI

| Workflow | On | Does |
| --- | --- | --- |
| *Build* | every push and pull request | builds all fonts from source on Ubuntu and **fails** if a committed font differs from the fresh build |
| *Validate* | every push and pull request | the test-suite, the interpolation count, fontbakery and ufolint; uploads the report |
| *Release* | a version tag | rebuilds, tests, packages, and drafts the release (`RELEASING.md`) |

## Visual test material (all rendered from the compiled fonts)

| File | Use |
| --- | --- |
| `assets/test-sheet-dark.png`, `-light.png` | the fixed sheet: `0O0o 1lI\|i 5S 8B 2Z rn/m cl/d`, `illinois immune millimeter minimum`, the PHP and JavaScript lines, brackets, punctuation and operators, an italic comment, alphabets, accents and box drawing at 10, 11, 12, 13, 14, 16 and 18 px. Same text, leading and colours every time |
| `specimens/specimen.png` | alphabets, Regular and Italic side by side, every ligature off and on, the italic before and after 1.4.0, small sizes |
| `specimens/code-samples.png` | PHP, Drupal PHP, JavaScript, TypeScript, Python, JSON, YAML, HTML, CSS, SQL, Bash, PowerShell; comments and keywords in the italic |
| `tests/visual-regression/before-after-*.png` | current Regular against the archived 1.000 at the same seven sizes |
| `tests/visual-regression/compare-previous-*.png` | the previous release (`tests/baseline/v1.400`) against the current fonts, dark and light: `Il1 \| O0 \| pqpq \| $S$S \| B8B8 \| GCGC` and the operators, ligatures off and on, at 10, 11, 12, 13, 14, 16, 18 and 20 px; PHP, JavaScript and Python at 12, 14 and 16 px; one line in all ten styles |
| `tests/rendering-tests/index.html` | self-contained page (all ten styles embedded) for a real browser: waterfalls, italics, look-alikes, feature toggles |
| `assets/comparison.png` | next to JetBrains Mono, Fira Code and Iosevka (`COMPARISON.md`) |

Rendering conditions for the PNGs: HarfBuzz shaping, FreeType greyscale with the fonts' own hinting, integer
pixel sizes, no subpixel positioning. They show what a Linux desktop shows.

`tests/baseline/` keeps the fonts of earlier versions that these comparisons need: the four weights of 1.000
(still named Vector Mono), the italic of 1.300, and three styles of 1.400.

## Testing on your own machine

This is the part automation has not done. On any system:

1. Install the ten `.ttf` files from `fonts/ttf/` and restart the application ([INSTALLATION.md](INSTALLATION.md)).
2. Open `tests/rendering-tests/index.html` in a browser.
3. In your editor and terminal, at 12, 13 and 14 px, light and dark theme, check: `0O 1lI|`, the dots of
   `. , : ;`, backtick against apostrophe, box-drawing joins, an italic comment, and Bold.
4. Compare with `assets/test-sheet-dark.png`. If something differs for the worse, open a *Rendering issue*
   with a screenshot at 100 % zoom.

## Known gaps

- No editor or terminal is driven by a test, on any system.
- macOS has not been looked at.
- The Nerd Font files are checked by `scripts/make-nerd-fonts.py` when they are built (`NERD-FONTS.md`), not by
  this suite, and were not tried in a terminal.
- The italics do not repeat the small-size look-alike bitmap tests of the uprights.

What was checked by hand, and on which machine, is in `QUALITY_REPORT.md`.
