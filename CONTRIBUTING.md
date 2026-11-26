# Contributing to Varcoda Mono

Thank you for helping. This project is small; the most valuable contributions are, in this order:

1. **Rendering reports from real machines**, especially Windows (VS Code, Windows Terminal, PowerShell,
   JetBrains IDEs) and macOS. Nothing has been verified there yet.
2. **Bug reports** about a specific glyph: wrong shape, collision, something that looks off at a given size.
3. **Fixes** to the drawing code, with before/after images.
4. **Glyph requests** with a concrete use case.

By taking part you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting a rendering problem

Use the *Rendering issue* template. A report is only actionable with: operating system and version,
application and version, font size and weight, display scaling, whether ligatures were on, and a
**screenshot at 100 % zoom** (no photos of screens). Opening `tests/rendering-tests/index.html` in a browser
and attaching a screenshot of it is a quick way to give all of that at once.

## Changing the design

The fonts are generated. Do not edit files in `fonts/`; edit the program that draws them.

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/build-fonts.py -w Regular --no-otf   # fast loop: one weight, TTF only
python scripts/build-fonts.py                       # everything
python -m pytest tests
```

- `scripts/fontsrc/params.py`: the grid (advance, heights, axis) and the pens of each weight.
- `scripts/fontsrc/glyphs_*.py`: one function per glyph, registered with `@g("name")`. A function receives a
  `Master` and returns a `Shape`. Use the helpers in `kit.py` (stems, arches, bowls, dots) so that new glyphs
  inherit the family's construction.
- `scripts/fontsrc/glyphs_liga.py`: ligatures, stylistic alternates and the generated feature code.

Rules that the tests enforce and reviews will ask for:

- Every glyph is exactly 600 units wide and stays inside its cell (ligatures: inside their *n* cells).
- A change must work in **all five weights**; look at Light and Bold, not just Regular.
- Do not copy outlines from other typefaces. Measuring and comparing is fine (`scripts/compare-fonts.py`).
- A new feature needs a test. A size or spacing change needs numbers: say what you measured.
- Do not renumber or repurpose existing stylistic sets.
- Keep `python scripts/check-interpolation.py` from getting worse (it prints how many glyphs are
  interpolation-compatible); the goal is zero incompatible glyphs.

## Pull requests

- One topic per pull request. Describe the problem, then the change.
- Attach before/after images for anything visual: `python scripts/make-regression.py` or a crop from
  `scripts/make-assets.py`.
- Run `python -m pytest tests`. If fontbakery is installed, `python tests/font-validation/validate.py` too.
- Commit the regenerated `sources/` and `fonts/` together with the script change, so the repository always
  contains fonts that match its sources. Builds are reproducible, so reviewers can verify this.
- Add a line to `CHANGELOG.md` under the unreleased heading.

## Releases (maintainers)

1. Update `VERSION_MINOR` and `RELEASE` in `scripts/fontsrc/build.py`, and `CHANGELOG.md`.
2. `python scripts/build-fonts.py && python -m pytest tests && python tests/font-validation/validate.py`
3. `python scripts/make-assets.py && python scripts/make-specimens.py && python scripts/make-release.py`
4. Tag `vX.Y.Z`. The release workflow rebuilds, tests and attaches the ZIP.

## License of contributions

Contributions are accepted under the SIL Open Font License 1.1, the license of the project.
