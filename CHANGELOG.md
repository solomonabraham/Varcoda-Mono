# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release tags are the bare semantic version
(`1.2.0`); the version inside the font files is the OpenType form of the same number (`1.200`).

## [1.5.0] - unreleased

A refinement after developer feedback. Every point of the brief was measured first;
`docs/history/AUDIT-1.5.0.md` has the numbers, including those for what was left alone.

### Changed

- **`$`**: the S is drawn at 94 % of the cap height and the strokes reach 0.15 cap heights beyond it (−108 to
  828 units; before −83 to 803 around a full-size S). `$` and `S` were the closest pair in the font: 14–16 % of
  their ink apart, now 30–44 %.
- **`G`**: the bar sits at 0.51 of the cap height (0.47) and starts left of the centre, and the upper arm is
  shorter than that of `C`. `G` and `C`: 21–22 % apart before, 27–28 % now.
- **`2`**: the side meets the diagonal at the waist of `3` and `8` (0.545 of the cap height, before 0.49). The
  head is as tall as their upper bowls and the diagonal runs at 44° instead of 40°.
- `Ĝ Ğ Ġ Ģ ² ₂ ½` follow. All other outlines are identical to 1.4.0 in all ten styles.

### Added

- Ligature **`|=`** (29 in total). Only the bar moves, as the colon does in `:=`: plain, the two signs stood 340
  units apart, twice as far as in any other compound assignment. `||=` keeps `||` and a plain `=`.
- **Nerd Font builds** as a separate download: `scripts/make-nerd-fonts.py` runs the official patcher
  (Nerd Fonts 3.5.1) in Docker for all ten styles in two variants, checks every file against its source and
  writes `releases/VarcodaMonoNerdFont-1.5.0.zip`. The fonts in `fonts/` are not touched. `docs/NERD-FONTS.md`
- **Release archives people can use.** `VarcodaMono-1.5.0.zip` now holds `ttf/`, `otf/`, `webfonts/`, the licence and
  a short `INSTALL.txt`, and nothing else; `VarcodaMono-1.5.0-web.zip` holds only the web fonts; `SHA256SUMS` lists
  their checksums. The earlier releases on GitHub had no files attached.
- `docs/INSTALLATION.md`: every system, eleven editors and terminals, OpenType features per application,
  troubleshooting, and a table of what was verified on which machine.
- `assets/code.png` and `assets/lookalikes.png` for the README.
- The project address in the fonts: name IDs 11 and 12, and the copyright line.
- `tests/test_project.py`: links and file names in the documentation resolve, its JSON and TOML examples parse and
  spell the family name correctly, and the release archives hold what the README promises (605 tests in total).
- `tests/visual-regression/compare-previous-dark.png` and `-light.png`: 1.4.0 against 1.5.0. Look-alikes and
  operators at 10, 11, 12, 13, 14, 16, 18 and 20 px, PHP, JavaScript and Python at 12, 14 and 16 px, one line in
  all ten styles. Written by `scripts/make-regression.py`; the 1.4.0 fonts it needs are in `tests/baseline/v1.400/`.
- Tests: `$` `S`, `G` `C` and `G` `6` joined the look-alike pairs; `|=` and `||=`; the shifts, ranges and compound
  assignments that must stay exactly as typed.
- The audit of this release, `docs/history/AUDIT-1.5.0.md`.

### Changed in the repository

- **Layout.** The TrueType fonts moved from `fonts/` to `fonts/ttf/`, next to `fonts/otf/` and `fonts/webfonts/`.
  The reference documents moved from the top level to `docs/` (`FEATURES`, `DESIGN`, `SPECIMEN`, `TESTING`,
  `QUALITY_REPORT`, `ROADMAP`; `BUILD.md` is now `docs/BUILDING.md`, `docs/PUBLISHING.md` is `docs/RELEASING.md`).
  The audits and release notes of all versions are in `docs/history/`.
- The README is a landing page: download, install, features with pictures, specifications, questions.
- The release workflow starts on the tags this project actually uses (`1.5.0`, not `v1.5.0`) and attaches both
  archives and the checksums to a draft release.
- The build workflow fails, instead of warning, when a committed font is not what the sources build.

### Fixed

- **Builds are byte-identical across machines again.** fontTools packs the GSUB table with HarfBuzz when
  `uharfbuzz` happens to be installed, and that package was listed only for the tests. A build without it produced
  the same fonts in a different byte layout, so every CI build since 1.2.0 warned that all committed fonts differed.
  `uharfbuzz` is now a pinned build dependency. Verified: 1.4.0 built on Windows 11 without it equals the Ubuntu CI
  artifact in all 30 files.
- The banner: the family name and the last line ran to the right edge of the picture.
- Documentation that still said the project was unpublished and its workflows had never run.
- A JSON example for VS Code that was not valid as written.
- `tests/font-validation/REPORT.md` no longer contains the path of the machine it was generated on.

### Evaluated, not changed

- **Weights.** Ink relative to Regular at 12–16 px: Light 0.74–0.77, Medium 1.13, SemiBold 1.28, Bold 1.42
  (JetBrains Mono Bold 1.33, Fira Code Bold 1.72). The steps are even and Light is clearly apart.
- **`a`** with a longer upper left: closer to `e` and `o` in every weight, under the limit of the tests in Light.
- `B 8`, `0 O`, `l I 1`, `p q`, `m`, quotes, backtick, brackets, braces, the question mark, `@`, `<=`: measured
  again, unchanged.
- Ligatures for `%=` `&=` `^=` `/=` `<<` `>>` `<<=` `>>=` `..` `...`; the features `salt`, `tnum` and `locl`:
  `docs/FEATURES.md`.
- Condensed widths (the program can redraw every glyph on a narrower cell, but `m w M W @` close up), Cyrillic,
  a variable font (552 of 649 glyphs are interpolation-compatible): not shipped.

## [1.4.0] - 2026-11-27

### Added

- **A written italic.** The italic lowercase is drawn instead of slanted: stems that reach the baseline leave it
  to the right (`a d h i k m n u`), arches branch out of their stem and thin there (`h m n r`, the bowls of
  `b p`), bowls run back up into their stem (`a d g q u y`), stems that start at the x-height begin with the
  blade cut, and `f` descends to the descender line and ends in a hook. Fifteen letters are redrawn in all five
  weights; `ı ŋ þ`, the accented letters and the alternates follow them (84 glyphs per italic differ from
  1.3.0). `c e j l o s t v w x z`, the capitals, figures and signs keep their construction and are sloped by
  9.5° as before. The drawings are in `scripts/fontsrc/glyphs_italic.py`; the reasons in `DESIGN.md` §13.
- Ligature **`*=`**, drawn like `+=` and `-=` (28 in total). `**=`, `/*=` and `??=` keep their longer ligature
  and a plain `=`.
- Specimen: comments and keywords of the twelve code samples are set in the italic; new sections "Regular and
  Italic" and "Before and after"; every ligature is listed. The Drupal sample covers namespaces, attributes,
  constructor promotion and the nullsafe operator.
- The browser test page embeds all ten styles and measures the italic.
- `tests/baseline/v1.300/VarcodaMono-Italic.ttf`: the previous italic, for the before/after panel.
- Tests for the italic letterforms, for clean and consistent italic outlines in all five weights, and for the
  operators of the brief (586 in total).
- `AUDIT.md` for this release (the previous one is now `docs/AUDIT-1.3.0.md`).

### Changed

- `scripts/fontsrc`: a glyph function chooses its italic form itself (`kit.ital`, `Master.italic`) instead of
  being swapped afterwards, so letters that are built from other letters follow them.

### Fixed

- In the italic, `ą` and `ª` were two-storey while `a` was single-storey.
- On Windows the headless Chrome test and the logo rasteriser built invalid `file://` URLs, and four scripts
  wrote CRLF line endings. The Chrome page test is now skipped on Windows, where `chrome.exe` returns no DOM.

### Unchanged

- **The five upright styles.** Every outline is identical to 1.3.0; only the version, the new ligature glyph and
  its lookup differ.

### Evaluated, not added

- A looped `k`, a script `s` and round `v` `w` in the italic; redrawn italic punctuation: see `AUDIT.md`.
- Variable font (551 of 648 glyphs are interpolation-compatible), Nerd Font builds, more arrows and
  mathematical operators: unchanged.

## [1.3.0] - 2026-11-26

### Added

- **Italics for all five weights** (Light Italic, Italic, Medium Italic, SemiBold Italic, Bold Italic), as TTF,
  OTF and WOFF2. Slant 9.5°. `a` is single-storey, `y` is the hooked squared form, `f` descends below the
  baseline; box drawing, block elements, arrows, geometric shapes, the radical and the Powerline symbols
  stay upright. Regular / Italic / Bold / Bold Italic are style-linked.
- A **STAT table** in every font (weight and italic axes), so applications group the ten styles correctly.
- Five more languages in the code specimen: TypeScript, Drupal PHP, YAML, Bash, PowerShell.
- `assets/test-sheet-dark.png` and `-light.png`: a fixed typography test at 10–18 px.
- `FEATURES.md`, `BUILD.md`, `TESTING.md`; `DESIGN.md` moved to the top level; a new `AUDIT.md` for this
  release (the 1.000 audit is now `docs/AUDIT-1.000.md`).
- 65 tests for the italics (580 in total).

### Changed

After feedback from readers:

- **The default zero is dotted.** The slashed zero was too close to the Danish and Norwegian letter `Ø`. It is
  still in the fonts as the registered `zero` feature (CSS `font-variant-numeric: slashed-zero`). `ss01`, which
  used to select the dotted zero, is retired: a setting that turns it on is ignored and shows the same zero
  as before. The number is not reused; `ss02`–`ss07` are unchanged.
- **`<=` and `>=` are no longer stretched** over both cells. The ligatures are 720 units wide instead of
  980 and centred on the border between the two cells, with white space on both sides; the chevron opens
  by 33° instead of 17° and reads as `<` again. Both signs now sit exactly on the operator axis.

### Evaluated, not added

- **Texture healing:** see `DESIGN.md`. Not implemented; the reasons are measurable and listed there.
- Ligatures for `*=`, `/=`, `%=`; `cvNN` features; a double-storey `g`: see `FEATURES.md`.
- Variable font (550 of 647 glyphs are interpolation-compatible) and Nerd Font builds: unchanged.

## [1.2.0] - 2026-11-26

First release under the name **Varcoda Mono**.
(An interim local build was called "Kerf Mono"; it was never published.)

### Changed

- **Renamed** from Vector Mono to Varcoda Mono (family name, file names, PostScript names). Vector Mono 1.000
  and Varcoda Mono can be installed side by side. Reasons: `docs/BRANDING.md`.
- **Squarer bowls,** in the direction of Saira: curve tension 0.62 → 0.67 and smaller corner radii; the
  squareness of `o` goes from 0.867 to 0.893 (Saira: 0.910).
- **Square dots** with a small radius on `i j . : ; ! ?` and the dieresis (were squircles).
- **Taller ascenders:** 756 → 772 units.
- **Blade cut:** the tops of `b d h k t` and the foot of `p` are sliced at an angle.
- `D` has tighter corners so it stays apart from the squarer `O`.
- After first public feedback: rounder parentheses, a heavier backtick in the lighter weights, and a question
  mark whose hook flows into the stem in one S-bend instead of meeting it at a right angle.
- After feedback on the first public post, two new defaults: **`q` has a short tail** turning right at the foot,
  so `p` and `q` are no longer mirror images, and **`m` has a short middle leg**. The previous shapes are
  `ss06` and `ss07`.
- **Weight scale.** Regular stem 78 → 84 units, Light 54 → 60, Medium 96 → 97; Bold unchanged at 124.
  Regular was the lightest of the fonts it was measured against.
- **Punctuation enlarged** after measurement: `. : ; ! ?` dots 124 → 150 units (Regular), comma 156×294 →
  189×319, quotes 80×241 → 94×270.
- Asterisk 344×360 → 404×426. Plus and equals 410 → 438 wide.
- Parentheses 180 → 286 wide, drawn as one continuous round curve. Brackets 213 → 240. Braces 285 → 336 with a sharper beak.
- `j` moved right and widened (side bearings 112/201 → 99/174); `r` moved left (135/81 → 121/77).
- Documentation restructured for a repository; the specification moved to `DESIGN.md`.

### Added

- **SemiBold** (600).
- Ligatures `:=` `**` `?.` `+=` `-=` (27 in total).
- Stylistic sets `ss03` (plain zero), `ss04` (flat-foot l), `ss05` (squared y), `ss06` (plain q) and `ss07` (long-leg m). `ss01` and `ss02` are unchanged.
- Powerline symbols U+E0A0–E0A2 and separators U+E0B0–E0B3.
- Superscript and subscript figures ⁰ ⁴–⁹ ₀–₉.
- WOFF2 web fonts and `varcoda-mono.css`.
- Tests for operator alignment, punctuation size, letter pairs that must not fuse (`rn`, `cl`), more
  look-alike pairs, the web fonts; 505 tests in total (350 before).
- Tools: `compare-fonts.py`, `check-interpolation.py`, `make-regression.py`, `make-assets.py`,
  `rename-family.py`.
- Repository files: audit, quality report, roadmap, contribution guide, issue and pull-request templates,
  CI workflows.

### Not included (investigated)

- Variable font: 97 of 647 glyphs are not interpolation-compatible yet.
- A squared (u-form) `y` as the default: at 12–14 px it measured too close to `g` and `u`, so it is `ss05`.
- Italics and a Nerd Font build: not started / not buildable in the release environment.

## [1.0.0] - 2026-11-25

Initial version, as "Vector Mono" (never published). Four weights (Light, Regular, Medium, Bold), 610
glyphs, Basic Latin, Latin-1, Latin Extended-A, box drawing and block elements, 22 ligatures, `ss01`,
`ss02`, TTF and OTF. The fonts are archived in `tests/baseline/v1.000/`.

[1.5.0]: https://github.com/solomonabraham/Varcoda-Mono/compare/1.4.0...HEAD
[1.4.0]: https://github.com/solomonabraham/Varcoda-Mono/releases/tag/1.4.0
[1.3.0]: https://github.com/solomonabraham/Varcoda-Mono/releases/tag/1.3.0
[1.2.0]: https://github.com/solomonabraham/Varcoda-Mono/releases/tag/1.2.0
