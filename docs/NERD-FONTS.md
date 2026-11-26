# Terminal symbols and Nerd Fonts

## What is built in

| Range | Content | Tested |
| --- | --- | --- |
| U+2500–257F | box drawing, complete | outlines overlap neighbouring cells; hinted seams at 12–16 px |
| U+2580–259F | block elements and shades, complete | same |
| U+E0A0–E0A2 | Powerline: branch, line number, padlock | drawn, inside the cell |
| U+E0B0–E0B3 | Powerline separators (solid and thin, both directions) | fill the cell with the same overlap as block elements |
| arrows, ✓ ✗, geometric shapes | see the glyph overview | - |

These are original drawings. With them a Powerline-style prompt works without a patched font.

## What is not built in

The Nerd Fonts icon collection (Devicons, Font Awesome, Octicons, Material Design, weather, and the extra
Powerline shapes from U+E0B4) is **not** included, and there is **no "Varcoda Mono Nerd Font" download**.

### Recommended today: a symbols-only fallback

Install *Symbols Nerd Font Mono* from the Nerd Fonts project next to Varcoda Mono and let the terminal fall
back to it. Varcoda Mono stays untouched and small.

- **kitty:** falls back automatically; to pin it: `symbol_map U+E000-U+F8FF,U+F0000-U+FFFFF Symbols Nerd Font Mono`
- **WezTerm:** `config.font = wezterm.font_with_fallback({ 'Varcoda Mono', 'Symbols Nerd Font Mono' })`
- **Windows Terminal** 1.21 or later: `"face": "Varcoda Mono, Symbols Nerd Font Mono"`
- **VS Code terminal:** `"terminal.integrated.fontFamily": "'Varcoda Mono', 'Symbols Nerd Font Mono'"`

These settings follow the documentation of each terminal; none of them was run for this release.

### Patching (untested recipe)

The official patcher needs FontForge, which was not available in the environment that built 1.2.0, so no
patched font was produced or checked. To try it yourself with the patcher's Docker image:

```sh
mkdir -p build/nerd
docker run --rm -v "$PWD/fonts:/in:ro" -v "$PWD/build/nerd:/out" nerdfonts/patcher --complete --mono
```

Things to verify before trusting the result: every advance is still 600 units, `post.isFixedPitch` is
still set, the vertical metrics are unchanged (980 / −250), the `calt` ligatures still shape, and the
family has a name of its own so it can sit next to the original. The project's tests are written for the
unpatched files; a CI job that patches and checks the result is planned for 1.5.
