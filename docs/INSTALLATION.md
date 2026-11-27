# Installing and setting up Varcoda Mono

From the download to a working editor in a few minutes. The short version is in the [README](../README.md#install).

- [1. Download](#1-download)
- [2. Install the fonts](#2-install-the-fonts)
- [3. Editors](#3-editors)
- [4. Terminals](#4-terminals)
- [5. Websites](#5-websites)
- [OpenType features in your application](#opentype-features-in-your-application)
- [Troubleshooting](#troubleshooting)
- [What was verified](#what-was-verified)

## 1. Download

From the [latest release](https://github.com/solomonabraham/Varcoda-Mono/releases/latest):

| File | Take it when |
| --- | --- |
| `VarcodaMono-<version>.zip` | you want the font on your computer. This is the one for almost everyone |
| `VarcodaMono-<version>-web.zip` | you only need the web fonts for a site |
| `VarcodaMonoNerdFont-<version>.zip` | your terminal prompt uses Nerd Fonts icons ([NERD-FONTS.md](NERD-FONTS.md)) |

Inside `VarcodaMono-<version>.zip`:

| Folder | Content |
| --- | --- |
| `ttf/` | TrueType fonts, hinted. **Install these**, on every system |
| `otf/` | the same fonts with PostScript outlines. An alternative, never an addition: both carry the same names |
| `webfonts/` | WOFF2 files and `varcoda-mono.css` |

## 2. Install the fonts

Install **all ten files** of the `ttf` folder. With only Regular installed, applications fake Bold by smearing
and Italic by slanting.

### Windows 10 and 11

Select the ten `.ttf` files, right-click and choose **Install** (for your account) or **Install for all users**.
Alternatively drag them into *Settings → Personalisation → Fonts*.

Check, in PowerShell:

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Fonts", "$env:WINDIR\Fonts" -Filter "VarcodaMono-*" | Select-Object Name
```

### macOS

Select the ten files, double-click, and press **Install** in Font Book. Or copy them:

```sh
cp ttf/*.ttf ~/Library/Fonts/
```

### Linux

```sh
mkdir -p ~/.local/share/fonts/varcoda-mono
cp ttf/*.ttf ~/.local/share/fonts/varcoda-mono/
fc-cache -f
fc-list "Varcoda Mono" family style      # should print ten lines
```

For all users, copy to `/usr/local/share/fonts/varcoda-mono/` instead.

### After installing

Restart the applications that should see the font: most read the font list once, at start-up.

**Updating:** install the new files over the old ones and restart the applications. On Windows a font file
that an open application is using cannot be replaced, so close editors and terminals first.

**Removing:** Windows: *Settings → Personalisation → Fonts → Varcoda Mono → Uninstall*. macOS: remove the family
in Font Book. Linux: delete the folder and run `fc-cache -f`.

### The name to type

| Where | Name |
| --- | --- |
| Family, in almost every application | `Varcoda Mono` |
| Weights | Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700 |
| PostScript names, where a tool asks for them (kitty's `font_features`, some PDF tools) | `VarcodaMono-Regular`, `VarcodaMono-Italic`, `VarcodaMono-Bold`, `VarcodaMono-BoldItalic`, `VarcodaMono-Light`, … |
| Older Windows font menus, which know only Regular, Italic, Bold and Bold Italic per family | `Varcoda Mono`, and separately `Varcoda Mono Light`, `Varcoda Mono Medium`, `Varcoda Mono SemiBold` |

## 3. Editors

### VS Code, Cursor, VSCodium, Windsurf

`settings.json` (*Preferences: Open User Settings (JSON)*):

```jsonc
{
  "editor.fontFamily": "'Varcoda Mono', Consolas, 'Courier New', monospace",
  "editor.fontSize": 14,
  "editor.fontWeight": "400",                   // "500" (Medium) can suit dark themes
  "editor.fontLigatures": true,                 // false: no ligatures
  "terminal.integrated.fontFamily": "'Varcoda Mono'",
  "terminal.integrated.fontLigatures.enabled": true
}
```

To let a theme set comments in the italic, no setting is needed: themes that use italics pick up the
real italic of the family.

### JetBrains IDEs

*Settings → Editor → Font*: choose **Varcoda Mono**, tick **Enable ligatures** if you want them. Under
*Typography Settings* the main and the bold weight can be chosen separately, for example Regular with SemiBold.

### Zed

`settings.json`:

```json
{
  "buffer_font_family": "Varcoda Mono",
  "buffer_font_size": 14,
  "buffer_font_features": { "calt": true },
  "terminal": { "font_family": "Varcoda Mono" }
}
```

### Sublime Text

*Preferences → Settings*:

```json
{
  "font_face": "Varcoda Mono",
  "font_size": 13,
  "font_options": ["no_calt"]
}
```

`"no_calt"` turns the ligatures off; leave `font_options` out to keep them.

### Vim and Neovim

In a terminal they use the terminal's font (next section). In a graphical front end:

```lua
vim.o.guifont = "Varcoda Mono:h13"   -- Neovide and other Neovim GUIs
```

```vim
set guifont=Varcoda_Mono:h13         " gVim on Windows
```

## 4. Terminals

### Windows Terminal

`settings.json`. Windows Terminal applies `calt` by default; set it to `0` to turn the ligatures off.

```jsonc
"profiles": { "defaults": { "font": {
  "face": "Varcoda Mono", "size": 11, "weight": "normal",
  "features": { "calt": 1 }
} } }
```

**PowerShell** and **Command Prompt** have no font setting of their own: they use the font of the window they
run in. In Windows Terminal that is the block above. In the classic console window, open *Properties → Font* and
choose *Varcoda Mono*; that window does not draw ligatures.

### kitty

`kitty.conf`:

```conf
font_family        Varcoda Mono
disable_ligatures  never            # or: cursor, always
```

### WezTerm

`wezterm.lua`:

```lua
config.font = wezterm.font('Varcoda Mono', { weight = 'Regular' })
config.harfbuzz_features = { 'calt=1' }     -- 'calt=0': no ligatures
```

### Ghostty

`config`:

```conf
font-family = Varcoda Mono
# font-feature = -calt        # uncomment for no ligatures
```

### Alacritty

`alacritty.toml`. Alacritty does not shape text, so it shows the plain operators; nothing breaks.

```toml
[font]
normal = { family = "Varcoda Mono", style = "Regular" }
size = 12.0
```

### iTerm2

*Settings → Profiles → Text → Font*: choose **Varcoda Mono**; tick **Use ligatures** if you want them.

### Icons in the prompt

The Powerline separators (U+E0B0–E0B3) and the branch, line-number and padlock symbols are built in. For the
Nerd Fonts icon set, see [NERD-FONTS.md](NERD-FONTS.md).

## 5. Websites

Copy the `webfonts` folder to your site. The stylesheet declares all ten styles under one family and expects the
WOFF2 files next to it.

```html
<link rel="stylesheet" href="/fonts/webfonts/varcoda-mono.css">
```

```css
code, pre, kbd, samp {
  font-family: "Varcoda Mono", ui-monospace, monospace;
  font-variant-ligatures: none;            /* ligatures off; remove the line to keep them */
}
```

A browser downloads only the styles a page uses. If you need just one or two, copy their `@font-face` rules
and files instead of the whole stylesheet; each file is under 30 kB.

## OpenType features in your application

What the features do is described in [FEATURES.md](FEATURES.md). This is how to switch them.

| Feature | Effect |
| --- | --- |
| `calt` | the 29 ligatures |
| `zero` | slashed zero |
| `ss02` `ss03` `ss04` `ss05` `ss06` `ss07` | single-storey a · plain zero · flat-foot l · squared y · plain q · long-leg m |

**VS Code and its relatives:** give `editor.fontLigatures` a feature string instead of `true` or `false`.

```jsonc
"editor.fontLigatures": "'calt', 'zero'",          // ligatures and a slashed zero
"editor.fontLigatures": "'calt' off, 'ss04'",      // no ligatures, flat-foot l
"terminal.integrated.fontLigatures.featureSettings": "'calt', 'zero'"
```

**Windows Terminal:**

```jsonc
"font": { "face": "Varcoda Mono", "features": { "calt": 1, "zero": 1, "ss05": 1 } }
```

**Zed:**

```json
"buffer_font_features": { "calt": false, "zero": true }
```

**kitty** (one line per style you use, with its PostScript name):

```conf
font_features VarcodaMono-Regular +zero +ss05
font_features VarcodaMono-Italic  +zero
```

**WezTerm:**

```lua
config.harfbuzz_features = { 'calt=1', 'zero=1', 'ss05=1' }
```

**Ghostty:**

```conf
font-feature = zero
font-feature = ss05
```

**CSS:**

```css
code { font-feature-settings: "calt" 1, "zero" 1; }
code { font-variant-numeric: slashed-zero; }        /* the same zero, the standard way */
```

JetBrains IDEs offer the ligature switch only; Sublime Text, Alacritty and simple editors such as Notepad have
no switch for `zero` or the stylistic sets.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| The font is not in the application's list | The application was running while you installed. Restart it. On Linux run `fc-cache -f`, then `fc-list "Varcoda Mono"` |
| The editor falls back to another font | The name must be exactly `Varcoda Mono`, with the space. In VS Code keep the inner quotes: `"'Varcoda Mono', monospace"` |
| Bold looks smeared, italic looks pushed over | Only some of the ten files are installed, and the application fakes the rest. Install all ten |
| Ligatures do not show | The application's ligature switch is off, or it cannot shape text at all (Alacritty, the classic Windows console). See the sections above |
| Ligatures show and you do not want them | Turn off the same switch. The font needs no change |
| Light, Medium or SemiBold are missing from a font menu | Older Windows applications list them as separate families: `Varcoda Mono Light`, `Varcoda Mono Medium`, `Varcoda Mono SemiBold` |
| Strange spacing or two versions fighting | Both the TTF and the OTF files are installed, or an old version is still there. Remove the family completely, install one set, restart |
| An update seems to change nothing | The application still holds the old files. Close it, install again, start it. On macOS log out and in if Font Book still shows the old version |
| Icons in the prompt show as boxes | Those are Nerd Fonts icons: [NERD-FONTS.md](NERD-FONTS.md) |
| A glyph looks blurry, clipped or misaligned | That is worth a report. Open a *Rendering issue* with a screenshot at 100 % zoom; `tests/rendering-tests/index.html` in a browser shows most of what is needed in one picture |

More: [SUPPORT.md](../SUPPORT.md).

## What was verified

Stated plainly, because an installation guide is a promise.

| | |
| --- | --- |
| Windows 11 | The ten TTF files of 1.5.0 were installed for one user. DirectWrite, which VS Code, Windows Terminal and browsers use, lists one family, `Varcoda Mono`, with ten faces: five weights, each upright and italic. The older GDI interface lists `Varcoda Mono` plus `Varcoda Mono Light`, `Medium` and `SemiBold`, as described above |
| Linux | The test-suite installs the fonts into a scratch font directory and checks that fontconfig and Chromium find the family by name, with the right weights, slant and spacing. This runs in CI on Ubuntu |
| Browsers | The web fonts were loaded in Chrome on Windows 11; all ten faces load, and text with and without ligatures has the same width |
| VS Code settings | Every setting name in this guide exists in VS Code 1.147 |
| macOS | **Not tested.** The steps are the standard ones for any font |
| Other editors and terminals | The settings follow each application's documentation. They were **not run** with Varcoda Mono |

If something here is wrong for your version of an application, please open an issue: a one-line correction is a
welcome contribution.
