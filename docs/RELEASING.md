# Releasing

For maintainers: how a version gets from this repository to the release page, and how the repository itself is
set up.

## A release, step by step

Tags are the bare version: `1.5.0`, not `v1.5.0`.

1. **Version.** Set `VERSION_MINOR` and `RELEASE` in `scripts/fontsrc/build.py`. Put the date on the heading in
   `CHANGELOG.md` and write `docs/history/RELEASE-NOTES-<version>.md`; that file becomes the text of the release.
2. **Build and check.**

   ```sh
   python scripts/build-fonts.py
   python -m pytest tests
   python tests/font-validation/validate.py
   ```

3. **Regenerate what shows the fonts:** `scripts/make-assets.py`, `scripts/make-specimens.py`,
   `scripts/make-regression.py`, `tests/rendering-tests/make_page.py`. Update the numbers in
   `docs/QUALITY_REPORT.md`.
4. **Commit and push** the sources, the fonts and the pictures together, and wait for *Build* and *Validate* to
   pass. *Build* fails if a committed font is not what the sources produce.
5. **Tag and push the tag:** `git tag 1.5.0 && git push origin 1.5.0`. The *Release* workflow checks that the tag
   matches the version in the sources, rebuilds, tests, and creates a **draft** release with
   `VarcodaMono-<version>.zip`, `VarcodaMono-<version>-web.zip` and `SHA256SUMS`.
6. **Nerd Font archive.** The workflow does not build it. Run `python scripts/make-nerd-fonts.py` (Docker), attach
   `releases/VarcodaMonoNerdFont-<version>.zip` to the draft, and append its checksum to the draft's `SHA256SUMS`
   (`sha256sum VarcodaMonoNerdFont-<version>.zip`).
7. **Read the draft, then publish it.**

To release without the workflow, run steps 1 to 4, then `python scripts/make-nerd-fonts.py`,
`python scripts/make-release.py`, and upload the four files in `releases/` by hand:

```sh
gh release create 1.5.0 releases/VarcodaMono-1.5.0.zip releases/VarcodaMono-1.5.0-web.zip \
  releases/VarcodaMonoNerdFont-1.5.0.zip releases/SHA256SUMS \
  --draft --title "Varcoda Mono 1.5.0" --notes-file docs/history/RELEASE-NOTES-1.5.0.md
```

### What users see on the release page

| Asset | Role |
| --- | --- |
| `VarcodaMono-<version>.zip` | the recommended download: desktop fonts (TTF, OTF), web fonts, licence, install guide |
| `VarcodaMono-<version>-web.zip` | web fonts only |
| `VarcodaMonoNerdFont-<version>.zip` | the patched family for prompts with icons |
| `SHA256SUMS` | checksums |
| *Source code* (zip, tar.gz) | added by GitHub: the sources at the tag |

## Repository settings

These live on GitHub, not in the repository.

| Setting | Value |
| --- | --- |
| Description | A squared, technical monospaced typeface for code and terminals. Five weights with written italics, 29 cell-preserving ligatures, OFL. |
| Topics | `font` `fonts` `typeface` `typography` `monospace` `monospaced-font` `programming-font` `coding-font` `ligatures` `opentype` `terminal` `vscode` `developer-tools` `open-source` `ofl` `ufo` |
| Social preview | upload `assets/banner.png` (1280 × 640) under *Settings → General → Social preview* |
| Private vulnerability reporting | **on** (*Settings → Code security*): `SECURITY.md` sends reporters to that form |
| Discussions | optional; `SUPPORT.md` mentions them conditionally |

```sh
gh repo edit solomonabraham/Varcoda-Mono \
  --description "A squared, technical monospaced typeface for code and terminals. Five weights with written italics, 29 cell-preserving ligatures, OFL." \
  --add-topic font,fonts,typeface,typography,monospace,monospaced-font,programming-font,coding-font,ligatures,opentype,terminal,vscode,developer-tools,open-source,ofl,ufo
gh api -X PUT repos/solomonabraham/Varcoda-Mono/private-vulnerability-reporting
```

## Open decisions

- **Contact.** `CODE_OF_CONDUCT.md` names the maintainer's GitHub profile. A dedicated address is better if the
  project grows.
- **Copyright holder.** `LICENSE` and the fonts say "The Varcoda Mono Project Authors". To name a person or an
  organisation instead, change `COPYRIGHT` and `DESIGNER` in `scripts/fontsrc/build.py` and the first line of
  `LICENSE`, then rebuild.
- **Vendor ID.** `OS/2.achVendID` is `NONE`. Microsoft registers four-letter vendor IDs free of charge.
- **Name clearance.** No trademark search was made (`BRANDING.md`).

## Being found, honestly

In rough order of value:

1. **Releases with files attached.** Most people never clone a font repository.
2. **Screenshots from real editors,** light and dark, on Windows and macOS, in the README once they exist.
3. **A page to try the font.** GitHub Pages with an editable code sample that loads `fonts/webfonts/varcoda-mono.css`.
4. **Package managers,** each with its own submission process; none has been started: a Homebrew cask
   (`font-varcoda-mono`), Scoop, winget, AUR (`ttf-varcoda-mono`), Nixpkgs, and npm or Fontsource for the web fonts.
5. **Listings that accept submissions:** Programming Fonts (programmingfonts.org), coding-font comparison sites,
   awesome-lists for fonts and terminals.
6. **Google Fonts** expects fontbakery's `googlefonts` profile to pass and usually wider Latin coverage. A later
   goal.

Not to do: buying or exchanging stars, automated starring, sock-puppet posts, invented testimonials or download
numbers, or claims the fonts do not back up ("variable", "tested on macOS") before they are true.
