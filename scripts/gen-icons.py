#!/usr/bin/env python3
"""iOS app icon (1024x1024): a clean stylized backgammon board in the
in-game Ivory theme palette.

Run from repo root:  python3 scripts/gen-icons.py
Writes ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png

No transparency / no pre-rounded corners (Apple applies the mask). The
board is inset on a cream field so Apple's corner rounding never clips
the board frame.
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(REPO,
    "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png")

S = 1024

# Ivory theme palette (from SKINS.ivory in www/index.html)
CANVAS      = (0xf8, 0xf0, 0xd8)
BOARD_BG    = (0xb8, 0x98, 0x68)
BOARD_LIGHT = (0xd4, 0xb8, 0x88)
BOARD_BORD  = (0x8a, 0x68, 0x38)
PT_DARK     = (0x6a, 0x48, 0x28)
PT_LIGHT    = (0xe8, 0xd8, 0xa8)
BAR_BG      = (0x6a, 0x48, 0x28)
P_CHK       = (0xfa, 0xf4, 0xe0)
P_CHK_BORD  = (0xb8, 0xa0, 0x70)
C_CHK       = (0x3a, 0x20, 0x10)
C_CHK_BORD  = (0x2a, 0x18, 0x08)


def rr(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


def checker(d, cx, cy, rad, fill, border):
    d.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=border)
    inset = max(1, int(rad*0.16))
    d.ellipse([cx-rad+inset, cy-rad+inset, cx+rad-inset, cy+rad-inset], fill=fill)
    # soft top-left highlight
    hr = int(rad*0.42)
    hx, hy = cx-int(rad*0.22), cy-int(rad*0.22)
    hl = tuple(min(255, c+28) for c in fill)
    d.ellipse([hx-hr, hy-hr, hx+hr, hy+hr], fill=hl)


def main():
    img = Image.new("RGB", (S, S), CANVAS)
    d = ImageDraw.Draw(img)

    M = 70                       # cream margin around the board
    bx0, by0, bx1, by1 = M, M, S-M, S-M
    # Board frame
    rr(d, [bx0, by0, bx1, by1], 46, fill=BOARD_BORD)
    fw = 30                      # frame thickness
    ix0, iy0, ix1, iy1 = bx0+fw, by0+fw, bx1-fw, by1-fw
    rr(d, [ix0, iy0, ix1, iy1], 22, fill=BOARD_BG)

    innerW = ix1 - ix0
    innerH = iy1 - iy0
    barW = int(innerW * 0.085)
    barX0 = ix0 + (innerW - barW)//2
    barX1 = barX0 + barW
    sideW = (innerW - barW) / 2.0
    colW = sideW / 6.0
    triH = innerH * 0.40
    midY = (iy0 + iy1) / 2.0

    def col_left(i):  # left-of-bar column i (0..5)
        return ix0 + i*colW
    def col_right(i):
        return barX1 + i*colW

    # 12 columns: top triangle (apex down) + bottom triangle (apex up),
    # checkerboard color phasing for a rich, unmistakable board look.
    for half, base in (("L", col_left), ("R", col_right)):
        for i in range(6):
            x0 = base(i)
            x1 = x0 + colW
            xm = (x0 + x1) / 2.0
            idx = i if half == "L" else i+6
            top_col = PT_DARK if idx % 2 == 0 else PT_LIGHT
            bot_col = PT_LIGHT if idx % 2 == 0 else PT_DARK
            # top, pointing down
            d.polygon([(x0, iy0), (x1, iy0), (xm, iy0+triH)], fill=top_col)
            # bottom, pointing up
            d.polygon([(x0, iy1), (x1, iy1), (xm, iy1-triH)], fill=bot_col)

    # Center bar
    d.rectangle([barX0, iy0, barX1, iy1], fill=BAR_BG)

    # A few checker stacks for the cream/dark colour pop (loosely the
    # classic opening shape — reads as "backgammon").
    cr = colW * 0.40
    sp = cr * 1.5

    def stack(cx, top_y, n, fill, bord, downward):
        for k in range(n):
            cy = top_y + (k*sp if downward else -k*sp)
            checker(d, cx, cy, cr, fill, bord)

    # left-bottom: cream 5 ; right-bottom: dark 5
    stack(col_left(0)+colW/2, iy1-cr-6, 5, P_CHK, P_CHK_BORD, downward=False)
    stack(col_right(5)+colW/2, iy1-cr-6, 5, C_CHK, C_CHK_BORD, downward=False)
    # top: dark 3 on a left point, cream 3 on a right point
    stack(col_left(4)+colW/2, iy0+cr+6, 3, C_CHK, C_CHK_BORD, downward=True)
    stack(col_right(1)+colW/2, iy0+cr+6, 3, P_CHK, P_CHK_BORD, downward=True)

    os.makedirs(os.path.dirname(ICON), exist_ok=True)
    img.save(ICON, "PNG", optimize=True)
    print("wrote", ICON)


if __name__ == "__main__":
    main()
