#!/usr/bin/env python3
"""Build the Varcoda Mono family.

    python3 scripts/build-fonts.py                 # generate sources + all fonts
    python3 scripts/build-fonts.py --from-ufo      # compile the UFOs in sources/ as they are
    python3 scripts/build-fonts.py -w Regular Bold # only some styles
    python3 scripts/build-fonts.py --no-otf --no-hint

Outputs
    sources/VarcodaMono-<Style>.ufo    editable sources (UFO 3)
    fonts/ttf/VarcodaMono-<Style>.ttf  TrueType, hinted with ttfautohint
    fonts/otf/VarcodaMono-<Style>.otf  OpenType/CFF, hinted with AFDKO otfautohint when it is installed
"""
from __future__ import annotations

import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import ufoLib2  # noqa: E402

from fontsrc import build, params  # noqa: E402
from fontsrc.draw import draw_master  # noqa: E402
from fontsrc.italic import italicize  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-w", "--weights", nargs="+", default=[w[0] for w in params.WEIGHTS] + [i[0] for i in params.ITALICS],
                    help="styles to build, e.g. Regular BoldItalic (default: all uprights and italics)")
    ap.add_argument("--from-ufo", action="store_true",
                    help="do not regenerate the UFOs; compile the (possibly hand-edited) sources as they are")
    ap.add_argument("--no-otf", action="store_true", help="skip the OpenType/CFF fonts")
    ap.add_argument("--no-woff2", action="store_true", help="skip the WOFF2 web fonts")
    ap.add_argument("--no-hint", action="store_true", help="skip autohinting (ttfautohint for TTF, otfautohint for OTF)")
    ap.add_argument("--root", default=ROOT, help="project directory (default: the parent of scripts/)")
    args = ap.parse_args(argv)

    known = {w[0]: (w, False) for w in params.WEIGHTS}
    known.update({i[0]: (i[1:], True) for i in params.ITALICS})
    for style in args.weights:
        if style not in known:
            ap.error("unknown style %r (choose from %s)" % (style, ", ".join(known)))

    t_all = time.time()
    for style in args.weights:
        t0 = time.time()
        (name, wclass, stem), italic = known[style]
        src = build.ufo_path(args.root, style)
        if args.from_ufo:
            if not os.path.isdir(src):
                sys.exit("missing source: %s" % src)
            ufo = ufoLib2.Font.open(src)
            n_glyphs = len(ufo)
        else:
            m = params.Master(name, wclass, stem, italic)
            glyphs = draw_master(m)
            if italic:
                glyphs = italicize(m, glyphs)
            ufo = build.make_ufo(m, glyphs)
            build.write_ufo(ufo, src)
            n_glyphs = len(glyphs)
        ttf = os.path.join(args.root, "fonts", "ttf", "%s-%s.ttf" % (build.PS_FAMILY, style))
        status = build.compile_ttf(ufo, ttf, hint=not args.no_hint)
        msg = "%-14s %4d glyphs  ttf: %s" % (style, n_glyphs, status)
        if not args.no_woff2:
            woff = os.path.join(args.root, "fonts", "webfonts", "%s-%s.woff2" % (build.PS_FAMILY, style))
            msg += "  woff2: %s" % build.compile_woff2(ttf, woff)
        if not args.no_otf:
            otf = os.path.join(args.root, "fonts", "otf", "%s-%s.otf" % (build.PS_FAMILY, style))
            msg += "  otf: %s" % build.compile_otf(ufo, otf, hint=not args.no_hint)
        print("%s  (%.1fs)" % (msg, time.time() - t0))
    if not args.no_woff2:
        build.write_webfont_css(args.root, params.WEIGHTS)
    print("done in %.1fs" % (time.time() - t_all))


if __name__ == "__main__":
    main()
