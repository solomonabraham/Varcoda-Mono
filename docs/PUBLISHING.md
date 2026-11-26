# Before and after publishing

Nothing in this project has been committed, pushed or published. This is the list for the person who does.

## Before the repository goes public

- [ ] **Name.** Search GitHub, npm and Homebrew for `varcoda-mono`; decide whether a trademark search is needed
      (`docs/BRANDING.md`). To change the name: `python scripts/rename-family.py "New Name"` and rebuild.
- [ ] **Contact.** Put a contact address into `CODE_OF_CONDUCT.md`; enable *private vulnerability reporting*
      (Settings → Code security) because `SECURITY.md` relies on it.
- [ ] **Copyright line.** `LICENSE` and the fonts say "The Varcoda Mono Project Authors". Replace it with your
      name or organisation if you prefer (`COPYRIGHT` and `DESIGNER` in `scripts/fontsrc/build.py`, then rebuild).
- [ ] **Vendor ID.** `OS/2.achVendID` is `NONE`. Register a four-letter ID with Microsoft if you want one.
- [ ] **Real machines.** Install the TTFs on Windows and macOS; open `tests/rendering-tests/index.html`; look
      at 12–14 px in VS Code and a terminal, light and dark. Record the result in `QUALITY_REPORT.md`.
- [ ] `git init`, first commit, push; watch the *Build* and *Validate* workflows run for the first time.
- [ ] Tag `v1.2.0`; the *Release* workflow creates a **draft** release with the ZIP and
      `docs/RELEASE-NOTES-1.2.0.md`. Review it, then publish.

## Repository settings

- **Description:** A geometric monospaced typeface for code and terminals. Five weights, optional ligatures, OFL.
- **Topics:** `font` `typeface` `monospace` `monospaced-font` `programming-font` `coding-font` `developer-tools`
  `ligatures` `opentype` `terminal` `vscode` `open-source` `ofl` `ufo`
- **Social preview:** upload `assets/banner.png` (1280×640).
- Enable Discussions if you want a place for setups and questions (`SUPPORT.md` mentions it conditionally).

## Honest discoverability

Things that help people find and evaluate the font, in rough order of value:

1. **A release with a ZIP.** Most users never clone a font repository.
2. **A specimen people can try.** Enable GitHub Pages and publish `tests/rendering-tests/index.html` or a small
   page that loads `fonts/webfonts/varcoda-mono.css`, with an editable code sample and feature toggles.
3. **Package managers**, once there is a tagged release: a Homebrew cask (`font-varcoda-mono`), Scoop, winget,
   AUR (`ttf-varcoda-mono`), Nixpkgs, and npm for the web fonts.
   Each has its own submission and review process; none has been started.
4. **Fontsource and Google Fonts.** Both require open sources and a certain glyph and quality baseline;
   Google Fonts in particular expects fontbakery's `googlefonts` profile to pass and usually asks for wider
   Latin coverage. Treat as later goals.
5. **Listings** that accept submissions: Programming Fonts (app.programmingfonts.org), coding-font comparison
   sites, awesome-lists for fonts and terminals.
6. **Screenshots in real editors**, light and dark, in the README, once they exist.

Not to do: buying or exchanging stars, automated starring, sock-puppet posts, or claims the fonts do not
back up ("variable", "italic", "Nerd Font", "tested on Windows") before those are true.
