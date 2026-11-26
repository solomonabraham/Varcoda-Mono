#!/usr/bin/env python3
"""Report whether the weights are point-compatible (the precondition for a
variable font with a weight axis).

    python scripts/check-interpolation.py [--list]

For every glyph the outline structure (contours, points per contour, segment
types, components) is compared across all weights.  Exit status 0 only when
every glyph is compatible.
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fontsrc import geom, params  # noqa: E402
from fontsrc.draw import draw_master  # noqa: E402
from fontsrc.geom import Shape  # noqa: E402


def signature(res):
    if not isinstance(res, Shape):
        return ("composite", tuple(res.parts))
    return tuple(tuple(seg[0] for seg in contour) for contour in res.contours)


def check(min_segment=None):
    if min_segment is not None:
        geom.MIN_SEGMENT = min_segment
    masters = [draw_master(params.Master(*w)) for w in params.WEIGHTS]
    bad = collections.OrderedDict()
    for name in masters[0]:
        sigs = [signature(m[name]) for m in masters]
        if len(set(sigs)) > 1:
            if sigs[0][0] == "composite":
                kind = "components"
            elif len({len(s) for s in sigs}) > 1:
                kind = "contour count"
            elif len({tuple(len(c) for c in s) for s in sigs}) > 1:
                kind = "point count"
            else:
                kind = "segment types"
            bad[name] = kind
    return len(masters[0]), bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print every incompatible glyph")
    ap.add_argument("--min-segment", type=float, default=None, help="experiment: override geom.MIN_SEGMENT")
    args = ap.parse_args()
    total, bad = check(args.min_segment)
    kinds = collections.Counter(bad.values())
    print("%d glyphs, %d weights: %d compatible, %d not (%s)" % (
        total, len(params.WEIGHTS), total - len(bad), len(bad),
        ", ".join("%s: %d" % kv for kv in sorted(kinds.items())) or "-"))
    if args.list:
        for name, kind in bad.items():
            print("  %-32s %s" % (name, kind))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
