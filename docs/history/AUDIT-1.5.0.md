# Audit and change report: Varcoda Mono 1.5.0

The state of the project when the 1.5.0 brief arrived (27 November 2026), what was measured for each of its
points, and what was done. Read from the files and measured on the compiled fonts, not assumed. Earlier audits:
`docs/AUDIT-1.4.0.md` (the written italic), `docs/AUDIT-1.3.0.md`, `docs/AUDIT-1.000.md`.

The brief in one line: *an evolutionary refinement. Character without confusion, personality without
sacrificing readability*, with a list of glyphs, operators, weights and features to review.

## 1. What was found

| Question | Finding |
| --- | --- |
| Authoritative source | the Python program in `scripts/fontsrc/`: one construction, drawn with five pens. The UFOs in `sources/` are regenerated on every build. No font editor is involved |
| State of the tree | Git at `Varcoda Mono 1.4.0`; all 6,663 tracked files identical to that commit (compared by content hash, because modification times cannot be trusted on this share) |
| Backup | that commit. `tests/baseline/v1.400/` keeps Regular, Italic and Bold of 1.4.0 for the comparison sheets. The work was done on a copy; the repository received only the files that changed |
| Styles | Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, each with a written italic. TTF and OTF (hinted), WOFF2 |
| Glyphs and features | 648 glyphs, 579 characters. `calt` with 28 ligatures, `zero`, `ss02`–`ss07`, STAT. No GPOS |
| Tests before any change | 586: 578 passed, 8 skipped (they need fontconfig or a Chrome that returns its DOM) |
| Tools on this machine | Python 3.13 with the pinned packages; Docker, which the Nerd Fonts patcher needs (no FontForge) |

Most of the brief had been answered by 1.2.0–1.4.0: the dotted zero, the tailed `q`, the short-leg `m`, compact
`<=` `>=`, larger punctuation, the written italic. This release is about what still measured badly.

## 2. Method

Two measures the test-suite already uses, applied to every pair the brief names, in all weights, and to
JetBrains Mono and Fira Code for scale:

- **outline difference:** the two glyphs rendered unhinted at 48 px, absolute difference divided by their mean
  ink. Identical drawings score 0; the tests require 15 %.
- **hinted difference:** FreeType bitmaps at 12–16 px, difference divided by the ink of the smaller glyph; the
  tests require 30 %. It jumps with the hinter from size to size, so it is read as a minimum.

## 3. Characters (brief §2)

Outline difference in per cent, Light / Regular / Bold.

| Pair | 1.4.0 | JetBrains Mono | Fira Code | Decision | 1.5.0 |
| --- | ---: | ---: | ---: | --- | ---: |
| `$` `S` | 16 / 15 / 14 | 30 / 28 / 20 | 63 / 50 / 33 | **changed.** The closest pair in the font, at the project's own limit | 44 / 36 / 30 |
| `G` `C` | 22 / 21 / 21 | 20 / 20 / 20 | 70 / 58 / 37 | **changed.** Hinted it was 23–25 %, under the 30 % the other pairs meet | 27 / 27 / 28 (hinted 29–30) |
| `2` | – | – | – | **changed** for harmony, see below; `2` `Z` stays far apart (97 / 84 / 58) | – |
| `a` | `a` `e`: 48 / 39 / 32 | 37 / 35 / 31 | 88 / 73 / 44 | **kept.** A longer upper left was drawn and measured: `a` `e` falls to 45 / 36 / 30, hinted to 27 % in Light | unchanged |
| `B` `8` | 54 / 42 / 32 | 40 / 35 / 23 | 41 / 33 / 22 | kept: clearer than both references | unchanged |
| `0` `O` | 45 / 41 / 37 | 22 / 20 / 14 | 69 / 53 / 27 | kept: dotted zero, slashed and plain as options | unchanged |
| `l` `I` `1` | hinted 33–95 | | | kept: three different structures | unchanged |
| `p` `q` | hinted 40–68 | | | kept: the tailed `q` of 1.2.0 | unchanged |
| `m` | | | | kept: the short middle leg is the default, the full `m` is `ss07` | unchanged |

**`$`.** The S is drawn at 94 % of the cap height and the strokes reach 0.15 cap heights beyond it (the sign now
spans −108 to 828 units; it was −83 to 803 with a full-size S). Strokes alone, at any length, moved the score
only to 18–21 %. A stroke through the whole S scored 29–41 % but closes the counters in Bold.

**`G`.** The bar sits at 0.51 of the cap height instead of 0.47 and starts left of the centre, and the upper arm
is shorter than that of `C`. `G` `6` stays clear (49 / 40 / 32).

**`2`.** The side met the diagonal at 0.49 of the cap height, which gave a flat diagonal (40°) under
a head taller than the upper bowls of `3` and `8`. It now meets at their waist (0.545): a 44° diagonal and a
head of the same height.

**`a`.** Extending the upper left makes the roof as wide as the bowl, and it costs what the table shows. The
opening between roof and bowl is what separates `a` from `e` and `o` at 12 px. Not changed.

## 4. Operators and ligatures (brief §3)

All 26 sequences of the brief were rendered with ligatures off and on at 13, 14 and 40 px. Nothing was
misleading; one pair was loose. Gap between the two signs, Regular, in units:

| `%=` | `&=` | `+=` `/=` | `-=` | `*=` `^=` | **`\|=`** |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 130 | 162 | 174 | 179 | **340** |

- **`|=` is new** (29 ligatures): only the bar moves, as the colon does in `:=`; the gap is 262. `||=` keeps
  `||` and a plain `=`.
- `%=` `&=` `^=` `/=` are already as close as `+=`; no ligature.
- `<<` `>>` `<<=` `>>=` `..` `...` `..=` stay plain. A test now states that the `<=` and `>=` ligatures never form
  inside the shifts.
- `<=`, the `@` sign, quotes, backtick, parentheses, brackets, braces and the question mark were reviewed and
  measured again (`` ` `` `'` 34–89 %, `(` `[` 46–71 %, `(` `{` 43–98 %); unchanged since 1.2.0–1.3.0.

## 5. Weights (brief §6)

Width of the bar `|`, and ink of two lines of text at 12–16 px relative to Regular:

| | Light | Regular | Medium | SemiBold | Bold | Bold ÷ Regular (ink) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Varcoda Mono** | 58 | 82 | 96 | 108 | 122 | 1.42 |
| JetBrains Mono | 80 | 90 | 108 | 116 | 126 | 1.33 |
| Fira Code | 54 | 75 | 102 | 122 | 147 | 1.72 |

Light is about a quarter lighter than Regular in ink (JetBrains Mono: a tenth); the steps above Regular are 13 %, 13 % and
11 %, more even than in either reference; Bold stands between the two. **Not changed.** A heavier Bold would
have to be drawn beyond the heaviest pen the constructions were made for.

## 6. Features, family, Nerd Fonts (brief §8–10)

| Point | Result |
| --- | --- |
| `calt`, `zero`, `ss02`–`ss07` | present, optional, tested. One ligature added |
| `liga` | deliberately not used: `calt` is what editor switches control |
| `salt` | not added: it would turn all six alternates on together; the sets already select each one |
| `tnum` | not added: every figure already has the one advance; the feature would be empty |
| `locl` | tried (Romanian `Ş Ţ` to `Ș Ț`, which are in the font) and removed: `locl` is always on, and the project's rule, enforced by a test, is that no feature acts without being asked |
| Medium to Bold with italics | exist |
| Condensed, SemiCondensed | **possible, not shipped.** With the width parameter at 540 or 500 the program redraws all 649 glyphs with unchanged pens (nothing is squeezed). At 540 Regular holds up; in Bold, and at 500 in both, `m w M W @` and the dot of the zero close at 13 px. They need their own narrow drawings first |
| Cyrillic | not present; a separate project |
| Nerd Fonts | **built, as a separate download.** `scripts/make-nerd-fonts.py` runs the official patcher (Nerd Fonts 3.5.1) in Docker and checks every result. `docs/NERD-FONTS.md` |

## 7. What changed, in one list

- Glyphs redrawn in all ten styles: `$`, `G`, `2`. What is built from them follows: `Ĝ Ğ Ġ Ģ ² ₂ ½`.
- Glyph added: `bar_equal.liga` (649 glyphs). Feature code: one lookup in `calt`.
- Every other outline is identical to 1.4.0.
- New: `scripts/make-nerd-fonts.py`, `tests/visual-regression/compare-previous-{dark,light}.png` (written by
  `scripts/make-regression.py`), `tests/baseline/v1.400/`.
- Tests: `$` `S`, `G` `C` and `G` `6` joined the look-alike pairs; `|=`, `||=` and the operators that must stay
  plain are checked in every weight.

## 8. Validation

| Check | Result |
| --- | --- |
| Test-suite | 601 tests: 593 passed, 8 skipped (as before: fontconfig, Chrome DOM), 0 failed |
| fontbakery, ufolint, OpenType Sanitizer | see `QUALITY_REPORT.md` and `tests/font-validation/REPORT.md` |
| Before and after | `tests/visual-regression/compare-previous-dark.png` and `-light.png`: the brief's test lines at 10, 11, 12, 13, 14, 16, 18 and 20 px, its PHP, JavaScript and Python samples at 12, 14 and 16 px, and one line in all ten styles |
| Nerd Font files | 20 of 20 pass: original glyphs unchanged, one advance, same line box, ligatures shape, hinting kept |

## 9. What remains

1. `q` and `g` differ by 21–22 % at small sizes (they share the bowl); known since 1.2.0, not in this brief.
2. No variable font: 552 of 649 glyphs are interpolation-compatible. No condensed widths. No Cyrillic.
3. The slant of the italic is a shear; italic punctuation, capitals and figures are the sloped upright forms.
4. Automatic hinting only. No editor or terminal was driven; macOS was not looked at.
5. The Nerd Font files were checked by measurement and by one rendered prompt line, not in a terminal.
