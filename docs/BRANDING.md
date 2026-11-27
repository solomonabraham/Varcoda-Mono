# Name and identity

## The name

The family is called **Varcoda Mono**. The name was chosen by the project owner.

History: the design started as "Vector Mono" (1.000, unpublished). That name was dropped before any public
release because it sits one letter from Victor Mono, a well-known open-source coding font, and close to
VCTR Mono, and because "vector font" is generic font jargon that makes the name hard to search for. An
interim working name, "Kerf Mono", was used for one local build and never published.

### What was and was not verified

- **Web search, 26 November 2026:** no typeface, font project or brand named "Varcoda" turned up. The nearest
  names found were "Varoca" and "Varo" (display fonts) and "Codda"; none is the same word.
- **Package names were not checked.** The repository is `solomonabraham/Varcoda-Mono` on GitHub. Whether
  `varcoda-mono` is free on npm, Homebrew, the AUR and other registries was not looked up; do that before
  submitting a package.
- **No trademark search was performed.** A web search is not a clearance. Check the relevant registers
  (USPTO, EUIPO) if that matters to you.

Changing the name is one command: `python scripts/rename-family.py "New Name"`, then rebuild. The script
was tested by renaming a copy, rebuilding and running the full test-suite.

## Design direction

Varcoda Mono asks what a strict coding monospace would look like with the squared, technical character of
Saira (Omnibus-Type), while keeping the reading comfort of fonts such as JetBrains Mono. Saira was measured
and looked at; **no outline, metric table or feature code was taken from it** (or from any other font).
No monospaced Saira was found to compare with (the `@fontsource` catalogue has none), so the proportions
are this project's own: every glyph is drawn by its own program. What was carried over is direction, expressed as numbers (`QUALITY_REPORT.md`):

| Trait | Saira | Varcoda Mono 1.000 | Varcoda Mono now |
| --- | ---: | ---: | ---: |
| Squareness of `o` (1 = rectangle, 0.785 = ellipse) | 0.910 | 0.867 | 0.893 |
| Squareness of `O` | 0.917 | 0.869 | 0.895 |
| Dots (`.` `i` `:`) | square, 1.000 | rounded, 0.898 | softened square, 0.979 |
| Ascender / cap height | 1.08 | 1.05 | 1.07 |

It deliberately stops short of Saira's squareness, and it does not follow Saira where a coding font needs
something else: the zero has a dot, `i` and `l` carry serifs and a tail, punctuation is far larger, and the
`y` stays diagonal by default (see below).

### Details that are Varcoda's own

- **A tailed `q` and a short-leg `m`.** `q` ends in a short tail turning right, so it is not the mirror
  image of `p`; the middle leg of `m` stops a third of the way up. Both came from early user feedback.
- **Blade cut.** The free ends of extenders are sliced at an angle: the tops of `b d h k t`, the foot of
  `p`. Top and bottom cuts are parallel. Capitals and figures stay square.
- **Flat shoulders.** Arches and bowls leave their stem level with the x-height, with one small eased
  corner inside, instead of the usual notch.
- **Softened square dots.** Square enough to snap to pixels, with a small radius so they match the bowls.
- **A zero whose slash dies in the ring**, a hooked `l`, a flagged `1`, and a squared `D` with tighter
  corners than `O`.
- **`ss05`, the squared y.** A `y` built like `u` with a hooked descender suits the squared bowls and is
  the form Saira uses. It is offered as a stylistic set rather than as the default because at 12–14 px it
  measured too close to `g` and `u`.

## Identity

| | |
| --- | --- |
| Family name | Varcoda Mono |
| Short description | A squared, technical monospaced typeface for code and terminals, on one strict 600-unit cell. |
| Tagline | Squared for code. |
| Repository | <https://github.com/solomonabraham/Varcoda-Mono> |
| Font files | `VarcodaMono-<Style>.ttf`, `.otf`, `.woff2` |
| PostScript names | `VarcodaMono-Light`, `-Regular`, `-Medium`, `-SemiBold`, `-Bold` |
| Suggested package names | npm `varcoda-mono`, Homebrew cask `font-varcoda-mono`, AUR `ttf-varcoda-mono` (none of these exist yet) |

### Logo and banner

`assets/logo.svg`: a capital V from the Bold next to an amber vertical bar, the family's own `|` glyph,
which reads as a text cursor. Both shapes are the actual glyph outlines.

`assets/banner.svg` and `banner.png` (1280 × 640): the name in Bold behind the same amber bar, the tagline, one line
of code with ligatures, and the facts in one line. It opens the README and is the picture to upload as the
repository's social preview. Both are written by `scripts/make-assets.py` from the font files, so they follow
every change to the letters.

### Pictures

One look for everything that shows the font: the dark background below, text in the light grey, labels in teal,
amber for the cursor bar and numbers, generous margins, and no decoration that is not type. The font is the
subject of every picture; the name appears once, in the banner. Every picture is rendered from the compiled
fonts and never retouched.

### Colours

| Role | Dark | Light |
| --- | --- | --- |
| Background | `#13151A` | `#F7F5F0` |
| Text | `#D8DCE5` | `#1B1E25` |
| Muted text | `#7A8396` | `#70727A` |
| Accent (teal) | `#5FD0C4` | `#007A70` |
| Cursor bar (amber) | `#F2B670` | `#B06200` |
