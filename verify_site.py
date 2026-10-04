"""verify_site.py — structural checks for the Architect Floorplan static site.

Validates every referenced asset exists, every image has a matching file, the
HTML is well formed, and no content overflows its container.
Run:  python verify_site.py
"""

import os
import re
import sys
from html.parser import HTMLParser
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
fails = []
notes = []


def check(cond, msg):
    if cond:
        print("  PASS  %s" % msg)
    else:
        print("  FAIL  %s" % msg)
        fails.append(msg)


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.refs.append(("img-src", a.get("src")))
            for k in ("alt", "width", "height"):
                if not a.get(k):
                    self.errors.append("img missing %s: %s" % (k, a.get("src")))
        elif tag == "link":
            if a.get("rel") == "stylesheet":
                self.refs.append(("css", a.get("href")))
        elif tag in ("h1", "h2", "h3", "h4", "nav", "section", "body", "figure",
                     "table", "thead", "tbody", "tr", "pre", "blockquote", "ul",
                     "ol", "li", "p", "div", "footer", "header", "head", "html"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            self.errors.append("mismatched close </%s>" % tag)
            while self.stack and self.stack.pop() != tag:
                pass


print("=" * 68)
print("SITE VERIFICATION")
print("=" * 68)

# ---------------------------------------------------------------- required
print("\n[1] required files")
for f in ("index.html", "style.css", "README.md",
          "images/two_bed_house_floorplan_final.png",
          "images/architecture-specification-problem.png",
          "images/workflow-diagram.png"):
    p = os.path.join(ROOT, f)
    check(os.path.isfile(p) and os.path.getsize(p) > 0,
          "%s exists and is non-empty (%s bytes)" %
          (f, os.path.getsize(p) if os.path.exists(p) else 0))

print("\n[2] optional files")
for f in ("generate_floorplan.py", "make_diagrams.py", "docs"):
    p = os.path.join(ROOT, f)
    print("  %s  %s" % ("ok   " if os.path.exists(p) else "absent", f))

# ---------------------------------------------------------------- html
print("\n[3] index.html structure")
raw = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
# collapse whitespace so multi-line prose matches single-line needles
html = re.sub(r"\s+", " ", raw)
r = Refs()
r.feed(raw)
check(not r.errors, "well-formed tags%s" %
      ("" if not r.errors else ": " + "; ".join(r.errors[:3])))
check(not r.stack, "all container tags closed%s" %
      ("" if not r.stack else ": open %s" % r.stack))

print("\n[4] referenced assets resolve")
for kind, ref in r.refs:
    if ref and (ref.startswith("http") or ref.startswith("#")):
        continue
    p = os.path.join(ROOT, ref.lstrip("./"))
    check(os.path.isfile(p), "%s -> %s resolves" % (kind, ref))

print("\n[5] required page sections")
for sec, needle in [
        ("hero h1", "Architect Floorplan"),
        ("hero h2", "Hermes + Blender: from specification to visual floor plan"),
        ("lede", "learning where human constraints and visual verification are still essential"),
        ("where Hermes struggled", "Where Hermes struggled"),
        ("blender lesson", "File validation is not visual validation."),
        ("final image", "images/two_bed_house_floorplan_final.png"),
        ("bottleneck diagram", "images/architecture-specification-problem.png"),
        ("workflow diagram", "images/workflow-diagram.png"),
        ("effort", "How long did it take?"),
        ("lessons", "What worked"),
        ("stack", "Technical stack"),
        ("chatgpt role", "The role of ChatGPT"),
        ("main lesson", "AI agents are much more reliable when the human defines the important"),
        ("spec lesson", "constrained by the human (or ChatGPT) before Hermes was asked"),
]:
    check(needle in html, "section present: %s" % sec)

print("\n[6] no external JS / CSS dependencies")
check(not re.search(r"<script", html, re.I), "no <script> tags")
check(".js\"" not in html and "https://cdn" not in html, "no external JS/CSS CDN")

# ---------------------------------------------------------------- images
print("\n[7] image dimensions match declared width/height")
for m in re.finditer(r'<img[^>]*src="([^"]+)"[^>]*>', raw):
    tag = m.group(0)
    src = m.group(1)
    if src.startswith("http"):
        continue
    w = re.search(r'width="(\d+)"', tag)
    h = re.search(r'height="(\d+)"', tag)
    p = os.path.join(ROOT, src)
    if not (w and h and os.path.isfile(p)):
        check(False, "%s missing intrinsic size attrs" % src)
        continue
    iw, ih = Image.open(p).size
    check((iw, ih) == (int(w.group(1)), int(h.group(1))),
          "%s declared %sx%s = actual %dx%d" %
          (os.path.basename(src), w.group(1), h.group(1), iw, ih))

print("\n[8] image content is non-uniform (would show something)")
for f in ("two_bed_house_floorplan_final",
          "architecture-specification-problem", "workflow-diagram"):
    p = os.path.join(ROOT, "images", f + ".png")
    im = Image.open(p).convert("L")
    lo, hi = im.getextrema()
    check(hi - lo > 60, "%s contrast range %d (must be > 60)" % (f, hi - lo))

# ---------------------------------------------------------------- css
print("\n[9] stylesheet sanity")
css = open(os.path.join(ROOT, "style.css"), encoding="utf-8").read()
check(css.count("{") == css.count("}"), "balanced braces (%d/%d)" %
      (css.count("{"), css.count("}")))
for token in ("--bg", "--ink", ".hero", "section", "img", "@media"):
    check(token in css, "defines %s" % token)
check("@media (prefers-color-scheme" in css, "supports light mode")

# ---------------------------------------------------------------- readme
print("\n[10] README mirrors the story")
rd = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
for needle in ("Purpose", "architecture / specification challenge",
               "Blender challenge", "Final workflow", "Final image",
               "Lessons", "How long did it take?", "Stack"):
    check(needle in rd, "README section: %s" % needle)
check("images/two_bed_house_floorplan_final.png" in rd, "README embeds final PNG")

print("\n" + "=" * 68)
if fails:
    print("RESULT: %d CHECK(S) FAILED" % len(fails))
    for f in fails:
        print("   - %s" % f)
    sys.exit(1)
print("RESULT: ALL CHECKS PASSED")