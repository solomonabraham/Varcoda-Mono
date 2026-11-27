"""Checks on the repository around the fonts: the documentation points at things that exist, its
configuration examples parse and name the family correctly, and the release archives hold what
the README promises."""
import importlib.util
import json
import os
import re
import sys
import zipfile

try:
    import tomllib
except ImportError:          # Python 3.10
    tomllib = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from fontsrc import build  # noqa: E402

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "refs", "build", "releases", "sources", "__pycache__", ".pytest_cache"}
STYLES = ["Light", "Regular", "Medium", "SemiBold", "Bold", "LightItalic", "Italic", "MediumItalic", "SemiBoldItalic", "BoldItalic"]
# the record of earlier versions names files where they were at the time
HISTORY = ("CHANGELOG.md", "docs/history/")
# written by the build or by a tool, not committed
GENERATED = ("releases/", "build/", "refs/", "tests/rendering-tests/proofs/", "fonts/webfonts/*", ".venv")


def docs():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(base, f)
                with open(path, encoding="utf-8") as fh:
                    yield os.path.relpath(path, ROOT).replace(os.sep, "/"), fh.read()


def anchors(text):
    """the anchors GitHub generates for the headings of a Markdown file"""
    out = set()
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*$", re.sub(r"```.*?```", "", text, flags=re.S), flags=re.M):
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title).replace("`", "")
        out.add(re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-"))
    return out


def test_links_in_the_documentation_resolve():
    texts = dict(docs())
    broken = []
    for rel, text in texts.items():
        prose = re.sub(r"```.*?```", "", text, flags=re.S)           # examples are not links
        for target in re.findall(r"\]\(([^)\s]+)\)|(?:src|href)=\"([^\"]+)\"", prose):
            target = target[0] or target[1]
            if re.match(r"[a-z]+:", target):                     # http:, https:, mailto:
                continue
            path, _, anchor = target.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(rel), path)).replace(os.sep, "/") if path else rel
            if not os.path.exists(os.path.join(ROOT, dest)):
                broken.append("%s -> %s" % (rel, target))
            elif anchor and dest in texts and anchor not in anchors(texts[dest]):
                broken.append("%s -> %s (no such heading)" % (rel, target))
    assert not broken, "\n".join(broken)


def test_files_named_in_the_documentation_exist():
    top = {e for e in os.listdir(ROOT) if not e.startswith(".git") or e == ".github"}
    basenames = {f for base, dirs, files in os.walk(ROOT) if not SKIP_DIRS & set(base.split(os.sep)) for f in files}
    missing = []
    for rel, text in docs():
        if rel.startswith(HISTORY):
            continue
        for token in set(re.findall(r"`([^`\s]+)`", text)):
            token = token.rstrip(".,:;")
            if re.search(r"[<>*{}$%|\\]|^[~/.]|^-", token) and not token.startswith(".github") or token.startswith(GENERATED):
                continue
            first = token.split("/")[0]
            if not ("/" in token and first in top or re.fullmatch(r"[\w.-]+\.(md|py|yml|txt|html|css|png|svg)", token)):
                continue                                         # not a path into this repository
            here = os.path.join(ROOT, os.path.dirname(rel), token)
            if "/" not in token and token in basenames:      # a file mentioned by its name alone
                continue
            if not (os.path.exists(os.path.join(ROOT, token)) or os.path.exists(here)):
                missing.append("%s names `%s`" % (rel, token))
    assert not missing, "\n".join(sorted(missing))


def test_configuration_examples_parse_and_name_the_family():
    """every JSON, JSONC and TOML example must be valid, and no example may misspell the family"""
    names = {build.FAMILY, build.FAMILY.replace(" ", "_"), build.PS_FAMILY} | {"%s-%s" % (build.PS_FAMILY, s) for s in STYLES}
    checked = 0
    for rel, text in docs():
        if rel.startswith(HISTORY):
            continue
        for lang, body in re.findall(r"```(\w+)\n(.*?)```", text, flags=re.S):
            for name in re.findall(r"%s[ _]?%s(?:-[A-Za-z]+)?" % tuple(build.FAMILY.split()), body):
                if "Nerd" not in body and "url(" not in body:
                    assert name in names, "%s: %r is not a name of the family" % (rel, name)
            if lang in ("json", "jsonc"):
                plain = re.sub(r'("(?:[^"\\]|\\.)*")|//[^\n]*', lambda m: m.group(1) or "", body).strip().rstrip(",")
                plain = re.sub(r",(\s*[}\]])", r"\1", plain if plain.startswith("{") else "{%s}" % plain)
                try:
                    json.loads(plain)
                except ValueError as exc:
                    raise AssertionError("%s: invalid %s example: %s\n%s" % (rel, lang, exc, body))
                checked += 1
            elif lang == "toml" and tomllib:
                tomllib.loads(body)
                checked += 1
    assert checked >= 8          # the examples are being found at all


def test_release_archives_hold_what_the_readme_promises(tmp_path):
    spec = importlib.util.spec_from_file_location("make_release", os.path.join(ROOT, "scripts", "make-release.py"))
    rel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rel)
    desktop, web = rel.make_packages(ROOT, str(tmp_path))
    top = "%s-%s" % (build.PS_FAMILY, build.RELEASE)
    css = build.FAMILY.lower().replace(" ", "-") + ".css"

    with zipfile.ZipFile(desktop) as zf:
        names = set(zf.namelist())
        assert names == ({"%s/INSTALL.txt" % top, "%s/OFL.txt" % top, "%s/webfonts/%s" % (top, css)}
                         | {"%s/%s/%s-%s.%s" % (top, folder, build.PS_FAMILY, s, ext) for s in STYLES
                            for folder, ext in (("ttf", "ttf"), ("otf", "otf"), ("webfonts", "woff2"))})
        guide = zf.read("%s/INSTALL.txt" % top).decode("utf-8")
        assert build.FAMILY in guide and build.RELEASE in guide and "{" not in guide
        assert b"SIL OPEN FONT LICENSE" in zf.read("%s/OFL.txt" % top)
        with open(os.path.join(ROOT, "fonts", "ttf", "%s-Regular.ttf" % build.PS_FAMILY), "rb") as fh:
            assert zf.read("%s/ttf/%s-Regular.ttf" % (top, build.PS_FAMILY)) == fh.read()

    with zipfile.ZipFile(web) as zf:
        names = set(zf.namelist())
        assert len(names) == 12 and "%s-web/OFL.txt" % top in names
        # the stylesheet finds every file it names, next to itself
        for url in re.findall(r'url\("([^"]+)"\)', zf.read("%s-web/%s" % (top, css)).decode("utf-8")):
            assert "%s-web/%s" % (top, url) in names

    with open(desktop, "rb") as fh:
        first = fh.read()
    rel.make_packages(ROOT, str(tmp_path))
    with open(desktop, "rb") as fh:
        assert fh.read() == first, "the archive is not deterministic"
    sums, lines = rel.write_checksums(str(tmp_path))
    assert len(lines) == 2 and all(re.fullmatch(r"[0-9a-f]{64}  \S+\.zip\n", line) for line in lines)
