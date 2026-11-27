# Building Varcoda Mono

## Requirements

- Python 3.10 or later (developed and tested with 3.13, on Linux)
- The pinned packages in `requirements.txt`. Optional parts degrade gracefully:

| Package | Needed for | Without it |
| --- | --- | --- |
| fontTools, ufoLib2, ufo2ft, skia-pathops | everything | no build |
| ttfautohint-py | hinted TTF | TTFs are built unhinted |
| afdko (`otfautohint`) | hinted OTF | OTFs are built unhinted |
| brotli | WOFF2 | web fonts are skipped |

```sh
python -m venv .venv
. .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt afdko
```

## Build

```sh
python scripts/build-fonts.py                 # all ten styles: UFO, TTF, OTF, WOFF2 (about 30 s)
python scripts/build-fonts.py -w Regular Italic --no-otf --no-woff2     # fast loop while designing
python scripts/build-fonts.py --from-ufo      # compile sources/*.ufo as they are (after hand edits)
python scripts/build-fonts.py --root /tmp/out # build somewhere else
```

Style names for `-w`: `Light Regular Medium SemiBold Bold LightItalic Italic MediumItalic SemiBoldItalic BoldItalic`.

| Output | Location |
| --- | --- |
| UFO sources | `sources/VarcodaMono-<Style>.ufo` |
| TrueType, hinted | `fonts/VarcodaMono-<Style>.ttf` |
| OpenType/CFF, hinted | `fonts/otf/VarcodaMono-<Style>.otf` |
| Web fonts and stylesheet | `fonts/webfonts/VarcodaMono-<Style>.woff2`, `varcoda-mono.css` |

Two builds of the same sources on one machine are byte-identical (the timestamp is fixed; set
`SOURCE_DATE_EPOCH` to change it). With the pinned packages a build on Windows 11 reproduced the Linux files of
1.3.0 byte for byte; 1.4.0 was built on Windows 11 only; macOS has not been tried.

## Where the design lives

| File | Content |
| --- | --- |
| `scripts/fontsrc/params.py` | the grid, the weights and their pens, the italic angle |
| `scripts/fontsrc/geom.py`, `kit.py` | geometry: pens, strokes, boolean operations, shared parts (stems, arches, bowls, the blade cut) |
| `scripts/fontsrc/glyphs_*.py` | one function per glyph |
| `scripts/fontsrc/glyphs_liga.py` | ligatures, alternates, generated feature code |
| `scripts/fontsrc/glyphs_italic.py` | the written italic lowercase: exit strokes, branching arches, returning bowls |
| `scripts/fontsrc/italic.py` | the slant, and which glyphs stay upright |
| `scripts/fontsrc/build.py` | names, metrics, tables, compilation, hinting |

Change the version in `build.py` (`VERSION_MINOR`, `RELEASE`). Rename the family with
`python scripts/rename-family.py "New Name"`.

## Images, reports, release

```sh
python scripts/make-assets.py [--refs DIR]    # assets/*.png, logo.svg, banner.svg
python scripts/make-specimens.py              # specimens/specimen.png, code-samples.png
python scripts/make-regression.py [--refs DIR]# tests/visual-regression/
python tests/rendering-tests/make_page.py     # tests/rendering-tests/index.html
python scripts/make-release.py --project      # releases/VarcodaMono-<version>.zip (+ project archive)
```

`--refs DIR` points to reference fonts for the comparison images (`docs/COMPARISON.md`). The logo and banner
PNGs are rasterised from their SVGs by headless Chrome or Chromium (`google-chrome` or `chromium` on `PATH`);
without one they are skipped.

## Not built here

Nerd Font variants (`docs/NERD-FONTS.md`) and a variable font (`ROADMAP.md`).
