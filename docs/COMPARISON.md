# Comparing with other fonts

Varcoda Mono was measured against JetBrains Mono, Fira Code and Iosevka to find out where it fell short
(`docs/history/AUDIT-1.000.md`, `QUALITY_REPORT.md`). Those fonts were **only measured and rendered**. No outline, metric table
or feature code was copied from them.

## Getting the reference fonts

They are not part of this repository. One way to obtain them (all three are OFL 1.1):

```sh
mkdir refs && cd refs
npm init -y
npm install --ignore-scripts @fontsource/jetbrains-mono @fontsource/fira-code @fontsource/iosevka
```

Convert the `latin-400-normal.woff2` file of each package to TTF, for example with fontTools:

```python
from fontTools.ttLib import TTFont
f = TTFont("node_modules/@fontsource/fira-code/files/fira-code-latin-400-normal.woff2")
f.flavor = None
f.save("ttf/FiraCode-Regular.ttf")
```

and name the results `JetBrainsMono-Regular.ttf`, `FiraCode-Regular.ttf`, `Iosevka-Regular.ttf`.
The measurements in this repository used version 5.3.0 of the three packages.

## Running the comparison

```sh
python scripts/compare-fonts.py fonts/ttf/VarcodaMono-Regular.ttf refs/ttf/JetBrainsMono-Regular.ttf refs/ttf/FiraCode-Regular.ttf
python scripts/make-assets.py --refs refs/ttf --only comparison     # assets/comparison.png
python scripts/make-regression.py --refs refs/ttf                   # density table
```

`compare-fonts.py` reports, in thousandths of the em: vertical metrics, stem and counter widths, a rhythm
figure (variation of the white gaps between stems), ink widths and side bearings of narrow and wide
letters, the size of punctuation marks, and the vertical centre of operators and brackets.

## Limits of the method

- The `@fontsource` files are web subsets and may be hinted differently from the desktop releases.
- Rendering is FreeType greyscale. DirectWrite and Core Text will give different pixels.
- Numbers describe geometry; they do not decide taste. They were used to find outliers, not to converge on
  another design.
