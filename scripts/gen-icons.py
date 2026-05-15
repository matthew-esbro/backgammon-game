#!/usr/bin/env python3
"""iOS app icon (1024x1024): full-bleed backgammon board, vibrant warm wood.

Run from repo root:  python3 scripts/gen-icons.py
Writes ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png

No margin, no frame, no border, no checkers — just the playing surface
(alternating points + center bar) filling the entire tile edge to edge
(Apple applies the rounded-square mask). Palette is a richer, more
saturated take on the in-game Ivory wood theme.
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(REPO,
    "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png")

S = 1024

# Vibrant warm-wood palette (richer/higher-contrast than muted Ivory)
BOARD_BG = (0xc9, 0x8a, 0x3e)   # saturated caramel
PT_DARK  = (0x6e, 0x3f, 0x1c)   # deep walnut
PT_LIGHT = (0xf2, 0xdc, 0xa0)   # warm honey cream
BAR_BG   = (0x5a, 0x32, 0x16)   # darker walnut


def main():
    img = Image.new("RGB", (S, S), BOARD_BG)
    d = ImageDraw.Draw(img)

    barW = int(S * 0.085)
    barX0 = (S - barW) // 2
    barX1 = barX0 + barW
    sideW = (S - barW) / 2.0
    colW = sideW / 6.0
    triH = S * 0.42

    def cL(i): return i * colW                 # left-of-bar columns 0..5
    def cR(i): return barX1 + i * colW         # right-of-bar columns 0..5

    # Full-bleed alternating triangles, top (apex down) + bottom (apex up).
    for half, base in (("L", cL), ("R", cR)):
        for i in range(6):
            x0 = base(i); x1 = x0 + colW; xm = (x0 + x1) / 2.0
            idx = i if half == "L" else i + 6
            top = PT_DARK if idx % 2 == 0 else PT_LIGHT
            bot = PT_LIGHT if idx % 2 == 0 else PT_DARK
            d.polygon([(x0, 0), (x1, 0), (xm, triH)], fill=top)
            d.polygon([(x0, S), (x1, S), (xm, S-triH)], fill=bot)

    # Center bar, full height.
    d.rectangle([barX0, 0, barX1, S], fill=BAR_BG)

    os.makedirs(os.path.dirname(ICON), exist_ok=True)
    img.save(ICON, "PNG", optimize=True)
    print("wrote", ICON)


if __name__ == "__main__":
    main()
