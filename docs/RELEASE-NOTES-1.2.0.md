**Varcoda Mono 1.2.0** is the first public release of the family formerly developed as Vector Mono: a squared,
technical monospaced typeface for code and terminals, in five weights, under the SIL Open Font License 1.1.

## Download

`VarcodaMono-1.2.0.zip` contains TTF (hinted, recommended on Windows), OTF and WOFF2 files for Light, Regular,
Medium, SemiBold and Bold, the license, and a browser test page. Install all five weights.

## What is in the fonts

- 645 glyphs: Basic Latin, Latin-1, Latin Extended-A, box drawing, block elements, arrows, math,
  superscript and subscript figures, Powerline symbols
- every glyph 600 units wide; no kerning; line height 1.23
- slashed zero; structurally different `1 l I |`
- 27 optional ligatures in `calt` that keep one cell per character:
  `=== !== <=> <-> != == => -> <- <= >= && || ?? ++ -- :: // /* */ |> <| := ** ?. += -=`
- stylistic sets: `ss01` dotted zero, `ss02` single-storey a, `ss03` plain zero, `ss04` flat-foot l,
  `ss05` squared y

## Changes since 1.000 (Vector Mono, unpublished)

- New name; new SemiBold; Regular and Light slightly heavier
- Squarer bowls and square dots in the direction of Saira, taller ascenders, blade-cut ends on `b d h k t p q`
- Larger punctuation, asterisk, parentheses, brackets and braces, sized against measurements
- Better placement of `j` and `r`
- Five new ligatures, three new stylistic sets, Powerline symbols, small figures, web fonts

Full list: `CHANGELOG.md`. Evidence: `AUDIT.md`, `QUALITY_REPORT.md`.

## Known limitations

- No italics, no variable font, no Nerd Font build
- Validated on Linux only (FreeType, HarfBuzz, fontconfig, Chromium). Rendering on Windows and macOS has
  not been checked yet: reports with screenshots are very welcome
- Automatic hinting only; Latin only

## Verify

`SHA256SUMS` is attached. The fonts can be rebuilt from the tagged sources with the pinned tool versions.
