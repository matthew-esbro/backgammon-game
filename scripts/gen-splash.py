#!/usr/bin/env python3
"""iOS launch screen (2732x2732 + 1x/2x/3x).

Esbro Labs wordmark stacked vertically, in Instrument Serif (the brand
font from the source SVG), styled like the in-game "BACKGAMMON" title
in the Ivory theme:
  bg         #f0e8d0   Ivory uiBg1 (matches the app menu background)
  text       #7a4818   Ivory uiAccent
  hard shadow #c8a878  offset down-right (letterpress emboss)
  soft glow  rgba(122,72,24,~0.15) blurred
  subtitle   #7a5838   Ivory uiTextDim (no heavy shadow, like the
                        in-game CLASSIC STRATEGY subtitle)
Centered so it survives Capacitor's per-device center-crop.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLASH_DIR = os.path.join(REPO, "ios/App/App/Assets.xcassets/Splash.imageset")
FONT_PATH = os.path.join(REPO, "scripts/InstrumentSerif-Regular.ttf")

OUT = 2732
BG = (0xf0, 0xe8, 0xd0)       # Ivory uiBg1
TXT = (0x7a, 0x48, 0x18)      # Ivory uiAccent
HARD = (0xc8, 0xa8, 0x78)     # in-game uiTitleShadow hard offset color
GLOW = (122, 72, 24)          # in-game uiTitleShadow glow color
SUB = (0x7a, 0x58, 0x38)      # Ivory uiTextDim

TITLE_SIZE = 220
SUB_SIZE = 52


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
    cx = OUT / 2.0

    title_font = imserif(TITLE_SIZE)
    title_track = TITLE_SIZE * 0.06  # in-game title is 3px / 32px ~ 0.09; a
                                     # touch tighter reads better stacked

    line_gap = int(TITLE_SIZE * 1.16)
    block_center_y = int(OUT * 0.45)
    l1 = block_center_y - line_gap // 2 + TITLE_SIZE // 3
    l2 = l1 + line_gap
    title_lines = [("ESBRO", l1), ("LABS", l2)]

    # 1. Soft glow — render the title lines opaque on a layer, blur, fade.
    glow = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for txt, by in title_lines:
        draw_tracked(gd, txt, cx, by, title_font, GLOW + (255,), title_track)
    glow = glow.filter(ImageFilter.GaussianBlur(int(TITLE_SIZE * 0.16)))
    alpha = glow.split()[3].point(lambda v: int(v * 0.18))
    glow.putalpha(alpha)
    img.paste(glow, (0, 0), glow)
    draw = ImageDraw.Draw(img)

    # 2. Hard offset shadow (down-right) then 3. the wordmark on top.
    off = max(2, int(TITLE_SIZE * 0.045))
    for txt, by in title_lines:
        draw_tracked(draw, txt, cx + off, by + off, title_font, HARD, title_track)
    for txt, by in title_lines:
        draw_tracked(draw, txt, cx, by, title_font, TXT, title_track)

    # Subtitle — plain dim color, like the in-game CLASSIC STRATEGY line.
    sub_font = imserif(SUB_SIZE)
    draw_tracked(draw, "EST. 2026", cx, l2 + int(TITLE_SIZE * 0.60),
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
