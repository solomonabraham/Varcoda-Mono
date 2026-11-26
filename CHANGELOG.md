# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release tags use semantic versioning
(`v1.2.0`); the version inside the font files is the OpenType form of the same number (`1.200`).

## [1.2.0] - unreleased

First release under the name **Varcoda Mono**. Prepared locally; not yet tagged or published.
(An interim local build was called "Kerf Mono"; it was never published.)

### Changed

- **Renamed** from Vector Mono to Varcoda Mono (family name, file names, PostScript names). Vector Mono 1.000
  and Varcoda Mono can be installed side by side. Reasons: `docs/BRANDING.md`.
- **Squarer bowls,** in the direction of Saira: curve tension 0.62 → 0.67 and smaller corner radii; the
  squareness of `o` goes from 0.867 to 0.893 (Saira: 0.910).
- **Square dots** with a small radius on `i j . : ; ! ?` and the dieresis (were squircles).
- **Taller ascenders:** 756 → 772 units.
- **Blade cut:** the tops of `b d h k t` and the feet of `p q` are sliced at an angle.
- `D` has tighter corners so it stays apart from the squarer `O`.
- After first public feedback: rounder parentheses, a heavier backtick in the lighter weights, and a question
  mark whose hook flows into the stem in one S-bend instead of meeting it at a right angle.
- **Weight scale.** Regular stem 78 → 84 units, Light 54 → 60, Medium 96 → 97; Bold unchanged at 124.
  Regular was the lightest of the fonts it was measured against.
- **Punctuation enlarged** after measurement: `. : ; ! ?` dots 124 → 150 units (Regular), comma 156×294 →
  189×319, quotes 80×241 → 94×270.
- Asterisk 344×360 → 404×426. Plus and equals 410 → 438 wide.
- Parentheses 180 → 286 wide, drawn as one continuous round curve. Brackets 213 → 240. Braces 285 → 336 with a sharper beak.
- `j` moved right and widened (side bearings 112/201 → 99/174); `r` moved left (135/81 → 121/77).
- Documentation restructured for a repository; the specification moved to `docs/DESIGN.md`.

### Added

- **SemiBold** (600).
- Ligatures `:=` `**` `?.` `+=` `-=` (27 in total).
- Stylistic sets `ss03` (plain zero), `ss04` (flat-foot l) and `ss05` (squared y). `ss01` and `ss02` are
  unchanged.
- Powerline symbols U+E0A0–E0A2 and separators U+E0B0–E0B3.
- Superscript and subscript figures ⁰ ⁴–⁹ ₀–₉.
- WOFF2 web fonts and `varcoda-mono.css`.
- Tests for operator alignment, punctuation size, letter pairs that must not fuse (`rn`, `cl`), more
  look-alike pairs, the web fonts; 490 tests in total (350 before).
- Tools: `compare-fonts.py`, `check-interpolation.py`, `make-regression.py`, `make-assets.py`,
  `rename-family.py`.
- Repository files: audit, quality report, roadmap, contribution guide, issue and pull-request templates,
  CI workflows.

### Not included (investigated)

- Variable font: 95 of 645 glyphs are not interpolation-compatible yet.
- A squared (u-form) `y` as the default: at 12–14 px it measured too close to `g` and `u`, so it is `ss05`.
- Italics and a Nerd Font build: not started / not buildable in the release environment.

## [1.0.0] - 2026-11-25

Initial version, as "Vector Mono" (never published). Four weights (Light, Regular, Medium, Bold), 610
glyphs, Basic Latin, Latin-1, Latin Extended-A, box drawing and block elements, 22 ligatures, `ss01`,
`ss02`, TTF and OTF. The fonts are archived in `tests/baseline/v1.000/`.
