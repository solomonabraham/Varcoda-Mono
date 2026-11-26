# Security

## Scope

Varcoda Mono ships font files and the Python scripts that build them. Relevant security issues are:

- a font file from this project that crashes, hangs or corrupts memory in a font parser, shaper or rasteriser
  (FreeType, HarfBuzz, DirectWrite, Core Text, a browser);
- a build or test script that executes untrusted input or writes outside the project directory;
- a compromised release artifact (a file that does not match what the tagged sources build).

Ordinary rendering or design bugs are not security issues; please use a normal issue for those.

## Supported versions

Only the latest release receives fixes.

## Reporting

Please do **not** open a public issue. Use the repository's **Security → Report a vulnerability** form
(GitHub private vulnerability reporting). Include the font file or commit, the application and platform,
and steps to reproduce. You should get an acknowledgement within a week.

## Verifying a release

Builds are reproducible. Check out the tag, install the pinned versions from `requirements.txt`, run
`python scripts/build-fonts.py --root /tmp/check` and compare the files with the release. Two builds on
the same machine are byte-identical (this is tested); identity across operating systems and CPU
architectures has not been verified yet. All released fonts pass the OpenType Sanitizer as part of the
test-suite.
