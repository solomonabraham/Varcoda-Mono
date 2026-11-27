# Roadmap

**1.6.0** is the version in the repository; it is not tagged yet, and the last release is 1.5.0. Everything below it is a plan, not a promise, and none of it is available in the
current fonts. Version numbers may shift; the order reflects dependencies and expected value.

| Version | Status | Scope |
| --- | --- | --- |
| 1.0.0 | never published (as Vector Mono) | four weights, Latin Extended-A, box drawing, 22 ligatures |
| 1.2.0 | released 26 November 2026 | rename, squared Saira-inspired geometry and blade-cut extenders, measured legibility refinements, SemiBold, 5 ligatures, 2 stylistic sets, Powerline, WOFF2, repository scaffolding. Covers what was originally sketched as 1.1 (legibility) and 1.2 (ligatures and features) |
| 1.3.0 | released 26 November 2026 | italics for all five weights (own `a`, `f`, `y`), STAT table, typography test sheet, feature / build / testing documentation |
| 1.4.0 | released 27 November 2026 | a written italic lowercase in all five weights, the `*=` ligature, a specimen with comments and keywords in the italic, build and tests on Windows 11 |
| 1.5.0 | tagged 27 November 2026 | `$`, `G` and `2` redrawn after measurement, the `\|=` ligature, a comparison sheet against the previous release, Nerd Font builds as a separate download; release archives with an install guide, the installation guide, a reorganised repository |
| **1.6.0** | **in the repository, not tagged** | a Regular 7 % heavier for dark themes, with Medium and SemiBold re-spaced; larger punctuation dots and comma tails; `Q` and `3` redrawn; `r f j l t` re-centred; the dot of `i j` clear of its stem at 11–16 px; a test bench against the previous release (`docs/history/AUDIT-1.6.0.md`) |
| 1.6.x | planned | fixes from real-machine testing: VS Code, Cursor, Windows Terminal, PowerShell and JetBrains IDEs on Windows, macOS, HiDPI |
| 1.7.0 | planned | interpolation-compatible outlines for all glyphs, then a variable font with a weight axis (300–700); optically corrected italic curves |
| 1.8.0 | planned | the Nerd Font build in CI, more arrows and math operators, Greek for technical text; narrow drawings of `m w M W @` as the first step towards a SemiCondensed width (`docs/history/AUDIT-1.5.0.md` §6) |
| 2.0.0 | planned | hand-checked hinting at 11–14 px, combining marks, wider Latin; a stable glyph-name and feature contract |

## Why the open items are open

**Variable font.** The weights are drawn from the same program, but 97 of 649 glyphs (among them
`a b d g p q k m & G K M`) end up with a different number of points or segment types in different weights,
because overlap removal resolves joins differently as strokes thicken. A variable font needs identical
structure in every master. `python scripts/check-interpolation.py --list` names the glyphs; fixing them
means restructuring how those joins are built. Until that reaches zero, shipping a "variable" file would
only be changed metadata.

**A weight between Regular and Medium for dark themes.** Light text on a dark background usually looks
thinner than the reverse. 1.2.0 answers this in two ways: Regular itself moved from a 78- to an 84-unit
stem (about 433 on the old 400–500 scale), and Medium (500) and SemiBold (600) are there to choose from.
1.6.0 moved the Regular again, to a 90-unit stem.
A continuous choice needs the variable font. `tests/visual-regression/density.md` has the measured
ink density per size.

**Italic curves.** Since 1.4.0 the italic lowercase has its own, written construction, but the slant is still
applied by the build as a shear, which thins and thickens curves slightly (under 3 % of the stem at 9.5°).
Drawing from slanted skeletons would remove that and is tied to the same restructuring the variable font needs.

**Nerd Font.** Since 1.5.0 `scripts/make-nerd-fonts.py` builds the patched files with the official patcher in
Docker and checks each one. They are a separate download, not part of the repository. Open: running that
build in CI and trying the files in real terminals. `docs/NERD-FONTS.md`.

## Ideas evaluated for 1.2.0

| Idea | Problem it solves | Benefit | Cost | Downside | Decision |
| --- | --- | --- | --- | --- | --- |
| Larger punctuation, brackets, asterisk | marks vanish at 12–13 px | high | low | none measured | **done** |
| Heavier Regular, SemiBold | thin text, gap in the scale | high | low | text looks slightly darker than 1.000 | **done** |
| `:= ** ?. += -=` ligatures | requested operators | medium | low | none (optional, tested) | **done** |
| Plain zero, flat-foot l | personal preference | low–medium | low | plain zero is closer to `O` | **done**, opt-in |
| Squarer bowls, square dots, taller ascenders | more character, in the direction of Saira | medium | low | `D`/`O` get closer (fixed with a squarer `D`) | **done** |
| Blade-cut extenders | a detail of its own | medium | low | invisible below about 16 px | **done** |
| Squared (u-form) y as default | matches the squared bowls | medium | low | too close to `g` and `u` at 12–14 px | opt-in (`ss05`) only |
| Powerline glyphs | prompts without a patched font | medium | low | uses private-use code points, as every terminal font does | **done** |
| Superscript/subscript figures | units, footnotes, chemistry | low–medium | low | none | **done** |
| WOFF2 | web use, documentation sites | medium | low | one more dependency (brotli) | **done** |
| Narrower capitals | more even capital rhythm | low | low | `8`/`B`, `0`/`O` get closer | rejected |
| Narrower cell / taller line | density, air | unclear | high | changes the design | rejected |
| Variable font | one file, any weight | high | high | needs restructured outlines | later (1.7) |
| Italic | emphasis, comments | high | medium (derived) | curves not optically corrected | **done** in 1.3.0; written lowercase in 1.4.0 |
| Texture healing | evens out m/w against i/l | unclear here: rhythm already measures level with the references | very high | glyphs must reach into neighbouring cells | not planned (see `DESIGN.md`) |
| Nerd Font build | icons in prompts | medium | medium | large files, third-party glyphs | **done** in 1.5.0, as a separate download |
| Manual hinting | crisper 11–13 px on Windows | unknown until tested on Windows | very high | maintenance | later (2.0), after evidence |
| Texture healing, width variants, more stylistic sets | - | low | high | complexity | not planned |
