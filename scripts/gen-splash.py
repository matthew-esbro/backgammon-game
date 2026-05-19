#!/usr/bin/env python3
"""iOS launch screen (2732x2732 + 1x/2x/3x).

Esbro Labs wordmark stacked vertically, lowercase, in Instrument Serif
(the brand font from the source SVG). Flat, no shadow or glow, in the
Ivory theme:
  bg        #f0e8d0   Ivory uiBg1 (matches the app menu background)
  text      #7a4818   Ivory uiAccent
  subtitle  #7a5838   Ivory uiTextDim
Centered so it survives Capacitor's per-device center-crop.
"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLASH_DIR = os.path.join(REPO, "ios/App/App/Assets.xcassets/Splash.imageset")
FONT_PATH = os.path.join(REPO, "scripts/InstrumentSerif-Regular.ttf")

OUT = 2732
BG = (0xf0, 0xe8, 0xd0)       # Ivory uiBg1
TXT = (0x7a, 0x48, 0x18)      # Ivory uiAccent
SUB = (0x7a, 0x58, 0x38)      # Ivory uiTextDim

TITLE_SIZE = 150
SUB_SIZE = 36


def imserif(size):
    return ImageFont.truetype(FONT_PATH, size)


def draw_tracked(draw, text, center_x, baseline_y, font, fill, tracking):
    """Centered text with per-glyph letter-spacing; baseline_y is the baseline."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = center_x - total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, baseline_y), ch, font=font, fill=fill, anchor="ls")
        x += w + tracking


def render():
    img = Image.new("RGB", (OUT, OUT), BG)
    draw = ImageDraw.Draw(img)
    cx = OUT / 2.0

    title_font = imserif(TITLE_SIZE)
    title_track = TITLE_SIZE * 0.06

    line_gap = int(TITLE_SIZE * 1.16)
    block_center_y = int(OUT * 0.45)
    l1 = block_center_y - line_gap // 2 + TITLE_SIZE // 3
    l2 = l1 + line_gap
    title_lines = [("esbro", l1), ("labs", l2)]

    # Flat wordmark — no shadow, no glow.
    for txt, by in title_lines:
        draw_tracked(draw, txt, cx, by, title_font, TXT, title_track)

    # Subtitle — plain dim color.
    sub_font = imserif(SUB_SIZE)
    draw_tracked(draw, "est. 2026", cx, l2 + int(TITLE_SIZE * 0.60),
                 sub_font, SUB, SUB_SIZE * 0.5)
    return img


def main():
    os.makedirs(SPLASH_DIR, exist_ok=True)
    img = render()
    for fn in ("splash-2732x2732.png",
               "splash-2732x2732-1.png",
               "splash-2732x2732-2.png"):
        path = os.path.join(SPLASH_DIR, fn)
        img.save(path, "PNG", optimize=True)
        print("wrote", path)


if __name__ == "__main__":
    main()
