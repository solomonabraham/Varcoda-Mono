# OpenType features

Everything here is in the compiled fonts and covered by tests (`TESTING.md`). Nothing is on by default
except what the application itself enables (most editors and terminals enable `calt`).

## Summary

| Feature | What it does | Default |
| --- | --- | --- |
| `calt` | 27 programming ligatures | controlled by the application's "ligatures" switch |
| `ss01` | dotted zero | off |
| `ss02` | single-storey `a` (and `à á â ã ä å ā ă ą`) | off |
| `ss03` | plain zero | off |
| `ss04` | `l` with a flat foot | off |
| `ss05` | squared, hooked `y` (and `ý ÿ ŷ`) | off |
| `ss06` | plain `q`, the mirror image of `p` (the default `q` has a tail) | off |
| `ss07` | `m` with three full legs (the default `m` has a short middle leg) | off |

There is no `liga`, `kern`, `cvNN` or `zero` feature and no GPOS table. See "What is deliberately missing".

## Ligatures (`calt`)

```
=== !== <=> <-> != == => -> <- <= >= && || ?? ++ -- :: // /* */ |> <| := ** ?. += -=
```

- **The text never changes.** Ligatures are drawn by substituting glyphs; copy, search and the file on disk
  see the original characters.
- **The grid never changes.** A ligature of *n* characters is *n* glyphs of 600 units: the first *n − 1* are
  empty spacers, the last one carries the drawing, which reaches back over the spacers.
- **Recognisable.** They are the original operators moved closer or joined, not new symbols. `!=` is an
  equals sign with a stroke, `=>` an arrow with a double shaft, `:=` lifts the colon to the level of the bars.
- **Longer runs are left alone:** `====`, `---`, `///`, `:::`, `>>=`, `-->`.
- **Why `calt` and not `liga`:** `calt` can look at context (needed to leave long runs alone), and it is the
  feature that editor and terminal ligature switches control. With `calt` off the font is complete.

### Turning ligatures off or on

| Application | Setting |
| --- | --- |
| VS Code | `"editor.fontLigatures": false` (or `true`) |
| Windows Terminal | `"font": { "features": { "calt": 0 } }` |
| JetBrains IDEs | Settings → Editor → Font → *Enable ligatures* |
| kitty | `disable_ligatures always` |
| WezTerm | `config.harfbuzz_features = { 'calt=0' }` |
| CSS | `font-feature-settings: "calt" 0;` or `font-variant-ligatures: none;` |

## Stylistic sets

| Set | Plain | With the set | Use it when |
| --- | --- | --- | --- |
| `ss01` | slashed `0` | dotted `0` | the slash feels heavy; still distinct from `O` |
| `ss02` | double-storey `a` | single-storey `a` | you want a more geometric texture (it is always single-storey in the italics) |
| `ss03` | slashed `0` | plain `0` | prose or data where the mark distracts; `0` and `O` then differ only in width |
| `ss04` | `l` with a curved tail | `l` with a flat foot | you prefer a typewriter `l` |
| `ss05` | diagonal `y` | squared, hooked `y` | you want the most Saira-like form (closer to `g` and `u` at 12–14 px) |
| `ss06` | tailed `q` | plain `q` | you prefer the conventional `q` |
| `ss07` | short-leg `m` | full `m` | you prefer the conventional `m` |

`assets/ligatures.png` shows every ligature and set, rendered from the fonts.

### Activating sets

```jsonc
// VS Code: a CSS feature string replaces true/false
"editor.fontLigatures": "'calt', 'ss01', 'ss05'"
"editor.fontLigatures": "'calt' off, 'ss03'"        // no ligatures, plain zero
```

```jsonc
// Windows Terminal
"font": { "face": "Varcoda Mono", "features": { "calt": 1, "ss01": 1, "ss05": 1 } }
```

```conf
# kitty (one line per style you use)
font_features VarcodaMono-Regular +ss01 +ss05
font_features VarcodaMono-Italic  +ss01
```

```lua
-- WezTerm
config.harfbuzz_features = { 'calt=1', 'ss01=1', 'ss05=1' }
```

```css
code { font-family: "Varcoda Mono", monospace; font-feature-settings: "calt" 1, "ss01" 1; }
```

JetBrains IDEs and simple editors such as Notepad offer no switch for stylistic sets.

`ss01` and `ss03` both replace the zero; if both are on, `ss03` wins.

## Italics and features

All features work the same in the italic styles. In the italics `a` is already single-storey and `y` is
already the hooked form, so `ss02` and `ss05` change nothing there.

## What is deliberately missing

| Not there | Why |
| --- | --- |
| `cvNN` character variants | they would duplicate the seven sets one-to-one; sets are supported by more applications |
| `ss08` | no eighth alternate improved on a default in testing; an empty set would only clutter font menus |
| A `zero` feature | the slashed zero is the default, so there is nothing for it to switch |
| A double-storey `g` | the single-storey `g` matches the squared bowls; a double-storey `g` needs two counters in a 600-unit cell and closes up in the heavier weights |
| Ligatures for `*=` `/=` `%=` | bringing the two signs closer would not make them easier to read; the plain pairs are clear on the test sheet |
| Kerning (`kern`, GPOS) | a monospaced font must not move glyphs |
| Texture healing | evaluated and declined: `DESIGN.md` §14 |
