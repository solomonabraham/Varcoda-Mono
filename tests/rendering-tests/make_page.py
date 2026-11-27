#!/usr/bin/env python3
"""Build tests/rendering-tests/index.html: a self-contained browser test page.

The ten TTFs are embedded as data: URIs, so the page works from any folder
and in any browser (no file:// font restrictions).  Open it on the machine
you want to check - e.g. in Chrome/Edge on Windows, which use the same
DirectWrite text stack as VS Code - and compare sizes, weights and features.

    python3 tests/rendering-tests/make_page.py
"""
from __future__ import annotations

import base64
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STYLES = [("Light", 300), ("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]

CODE = """<?php

final class ApplicationService
{
    public function execute(array $options): bool
    {
        $enabled = $options['enabled'] ?? false;

        if ($enabled !== true) {
            return false;
        }

        return true;
    }
}

const fn = (a, b) => a !== b && a >= 0 || b <= 0xFF ? a ?? b : a++ - --b; // -> => <=> != == ===
/* 0O 1lI| 5S 8B 2Z  `'"  .,:;  {}[]()<>  #@$%^&*_~\\ */"""

BOX = """┌──────────┬────────┬─────────┐  ╔══════╦══════╗  ╭──────╮
│ Style    │ Glyphs │ Status  │  ║ ▁▂▃▄ ║ ░▒▓█ ║  │ done │
├──────────┼────────┼─────────┤  ╠══════╬══════╣  ╰──────╯
│ Regular  │    610 │ ✓ ok    │  ║ ←↑→↓ ║ ≠≤≥∞ ║
└──────────┴────────┴─────────┘  ╚══════╩══════╝"""


def build() -> str:
    faces = []
    for style, weight in STYLES:
        for slope, name in (("normal", style), ("italic", "Italic" if style == "Regular" else style + "Italic")):
            with open(os.path.join(ROOT, "fonts", "ttf", "VarcodaMono-%s.ttf" % name), "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            faces.append('@font-face{font-family:"Varcoda Mono Test";font-weight:%d;font-style:%s;'
                         'src:url(data:font/ttf;base64,%s) format("truetype");}' % (weight, slope, b64))
    waterfall = "\n".join(
        '<div class="row" style="font-size:%dpx"><span class="tag">%dpx</span>'
        'for (let i = 0; i &lt; n; i++) { total += items[i].price * 1.07; }  // 0O 1lI| {}[]() !== =&gt;</div>' % (s, s)
        for s in (11, 12, 13, 14, 15, 16, 18, 20, 24))
    weights = "\n".join(
        '<div class="row" style="font-weight:%d;font-size:20px"><span class="tag wide">%s %d</span>'
        'The quick brown fox jumps over the lazy dog 0123456789</div>' % (w, s, w) for s, w in STYLES)
    italics = "\n".join(
        '<div class="row" style="font-size:%dpx"><span class="tag">%dpx</span>'
        '<i>// a quick fix for every file: handle the empty input, unify buffering (0O 1lI) -&gt; done</i></div>' % (s, s)
        for s in (12, 13, 14, 16, 20)) + "\n" + "\n".join(
        '<div class="row" style="font-weight:%d;font-size:20px"><span class="tag wide">%s %d</span>'
        'minimum quality <i>minimum quality</i>  final public <i>final public</i></div>' % (w, s, w) for s, w in STYLES)
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Varcoda Mono - rendering test</title>
<style>
%(faces)s
:root { color-scheme: dark; }
body { margin: 24px; background: #13151a; color: #d8dce5; font: 400 14px/1.5 "Varcoda Mono Test", monospace;
       font-feature-settings: "calt" 0; }
body.calt { font-feature-settings: "calt" 1; }
body.zero.calt { font-feature-settings: "calt" 1, "zero" 1; }
body.zero:not(.calt) { font-feature-settings: "calt" 0, "zero" 1; }
body.light { background: #fafaf8; color: #14161c; color-scheme: light; }
h1 { font-size: 30px; margin: 0 0 4px; }
h2 { font-size: 13px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; color: #5fd0c4;
     border-bottom: 1px solid #2c313c; padding-bottom: 6px; margin: 28px 0 12px; }
.row { white-space: pre; line-height: 1.6; }
.tag { display: inline-block; width: 9ch; color: #7a8396; font-size: 12px; font-weight: 400; }
.tag.wide { width: 13ch; }
pre { margin: 0; font: inherit; }
pre.box { line-height: normal; font-size: 18px; }
label { margin-right: 18px; cursor: pointer; }
#report { color: #7a8396; font-size: 12px; white-space: pre-wrap; }
.probe { position: absolute; left: -9999px; top: 0; white-space: pre; font-size: 16px; }
</style>
</head>
<body>
<h1>Varcoda Mono</h1>
<div>
  <label><input type="checkbox" id="t-calt"> ligatures (calt)</label>
  <label><input type="checkbox" id="t-zero"> slashed zero (zero)</label>
  <label><input type="checkbox" id="t-light"> light background</label>
</div>

<h2>Sizes</h2>
%(waterfall)s

<h2>Weights</h2>
%(weights)s

<h2>Italic</h2>
%(italics)s

<h2>Code</h2>
<pre id="code">%(code)s</pre>

<h2>Box drawing (line-height: normal)</h2>
<pre class="box">%(box)s</pre>

<h2>Report</h2>
<pre id="report">measuring...</pre>

<span class="probe" id="p-i">iiiiiiiiiiiiiiiiiiii</span>
<span class="probe" id="p-m">MMMMMMMMMMMMMMMMMMMM</span>
<span class="probe" id="p-op" style="font-feature-settings:'calt' 0">!== === =&gt; -&gt; &lt;=&gt; &amp;&amp; ||</span>
<span class="probe" id="p-lig" style="font-feature-settings:'calt' 1">!== === =&gt; -&gt; &lt;=&gt; &amp;&amp; ||</span>
<span class="probe" id="p-bold" style="font-weight:700">MMMMMMMMMMMMMMMMMMMM</span>
<span class="probe" id="p-line" style="font-size:20px;line-height:normal">Mg</span>
<span class="probe" id="p-ital" style="font-style:italic">fafafafafafafafafafa</span>

<script>
for (const [id, cls] of [["t-calt", "calt"], ["t-zero", "zero"], ["t-light", "light"]]) {
  document.getElementById(id).addEventListener("change", (e) => document.body.classList.toggle(cls, e.target.checked));
}
document.fonts.ready.then(() => {
  const w = (id) => document.getElementById(id).getBoundingClientRect().width;
  const report = {
    faces: [...document.fonts].map((f) => [f.family, f.weight, f.status, f.style]),
    width_i_x20: w("p-i"),
    width_M_x20: w("p-m"),
    width_bold_M_x20: w("p-bold"),
    width_italic_x20: w("p-ital"),
    width_operators_plain: w("p-op"),
    width_operators_ligatures: w("p-lig"),
    line_height_20px: document.getElementById("p-line").getBoundingClientRect().height,
    userAgent: navigator.userAgent,
  };
  document.getElementById("report").textContent = JSON.stringify(report, null, 1);
  document.body.dataset.done = "1";
});
</script>
</body>
</html>
""" % dict(faces="\n".join(faces), waterfall=waterfall, weights=weights, italics=italics, code=html.escape(CODE),
           box=html.escape(BOX))


def main():
    path = os.path.join(HERE, "index.html")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build())
    print("wrote", path, "%.0f kB" % (os.path.getsize(path) / 1024))


if __name__ == "__main__":
    main()
