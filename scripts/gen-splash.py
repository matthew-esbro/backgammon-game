#!/usr/bin/env python3
"""Generate the iOS launch screen (2732x2732 + 1x/2x/3x).

Esbro Labs wordmark, stacked vertically, in the in-game "Ivory" theme:
  bg    #f0e8d0  (Ivory uiBg1 — matches the app's menu background)
  title #3a2818  (Ivory uiText — dark espresso)
  sub   #7a5838  (Ivory uiTextDim)
Rendered with Georgia (matches the in-game serif type). Centered so it
survives Capacitor's per-device center-crop.
"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLASH_DIR = os.path.join(REPO, "ios/App/App/Assets.xcassets/Splash.imageset")

OUT = 2732
BG = (0xf0, 0xe8, 0xd0)     # Ivory uiBg1
TITLE = (0x3a, 0x28, 0x18)  # Ivory uiText
SUB = (0x7a, 0x58, 0x38)    # Ivory uiTextDim


def georgia(size):
    for p in (
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/Library/Fonts/Georgia.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


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

    title_size = 300
    title_font = georgia(title_size)
    title_track = title_size * 0.10

    # Two stacked title lines, vertically centred slightly above middle.
    line_gap = int(title_size * 1.18)
    block_center_y = int(OUT * 0.46)
    l1_baseline = block_center_y - line_gap // 2 + title_size // 3
    l2_baseline = l1_baseline + line_gap

    draw_tracked(draw, "Esbro", cx, l1_baseline, title_font, TITLE, title_track)
    draw_tracked(draw, "Labs", cx, l2_baseline, title_font, TITLE, title_track)

    # Subtitle below the stack.
    sub_size = 64
    sub_font = georgia(sub_size)
    draw_tracked(draw, "EST. 2026", cx, l2_baseline + int(title_size * 0.62),
                 sub_font, SUB, sub_size * 0.45)
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
