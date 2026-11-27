**Varcoda Mono 1.3.0** adds italics and makes the dotted zero the default.

## New

- **Italics for all five weights**: Light Italic, Italic, Medium Italic, SemiBold Italic, Bold Italic.
  Slanted 9.5°, with a single-storey `a`, a hooked `y` and a descending `f`, so comments read differently
  from code at a glance. Box drawing, arrows and Powerline symbols stay upright.
- A STAT table in every font, so applications group the ten styles correctly.
- Since 1.2.0: `q` has a short tail (it is no longer the mirror image of `p`) and `m` a short middle leg;
  the previous shapes are `ss06` and `ss07`. Rounder parentheses, a heavier backtick, a smoother question mark.
- New documentation: `FEATURES.md`, `BUILD.md`, `TESTING.md`.

## Changed

- **The zero is dotted by default**, because a slashed zero is easily read as `Ø`. The slashed zero is the
  `zero` feature. `ss01` (the dotted zero until now) is retired; settings that use it need no change.
- **`<=` and `>=`** are compact signs with white space around them instead of being stretched over both cells.

## Download

`VarcodaMono-1.3.0.zip`: TTF (recommended on Windows), OTF and WOFF2 for all ten styles. Install all of
them so that applications find Bold and Italic.

## Known limitations

- The italics are derived from the upright program: three letters are redrawn, the rest is slanted, and
  curve weights are not optically corrected
- No variable font, no Nerd Font build
- Validated with FreeType and HarfBuzz (Linux and Windows), fontconfig and Chromium (Linux only); not yet looked at
  in Windows or macOS applications (DirectWrite, Core Text): reports are welcome
- Automatic hinting only; Latin only

Full list: `CHANGELOG.md`. Evidence: `QUALITY_REPORT.md`.
