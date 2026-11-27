# Quality report: Varcoda Mono 1.6.0

What was checked, how, and with what result. Every feature the README claims has a row here. The checks for
1.6.0 ran on Windows 11 (Python 3.13, FreeType, HarfBuzz, Chrome 157; no fontconfig) on 27 November 2026.
The tests that need fontconfig or a Chromium that returns its page are skipped there. They run in CI on Ubuntu,
where the whole suite passed on every push up to 1.4.0 (586 of 586); rows marked *CI, 1.4.0* rest on that run and
will be repeated for 1.5.0 when it is pushed.
`tests/font-validation/REPORT.md` is the machine-generated companion with tool versions.

## Summary

| Area | Result |
| --- | --- |
| Project test-suite | 635 tests (`python -m pytest tests`). On Windows 11: **627 passed**, 0 failed, 8 skipped (they need fontconfig, or a Chrome that returns the page to the console). *CI, 1.4.0:* 586 of 586 passed on Ubuntu, none skipped |
| fontbakery universal, 10 TTF (upright and italic) | 0 FAIL · 30 WARN (3 checks, all reviewed) · 715 PASS |
| fontbakery universal, 10 OTF | 0 FAIL · 10 WARN · 10 ERROR (one check that crashes inside fontbakery on CFF fonts) · 635 PASS |
| OpenType Sanitizer | all 20 fonts pass (TTF and OTF of ten styles) |
| ufolint | 10 of 10 UFO sources pass |
| Reproducible build | **on one machine:** a second build of Regular, Bold, Italic and Bold Italic is byte-identical (TTF, OTF, WOFF2; a test), and a fresh build of 1.5.0 reproduced all 30 committed fonts, every UFO file and the stylesheet. **Across machines:** 1.4.0 built on Windows 11 equals the Ubuntu CI build in all 30 files when both have the same packages. The committed fonts of 1.2.0 to 1.4.0 did not: they were built with `uharfbuzz` installed and CI built without it, which packs the GSUB table differently (same content, different bytes; outlines and hinting identical). Since 1.5.0 `uharfbuzz` is a pinned build dependency and the *Build* workflow fails on any difference |
| Names and metadata | read back from all 30 files: one family with correct style linking (Regular, Italic, Bold, Bold Italic linked; Light, Medium, SemiBold with typographic family names), weight classes 300 to 700, PostScript names, version 1.600, embedding allowed, licence and licence address. New in 1.5.0: the project address (name IDs 11 and 12, and in the copyright line). Adding it changed `name` and `head` (in the OTFs also the copyright string inside `CFF`) and **no outline**: compared glyph by glyph in all 30 files |
| Installed on Windows 11 | the ten TTFs, for one user. DirectWrite lists one family, `Varcoda Mono`, with ten faces (five weights, upright and italic); the older GDI interface lists `Varcoda Mono` and, separately, Light, Medium and SemiBold, as the name table intends |
| Web fonts | the web archive, unpacked and served as it ships, in Chrome 157 on Windows 11: all ten faces load through `varcoda-mono.css`; text with and without ligatures is equally wide (264 px); 20 × `i` and 20 × `M` are both 240 px at 20 px; `zero` switches the zero without changing its width |
| Release archives | `VarcodaMono-1.6.0.zip` (33 files) and `VarcodaMono-1.6.0-web.zip` (12 files): contents, stylesheet references and determinism are tested (`tests/test_project.py`) |
| Documentation | every link, heading anchor and file name resolves; every JSON, JSONC and TOML example parses and spells the family name correctly (`tests/test_project.py`). The VS Code setting names were looked up in VS Code 1.147 |
| Italics | **shipped** for five weights, lowercase written since 1.4.0; 66 dedicated tests pass |
| Outlines | ten glyphs differ from 1.4.0, the same ten in every style: `$ G 2` and what is built from them (`Ĝ Ğ Ġ Ģ ² ₂ ½`). One glyph added (`bar_equal.liga`). All others identical (compared glyph by glyph in Regular, Bold, Italic and Light Italic) |
| Nerd Font builds | **built, as a separate download**, with the official patcher (Nerd Fonts 3.5.1) in Docker: 20 of 20 files pass the checks below. Not tried in a terminal |
| Variable font | **not shipped**: 552 of 649 glyphs compatible |
| Windows rendering | Chrome 157 on Windows 11 (below). **No editor or terminal was driven** |
| macOS rendering | **not tested** |

## Measured for 1.6.0

`docs/history/AUDIT-1.6.0.md` has the full tables, the variants that were built and rejected, and the weaknesses
that remain. Regular unless a weight is named.

| Claim | Measured | Result |
| --- | --- | --- |
| Regular is heavier | stem 84 → 90 units; ink of hinted text at 12–16 px +6.6 to +8.1 %, unhinted +6.3 to +7.4 % | measured |
| The weights are still stepped | ink at 12–16 px relative to Regular: Light 0.69–0.73, Medium 1.11–1.13, SemiBold 1.21–1.23, Bold 1.32–1.33 | pass (`test_weights_are_ordered`) |
| Punctuation is larger | period 150 → 166 units, comma 189 × 319 → 234 × 355; `. ,` and `: ;` differ by 2.8 px of ink at their worst size (2.4) | pass (`test_punctuation_is_not_undersized`, look-alike tests) |
| `Q` cannot be taken for `O` | outline difference 15–17 % across the weights (1.5.0: 10 %), hinted 17–19 % | measured; the pair is not in the test |
| `3` stands further from `8` | 39 % as outlines, 45 % hinted (35 and 38 %) | measured |
| The dot of `i j ! : ;` never touches its stem | an empty row at 11–16 px in all five weights | pass (`test_dots_stay_clear_of_their_stems`) |
| Narrow letters sit more evenly | variation of the pair gaps 31.9 → 31.3 % (JetBrains Mono 27.8 %); `rl` 555 → 526 units | measured |
| Nothing left its cell, no debris | the existing tests | pass |
| In a browser on Windows | `tests/visual-regression/testbench.html` in headless Chrome 157 (DirectWrite, greyscale): 1.5.0 and 1.6.0 side by side, read by eye at 12 and 14 px, dark and light | seen |

**Repeated for 1.6.0:** the Nerd Font build (20 of 20 files pass the checks below, 10,873 code points added to
each, patcher 3.5.1) and the release archives. **Not repeated:** the web archive in Chrome and the listing of the
installed family. The rows about them below describe 1.5.0, and the fonts installed on the test machine are
still 1.5.0.

## Measured for 1.5.0

`docs/history/AUDIT-1.5.0.md` has the full tables and the variants that were drawn and rejected.

| Claim | Measured | Result |
| --- | --- | --- |
| `$` cannot be taken for `S` | outline difference 30–44 % across the weights, upright and italic (1.4.0: 14–16 %; the test requires 15 %). Hinted at 12–16 px the minimum rose from 14–19 % to 19–45 %; that figure jumps with the hinter and is not a test | pass (`test_lookalikes_differ`) |
| `G` cannot be taken for `C` | outline 27–28 % (1.4.0: 21–22 %), hinted 29–30 % (23–25 %). `G` `6`: 32–49 % | pass (`test_lookalikes_differ`) |
| The new `2` stays apart from `Z` and `7` | outline 58–97 % and 69–111 % | pass |
| `\|=` has its ligature; `\|\|=` keeps `\|\|` and a plain `=` | HarfBuzz, five weights | pass (`test_everyday_operators_have_their_ligature`) |
| `<<` `>>` `<<=` `>>=` `>>>` `..` `...` `..=` `%=` `&=` `^=` `/=` are never changed | HarfBuzz, five weights | pass (same test) |
| Weights are evenly stepped | ink at 12–16 px relative to Regular: Light 0.74–0.77, Medium 1.13–1.14, SemiBold 1.28–1.29, Bold 1.41–1.42 (JetBrains Mono Bold 1.33, Fira Code Bold 1.72) | measured, unchanged |
| Nothing else moved | all look-alike scores of the unchanged pairs are equal to 1.4.0 to the last digit printed | pass |

### Nerd Font files

`scripts/make-nerd-fonts.py` checks each of the 20 files against the font it was made from and refuses to package a file that fails.

| Check | Result |
| --- | --- |
| Every character of the original is still there, with the same bounding box (± 1 unit) and an advance of 600 | 20 of 20 |
| Icons added, one code point checked per set (Powerline Extra, Seti-UI, Devicons, Font Awesome, Octicons, Font Logos, Weather, Codicons, Material Design) | 10,873 code points in every file |
| Varcoda Mono's own Powerline symbols, box drawing and arrows were kept (`--careful`) | identical outlines |
| Every advance is 600 and `post.isFixedPitch` is set | both variants |
| hhea and typo line box 980 / −250 / 0, `USE_TYPO_METRICS`, weight class | unchanged |
| `!=` still shapes to its ligature on the grid | 20 of 20 |
| TrueType hinting kept; OpenType Sanitizer (three files) | yes; pass |
| **Different from the original** | `usWinAscent` / `usWinDescent` are 980 / 250 instead of 1010 / 280, so the overshoot of box drawing lies outside the Windows clipping box; the STAT table is gone; the family is called "VarcodaMono Nerd Font" |

One prompt line with Powerline separators and icons was rendered with FreeType at 14 and 28 px and read by eye. No terminal and no prompt theme was run.

## Italics (since 1.3.0; the lowercase is written since 1.4.0)

| Claim | Validated by (`test_italics.py`) | Result |
| --- | --- | --- |
| Five italic styles exist as TTF, OTF, WOFF2 and stay monospaced | `test_files_exist_and_stay_monospaced` | pass |
| Italic angle −9.5°, caret slope, ITALIC/BOLD bits, style linking, STAT axes | `test_italic_metadata` | pass |
| Same line box, x-height, character set and features as the upright | `test_italic_metadata`, `test_same_characters_and_features_as_the_upright` | pass |
| Letters are slanted; box drawing, blocks, arrows, shapes, Powerline are identical to the upright | `test_letters_are_slanted_and_joining_glyphs_are_not` | pass |
| The lowercase is written: exit strokes of `a d h i m n u` reach at least 35 units beyond their stem at the baseline, `f` reaches the descender line, `ss02` and `ss05` equal the defaults, `ą` follows `a` | `test_italic_letterforms` | pass |
| Italic outlines are clean: the same number of contours in all five weights, no slivers, no micro-segments, integer coordinates | `test_italic_outlines_are_clean_and_consistent` | pass |
| Ligatures and stylistic sets shape exactly as in the upright, all advances 600 | `test_ligatures_and_sets_shape_like_the_upright` (TTF, OTF) | pass |
| One advance at 10–24 px hinted; fontconfig reports slant 100, spacing 100 | `test_hinted_advances_and_fontconfig` | pass |
| OpenType Sanitizer | `test_opentype_sanitizer` | pass |
| Ink stays close to the cell | `test_ink_stays_close_to_the_cell`: at most 52 units over the right edge (V, W in Bold Italic); ď ľ ť up to 79; of the written lowercase, the top of `f` leans furthest: 24 units in Bold Italic | pass, with that stated tolerance |

Viewed by eye in `specimens/specimen.png` (with the italic of 1.3.0 next to it), `specimens/code-samples.png`,
`assets/weights.png`, the test sheets at 10–18 px, in all five weights at display size, and in Chrome on
Windows 11 at 12–20 px. 84 glyphs of each italic differ from 1.3.0: the fifteen redrawn letters and what is
built from them. **Not done for the italics:** the small-size look-alike bitmap tests of the upright were
not repeated, and no italic was looked at on macOS.

Known weakness: the slant is a shear, so the weight of curves varies by up to about 3 % of the stem around a
bowl.

## Chrome on Windows 11 (since 1.4.0, repeated for 1.5.0)

`tests/rendering-tests/index.html`, with the ten TTFs embedded, was opened in headless Chrome 157 on Windows 11.
Chrome rasterises with DirectWrite and shapes with HarfBuzz there, as VS Code and Cursor do. Read from the
page's own report:

| Measurement | Expected | Result |
| --- | --- | --- |
| The ten faces | loaded | all ten loaded |
| 20 × `i`, 20 × `M`, 20 × Bold `M`, 10 × italic `fa`, at 16 px | 192 px | 192 px each |
| Operators with and without ligatures | equal widths | 220.8125 px both |
| Line height at 20 px | 24.6 px | 25 px |

The screenshot was read by eye at 11–24 px (upright) and 12–20 px (italic, all five weights at 20 px). This is
evidence for the browser text stack on one machine. It is not evidence for an installed font, for font menus or
for an editor's own settings.

## Claimed features and their validation

| Claim | Validated by | Result |
| --- | --- | --- |
| Every glyph is 600 units wide | `test_every_advance_width_is_one_cell`, hinted advances 8–32 ppem, fontconfig `spacing=100` | pass |
| Nothing moves glyphs off the grid | no GPOS/kern table (`test_no_kerning_or_positioning…`) | pass |
| Same line height on all platforms | hhea = typo = 980/−250/0, `USE_TYPO_METRICS`, win 1010/280 (`test_vertical_metrics`) | pass |
| No clipping | all glyphs inside the line box; tallest ĥ 936 < 980, lowest cedilla −196 > −250 (`test_glyphs_stay_inside_their_cells`) | pass |
| Basic Latin, Latin-1, Latin Extended-A, box drawing, blocks complete | `test_unicode_coverage` | pass |
| Five weights, correct style linking | `test_names_and_style_linking`, `test_weights_are_ordered`, fontconfig weights 50/80/100/180/200 | pass |
| Look-alikes stay distinct | outline test (36 pairs, among them `0 Ø`, `D O`, `y g`, `y v`, `b h`, `$ S`, `G C`) and hinted bitmaps at 12–16 px, all weights (18 pairs: `0O 1l 1I lI l| 5S 8B ., :; `' 2Z {( }) 1| I| '" yv yg`) | pass |
| `rn` / `cl` do not fuse | `test_adjacent_letters_do_not_fuse` at 12, 13, 14 px, all weights | pass |
| Operators and brackets share one axis | `test_operators_and_brackets_are_centred_on_the_axis` (± 2 units; asterisk ± 20) | pass |
| Punctuation is no longer undersized | `test_punctuation_is_not_undersized`, measurements below | pass |
| 29 ligatures substitute, keep the grid, and are optional | HarfBuzz shaping with `calt` on and off for every ligature, TTF and OTF; long runs; 400 random operator strings per font; ink stays inside the cells at 14/16/20 px | pass |
| The operators named in the 1.4.0 brief | `test_everyday_operators_have_their_ligature`: all twenty have their ligature, and since 1.5.0 `\|=`; the nullsafe `?->` is `?` and the arrow; `**=`, `??=`, `\|\|=` and `/*=*/` keep the longer ligature and a plain `=` | pass |
| Ligatures work in a browser | width of ligated text = width of plain text: read from the test page and from the web archive in Chrome on Windows 11; headless Chromium test (*CI, 1.4.0*) | pass |
| `<=` and `>=` are compact | `test_comparison_ligatures_are_not_stretched`: ink within ±0.62 of the advance, height more than 0.6 of the width, mirror images, centred on the operator axis | pass |
| `zero`, `ss02`–`ss07` | HarfBuzz shaping, outline checks that the default `q` and `m` differ from `q.ss06` and `m.ss07` and that the dotted, slashed and plain zero share one ring, feature names in the name table; nothing is on by default; `ss01` changes nothing | pass |
| Box drawing and Powerline separators join | overshoot test on outlines, seam test on hinted bitmaps (box drawing) | pass |
| WOFF2 equals the TTF | `test_webfont_matches_the_ttf` | pass |
| Fonts install and resolve by family name | Linux: fontconfig scan and Chromium using the installed family (*CI, 1.4.0*). Windows 11: DirectWrite and GDI list the installed 1.5.0 files as described above | pass |
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
| Parenthesis width | 180 | **286** | 300 | 302 | 295 |
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

**`p` and `q`.** The default `q` now has a tail; `p`/`q` is part of the hinted look-alike test and passes
at 12–16 px in all weights. One pair is knowingly below the project's 30 % bar and is not in the test:
`q` and `g` differ by 21–24 % of their ink at 12–16 px (they share the bowl and differ only in the
descender). This is not new: with the old mirror-image `q` it was 19–23 %.

**Blade cut:** the angled ends of `b d h k t p` (and of `q.ss06`) rise 32 % of the stem width (27 units in Regular, about a
third of a pixel at 14 px). The baseline, x-height and cap-height consistency tests at 12–16 px still pass;
the cut is a display-size detail and is not visible in small text.

## Ink density (per cent of the text area, hinted greyscale)

From `tests/visual-regression/density.md`.

| | 10 px | 11 px | 12 px | 13 px | 14 px | 16 px | 18 px |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.000 Regular | 12.3 | 10.5 | 12.1 | 10.8 | 12.4 | 11.1 | 11.1 |
| 1.5.0 Regular | 13.4 | 11.5 | 13.1 | 11.6 | 13.5 | 12.0 | 12.1 |
| **1.6.0 Regular** | 14.3 | 12.3 | 14.2 | 12.5 | 14.4 | 13.0 | 13.0 |
| 1.6.0 Medium | 16.0 | 13.8 | 16.0 | 14.0 | 16.3 | 14.5 | 14.4 |
| 1.5.0 Medium | 15.1 | 13.0 | 14.9 | 13.1 | 15.3 | 13.7 | 13.7 |
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

- **Windows:** GDI ClearType rendering, VS Code, Cursor, Windows Terminal, the PowerShell console, JetBrains IDEs.
  The fonts are installed and listed correctly; their DirectWrite rendering was seen only through Chrome.
- **macOS:** installation, Core Text rendering.
- **Editors:** no editor was run. Chrome on Windows shares its text stack with VS Code and Cursor; that is
  evidence for the rendering, not for an editor.
- **fontconfig and the installed-font Chromium test for 1.5.0:** they ran in CI for 1.4.0 and are skipped on
  Windows, so they have not yet run for 1.5.0.
- **Powerline separators at small sizes:** outline overlap is tested; hinted seams were only tested for
  box drawing.
- **The workflows as changed for 1.5.0.** *Build* and *Validate* passed on every push up to 1.4.0. The *Release*
  workflow has never run: it waited for tags that start with `v`, which this project does not use. Its corrected
  version, and the *Build* check that now fails instead of warning, run for the first time with 1.5.0.
- **Nerd Font files in use:** built and measured, one prompt line rendered; no terminal and no Oh My Posh theme was run.
- **VS Code, Cursor, Windows Terminal, PowerShell:** not run. Real applications remain the largest gap.
- **Trademark and repository-name clearance:** see `docs/BRANDING.md`.
