# Audit: Varcoda Mono before the 1.3.0 upgrade

The state of the project when the upgrade brief arrived (26 November 2026), what was found, and what was
done about each point. Read from the files, not assumed. The earlier audit of 1.000, which led to the
measured changes of 1.2.0, is kept as `docs/AUDIT-1.000.md`.

## 1. What the project is

| Question | Finding |
| --- | --- |
| Authoritative source | The Python program in `scripts/fontsrc/` (`params.py` + `glyphs_*.py`). It draws every glyph of every weight from a set of pens. |
| Editable source format | UFO 3 in `sources/`, regenerated on each build; hand-edited UFOs can be compiled with `build-fonts.py --from-ufo` |
| Font editor | none required; the UFOs open in any UFO editor |
| Build tools | fontTools, ufo2ft, ufoLib2, skia-pathops, ttfautohint, AFDKO otfautohint, brotli (all pinned in `requirements.txt`) |
| Output formats | TTF (hinted), OTF/CFF (hinted), WOFF2 |
| Version control | **The working directory is not a Git repository.** There was no uncommitted work to protect. The owner's GitHub repository is separate; nothing was committed or pushed from here |
| Backup taken | the complete 1.2.0 project as a ZIP outside the project, before any change; `tests/baseline/v1.000/` holds the original 1.000 fonts |

## 2. Inventory before the upgrade (1.2.0)

| | |
| --- | --- |
| Styles | Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700. **No italics** |
| Glyphs | 647 per font, 579 encoded characters |
| Coverage | Basic Latin, Latin-1, Latin Extended-A (complete); box drawing and block elements (complete); arrows, math, currency, superscript/subscript figures, 7 Powerline symbols; Greek Δ Λ Π λ π only |
| Metrics | UPM 1000, advance 600 for every glyph, x-height 540, cap 720, ascender 772, descender −192, line box 980/−250 |
| OpenType | `calt` (27 ligatures that keep one cell per character), `ss01`–`ss07`. No GPOS, no kerning, no STAT |
| Tests | 505 pytest cases; fontbakery universal profile without FAIL; OTS; ufolint; headless Chromium |

## 3. What already worked and must be preserved

- The strict grid: one advance, no positioning, ligatures inside their cells.
- The Saira direction already built in: squared bowls (squareness 0.89), square dots, tall ascenders.
- Its own details: blade-cut extenders, flat shoulders, tailed `q`, short-leg `m`, hooked `l`, slashed zero.
- Measured punctuation and bracket sizes, one operator axis.
- Look-alike protection, enforced by tests at 12–16 px: `0 O`, `1 l I |`, `5 S`, `8 B`, `2 Z`, `{ (`, `' "` `` ` ``, `p q`, and `rn`/`cl` not fusing.
- Stylistic-set numbering (`ss01`, `ss02` unchanged since 1.000).
- Reproducible builds and sources that match the binaries.

## 4. Findings against the brief, and what happened

| Brief section | Finding | Action |
| --- | --- | --- |
| 2 Visual identity | Saira direction present and measured | kept; documented in `DESIGN.md` §12 and `docs/BRANDING.md` |
| 3 Character recognition | all listed pairs already tested and passing; slashed, dotted and plain zero and single-storey `a` exist | kept. A double-storey `g` was **not** added: see `FEATURES.md` |
| 4 Spacing | lowercase rhythm level with the references; no kerning by design | kept. **Texture healing evaluated, not implemented** (`DESIGN.md` §14) |
| 5 Programming symbols | sizes and alignment measured and tested | kept. `*=` `/=` `%=` checked on the test sheet; no ligature added |
| 6 Ligatures | all sixteen prioritised sequences present, optional, tested | kept; documented in `FEATURES.md` |
| 7 OpenType | seven meaningful stylistic sets; no `cvNN` | kept; `cvNN` not added (would duplicate the sets). **STAT table added.** After feedback the dotted zero became the default: `ss01` is retired (not renumbered) and the slashed zero is the `zero` feature |
| 8 Weights and italics | five weights; **no italic**; no variable font | **italics added for all five weights**. Variable font still not feasible: 550 of 647 glyphs compatible |
| 9 Nerd Font | Powerline built in; no patched builds | **not done**: the official patcher needs FontForge, which is not available in this environment |
| 10 Developer workflows | specimens covered 7 languages | **5 languages added** (TypeScript, Drupal PHP, YAML, Bash, PowerShell). **Windows, VS Code and Windows Terminal were not tested**: no Windows machine was available to the build |
| 11 Test system | regression renders existed | **fixed test sheet added** (the brief's lines, 10–18 px, light and dark) |
| 12 QA | extensive | **65 italic tests added**; fontbakery run over all ten fonts |
| 13 Documentation | README, changelog, specimen, design, contributing, license present | **`FEATURES.md`, `BUILD.md`, `TESTING.md` added**, the rest updated |

## 5. Technical limitations that remain

1. No variable font.
2. No Nerd Font builds.
3. Italics are derived by slanting, with three redrawn letters; curve weights are not optically corrected.
4. Automatic hinting only.
5. No rendering evidence from Windows or macOS.
6. Latin only; accents precomposed.
7. `q` and `g` are closer than the project's own bar at small sizes (21–24 % vs 30 %).

## 6. Recommended next steps

1. Install on Windows and look at 12–14 px in VS Code and Windows Terminal, light and dark; record it in `QUALITY_REPORT.md`.
2. Restructure the 97 incompatible glyphs, then build the variable font and draw italic curves from slanted skeletons.
3. Add a CI job that runs the Nerd Fonts patcher and the grid tests on its output.
