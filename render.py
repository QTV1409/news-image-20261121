#!/usr/bin/env python3
"""Draw the 21 November 2026 world-news front page as entry.png.

Self-contained: Pillow + stdlib only, DejaVu fonts, deterministic output
(the same run always writes the same PNG bytes). Layout is a newspaper
front page: masthead, dateline, one lead story, a 2x3 grid of stories,
an "also in the news" strip and a sources footer.

Stories are the day's verified reporting (21 Nov 2026, in at least one
time zone): the Palisades fire retrial verdict, Russian missiles landing
in Poland, Denmark's expulsion of a Russian diplomat, BepiColombo's
arrival at Mercury, Mamdani's Rikers plan, Europe's Gen Z protests and
the COP31 talks running past their deadline.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (253, 251, 244)
INK = (26, 26, 26)
RED = (178, 34, 34)
GREY = (110, 108, 100)
RULE = (26, 26, 26)
FAINT = (200, 198, 188)
BLUE = (31, 73, 125)
ORANGE = (204, 85, 0)
GREEN = (46, 125, 50)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, max_lines, fill=INK):
    """Draw wrapped text, capped at max_lines with an ellipsis."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " …", font=fnt) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
        lines[-1] = (lines[-1] + " …").strip()
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def fit(draw, text, fnt_path, size, max_w):
    """Shrink a one-line title until it fits max_w; returns (font, width)."""
    while size > 20:
        fnt = font(fnt_path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt, draw.textlength(text, font=fnt)
        size -= 2
    fnt = font(fnt_path, size)
    return fnt, draw.textlength(text, font=fnt)


# ---- icons: small pictograms drawn with shapes only -----------------------

def icon_flame(d, x, y, s):
    d.ellipse([x + s * 0.28, y + s * 0.30, x + s * 0.72, y + s * 0.88], fill=ORANGE)
    d.polygon([(x + s * 0.50, y + s * 0.02), (x + s * 0.78, y + s * 0.55),
               (x + s * 0.62, y + s * 0.45), (x + s * 0.66, y + s * 0.80),
               (x + s * 0.34, y + s * 0.80), (x + s * 0.38, y + s * 0.45),
               (x + s * 0.22, y + s * 0.55)], fill=RED)
    d.ellipse([x + s * 0.40, y + s * 0.58, x + s * 0.60, y + s * 0.82], fill=(255, 205, 60))


def icon_missile(d, x, y, s):
    d.polygon([(x + s * 0.55, y + s * 0.05), (x + s * 0.75, y + s * 0.45),
               (x + s * 0.55, y + s * 0.38), (x + s * 0.35, y + s * 0.45)],
              fill=INK)
    d.polygon([(x + s * 0.35, y + s * 0.45), (x + s * 0.15, y + s * 0.75),
               (x + s * 0.38, y + s * 0.62)], fill=RED)
    d.polygon([(x + s * 0.55, y + s * 0.38), (x + s * 0.78, y + s * 0.68),
               (x + s * 0.62, y + s * 0.55)], fill=RED)
    for i in range(3):
        d.ellipse([x + s * (0.10 + i * 0.09), y + s * (0.82 + i * 0.05),
                   x + s * (0.18 + i * 0.09), y + s * (0.90 + i * 0.05)],
                  fill=FAINT)


def icon_flag(d, x, y, s):
    d.rectangle([x + s * 0.18, y + s * 0.05, x + s * 0.24, y + s * 0.95], fill=INK)
    d.polygon([(x + s * 0.24, y + s * 0.08), (x + s * 0.85, y + s * 0.20),
               (x + s * 0.24, y + s * 0.42)], fill=RED)
    d.polygon([(x + s * 0.24, y + s * 0.42), (x + s * 0.85, y + s * 0.54),
               (x + s * 0.24, y + s * 0.76)], fill=BLUE)


def icon_planet(d, x, y, s):
    d.ellipse([x + s * 0.12, y + s * 0.18, x + s * 0.88, y + s * 0.94], fill=BLUE)
    d.ellipse([x + s * 0.30, y + s * 0.32, x + s * 0.44, y + s * 0.46], fill=(120, 165, 210))
    d.ellipse([x + s * 0.58, y + s * 0.60, x + s * 0.72, y + s * 0.74], fill=(120, 165, 210))
    d.ellipse([x + s * 0.02, y + s * 0.42, x + s * 0.98, y + s * 0.62],
              outline=(255, 205, 60), width=max(2, s // 24))


def icon_bars(d, x, y, s):
    d.rectangle([x + s * 0.08, y + s * 0.05, x + s * 0.92, y + s * 0.95],
                outline=INK, width=max(2, s // 28))
    for i in range(4):
        bx = x + s * (0.24 + i * 0.18)
        d.rectangle([bx, y + s * 0.05, bx + s * 0.07, y + s * 0.95], fill=INK)


def icon_people(d, x, y, s):
    for cx, cy, r, col in ((0.30, 0.34, 0.13, RED), (0.70, 0.34, 0.13, BLUE),
                           (0.50, 0.28, 0.15, INK)):
        d.ellipse([x + s * (cx - r), y + s * (cy - r), x + s * (cx + r),
                   y + s * (cy + r)], fill=col)
        d.pieslice([x + s * (cx - r - 0.06), y + s * (cy + r - 0.02),
                    x + s * (cx + r + 0.06), y + s * (cy + r + 0.42)],
                   180, 360, fill=col)


def icon_globe(d, x, y, s):
    d.ellipse([x + s * 0.06, y + s * 0.06, x + s * 0.94, y + s * 0.94],
              outline=GREEN, width=max(2, s // 26))
    d.ellipse([x + s * 0.30, y + s * 0.06, x + s * 0.70, y + s * 0.94],
              outline=GREEN, width=max(2, s // 30))
    d.line([x + s * 0.06, y + s * 0.50, x + s * 0.94, y + s * 0.50],
           fill=GREEN, width=max(2, s // 30))
    d.arc([x + s * 0.06, y + s * 0.22, x + s * 0.94, y + s * 0.78],
          200, 340, fill=GREEN, width=max(2, s // 30))
    d.arc([x + s * 0.06, y + s * 0.22, x + s * 0.94, y + s * 0.78],
          20, 160, fill=GREEN, width=max(2, s // 30))


ICONS = {"flame": icon_flame, "missile": icon_missile, "flag": icon_flag,
         "planet": icon_planet, "bars": icon_bars, "people": icon_people,
         "globe": icon_globe}


# ---- the front page --------------------------------------------------------

LEAD = {
    "kicker": "UNITED STATES  ·  JUSTICE",
    "headline": "Palisades fire arsonist found guilty at retrial",
    "body": ("Jonathan Rinderknecht, 30, was convicted of federal arson "
             "charges for the January 2025 fire that killed 12 people and "
             "destroyed about 6,800 structures. He faces up to 40 years "
             "in prison."),
    "icon": "flame",
}

GRID = [
    {"kicker": "UKRAINE  ·  EUROPE", "icon": "missile",
     "headline": "Russian missiles land in Poland",
     "body": "Two missiles and a drone crossed the border during strikes on Ukraine, Poland's PM says."},
    {"kicker": "DENMARK  ·  EUROPE", "icon": "flag",
     "headline": "Denmark expels Russian diplomat over 'plot'",
     "body": "Copenhagen says the envoy was tied to a plot to kill a Ukrainian rapper."},
    {"kicker": "SPACE", "icon": "planet",
     "headline": "BepiColombo enters orbit around Mercury",
     "body": "After eight years in space, the ESA–JAXA craft is captured by the smallest planet."},
    {"kicker": "NEW YORK", "icon": "bars",
     "headline": "Mamdani vows to close Rikers jail by 2032",
     "body": "New York's mayor-elect unveils a plan to shut the notorious jail complex."},
    {"kicker": "EUROPE", "icon": "people",
     "headline": "Gen Z rallies across Europe over war and prices",
     "body": "Young protesters march against wars, rising costs and climate inaction."},
    {"kicker": "CLIMATE", "icon": "globe",
     "headline": "COP31 talks run past deadline with no deal",
     "body": "Negotiators stall over fossil fuels as the summit goes into overtime."},
]

BRIEFS = [
    "ANC fights to hold South Africa's big cities after election setback",
    "Saudi-led coalition says it downed Houthi missiles over Yemen",
    "Trump cites 'good talks' with Putin on Ukraine, holds back on guarantees",
]


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36  # side margin

    # Masthead
    fnt, mw = fit(d, "THE WORLD IN ONE PAGE", SERIF, 60, W - 2 * mx)
    d.text(((W - mw) / 2, 26), "THE WORLD IN ONE PAGE", font=fnt, fill=INK)
    d.line([mx, 104, W - mx, 104], fill=RULE, width=3)
    d.line([mx, 110, W - mx, 110], fill=RULE, width=1)

    # Dateline row
    dl = font(SANS_B, 19)
    d.text((mx, 120), "SATURDAY, 21 NOVEMBER 2026", font=dl, fill=RED)
    right = "ONE DAY  ·  ONE PAGE  ·  WORLD NEWS"
    rw = d.textlength(right, font=dl)
    d.text((W - mx - rw, 120), right, font=dl, fill=INK)
    d.line([mx, 150, W - mx, 150], fill=FAINT, width=1)

    # Lead story
    y = 168
    ICONS[LEAD["icon"]](d, mx, y + 6, 148)
    tx = mx + 172
    tw = W - mx - tx
    kf = font(SANS_B, 16)
    d.text((tx, y), LEAD["kicker"], font=kf, fill=RED)
    hf = font(SERIF, 38)
    y = para(d, tx, y + 26, LEAD["headline"], hf, tw, 46, 2)
    bf = font(SANS, 20)
    para(d, tx, y + 8, LEAD["body"], bf, tw, 27, 4)
    d.line([mx, 398, W - mx, 398], fill=RULE, width=2)

    # Grid: 2 columns x 3 rows
    col_w = (W - 2 * mx - 24) // 2
    row_h = 136
    gy = 420
    for i, s in enumerate(GRID):
        cx = mx + (i % 2) * (col_w + 24)
        cy = gy + (i // 2) * row_h
        ICONS[s["icon"]](d, cx, cy + 4, 82)
        sx = cx + 98
        sw = col_w - 98
        d.text((sx, cy), s["kicker"], font=font(SANS_B, 13), fill=RED)
        yy = para(d, sx, cy + 20, s["headline"], font(SERIF, 21), sw, 25, 2)
        para(d, sx, yy + 3, s["body"], font(SANS, 16), sw, 20, 2)
        if i % 2 == 0:
            d.line([cx + col_w + 12, cy + 4, cx + col_w + 12, cy + row_h - 14],
                   fill=FAINT, width=1)
        if i < 4:
            d.line([cx, cy + row_h - 8, cx + col_w, cy + row_h - 8],
                   fill=FAINT, width=1)

    # Also-in-the-news strip
    ay = gy + 3 * row_h + 6
    d.line([mx, ay, W - mx, ay], fill=RULE, width=2)
    d.text((mx, ay + 12), "ALSO IN THE NEWS", font=font(SANS_B, 16), fill=RED)
    by = ay + 42
    for b in BRIEFS:
        d.text((mx, by), "•", font=font(SANS_B, 17), fill=RED)
        para(d, mx + 22, by, b, font(SANS, 17), W - 2 * mx - 22, 22, 1)
        by += 28

    # Footer
    fy = H - 44
    d.line([mx, fy, W - mx, fy], fill=FAINT, width=1)
    foot = ("Sources: Reuters, CNN, BBC, Al Jazeera, The Guardian, ESA, "
            "U.S. Dept. of Justice  ·  All stories first reported 21 November 2026")
    para(d, mx, fy + 10, foot, font(SANS, 13), W - 2 * mx, 17, 1, fill=GREY)

    img.save(OUT, "PNG")
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    draw_page()
