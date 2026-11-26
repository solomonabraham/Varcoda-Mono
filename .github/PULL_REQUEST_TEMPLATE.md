## What and why

<!-- The problem first, then the change. Link the issue if there is one. -->

## Evidence

<!-- For visual changes: before/after images (python scripts/make-regression.py) and what you measured. -->

## Checklist

- [ ] `python scripts/build-fonts.py` and `python -m pytest tests` pass
- [ ] Looked at Light and Bold, not only Regular
- [ ] Every glyph is still 600 units wide; ligatures keep one cell per character
- [ ] New feature or glyph has a test
- [ ] Regenerated `sources/` and `fonts/` are committed with the script change
- [ ] `CHANGELOG.md` updated
- [ ] No outlines copied from other typefaces
