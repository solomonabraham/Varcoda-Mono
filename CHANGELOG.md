# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release tags use semantic versioning
(`v1.2.0`); the version inside the font files is the OpenType form of the same number (`1.200`).

## [1.3.0] - unreleased

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
- 65 tests for the italics (570 in total).

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
