# Roadmap

Only **1.3.0** and its predecessors exist. Everything below it is a plan, not a promise, and none of it is available in the
current fonts. Version numbers may shift; the order reflects dependencies and expected value.

| Version | Status | Scope |
| --- | --- | --- |
| 1.0.0 | done (unpublished, as Vector Mono) | four weights, Latin Extended-A, box drawing, 22 ligatures |
| **1.2.0** | **done locally, not published** | rename, squared Saira-inspired geometry and blade-cut extenders, measured legibility refinements, SemiBold, 5 ligatures, 2 stylistic sets, Powerline, WOFF2, repository scaffolding. Covers what was originally sketched as 1.1 (legibility) and 1.2 (ligatures and features) |
| **1.3.0** | **done locally** | italics for all five weights (own `a`, `f`, `y`), STAT table, typography test sheet, feature / build / testing documentation |
| 1.3.x | planned | fixes from real-machine testing: Windows (DirectWrite, ClearType, VS Code, Windows Terminal, PowerShell), macOS, HiDPI. First run of the CI workflows |
| 1.4.0 | planned | interpolation-compatible outlines for all glyphs, then a variable font with a weight axis (300–700); optically corrected italic curves |
| 1.5.0 | planned | a Nerd Font build in CI, more arrows and math operators, Greek for technical text |
| 2.0.0 | planned | hand-checked hinting at 11–14 px, combining marks, wider Latin; a stable glyph-name and feature contract |

## Why the open items are open

**Variable font.** The weights are drawn from the same program, but 97 of 647 glyphs (among them
`a b d g p q k m & G K M`) end up with a different number of points or segment types in different weights,
because overlap removal resolves joins differently as strokes thicken. A variable font needs identical
structure in every master. `python scripts/check-interpolation.py --list` names the glyphs; fixing them
means restructuring how those joins are built. Until that reaches zero, shipping a "variable" file would
only be changed metadata.

**A weight between Regular and Medium for dark themes.** Light text on a dark background usually looks
thinner than the reverse. 1.2.0 answers this in two ways: Regular itself moved from a 78- to an 84-unit
stem (about 433 on the old 400–500 scale), and Medium (500) and SemiBold (600) are there to choose from.
A continuous choice needs the variable font. `tests/visual-regression/density.md` has the measured
ink density per size.

**Italic curves.** The 1.3.0 italics have their own `a`, `f` and `y`, but the other letters are slanted by
the build, which thins and thickens curves slightly (under 3 % of the stem at 9.5°). Drawing the italic
from slanted skeletons would remove that and is tied to the same restructuring the variable font needs.

**Nerd Font.** The official patcher needs FontForge, which was not available where 1.2.0 was built, so no
patched font was produced or tested. `docs/NERD-FONTS.md` describes the working fallback setup and the
recipe to try.

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
| Variable font | one file, any weight | high | high | needs restructured outlines | later (1.4) |
| Italic | emphasis, comments | high | medium (derived) | curves not optically corrected | **done** in 1.3.0 |
| Texture healing | evens out m/w against i/l | unclear here: rhythm already measures level with the references | very high | glyphs must reach into neighbouring cells | not planned (see `DESIGN.md`) |
| Nerd Font build | icons in prompts | medium | medium | large files, third-party glyphs | later (1.5) |
| Manual hinting | crisper 11–13 px on Windows | unknown until tested on Windows | very high | maintenance | later (2.0), after evidence |
| Texture healing, width variants, more stylistic sets | - | low | high | complexity | not planned |
