"""Draw every registered glyph for one master."""
from __future__ import annotations

import importlib

from .geom import Shape, finalize
from .kit import GLYPHS, ORDER, Composite

MODULES = ["glyphs_lower", "glyphs_upper", "glyphs_punct", "glyphs_marks", "glyphs_symbols", "glyphs_box", "glyphs_term", "glyphs_liga"]


def load_modules():
    for name in MODULES:
        importlib.import_module("." + name, __package__)


def draw_master(m, only=None):
    """-> dict name -> Shape | Composite (finalized outlines)"""
    load_modules()
    out = {}
    for name in ORDER:
        if only and name not in only:
            continue
        res = GLYPHS[name]["func"](m)
        if isinstance(res, Shape):
            res = finalize(res)
        out[name] = res
    return out


def cmap():
    load_modules()
    cm = {}
    for name in ORDER:
        for cp in GLYPHS[name]["unicodes"]:
            cm[chr(cp)] = name
    return cm


def resolve(glyphs):
    """flatten composites into plain shapes (for proofs and metrics)"""
    out = {}

    def get(name):
        if name in out:
            return out[name]
        gl = glyphs[name]
        if isinstance(gl, Composite):
            sh = Shape()
            for part, dx, dy in gl.parts:
                p = get(part)
                sh = Shape(sh.contours + p.move(dx, dy).contours)
            gl = sh
        out[name] = gl
        return gl

    for name in glyphs:
        get(name)
    return out
