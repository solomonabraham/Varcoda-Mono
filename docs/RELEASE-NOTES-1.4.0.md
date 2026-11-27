**Varcoda Mono 1.4.0** gives the family a written italic.

## New

- **The italic lowercase is drawn, not slanted.** Stems that reach the baseline leave it to the right
  (`a d h i k m n u`), arches branch out of their stem (`h m n r`, the bowls of `b p`), bowls run back up into
  it (`a d g q u y`), stems that start at the x-height begin with the family's angled cut, and `f` descends and
  ends in a hook. Fifteen letters are redrawn in all five weights; `ı ŋ þ` and the accented letters follow them.
  Capitals, figures and signs are sloped by 9.5° as before; box drawing, arrows and Powerline symbols stay upright.
- **`*=`** joins `+=` and `-=` (28 ligatures). `**=`, `/*=` and `??=` keep their longer ligature and a plain `=`.
- The specimen sets comments and keywords in the italic in twelve languages, and compares the new italic with
  the one of 1.3.0.

## Unchanged

The five upright styles: every outline is identical to 1.3.0. Metrics, the grid, the stylistic sets and the
way ligatures are switched are the same, so no setting needs to change.

## Fixed

- In the italic, merged letters such as `ą` now use the same single-storey `a` as the plain letter.
- The build and test scripts run on Windows without manual steps (file URLs, line endings).

## Download

`VarcodaMono-1.4.0.zip`: TTF (recommended on Windows), OTF and WOFF2 for all ten styles. Install all of
them so that applications find Bold and Italic.

## Known limitations

- The slant is a shear, so curve weights in the italic are not optically corrected (under 3 % of the stem)
- No variable font, no Nerd Font build
- Built, tested and rendered in Chrome on Windows 11; no editor or terminal was driven, macOS was not looked at
- Automatic hinting only; Latin only

Full list: `CHANGELOG.md`. Evidence: `QUALITY_REPORT.md`.
