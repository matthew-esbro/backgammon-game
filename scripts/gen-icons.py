#!/usr/bin/env python3
"""iOS app icon (1024x1024): a single bold backgammon "point" (triangle)
with a clean chip-stack of checkers resting on it. Minimal flat
pictogram in the Ivory brand palette (matches the Esbro Labs launch
screen), with generous margins so it stays legible at home-screen size.

Run from repo root:  python3 scripts/gen-icons.py
Writes ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png

Apple applies the rounded-square mask, so this draws full-bleed on a
solid Ivory tile. Palette = Ivory Classic:
  tile        #f0e8d0   Ivory uiBg1 (same as the launch screen)
  point       #6e3f1c   deep walnut
  chip fill   #f6e4b0   honey cream
  chip rim    #6e3f1c   deep walnut
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(REPO,
    "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png")

S = 1024

BG  = (0xf0, 0xe8, 0xd0)   # Ivory uiBg1 tile
TRI = (0x6e, 0x3f, 0x1c)   # deep walnut point
CF  = (0xf6, 0xe4, 0xb0)   # honey-cream chip face
CR  = (0x6e, 0x3f, 0x1c)   # deep walnut chip rim


def main():
    img = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(img)
    cx = S / 2.0

    # Squat, wide point (reads as a pennant, not a pine tree).
    half = S * 0.258
    base_y = S * 0.762
    apex_y = S * 0.252
    d.polygon([(cx-half, base_y), (cx+half, base_y), (cx, apex_y)], fill=TRI)

    # Chunky side-on chip stack: overlapping flat discs read as stacked
    # game pieces and survive the 48px home-screen test.
    rw = S * 0.142
    rh = S * 0.056
    step = rh * 1.34
    n = 3
    ow = max(3, int(rh * 0.17))
    bottom = base_y - rh * 1.15
    for k in range(n):
        cy = bottom - k * step
        d.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], fill=CF)
        d.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], outline=CR, width=ow)
    ty = bottom - (n-1) * step
    hl = tuple(min(255, c+22) for c in CF)
    d.ellipse([cx-rw*0.52, ty-rh*0.46, cx+rw*0.52, ty+rh*0.16], fill=hl)

    os.makedirs(os.path.dirname(ICON), exist_ok=True)
    img.save(ICON, "PNG", optimize=True)
    print("wrote", ICON)


if __name__ == "__main__":
    main()
