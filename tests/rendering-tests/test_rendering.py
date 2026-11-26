"""Rendering tests on the compiled fonts.

    python3 -m pytest tests/rendering-tests -q

* FreeType (hinted, grey-scale) at 12-16 px: grid alignment, baseline and
  x-height consistency, legibility of look-alikes.  Proof images are written
  to tests/rendering-tests/proofs/.
* Chromium, if a Chrome/Chromium binary is installed: loads the fonts as web
  fonts (same text stack as VS Code / Electron), checks that all four faces
  load, that the cell width is constant and that ligatures do not change it,
  and saves a screenshot.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)

from fontsrc.render import FontRenderer, new_canvas, render_lines, to_image  # noqa: E402

STYLES = ["Light", "Regular", "Medium", "SemiBold", "Bold"]
SIZES = [12, 13, 14, 15, 16]
OUT = os.path.join(HERE, "proofs")
os.makedirs(OUT, exist_ok=True)


def ttf(style):
    return os.path.join(ROOT, "fonts", "VarcodaMono-%s.ttf" % style)


def ink(style, px, text, features=None):
    """coverage array (0..1) of one line rendered white on black"""
    r = FontRenderer(ttf(style), px)
    h = r.ascent + r.descent + 8
    cv = new_canvas(r.cell * len(text) + 8, h, (0, 0, 0))
    r.draw(cv, 4, 4 + r.ascent, text, (255, 255, 255), features or {"calt": False})
    return cv[:, :, 0] / 255.0, r


SAMPLE = ["final class ApplicationService {",
          "    public function execute(array $options): bool {",
          "        $enabled = $options['enabled'] ?? false;",
          "        if ($enabled !== true && $n >= 10) { return false; }",
          "        return $this->items[0] != null || x <= 0xFF; // 0O 1lI| 5S 8B",
          "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789",
          "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~  ÀÉÎÕÜ àéîõü ß ø æ ç ñ  €£¥  ←→ ≠≤≥"]


@pytest.mark.parametrize("style", STYLES)
def test_waterfall_proofs(style):
    """write a proof image per style; every line must contain ink"""
    from PIL import Image
    imgs = []
    for px in SIZES:
        img = render_lines(ttf(style), px, ["%d px" % px] + SAMPLE, features={"calt": False}, zoom=2)
        arr = np.asarray(img).astype(int)
        assert (arr.max(axis=2) > 120).sum() > 2000, "almost no ink at %d px" % px
        imgs.append(img)
    w, h = max(i.width for i in imgs), sum(i.height for i in imgs)
    sheet = Image.new("RGB", (w, h), (24, 26, 31))
    y = 0
    for i in imgs:
        sheet.paste(i, (0, y))
        y += i.height
    sheet.save(os.path.join(OUT, "waterfall-%s.png" % style.lower()))


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("px", SIZES)
def test_grid_alignment(style, px):
    """a run of vertical bars lands on the same pixel column in every cell"""
    cov, r = ink(style, px, "||||||||||||")
    cols = cov.sum(axis=0)
    cells = [cols[4 + i * r.cell: 4 + (i + 1) * r.cell] for i in range(12)]
    for c in cells[1:]:
        assert np.allclose(c, cells[0], atol=1e-3), "bars are not identical from cell to cell"
    assert cells[0].max() > 0.3 * cov.shape[0] * 0.5, "bar is too faint"


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("px", SIZES)
def test_baseline_and_xheight_are_consistent(style, px):
    """hinting must put flat letters on one baseline and one x-height row"""
    def rows(ch):
        cov, r = ink(style, px, ch)
        ys = np.where(cov.max(axis=1) > 0.35)[0]
        return ys.min(), ys.max()

    tops = {ch: rows(ch)[0] for ch in "xnzvuri"}       # i: its head serif sits on the x-height
    bottoms = {ch: rows(ch)[1] for ch in "xnzhklHLEZ"}
    assert len(set(v for k, v in tops.items() if k != "i")) == 1, ("x-height rows differ", tops)
    assert len(set(bottoms.values())) == 1, ("baseline rows differ", bottoms)
    cap = {ch: rows(ch)[0] for ch in "HEZTLN"}
    assert len(set(cap.values())) == 1, ("cap-height rows differ", cap)


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("px", SIZES)
def test_lookalikes_stay_distinct_at_small_sizes(style, px):
    """Hinted bitmaps of look-alike characters must differ clearly: by at
    least 1.5 pixels of ink *and* by 30 % of the ink of the smaller glyph
    (identical drawings score 0 %, the closest real pair here - 8/B at 12 px -
    scores 37 %; tiny marks such as . , ` ' only have 1-3 pixels of ink)."""
    def bitmap(ch):
        cov, r = ink(style, px, ch)
        return cov

    for a, b in [("0", "O"), ("1", "l"), ("1", "I"), ("l", "I"), ("l", "|"), ("5", "S"), ("8", "B"), (".", ","),
                 (":", ";"), ("`", "'"), ("2", "Z"), ("{", "("), ("}", ")"), ("1", "|"), ("I", "|"), ("'", '"'), ("y", "v"), ("y", "g"), ("q", "p")]:
        ba, bb = bitmap(a), bitmap(b)
        d = np.abs(ba - bb).sum()
        rel = d / min(ba.sum(), bb.sum())
        msg = "%r and %r differ by only %.1f px of ink (%.0f %%) at %d px (%s)" % (a, b, d, 100 * rel, px, style)
        assert d >= 1.5 and rel >= 0.30, msg


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("px", [12, 13, 14])
def test_adjacent_letters_do_not_fuse(style, px):
    """'rn' must not read as 'm' and 'cl' not as 'd': on a fixed grid they
    already take two cells, so what can go wrong is the two letters touching.
    Between them there must be a column that stays (almost) empty over the
    whole x-height zone."""
    r = FontRenderer(ttf(style), px)
    for pair in ("rn", "cl", "vv", "nn"):
        cv = new_canvas(r.cell * 2 + 8, px * 2, (0, 0, 0))
        base = int(px * 1.5)
        r.draw(cv, 4, base, pair, (255, 255, 255), {"calt": False})
        cov = cv[:, :, 0] / 255.0
        xh_rows = cov[base - round(px * 0.54):base, :]
        cols = xh_rows.max(axis=0)
        seam = 4 + r.cell
        assert cols[seam - 2:seam + 3].min() < 0.35, "%r fuses at %d px (%s): %s" % (
            pair, px, style, np.round(cols[seam - 2:seam + 3], 2))


@pytest.mark.parametrize("style", ["Regular", "Bold"])
def test_ligatures_draw_inside_their_cells(style):
    """with calt on, ink never spills into the neighbouring characters"""
    for px in (14, 16, 20):
        for seq in ["!=", "===", "=>", "->", "<=", ">=", "&&", "||", "<=>", "/*", "::", ":=", "**", "?.", "+=", "-="]:
            text = "H" + seq + "H"
            on, r = ink(style, px, text, {"calt": True})
            off, _ = ink(style, px, text, {"calt": False})
            first = slice(4, 4 + r.cell)
            last = slice(4 + (len(text) - 1) * r.cell, 4 + len(text) * r.cell)
            assert np.allclose(on[:, first], off[:, first], atol=0.02), (seq, px, "ligature touches the left neighbour")
            assert np.allclose(on[:, last], off[:, last], atol=0.02), (seq, px, "ligature touches the right neighbour")
            assert on.shape == off.shape


def test_box_drawing_tiles_without_seams():
    """stacked box characters form unbroken lines at the font's own line
    height: along a line the ink never dips (a seam would be a dark row)"""
    for style in ("Light", "Regular", "Bold"):
        for px in (12, 13, 14, 15, 16, 18, 20, 30):
            r = FontRenderer(ttf(style), px)
            lh = r.ascent + r.descent
            cv = new_canvas(r.cell * 6 + 8, lh * 4 + 8, (0, 0, 0))
            for row in range(4):
                r.draw(cv, 4, 4 + row * lh + r.ascent, "│█║┼──", (255, 255, 255))
            cov = cv[:, :, 0] / 255.0
            body = cov[4:4 + lh * 4]
            for col_cell, name in ((0, "│"), (1, "█"), (2, "║")):
                strip = body[:, 4 + col_cell * r.cell: 4 + (col_cell + 1) * r.cell].max(axis=1)
                assert strip.min() > 0.9 * np.median(strip), "vertical seam in %s at %d px (%s)" % (name, px, style)
            run = body[: lh, 4 + 4 * r.cell: 4 + 6 * r.cell].max(axis=0)
            assert run.min() > 0.85 * np.median(run), "horizontal seam in ── at %d px (%s)" % (px, style)


# --------------------------------------------------------------------------
# Chromium
# --------------------------------------------------------------------------
def _chrome():
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    return None


@pytest.fixture(scope="module")
def page():
    import make_page
    make_page.main()
    return os.path.join(HERE, "index.html")


def test_chromium_loads_the_fonts_and_keeps_the_grid(page):
    chrome = _chrome()
    if not chrome:
        pytest.skip("no Chrome/Chromium binary available")
    base = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", "--virtual-time-budget=8000"]
    dom = subprocess.run(base + ["--dump-dom", "file://" + page], capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<pre id="report">(.*?)</pre>', dom, re.S)
    assert m, "page did not produce a report"
    import html as _html
    rep = json.loads(_html.unescape(m.group(1)))
    faces = {(f[1], f[2]) for f in rep["faces"]}
    assert faces == {("300", "loaded"), ("400", "loaded"), ("500", "loaded"), ("600", "loaded"), ("700", "loaded")}, rep["faces"]
    cell = 16 * 0.6
    assert abs(rep["width_i_x20"] - 20 * cell) < 0.05, rep
    assert abs(rep["width_M_x20"] - 20 * cell) < 0.05, rep
    assert abs(rep["width_bold_M_x20"] - 20 * cell) < 0.05, rep
    assert abs(rep["width_operators_plain"] - rep["width_operators_ligatures"]) < 0.01, "ligatures change the width"
    assert abs(rep["line_height_20px"] - 20 * 1.23) < 1.0, rep          # hhea/typo line box
    shot = os.path.join(OUT, "chromium.png")
    subprocess.run(base + ["--window-size=1280,1900", "--screenshot=" + shot, "file://" + page],
                   capture_output=True, timeout=120)
    assert os.path.getsize(shot) > 20000
    with open(os.path.join(OUT, "chromium-report.json"), "w") as fh:
        json.dump(rep, fh, indent=1)


SYSTEM_PAGE = """<!doctype html><meta charset="utf-8">
<style>body{font:400 16px/1.5 "Varcoda Mono";font-feature-settings:"calt" 0}.p{position:absolute;left:-9999px;white-space:pre}</style>
<p style="font-weight:300">Light const fn = (a, b) =&gt; a !== b;</p><p>Regular 0O 1lI|</p>
<p style="font-weight:500">Medium</p><p style="font-weight:700">Bold</p>
<span class="p" id="a">iiiiiiiiii</span><span class="p" id="b" style="font-weight:700">WWWWWWWWWW</span>
<span class="p" id="c" style="font-family:serif">iiiiiiiiii</span>
<span class="p" id="d" style="font-feature-settings:'calt' 1">!== =&gt; -&gt; &lt;=&gt;</span>
<span class="p" id="e">!== =&gt; -&gt; &lt;=&gt;</span>
<pre id="report"></pre>
<script>document.fonts.ready.then(()=>{const w=id=>document.getElementById(id).getBoundingClientRect().width;
document.getElementById("report").textContent=JSON.stringify({light:document.fonts.check('300 16px "Varcoda Mono"'),
regular:document.fonts.check('16px "Varcoda Mono"'),i10:w("a"),W10bold:w("b"),serif_i10:w("c"),lig:w("d"),plain:w("e")});});</script>
"""


def test_installed_fonts_work_as_system_fonts_in_chromium(tmp_path):
    """Install the TTFs into a scratch font directory (the user's own fonts
    are not touched) and let fontconfig and Chromium use them by family name,
    the way VS Code on Linux finds an installed font."""
    chrome = _chrome()
    if not chrome or not shutil.which("fc-list"):
        pytest.skip("needs fontconfig and a Chrome/Chromium binary")
    # fontconfig's standard configuration scans $XDG_DATA_HOME/fonts: pointing
    # it at a scratch directory "installs" the fonts for these processes only
    fonts = tmp_path / "data" / "fonts"
    fonts.mkdir(parents=True)
    for style in STYLES:
        shutil.copy(ttf(style), fonts / os.path.basename(ttf(style)))
    env = dict(os.environ, XDG_DATA_HOME=str(tmp_path / "data"), XDG_CACHE_HOME=str(tmp_path / "cache"))
    listing = subprocess.run(["fc-list", "Varcoda Mono", "family", "style", "spacing", "weight"], capture_output=True,
                             text=True, env=env).stdout
    lines = sorted(set(l for l in listing.splitlines() if "Varcoda Mono" in l))
    assert len(lines) == len(STYLES), listing
    assert all("spacing=100" in l for l in lines), "fontconfig does not classify the family as monospaced"
    assert {re.search(r"weight=(\d+)", l).group(1) for l in lines} == {"50", "80", "100", "180", "200"}   # light, regular, medium, semibold, bold
    match = subprocess.run(["fc-match", "Varcoda Mono:bold", "file"], capture_output=True, text=True, env=env).stdout
    assert "VarcodaMono-Bold.ttf" in match

    page = tmp_path / "system.html"
    page.write_text(SYSTEM_PAGE, encoding="utf-8")
    dom = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=6000",
                          "--user-data-dir=%s" % (tmp_path / "profile"), "--dump-dom", "file://%s" % page],
                         capture_output=True, text=True, timeout=120, env=env).stdout
    m = re.search(r'<pre id="report">(.*?)</pre>', dom, re.S)
    assert m and m.group(1).strip(), "no report from Chromium"
    import html as _html
    rep = json.loads(_html.unescape(m.group(1)))
    assert rep["light"] and rep["regular"], rep
    assert abs(rep["i10"] - 96) < 0.1 and abs(rep["W10bold"] - 96) < 0.1, rep       # 10 cells of 0.6 em at 16 px
    assert abs(rep["serif_i10"] - rep["i10"]) > 5, "the page fell back to another font"
    assert abs(rep["lig"] - rep["plain"]) < 0.01, rep
