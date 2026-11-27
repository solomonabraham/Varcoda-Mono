# Audit: Varcoda Mono before the 1.4.0 upgrade

The state of the project when the 1.4.0 brief arrived (26 November 2026), how it measured up against the four
references the brief names, and what was done about each point. Read from the files, not assumed. Earlier
audits: `docs/AUDIT-1.3.0.md` (before the italics) and `docs/AUDIT-1.000.md` (the measured changes of 1.2.0).

The brief in one line: *Saira's personality, Operator Mono's expressive italics, MonoLisa's readability,
Dank Mono's programming ligatures*, as references for a direction, not as templates.

## 1. What was found

| Question | Finding |
| --- | --- |
| Authoritative source | The Python program in `scripts/fontsrc/`: one construction, drawn with five pens. UFO 3 sources in `sources/` are regenerated on every build |
| Build tools | fontTools, ufo2ft, ufoLib2, skia-pathops, ttfautohint, AFDKO otfautohint, brotli, all pinned. No font editor is involved |
| State of the tree | Git repository at `1.3.0: italics`, with uncommitted work on top (dotted zero as the default, compact `<=` `>=`) and a release ZIP of that state |
| Backup | the complete working tree as `varcoda-mono-backup-pre-1.4.0-20261126.tar.gz` next to the project, taken before the first change. `releases/VarcodaMono-1.3.0.zip` was not touched |
| Styles | Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, each with an italic. TTF and OTF (hinted), WOFF2 |
| Glyphs | 647 per font, 579 encoded characters |
| Coverage | Basic Latin, Latin-1, Latin Extended-A, box drawing and block elements, complete. Nine arrows, thirteen mathematical operators, six currency signs, 7 Powerline symbols, Greek Δ Λ Π λ π |
| Metrics | 1000 units per em, one advance of 600, x-height 540, cap height 720, line box 980 / −250 |
| OpenType | `calt` with 27 ligatures that keep one cell per character, `zero`, `ss02`–`ss07`, STAT. No GPOS, no kerning |
| Variable font | none: 97 glyphs change their point structure between weights |
| Tests | 580, of which 572 passed on this machine, 7 were skipped (no fontconfig) and 1 failed: the headless Chrome test built a `file://` URL that is wrong on Windows |

A baseline was rendered from the untouched fonts before anything was changed, and the italic of that state is
kept as `tests/baseline/v1.300/VarcodaMono-Italic.ttf` for the before/after panel of the specimen.

## 2. Against the four references

| Reference | What it stands for | Finding | Verdict |
| --- | --- | --- | --- |
| Saira | geometric personality | squared bowls (squareness 0.89, Saira 0.91), square dots, tall ascenders, plus details of its own: blade-cut extenders, flat shoulders, tailed `q`, short-leg `m` | **there already.** Not redrawn |
| MonoLisa | readability | every pair the brief lists (`0 O o`, `1 I l`, `S 5`, `B 8`, brackets, `; : , .`, `rn m`) is measured by the tests on outlines and on hinted bitmaps at 12–16 px and passes; looked at again at 12, 13, 14 and 16 px, Regular and Bold | **there already.** No upright glyph was changed |
| Dank Mono | ligatures | twenty of the twenty-one sequences in the brief were present, optional and cell-preserving. `*=` was missing; `?->` already rendered as `?` and the arrow | **one gap** |
| Operator Mono | expressive italics | the italic was the roman, slanted, with three substituted letters (`a`, `f`, `y`). It read as an oblique | **the real gap** |

## 3. Priorities, and what happened

| # | Improvement | Why | Result |
| --- | --- | --- | --- |
| 1 | A written italic lowercase | the only place where the family fell clearly short of the brief | **done.** Fifteen letters redrawn (`a b d f g h i k m n p q r u y`), with `ı ŋ þ` and 65 derived glyphs (accented letters, alternates, `ª µ`) following them: exit strokes, branching arches, bowls that return into their stem, pen-cut stem tops, an `f` with two hooks. `DESIGN.md` §13 |
| 2 | Italic and upright in real code | the italic is used for comments and keywords, so it has to hold up next to the roman on one grid | **done.** `specimens/code-samples.png` sets comments and keywords in the italic in twelve languages |
| 3 | `*=` | named in the brief; `+=` and `-=` were tightened and `*=` was not | **done**, with tests that `**=`, `/*=` and `??=` keep their longer ligature |
| 4 | Derived letters follow their base letter | `ą` was two-storey in the italic while `a` was not: the substitution only reached the plain letter | **fixed** by moving the choice of form into the glyph functions |
| 5 | Evidence from Windows | the largest gap named in every earlier report | **partly done.** Built, tested and validated on Windows 11; rendered in Chrome 157 there (the text stack of VS Code and Cursor). No editor or terminal was driven |
| 6 | Tooling on Windows | one failing test, four scripts writing CRLF | **fixed** |
| 7 | Italic punctuation, capitals, figures | brief: "carefully designed italic punctuation" | **reviewed, kept sloped.** Brackets, quotes, dots and operators slant with the text and stay centred in their cells; redrawing them would only make the same sign look different in a comment |
| 8 | Variable font | brief: "if supported" | **not possible yet**: 551 of 648 glyphs are compatible, 97 are not. Unchanged, and no file is labelled variable |
| 9 | More arrows, operators, currency signs | brief: "examine appropriate support" | **examined, not extended.** What exists is listed in `DESIGN.md` §7 and tested; nothing more is claimed |

## 4. What was deliberately left alone

- Every upright glyph. The five upright TTFs of 1.4.0 differ from 1.3.0 only in the version, the new ligature and
  its lookup; all other outlines are identical point for point.
- The grid, the metrics, the numbering of the stylistic sets, the feature that carries the ligatures.
- `c e j l o s t v w x z` in the italic: they have no stem standing on the baseline, so they keep the roman
  construction. A looped `k`, a script `s` or a round `v` and `w` in the manner of Operator Mono were considered
  and not drawn: at 12–14 px a looped `k` fills in, and a round `v` comes too close to `u`.

## 5. Limitations that remain

1. No variable font, no Nerd Font build.
2. The slant is a shear: curve weights in the italic are not optically corrected (under 3 % of the stem).
3. Automatic hinting only.
4. No editor or terminal was driven; macOS was not looked at.
5. Latin only; accents precomposed; a modest set of arrows and mathematical operators.
6. `q` and `g` are closer than the project's own bar at small sizes (21–24 % against 30 %).
