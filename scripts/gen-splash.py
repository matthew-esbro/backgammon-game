#!/usr/bin/env python3
"""Rasterize the Esbro Labs wordmark (scripts/esbro-labs-wordmark.svg) to the
iOS launch screen PNGs at 2732x2732.

The source SVG is a 1024-unit canvas:
  - bg rect          #1a3a1e
  - "ESBRO LABS"      serif, size 64, letter-spacing 10.24, #e2c07a
  - "EST. 2026"       serif, size 11.5, letter-spacing 5.98, #e2c07a @ 0.45
SVG `y` is the text baseline. We scale everything by 2732/1024 and render
with Georgia (the SVG's declared fallback, installed on macOS).
"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLASH_DIR = os.path.join(REPO, "ios/App/App/Assets.xcassets/Splash.imageset")

OUT = 2732
SCALE = OUT / 1024.0

BG = (0x1a, 0x3a, 0x1e)
GOLD = (0xe2, 0xc0, 0x7a)


def georgia(size):
    for p in (
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/Library/Fonts/Georgia.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def blend(fg, bg, a):
    return tuple(int(bg[i] + (fg[i] - bg[i]) * a) for i in range(3))


def draw_tracked(draw, text, center_x, baseline_y, font, fill, tracking):
    """Draw text centered on center_x with per-glyph letter-spacing.
    baseline_y is the text baseline (to match SVG `y` semantics)."""
    # Measure each glyph's advance
    widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font, anchor="ls")
        # advance ~ glyph width; use textlength for proper advance
        widths.append(draw.textlength(ch, font=font))
    total = sum(widths) + tracking * (len(text) - 1)
    x = center_x - total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, baseline_y), ch, font=font, fill=fill, anchor="ls")
        x += w + tracking


def render():
    img = Image.new("RGB", (OUT, OUT), BG)
    draw = ImageDraw.Draw(img)

    # Title: "ESBRO LABS"
    title_font = georgia(int(round(64 * SCALE)))
    draw_tracked(
        draw, "ESBRO LABS",
        center_x=517.12 * SCALE,
        baseline_y=500 * SCALE,
        font=title_font,
        fill=GOLD,
        tracking=10.24 * SCALE,
    )

    # Subtitle: "EST. 2026" at 0.45 opacity (precomputed over BG)
    sub_font = georgia(int(round(11.5 * SCALE)))
    draw_tracked(
        draw, "EST. 2026",
        center_x=514.99 * SCALE,
        baseline_y=548 * SCALE,
        font=sub_font,
        fill=blend(GOLD, BG, 0.45),
        tracking=5.98 * SCALE,
    )
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
