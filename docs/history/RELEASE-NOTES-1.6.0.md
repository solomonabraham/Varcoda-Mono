**Varcoda Mono 1.6.0** is a weight and legibility refinement for long sessions at 12–16 px: a Regular that holds
up on dark themes, punctuation that registers at a glance, and three look-alike pairs pulled apart. The grid, the
bowls and the features are unchanged.

## Download

| File | For |
| --- | --- |
| **`VarcodaMono-1.6.0.zip`** | **almost everyone:** `ttf/` to install, `otf/` as an alternative, `webfonts/`, the licence and a short install guide |
| `VarcodaMono-1.6.0-web.zip` | websites: ten WOFF2 files and `varcoda-mono.css` |
| `VarcodaMonoNerdFont-1.6.0.zip` | terminal prompts with icons: "VarcodaMono Nerd Font" and "VarcodaMono Nerd Font Mono", all ten styles |
| `SHA256SUMS` | checksums of the archives |

Install all ten files of the `ttf` folder, so that applications find the real Bold and Italic, then choose the
family `Varcoda Mono`. Every system, editor and terminal:
[docs/INSTALLATION.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/docs/INSTALLATION.md).
Coming from 1.5.0, no setting needs to change. If you had chosen Medium to get more weight on a dark theme, try
the Regular again.

## Changed

- **Regular is 7 % heavier.** Its stems go from 84 to 90 units and its horizontal strokes from 70 to 75. It
  rendered thin on dark themes at 13–15 px; text at 12–16 px now carries 6.6–8.1 % more ink. The counters stay
  open: that of `n` loses 3 %.
- **Medium and SemiBold** moved with it, so the steps up to the Bold stay even. Light and Bold keep their pens.
- **Punctuation is easier to see.** The dots of `. : ; ! ?` are 11 % larger, the tails of `,` and `;` are deeper
  and thicker, and straight quotes are taller.
- **`Q` no longer looks like `O`.** The tail starts inside the counter and crosses the ring. The two were the
  closest pair in the font (10 % of their ink apart); now it is 17–19 %.
- **`3` stands further from `8`:** its arms and its middle bar are shorter, so the left side is open.
- **`r` sits more evenly between its neighbours.** Its stem moved right and its arm ends lower, which closes the
  hole in words like `url` and `return`. `f` and `j` moved slightly, and the tails of `l` and `t` are larger.
- **The dot of `i` and `j`** sits a little higher, so that a pixel row stays empty between dot and stem at
  11–16 px in every style. In 1.5.0 the Bold lost that row at 11 px.
- `*` is larger and heavier, `%` slightly heavier.

In Light and Bold only `! " % ' * , . 3 : ; ? Q f i j l r t` and what is built from them differ from 1.5.0.

## New

- **A test bench against the previous release:** `tests/visual-regression/testbench.html` sets 1.5.0 and 1.6.0
  side by side on dark and light at 12, 14 and 16 px, with the look-alike characters and code in PHP, TypeScript,
  Python and regular expressions. Open it in the browser of the machine you want to judge.

## Looked at and kept

- **The x-height.** 546 and 550 units were built and measured: they gain a pixel row at 13 px and cost the
  capitals one at 14 px, which narrows the step between `a` and `A`.
- The operator axis, `l` with its head serif, the open `c` and `e`, the `$` without a through-stroke.

## Known limitations

- The rhythm around narrow letters improved only a little; the wide counters and open apertures that cause the
  rest were kept on purpose. `g` and `q`, and `$` and `S` at small sizes, are as close as before.
- Bold is 1.32 times as dark as Regular (1.42 before), so bold keywords stand out a little less.
- No variable font, no condensed widths, Latin only
- The slant of the italic is a shear; italic capitals, figures and signs are the sloped upright forms
- Automatic hinting only
- Built and tested on Windows 11 and rendered in Chrome there; no editor or terminal was driven by a test, macOS
  was not looked at; the Nerd Font files were measured but not tried in a terminal

Full list: [CHANGELOG.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/CHANGELOG.md).
Measurements: [docs/history/AUDIT-1.6.0.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/docs/history/AUDIT-1.6.0.md).
Evidence: [docs/QUALITY_REPORT.md](https://github.com/solomonabraham/Varcoda-Mono/blob/main/docs/QUALITY_REPORT.md).
