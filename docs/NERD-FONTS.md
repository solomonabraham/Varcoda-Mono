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

The Nerd Fonts icon collection (Devicons, Font Awesome, Octicons, Material Design, weather, and the extra
Powerline shapes from U+E0B4) is **not** in the fonts of this repository. There are two ways to get it.

## 1. The Nerd Font build (since 1.5.0)

`VarcodaMonoNerdFont-<version>.zip` is a separate download. It is made from the released TTFs by the official
Nerd Fonts patcher; the original files are not touched and can stay installed next to it.

| Family name | Files | Icons |
| --- | --- | --- |
| VarcodaMono Nerd Font | `VarcodaMonoNerdFont-<Style>.ttf`, ten styles | drawn larger, may reach into the next cell |
| VarcodaMono Nerd Font Mono | `VarcodaMonoNerdFontMono-<Style>.ttf`, ten styles | every icon inside one cell |

Use the *Mono* family where a terminal clips each cell or insists on a strictly monospaced font; use the other
where icons should be as large as the text allows. Prompt themes such as those of Oh My Posh use these code
points; none was run here.
Every glyph advances 600 units in both.

```jsonc
// Windows Terminal, settings.json
"font": { "face": "VarcodaMono Nerd Font" }
```

```jsonc
// VS Code, settings.json
"terminal.integrated.fontFamily": "'VarcodaMono Nerd Font'"
```

### Building it

```sh
python scripts/make-nerd-fonts.py        # needs Docker; about two minutes
```

The script copies `fonts/ttf/*.ttf`, runs `nerdfonts/patcher --complete --careful` (and once more with `--mono`),
checks every result against the font it came from, and writes `build/nerd/` and
`releases/VarcodaMonoNerdFont-<version>.zip`. `--careful` keeps every glyph Varcoda Mono already has: its own
Powerline symbols, box drawing and arrows are not replaced.

### What was checked (1.5.0, patcher 3.5.1)

All 20 files:

- every character of the original is still there with the same bounding box (± 1 unit) and advance;
- 10,873 code points were added, with one code point checked from each icon set;
- one advance of 600 units, `post.isFixedPitch` set;
- the line box (hhea and typo 980 / −250 / 0, `USE_TYPO_METRICS`) and the weight class are unchanged;
- `!=` still shapes to its ligature on the grid; TrueType hinting is kept.

### What is different from the original

- `usWinAscent` / `usWinDescent` become 980 / 250 (original: 1010 / 280). The 30 units by which box drawing
  overshoots its cell then lie outside the Windows clipping box.
- The STAT table is removed, and the family is named after the PostScript name ("VarcodaMono", without the
  space).
- The files are 2.4 MB each instead of 80 kB, and two builds are not byte-identical (FontForge writes the time).
- The icons have their own licences; see the licence audit of the Nerd Fonts project.

**Not done:** the files were measured and one prompt line was rendered with FreeType. No terminal, no prompt
theme and no Oh My Posh configuration was run with them, and the project's test-suite does not cover them.

## 2. A symbols-only fallback

Install *Symbols Nerd Font Mono* from the Nerd Fonts project next to Varcoda Mono and let the terminal fall
back to it. Varcoda Mono stays untouched and small.

- **kitty:** falls back automatically; to pin it: `symbol_map U+E000-U+F8FF,U+F0000-U+FFFFF Symbols Nerd Font Mono`
- **WezTerm:** `config.font = wezterm.font_with_fallback({ 'Varcoda Mono', 'Symbols Nerd Font Mono' })`
- **Windows Terminal** 1.21 or later: `"face": "Varcoda Mono, Symbols Nerd Font Mono"`
- **VS Code terminal:** `"terminal.integrated.fontFamily": "'Varcoda Mono', 'Symbols Nerd Font Mono'"`

These settings follow the documentation of each terminal; none of them was run here.
