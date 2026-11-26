# Quality report: Varcoda Mono 1.2.0

What was checked, how, and with what result. Every feature the README claims has a row here. Checks ran on
Linux (Python 3.13, FreeType, HarfBuzz, fontconfig, Chrome headless) on 26 November 2026.
`tests/font-validation/REPORT.md` is the machine-generated companion with tool versions.

## Summary

| Area | Result |
| --- | --- |
| Project test-suite | **490 passed**, 0 failed (`python -m pytest tests`) |
| fontbakery universal, 5 TTF | 0 FAIL · 15 WARN (3 checks, all reviewed) · 350 PASS |
| fontbakery universal, 5 OTF | 0 FAIL · 5 WARN · 5 ERROR (one check that crashes inside fontbakery on CFF fonts) · 310 PASS |
| OpenType Sanitizer | all 10 fonts pass |
| ufolint | 5 of 5 UFO sources pass |
| Reproducible build | two clean builds are byte-identical (TTF, OTF, WOFF2) |
| Variable font | **not shipped**: 553 of 645 glyphs compatible |
| Windows / macOS rendering | **not tested** |

## Claimed features and their validation

| Claim | Validated by | Result |
| --- | --- | --- |
| Every glyph is 600 units wide | `test_every_advance_width_is_one_cell`, hinted advances 8–32 ppem, fontconfig `spacing=100` | pass |
| Nothing moves glyphs off the grid | no GPOS/kern table (`test_no_kerning_or_positioning…`) | pass |
| Same line height on all platforms | hhea = typo = 980/−250/0, `USE_TYPO_METRICS`, win 1010/280 (`test_vertical_metrics`) | pass |
| No clipping | all glyphs inside the line box; tallest ĥ 936 < 980, lowest cedilla −196 > −250 (`test_glyphs_stay_inside_their_cells`) | pass |
| Basic Latin, Latin-1, Latin Extended-A, box drawing, blocks complete | `test_unicode_coverage` | pass |
| Five weights, correct style linking | `test_names_and_style_linking`, `test_weights_are_ordered`, fontconfig weights 50/80/100/180/200 | pass |
| Look-alikes stay distinct | outline test (29 pairs, among them `D O`, `y g`, `y v`, `b h`) and hinted bitmaps at 12–16 px, all weights (18 pairs: `0O 1l 1I lI l| 5S 8B ., :; `' 2Z {( }) 1| I| '" yv yg`) | pass |
| `rn` / `cl` do not fuse | `test_adjacent_letters_do_not_fuse` at 12, 13, 14 px, all weights | pass |
| Operators and brackets share one axis | `test_operators_and_brackets_are_centred_on_the_axis` (± 2 units; asterisk ± 20) | pass |
| Punctuation is no longer undersized | `test_punctuation_is_not_undersized`, measurements below | pass |
| 27 ligatures substitute, keep the grid, and are optional | HarfBuzz shaping with `calt` on and off for every ligature, TTF and OTF; long runs; 400 random operator strings per font; ink stays inside the cells at 14/16/20 px | pass |
| Ligatures work in a browser | headless Chromium: width of ligated text = width of plain text | pass |
| `ss01`–`ss05` | HarfBuzz shaping, feature names in the name table; nothing is on by default | pass |
| Box drawing and Powerline separators join | overshoot test on outlines, seam test on hinted bitmaps (box drawing) | pass |
| WOFF2 equals the TTF | `test_webfont_matches_the_ttf` | pass |
| Fonts install and resolve by family name | fontconfig scan + Chromium using the installed family (Linux) | pass |
| Sources match binaries, no outline debris | `test_ufo_sources_match_fonts`, `test_sources_have_no_outline_debris` | pass |
| `rename-family.py` works | a copy renamed to "Vector Mono", rebuilt, all tests passed | pass (manual run) |

## Measured before and after (Regular, thousandths of the em)

`python scripts/compare-fonts.py <fonts…>` prints the full table.

| | 1.000 | **1.2.0** | JetBrains Mono | Fira Code | Iosevka |
| --- | ---: | ---: | ---: | ---: | ---: |
| Advance | 600 | 600 | 600 | 600 | 500 |
| x-height | 540 | 540 | 550 | 526 | 520 |
| Line height | 1230 | 1230 | 1320 | 1312 | 1250 |
| Stem of n | 78 | **84** | 90 | 85 | 78 |
| Counter of n | 280 | 264 | 238 | 231 | 216 |
| Lowercase rhythm, CV of stem gaps | 35 % | 35 % | 37 % | 36 % | 39 % |
| Capital rhythm, CV | 33 % | 33 % | 30 % | 28 % | 30 % |
| Period | 124×125 | **150×150** | 166×166 | 176×176 | 156×156 |
| Comma | 156×294 | **189×319** | 210×311 | 176×344 | 172×363 |
| Single quote | 80×241 | **94×270** | 97×300 | 105×260 | 86×330 |
| Asterisk | 344×360 | **404×426** | 530×516 | 503×480 | 424×400 |
| Plus | 410×410 | **438×438** | 470×470 | 469×468 | 372×386 |
| Parenthesis width | 180 | **274** | 300 | 302 | 295 |
| Bracket width | 213 | **240** | 245 | 250 | 276 |
| Brace width | 285 | **336** | 430 | 334 | 316 |
| j side bearings | 112 / 201 | **99 / 174** | 85 / 144 | 96 / 155 | 20 / 137 |
| r side bearings | 135 / 81 | **121 / 77** | 111 / 66 | 106 / 70 | 124 / 49 |

Rhythm is the coefficient of variation of the white gaps between stems in `nihmulnhimun` and
`HIUHLHIHUH`; lower is more even.

## Shape character: the Saira direction

Saira (Regular, from `@fontsource/saira` 5.3.0) was measured, not copied. "Squareness" is the area inside the
outer contour divided by its bounding box: 1.0 for a rectangle, 0.785 for an ellipse.

| | 1.000 | **1.2.0** | Saira | JetBrains Mono |
| --- | ---: | ---: | ---: | ---: |
| Squareness of `o` | 0.867 | **0.893** | 0.910 | 0.862 |
| Squareness of `O` | 0.869 | **0.895** | 0.917 | 0.897 |
| Squareness of `0` | 0.879 | **0.897** | 0.919 | 0.892 |
| Squareness of the period | 0.898 | **0.979** | 1.000 | 0.812 |
| Ascender / cap height | 1.050 | **1.072** | 1.080 | 1.000 |

**The squared `y` was tested and not made the default.** Saira's `y` is a `u` with a hooked descender.
Built that way, hinted bitmaps of `y` and `g` differed by only 20–28 % of their ink at 12–16 px (the
project's threshold for look-alikes is 30 %); with a shorter hook, `y` and `u` differed by 19–26 %. The
diagonal `y` stays the default and the squared form is `ss05`.

**Side effect found and fixed:** with a squarer `O`, the outline difference between `D` and `O` fell to
14 % in one weight (threshold 15 %). `D` now has tighter corners; all weights pass.

**Blade cut:** the angled ends of `b d h k t p q` rise 32 % of the stem width (27 units in Regular, about a
third of a pixel at 14 px). The baseline, x-height and cap-height consistency tests at 12–16 px still pass;
the cut is a display-size detail and is not visible in small text.

## Ink density (per cent of the text area, hinted greyscale)

From `tests/visual-regression/density.md`.

| | 10 px | 11 px | 12 px | 13 px | 14 px | 16 px | 18 px |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.000 Regular | 12.3 | 10.5 | 12.1 | 10.8 | 12.4 | 11.1 | 11.1 |
| **1.2.0 Regular** | 13.5 | 11.6 | 13.2 | 11.7 | 13.6 | 12.1 | 12.2 |
| 1.2.0 Medium | 15.2 | 13.1 | 15.0 | 13.2 | 15.4 | 13.8 | 13.8 |
| JetBrains Mono | 13.2 | 12.4 | 13.6 | 12.9 | 13.9 | 12.7 | 13.0 |
| Fira Code | 12.0 | 11.3 | 12.4 | 11.7 | 12.6 | 11.5 | 11.8 |
| Iosevka | 15.2 | 12.7 | 15.1 | 15.2 | 14.7 | 14.8 | 14.4 |

Caveat: the reference files are the web subsets from `@fontsource`, which may carry different hinting from
the desktop releases of those fonts. The numbers show order of magnitude, not a ranking.

## Visual regression

`tests/visual-regression/before-after-dark.png` and `before-after-light.png` set the same two lines in the
1.000 Regular and the current Regular at 10, 11, 12, 13, 14, 16 and 18 px, pixel for pixel and enlarged
3×. Reviewed by eye: squarer bowls, square and larger dots, larger quotes and asterisk, deeper
parentheses, wider braces, slightly darker text; no glyph became less distinct. Regenerate with `python scripts/make-regression.py`.

## fontbakery findings

| Result | Check | Assessment |
| --- | --- | --- |
| WARN | `soft_hyphen` | U+00AD belongs to Latin-1, which is covered completely |
| WARN | `contour_count` (uni00AD only) | the soft hyphen is drawn visibly on purpose, so it shows up in source code |
| WARN | `alt_caron` | ď is an outline, not a composite, so fontbakery cannot inspect it; ď ľ ť Ľ use the apostrophe-shaped caron |
| ERROR (OTF) | `opentype/monospace` | the check reads the `glyf` table and crashes on CFF fonts; the same properties are covered by the test-suite |

## Not validated

- **Windows:** installation, DirectWrite and GDI ClearType rendering, VS Code, Windows Terminal,
  PowerShell console, JetBrains IDEs.
- **macOS:** installation, Core Text rendering.
- **Editors:** no editor was run. The Chromium tests exercise the same text stack VS Code uses on Linux,
  which is not evidence for Windows.
- **Powerline separators at small sizes:** outline overlap is tested; hinted seams were only tested for
  box drawing.
- **GitHub Actions workflows:** parsed as YAML, never executed.
- **Nerd Fonts patching:** not run (no FontForge).
- **Trademark and repository-name clearance:** see `docs/BRANDING.md`.
