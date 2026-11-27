**Varcoda Mono 1.5.0** is a refinement: three glyphs redrawn after measurement, one ligature, Nerd Font builds,
and, for the first time, a download you can install without cloning the repository.

## Download

| File | For |
| --- | --- |
| **`VarcodaMono-1.5.0.zip`** | **almost everyone:** `ttf/` to install, `otf/` as an alternative, `webfonts/`, the licence and a short install guide |
| `VarcodaMono-1.5.0-web.zip` | websites: ten WOFF2 files and `varcoda-mono.css` |
| `VarcodaMonoNerdFont-1.5.0.zip` | terminal prompts with icons: "VarcodaMono Nerd Font" and "VarcodaMono Nerd Font Mono", all ten styles |
| `SHA256SUMS` | checksums of the archives |

Install all ten files of the `ttf` folder, so that applications find the real Bold and Italic, then choose the
family `Varcoda Mono`. Every system, editor and terminal:
[docs/INSTALLATION.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/docs/INSTALLATION.md).
Coming from 1.4.0, no setting needs to change.

## Changed

- **`$` no longer looks like `S`.** Its S is slightly smaller and the strokes above and below are longer. The two
  were the closest pair in the font (14–16 % of their ink apart); now it is 30–44 %.
- **`G` stands further from `C`:** the bar sits just above the middle and reaches past the centre, and the upper
  arm is shorter.
- **`2`** meets its diagonal at the waist of `3` and `8`, so the head is as tall as their upper bowls and the
  diagonal is steeper.

`Ĝ Ğ Ġ Ģ ² ₂ ½` follow. Every other outline is identical to 1.4.0, in all ten styles.

## New

- **`|=`** has a ligature (29 in total): the bar moves towards the equals sign, as the colon does in `:=`.
  `||=` keeps `||` and a plain `=`.
- **Nerd Font builds** as a separate download, made with the official patcher.
- **An installation guide** for Windows, macOS, Linux, eleven editors and terminals, and the web, with a table of
  what was verified on which machine.
- The fonts carry the project's address in their name table.

## For people who build the fonts

- The TrueType fonts moved from `fonts/` to `fonts/ttf/`; the reference documents moved to `docs/`.
- Builds are byte-identical across machines again: `uharfbuzz`, which decides how one table is packed, is now a
  pinned build dependency. CI fails when a committed font is not what the sources build.

## Looked at and kept

The weight scale (evenly stepped; Bold stands between JetBrains Mono and Fira Code), `a` (a longer upper left
measured closer to `e`), `B 8`, `0 O`, `l I 1`, `p q`, quotes, brackets, the question mark and `@`.

## Known limitations

- No variable font, no condensed widths, Latin only
- The slant of the italic is a shear; italic capitals, figures and signs are the sloped upright forms
- Automatic hinting only
- Built, tested and installed on Windows 11 and rendered in Chrome there; no editor or terminal was driven by a
  test, macOS was not looked at; the Nerd Font files were measured but not tried in a terminal

Full list: [CHANGELOG.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/CHANGELOG.md).
Evidence: [docs/QUALITY_REPORT.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/docs/QUALITY_REPORT.md).
