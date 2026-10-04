"""
make_diagrams.py
================
Generates the two PNG diagrams used by the Architect Floorplan documentation
site. Pure Pillow drawing - no external assets, no network.

Outputs:
    images/architecture-specification-problem.png
    images/workflow-diagram.png

Run:  python make_diagrams.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

BG = (13, 15, 20)
CARD = (23, 27, 35)
CARD_EDGE = (46, 54, 68)
INK = (233, 237, 243)
MUTED = (152, 162, 178)
ACCENT = (108, 166, 245)
GOOD = (96, 190, 140)
BAD = (226, 122, 110)
WARN = (226, 182, 106)
RULE = (56, 64, 78)


def font(size, bold=False):
    names = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else \
            ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    for n in names:
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            p = os.path.join(base, n)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()


F_TITLE = font(38, True)
F_H = font(24, True)
F_BODY = font(18)
F_SMALL = font(15)
F_MONO = font(16, True)
F_TINY = font(13)
F_NUM = font(19, True)


def tw(d, text, fnt):
    """Rendered width of a text run, in pixels."""
    return d.textbbox((0, 0), text, font=fnt)[2]


def centered(d, cx, y, text, fnt, fill):
    d.text((cx - tw(d, text, fnt) / 2, y), text, font=fnt, fill=fill)


def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


# ============================================================================
# DIAGRAM 1 - Why the specification became the bottleneck
# ============================================================================
def diagram_spec():
    W, H = 1120, 1340
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    centered(d, W / 2, 38, "Why the specification became the bottleneck",
             F_TITLE, INK)
    centered(d, W / 2, 92,
             "the agent was asked to invent architecture before it could draw anything",
             F_SMALL, MUTED)

    cx = W / 2
    box_w, box_h = 900, 132

    def stage(y, step, title, lines, edge, accent):
        rounded(d, (cx - box_w / 2, y, cx + box_w / 2, y + box_h), 12,
                CARD, edge, 2)
        d.rectangle((cx - box_w / 2, y, cx - box_w / 2 + 6, y + box_h), fill=accent)
        d.text((cx - box_w / 2 + 28, y + 22), step, font=F_NUM, fill=accent)
        centered(d, cx + 16, y + 24, title, F_H, INK)
        yy = y + 68
        for ln in lines:
            centered(d, cx + 16, yy, ln, F_SMALL, MUTED)
            yy += 24

    def arrow(y0, y1, fill):
        d.line([(cx, y0), (cx, y1 - 13)], fill=fill, width=3)
        d.polygon([(cx - 9, y1 - 13), (cx + 9, y1 - 13), (cx, y1)], fill=fill)

    y = 148
    stage(y, "1", "HOUSE REQUIREMENTS",
          ["5.50 m  x  10.00 m external footprint        two storeys",
           "mid-terrace, no side windows        ~200 mm external walls"],
          CARD_EDGE, ACCENT)
    arrow(y + box_h, y + box_h + 38, RULE)
    y += box_h + 46

    stage(y, "2", "HERMES DESIGNS THE HOUSE",
          ["picks room sizes, stair position, wall layout and openings",
           "writes the specification and the Blender script"],
          CARD_EDGE, ACCENT)
    arrow(y + box_h, y + box_h + 38, BAD)
    y += box_h + 46

    ph = 300
    rounded(d, (cx - box_w / 2, y, cx + box_w / 2, y + ph), 12,
            (36, 25, 25), (120, 66, 60), 2)
    d.rectangle((cx - box_w / 2, y, cx - box_w / 2 + 6, y + ph), fill=BAD)
    d.text((cx - box_w / 2 + 28, y + 22), "3", font=F_NUM, fill=BAD)
    centered(d, cx + 16, y + 24, "PROBLEMS FOUND", F_H, (250, 202, 197))
    probs = [
        "bedrooms far too small or too narrow",
        "huge circulation and landing areas",
        "awkward room proportions",
        "stair run did not fit the space",
        "unexplained leftover \u201cpartition\u201d area",
        "side windows on a mid-terrace",
        "stated areas disagreed with geometry",
        "stairs overlapping other rooms",
    ]
    colw = box_w / 2 - 56
    for i, p in enumerate(probs):
        col, row = i % 2, i // 2
        px = cx - box_w / 2 + 30 + col * colw
        py = y + 74 + row * 42
        d.ellipse((px, py + 6, px + 9, py + 15), fill=BAD)
        d.text((px + 20, py), p, font=F_SMALL, fill=(228, 194, 189))
    arrow(y + ph, y + ph + 38, GOOD)
    y += ph + 46

    stage(y, "4", "HUMAN / CHATGPT CONSTRAINS THE ARCHITECTURE",
          ["fixes envelope, room count, room sizes and stair position",
           "drops requirements that cannot work (WC, side windows)"],
          (52, 96, 76), GOOD)
    arrow(y + box_h, y + box_h + 38, GOOD)
    y += box_h + 46

    stage(y, "5", "HERMES COORDINATES, BLENDER DRAWS",
          ["converts the approved layout into exact X / Y coordinates",
           "Blender renders the 2D plan, Hermes inspects the image"],
          (52, 96, 76), GOOD)

    cy = H - 104
    rounded(d, (cx - box_w / 2, cy, cx + box_w / 2, cy + 72), 12,
            (21, 30, 25), (52, 96, 76), 2)
    centered(d, cx, cy + 16, "The specification had to be constrained",
             F_MONO, (182, 228, 202))
    centered(d, cx, cy + 42, "before it could be drawn reliably.",
             F_MONO, (182, 228, 202))

    p = os.path.join(OUT, "architecture-specification-problem.png")
    im.save(p, "PNG", optimize=True)
    return p


# ============================================================================
# DIAGRAM 2 - Final workflow (vertical, so every line has room)
# ============================================================================
def diagram_workflow():
    W, H = 1180, 1330
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    centered(d, W / 2, 38, "Final workflow", F_TITLE, INK)
    centered(d, W / 2, 92, "the division of responsibility that actually worked",
             F_SMALL, MUTED)

    steps = [
        ("1", "Specification",
         "Human / ChatGPT defines a basic, believable layout", ACCENT),
        ("2", "Coordinates",
         "Hermes converts it into precise X / Y room rectangles", ACCENT),
        ("3", "Blender Python",
         "Hermes writes the generator; Blender builds the geometry", WARN),
        ("4", "2D floor plan",
         "Workbench renders both floors side by side on white", GOOD),
        ("5", "Visual inspection",
         "Hermes looks at the rendered image, not just the file", WARN),
        ("6", "Correction",
         "Presentation fixed; the architecture is left alone", GOOD),
    ]

    cx = W / 2
    box_w, box_h = 860, 116
    top = 148

    for i, (num, title, body, col) in enumerate(steps):
        y = top + i * (box_h + 34)
        rounded(d, (cx - box_w / 2, y, cx + box_w / 2, y + box_h), 12,
                CARD, CARD_EDGE, 2)
        d.rectangle((cx - box_w / 2, y, cx - box_w / 2 + 6, y + box_h), fill=col)
        bx, by, br = cx - box_w / 2 + 48, y + box_h / 2, 24
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=col)
        centered(d, bx, by - 12, num, F_NUM, (16, 18, 24))
        d.text((bx + 46, y + 30), title, font=F_H, fill=INK)
        d.text((bx + 46, y + 70), body, font=F_BODY, fill=MUTED)

        if i < len(steps) - 1:
            d.line([(cx, y + box_h), (cx, y + box_h + 21)], fill=RULE, width=3)
            d.polygon([(cx - 8, y + box_h + 21), (cx + 8, y + box_h + 21),
                       (cx, y + box_h + 33)], fill=RULE)

    # loop-back: step 6 returns to step 5
    last_mid = top + 5 * (box_h + 34) + box_h / 2
    fifth_mid = top + 4 * (box_h + 34) + box_h / 2
    lx = cx + box_w / 2 + 34
    d.line([(cx + box_w / 2 - 4, last_mid), (lx, last_mid)], fill=WARN, width=2)
    d.line([(lx, last_mid), (lx, fifth_mid)], fill=WARN, width=2)
    d.polygon([(lx - 7, fifth_mid - 8), (lx + 7, fifth_mid - 8), (lx, fifth_mid)],
              fill=WARN)
    mid = (last_mid + fifth_mid) / 2
    d.text((lx + 16, mid - 34), "if the image is", font=F_TINY, fill=WARN)
    d.text((lx + 16, mid - 14), "wrong, fix the", font=F_TINY, fill=WARN)
    d.text((lx + 16, mid + 6), "presentation, not", font=F_TINY, fill=WARN)
    d.text((lx + 16, mid + 26), "the architecture", font=F_TINY, fill=WARN)

    oy = H - 128
    rounded(d, (cx - box_w / 2, oy, cx + box_w / 2, oy + 88), 12,
            (21, 30, 25), (52, 96, 76), 2)
    centered(d, cx, oy + 16, "Result", F_H, (182, 228, 202))
    centered(d, cx, oy + 52,
             "A readable 2D floor plan whose geometry matches a written specification.",
             F_SMALL, MUTED)

    p = os.path.join(OUT, "workflow-diagram.png")
    im.save(p, "PNG", optimize=True)
    return p


if __name__ == "__main__":
    for p in (diagram_spec(), diagram_workflow()):
        print("wrote", p, os.path.getsize(p), "bytes")