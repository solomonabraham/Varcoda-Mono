# Audit and change report: Varcoda Mono 1.6.0

What the 1.6.0 brief asked for, what was measured for each of its points, what was changed and what was left
alone (27 November 2026). Read from the sources and measured on the compiled fonts, not assumed. Earlier audits:
`AUDIT-1.5.0.md`, `AUDIT-1.4.0.md`, `AUDIT-1.3.0.md`, `AUDIT-1.000.md`.

The brief in one line: *an all-day coding standard at 12–16 px on dark and light themes: a slightly heavier
Regular, punctuation that registers at a glance, an even rhythm around narrow letters, and an audit of every
confusable pair, without losing the open counters, the dotted zero or the restraint of the design.*

## 1. Method

- **State of the tree:** Git at tag `1.5.0`; all tracked files identical to it by content hash. A fresh build
  reproduced the committed Regular byte for byte before anything was changed.
- **Geometry:** every glyph rendered unhinted at 1000 px per em, so one pixel is one font unit. JetBrains Mono,
  Fira Code and Iosevka (`@fontsource` 5.3.0, as in `docs/COMPARISON.md`) were measured the same way, for scale
  only.
- **Look-alikes:** the two measures of the test-suite. *Outline:* unhinted at 48 px, absolute difference divided
  by the mean ink. *Hinted:* FreeType greyscale at 12–16 px, difference divided by the ink of the smaller glyph;
  the minimum over the five sizes is quoted.
- **Rhythm:** for every lowercase letter, the mean white to the left and to the right of its ink between baseline
  and x-height. The gap of a pair is the right white of the first letter plus the left white of the second. The
  figure quoted is the coefficient of variation of those gaps, weighted by how often each pair occurs in the
  project's own code and documentation (288,000 pairs). Lower is more even.
- **Weight on screen:** ink density, the average coverage of the text area, hinted and unhinted, at 12–16 px.
- **Hinting:** variants were built and their pixel rows counted, instead of predicting what the hinter does.

## 2. What was found (Regular 1.5.0, units of a 1000-unit em)

| | Varcoda Mono 1.5.0 | JetBrains Mono | Fira Code | Iosevka |
| --- | ---: | ---: | ---: | ---: |
| Advance | 600 | 600 | 600 | 500 |
| x-height / cap height | 540 / 720 | 550 / 730 | 526 / 688 | 520 / 735 |
| Vertical stem (`n`) | 84 | 90 | 85 | 78 |
| Horizontal stroke (`z`) | 70 | 82 | 72 | 70 |
| Diagonal (`v`, at right angles) | 82 | 86 | 79 | 73 |
| Counter of `n` | 264 | 238 | 231 | 216 |
| Period | 150 × 150 | 166 × 166 | 176 × 176 | 156 × 156 |
| Comma | 189 × 319 | 210 × 311 | 176 × 344 | 172 × 363 |
| Dot of `i` | 115 | 126 | 109 | 112 |
| Centre of `+ - = < >` | 320 | 330 | 312 | 340 |
| Ink density at 13 px, hinted | 13.1 % | 14.8 % | 13.2 % | 17.1 % |
| Rhythm, variation of pair gaps | 31.9 % | 27.8 % | 27.7 % | not measured |

Line box: `hhea` and OS/2 typo 980 / −250 / 0 with `USE_TYPO_METRICS`, `usWinAscent` / `usWinDescent` 1010 / 280.
The underscore lies at −146 … −76 and the descenders end at −192 (−200 with overshoot), all inside the box.

Where the brief was right, and where the measurements said otherwise:

| Point of the brief | Finding |
| --- | --- |
| Regular is light on dark themes | **Confirmed.** The thinnest stem and horizontal of the three 600-unit fonts, and 11 % less ink than JetBrains Mono at 13 px |
| Dots 10–15 % above the stem width | The dot was already 1.79 × the stem; read literally the brief would shrink it. It was still the smallest dot of the four fonts, and `:` `;` was the weakest punctuation pair (35 % hinted), so dot and tail grew |
| Uneven gaps around `i l r t f` | **Confirmed in part.** The rhythm figure is four points worse than the references. `r` is the outlier (310 units of white on its right; JetBrains Mono 273). `i l t f` were already within 3 % of the references |
| Redraw `l` to separate it from `i I 1 \|` | **Not needed.** `1 l` 85 %, `l I` 67 %, `l \|` 74 %, `i l` 75 % hinted: the group was healthy. Only the tail was enlarged |
| Confusable pairs | The weak ones were not on the usual list: **`O Q` 10 %** (the closest pair in the font), `3 8` 38 %, `: ;` 35 %; `g q` 21 % and `$ S` 24 % hinted were known |
| Raise the x-height by 1–2 % | Built and measured; it costs the capitals a pixel row at 14 px (section 4) |
| Operators on the optical centre | All within 2 units of y = 320, 59 % of the x-height. The references sit at the same relative height (JetBrains Mono 60 %, Fira Code 59 %) |
| Vertical metrics | Consistent in all 20 files (`test_vertical_metrics`); nothing to change |

## 3. Changes: before, after, reason

Regular values; the other weights follow from the same program.

| | 1.5.0 | 1.6.0 | Reason |
| --- | ---: | ---: | --- |
| **Regular stem** (vertical) | 84 | **90** (+7.1 %) | the dark-theme weight asked for; now equal to JetBrains Mono |
| Regular horizontal | 70 | 75 (+6.3 %) | follows the stem (elliptical pen, ratio 0.83) |
| Regular capital stem / horizontal | 90 / 75 | 96 / 79 | capitals stay 7 % heavier than the lowercase |
| Diagonals `v` / `x` / `/` / `w` | 82 / 81 / 80 / 70 | 88 / 86 / 85 / 73 | same pen: within 2–5 % of the stem, `w` reduced as before |
| Left edge of `n` | 84 | 82 | letters grow outwards, so the counter of `n` loses 3 % (264 → 256), not 5 % |
| **Medium stem** | 97 | **101** | keeps the step from Regular at 1.12 (it would have fallen to 1.08) |
| **SemiBold stem** | 110 | **112** | even steps: 90 · 101 · 112 · 124 |
| Light, Bold stems | 60, 124 | unchanged | the brief concerns the Regular; the Bold is the anchor of the pen system |
| **Punctuation dot** `. : ; ! ?` | 150 | **166** (+10.7 %) | 1.84 × the stem; two full pixel rows at 12–15 px, nearly three at 16 px |
| Comma tail: depth, reach to the left | −169, 39 | **−189, 68** | `,` `;` must not shrink relative to the larger dot; 14 % thicker |
| Straight quotes `'` `"` | 94 × 270 | 100 × 288 | presence next to the heavier stems |
| **Dot of `i j`**: size, centre | 115, y = 678 | 121, **y = 694** | gap to the stem 80 → 93 units: see section 5 |
| **`r`**: stem, arm | left edge 121, arm cut at 70 % | **left edge 134**, cut at 65.5 % | white on its right 310 → 282, on its left 121 → 134 |
| `f`, `j` stems | 264, 369 (centre) | 273, 360 | both moved towards the middle of their white |
| `l`, `t` tails | radius 150, to 520 | radius 168, to 530 | a stronger curve at the foot; fills the right side |
| `i` head serif | from 129 | from 115 | |
| **`Q` tail** | hangs below the ring | **starts in the counter and crosses the ring** | `O Q` 10 % → 17–19 % |
| **`3`** | arms cut at 23.5 / 76.5 %, bar to 258 | arms cut at **20 / 80 %**, bar to 282 | more open on the left: `3 8` 38 % → 45 % hinted |
| `*` | 404 × 426, arms 70 | 418 × 438, arms 79 | the lightest operator against the references (17.8 % of its cell, now 20.3 %) |
| `%` | rings and slash at 76 % of the pen | 78 % | 30.7 % → 32.9 % of its cell |

Not touched: the vertical grid (x-height 540, cap height 720, ascender 772, descender −192), the advance, the
operator axis, the line box, every bowl, the dotted zero, `a g e s m n u`, the gap between `=` signs, brackets,
feature code and ligature logic.

## 4. Evaluated and left alone

**x-height.** Regular was built with 540, 546 and 550 and its hinted pixel rows counted (x-height, cap height):

| x-height | 12 px | 13 px | 14 px | 15 px | 16 px |
| --- | --- | --- | --- | --- | --- |
| 540 (kept) | 7, 9 | 7, 9 | 8, **11** | 8, **11** | 9, 12 |
| 546 (+1.1 %) | 7, 9 | **8**, 10 | 8, 10 | 8, 10 | 9, 12 |
| 550 (+1.9 %) | 7, 9 | **8**, 10 | 8, 10 | 9, 12 | 9, 12 |

Nothing changes at 12 px. At 13 px the lowercase gains a row, but at 14 px, the default of VS Code, the capitals
lose one and the step between `a` and `A` falls from three pixels to two. That is the camelCase distinction the
brief asks to keep, so the x-height stays. Unhinted (macOS) the difference is 0.13 px at 13 px.

**Operator axis.** The colon is centred on the x-height (y = 270), the operators on 320. Raising the colon would
lift its lower dot off the baseline and away from the period; lowering the axis would drop `-` and `=` between
capitals. `::` and `:=` meet in their ligatures. Left alone, as in every reference font.

**`l` without its head serif** (the "minimal top" of the brief). The serif is what separates `l` from `|`; the
measured separation gave no reason to trade it.

**`c`, `e`, `k`: closing the apertures.** Their open right sides are the largest remaining source of uneven gaps
(`c` leaves 267 units of white, JetBrains Mono 224). Closing them would cost the open counters the brief lists as
a strength and bring `c` closer to `e` and `o`.

**`$` with a through-stroke.** Rejected for 1.5.0 because it fills the counters at 12 px; not reopened.

**Narrower letters.** The counter of `n` is 256 units against a gap of 179 between two `n`. Moving the stems in
by 6 units a side would even the rhythm and give up the wide counters. Not done.

**Hinting.** `-` `=` `_` render as one row at 12–13 px (96 % coverage) and one row plus a 13–20 % edge at 14–16 px; baseline,
x-height and cap height land on one row each in every weight (tested). Nothing was added to the automatic hints.

## 5. A regression caught on the way

The first build drew the dot of `i` and `j` 9 % larger at its old height. In Chrome on Windows the 12 px sample
then showed `i` as `1`: the gap to the stem had gone from 80 to 75 units, and the hinter closed it at 12 and
13 px. The test-suite had no check for this. A scan of dot sizes and heights showed that 1.5.0 was itself on the
edge (Bold lost the gap at 11 px). The dot is now 121 units and sits 16 units higher, with a clear row at
11–16 px in all ten styles, and `test_dots_stay_clear_of_their_stems` guards it for `i j ! : ;`.

## 6. Result

| | 1.5.0 | 1.6.0 |
| --- | --- | --- |
| Ink density of Regular, hinted, 12 / 13 / 14 / 15 / 16 px | 14.8 / 13.1 / 15.1 / 13.5 / 13.5 % | 15.9 / 14.1 / 16.1 / 14.4 / 14.6 % (**+6.6 to +8.1 %**) |
| The same, unhinted | 14.0 / 13.3 / 14.4 / 13.6 / 13.1 % | 15.0 / 14.2 / 15.3 / 14.6 / 14.0 % (+6.3 to +7.4 %) |
| JetBrains Mono, for scale | 15.6 / 14.8 / 16.0 / 15.2 / 14.6 % | |
| Ink relative to Regular: Light, Medium, SemiBold, Bold | 0.74–0.78, 1.13–1.14, 1.28–1.29, 1.42–1.43 | 0.69–0.73, 1.11–1.13, 1.21–1.23, 1.32–1.33 |
| Rhythm, variation of pair gaps | 31.9 % | 31.3 % |
| Widest pairs: `rl`, `ri`, `rt`, `fi` | 555, 536, 519, 493 | 526, 501, 489, 473 |
| `O Q` outline / hinted | 10 / 10 % | 17 / 19 % (15–17 / 17–19 % over the weights) |
| `3 8` | 35 / 38 % | 39 / 45 % |
| `: ;` | 32 / 35 %, 2.4 px of ink | 35 / 34 %, 2.8 px |
| `. ,` | 56 / 70 %, 2.4 px | 59 / 69 %, 2.8 px |
| `'` and backtick | 70 / 50 % | 70 / 67 % |
| Dot of `i j` at 11–16 px | fused: Bold at 11 px | separate in all styles |
| Outlines that differ from 1.5.0 | | Regular, Medium, SemiBold and their italics: 603–604 of 649. Light, Bold and their italics: 67–69, the eighteen redrawn glyphs `! " % ' * , . 3 : ; ? Q f i j l r t` and what is built from them |

Test-suite: 635 tests, 627 passed and 8 skipped on Windows 11 (the usual skips: fontconfig, and a Chrome that
returns its page). fontbakery: no FAIL; the same three reviewed warnings, and the same check that crashes on CFF, as for 1.5.0. ufolint: 10 of 10.

Seen by eye: `tests/visual-regression/compare-previous-dark.png` and `-light.png`, and `testbench.html` in
headless Chrome 157 on Windows 11 (DirectWrite, greyscale) at 12 and 14 px, dark and light.

## 7. What is still weak

- **The rhythm gain is small:** 31.9 → 31.3 %, against 27.8 % for JetBrains Mono. The pairs of narrow letters
  are now level with the references; what remains comes from the wide counters and the open `c e k`, which were
  kept on purpose.
- **`g q`: 21 %.** Unchanged. They share the bowl and differ only below the baseline.
- **`$ S`: 24 % hinted at the worst size** (35 % as outlines). Unchanged.
- **`: ;` did not improve as a ratio** (34 %): dot and tail grew together. The absolute difference rose by 17 %.
- **`O Q` is at 17–19 %:** nearly doubled, and by this measure still the closest pair in the font (`g q` 21 %,
  `O D` 22 %). The measure divides by the ink of a large ring; at 12 px the tail is two clear pixels.
- **Bold now stands 1.32 × the Regular in ink** (1.42 before; JetBrains Mono 1.33). Bold keywords stand out a
  little less.
- **Light to Regular is a wide step** (stems 60 and 90).
- **`r` sits right of the optical centre of its cell.** In `rr` and after a space it looks slightly indented.
- **The comma is large** (234 × 355 units, ending 3 units above the descender line).
- **Not looked at:** GDI ClearType, VS Code, Windows Terminal and JetBrains IDEs themselves, macOS, and HiDPI.
  The Chrome check is greyscale, not subpixel. The italics were built, tested and looked at once at display
  size; their look-alike scores were not measured.
- **The Nerd Font files** were rebuilt and pass their checks (20 of 20); as before, they were not tried in a
  terminal.
