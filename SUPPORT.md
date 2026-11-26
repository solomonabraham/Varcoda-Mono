# Support

**Before opening an issue**

- Installation, editor and terminal settings: see the README.
- "The ligatures don't show" / "I don't want ligatures": they are controlled by the application
  (`editor.fontLigatures` in VS Code, *Enable ligatures* in JetBrains IDEs, the `calt` feature in terminals).
- "Bold looks wrong / is synthesised": install all five weights, then restart the application.
- "The font does not appear in the list": restart the application; on Linux run `fc-cache -f` and check
  `fc-list "Varcoda Mono"`.
- Icons in a prompt show as boxes: only the core Powerline symbols are built in; see `docs/NERD-FONTS.md`.

**Where to ask**

| For | Use |
| --- | --- |
| A glyph that looks wrong, a rendering problem | an issue with the *Rendering issue* template and a screenshot |
| A bug in the build scripts or tests | an issue with the *Bug report* template |
| A missing character or feature | an issue with the *Glyph or feature request* template |
| A question or a setup that works and is worth sharing | GitHub Discussions, if enabled for the repository |
| A security problem | `SECURITY.md` |

This is a volunteer project without guaranteed response times.
