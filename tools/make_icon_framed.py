import colorsys
import os

import numpy as np
from PIL import Image, ImageDraw

GREEN = (47, 179, 68)     # COLOR_READY      #2fb344
RED = (229, 72, 77)       # COLOR_RECORDING  #e5484d
FRAME_START = (144, 226, 158)  # frame gradient start (top-left): light mint green
FRAME_END = (47, 179, 68)      # frame gradient end (bottom-right): COLOR_READY green
NAVY = (13, 29, 66, 255)  # screen
SS = 1024
K = 8                     # supersampling factor for the frame's rounded corners
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Frame 7 bars green.ico")
BARS = 7


def color_at(t):
    """Green -> red via yellow (hue sweep)."""
    h0, s0, v0 = colorsys.rgb_to_hsv(*[c / 255 for c in GREEN])
    h1, s1, v1 = colorsys.rgb_to_hsv(*[c / 255 for c in RED])
    h1 -= 1
    r, g, b = colorsys.hsv_to_rgb((h0 + (h1 - h0) * t) % 1, s0 + (s1 - s0) * t, v0 + (v1 - v0) * t)
    return (round(r * 255), round(g * 255), round(b * 255), 255)


BAR_COLORS = [color_at(i / (BARS - 1)) for i in range(BARS)]  # one flat colour per bar, stepping green -> red


def layout(frame, w, gap, heights, x0):
    """Bars as (x0, x1, y0, y1) inclusive, centred vertically on the frame."""
    bars, x = [], x0
    for h in heights:
        y0 = (frame - h) // 2
        bars.append((x, x + w - 1, y0, y0 + h - 1))
        x += w + gap
    return bars


# f = frame edge length in px (odd where 7 bars of odd total width must sit symmetrically). Every coordinate is an integer.
NATIVE = {
    16: dict(f=15, r=4, b=1, bars=layout(15, 1, 1, [3, 5, 9, 11, 9, 5, 3], 1)),
    24: dict(f=23, r=6, b=2, bars=layout(23, 1, 1, [5, 9, 13, 15, 13, 9, 5], 5)),
    32: dict(f=32, r=8, b=2, bars=layout(32, 2, 1, [8, 14, 18, 22, 18, 14, 8], 6)),
    48: dict(f=48, r=11, b=3, bars=layout(48, 2, 3, [10, 18, 26, 34, 26, 18, 10], 8)),
}


def diagonal_gradient(size):
    yy, xx = np.mgrid[0:size, 0:size]
    t = ((xx + yy) / (2 * (size - 1)))[..., None]
    arr = np.array(FRAME_START) + (np.array(FRAME_END) - np.array(FRAME_START)) * t
    rgba = np.dstack([arr, np.full((size, size), 255)]).astype("uint8")
    return Image.fromarray(rgba, "RGBA")


def frame_layer(n, f, r, b):
    """Gradient frame + navy screen drawn at K x, then box-downsampled: smooth corners, pixel-exact straight edges."""
    big, fbig = n * K, f * K
    outer = Image.new("L", (big, big), 0)
    ImageDraw.Draw(outer).rounded_rectangle((0, 0, fbig - 1, fbig - 1), radius=r * K, fill=255)
    layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    layer.paste(diagonal_gradient(fbig), (0, 0), outer.crop((0, 0, fbig, fbig)))
    ImageDraw.Draw(layer).rounded_rectangle(
        (b * K, b * K, fbig - 1 - b * K, fbig - 1 - b * K), radius=max(r - b, 0) * K, fill=NAVY
    )
    return layer.resize((n, n), Image.BOX)


def draw_native(size):
    p = NATIVE[size]
    im = frame_layer(size, p["f"], p["r"], p["b"])
    d = ImageDraw.Draw(im)
    for (x0, x1, y0, y1), color in zip(p["bars"], BAR_COLORS):
        d.rectangle((x0, y0, x1, y1), fill=color)
    return im


def draw_smooth(size):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    outer = Image.new("L", (SS, SS), 0)
    ImageDraw.Draw(outer).rounded_rectangle((16, 16, SS - 17, SS - 17), radius=230, fill=255)
    im.paste(diagonal_gradient(SS), (0, 0), outer)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16 + 60, 16 + 60, SS - 17 - 60, SS - 17 - 60), radius=170, fill=NAVY)
    heights, w, gap = [180, 320, 470, 640, 470, 320, 180], 58, 46
    x = (SS - (BARS * w + (BARS - 1) * gap)) // 2
    for h, color in zip(heights, BAR_COLORS):
        d.rounded_rectangle((x, (SS - h) // 2, x + w, (SS + h) // 2), radius=w // 2, fill=color)
        x += w + gap
    return im.resize((size, size), Image.LANCZOS)


order = [256, 128, 64, 48, 32, 24, 16]
images = [draw_native(s) if s in NATIVE else draw_smooth(s) for s in order]
images[0].save(OUT, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
print("sizes in ico:", sorted(Image.open(OUT).ico.sizes()))

dark = (32, 32, 32, 255)
sheet = Image.new("RGBA", (16 * 8 + 24 * 8 + 32 * 6 + 48 * 4 + 5 * 24 + 40 + 140, 48 * 4 + 100), dark)
x = 20
for s, z_ in ((16, 8), (24, 8), (32, 6), (48, 4)):
    z = draw_native(s).resize((s * z_, s * z_), Image.NEAREST)
    sheet.paste(z, (x, 20), z)
    x += s * z_ + 24
x = 20
for s in (16, 24, 32, 48):
    im = draw_native(s)
    sheet.paste(im, (x, 48 * 4 + 40), im)
    x += s + 20
big = draw_smooth(128)
sheet.paste(big, (x + 20, 48 * 4 - 20), big)
sheet.save(os.path.join(HERE, "preview_framed.png"))
