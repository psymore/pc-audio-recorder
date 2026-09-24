import colorsys
import os

from PIL import Image, ImageDraw

GREEN = (47, 179, 68)   # COLOR_READY  #2fb344
RED = (229, 72, 77)     # COLOR_RECORDING #e5484d
SS = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Wave 5 gradient bars.ico")


def color_at(t):
    """Continuous green -> red gradient via yellow (hue sweep), t in [0, 1]."""
    h0, s0, v0 = colorsys.rgb_to_hsv(*[c / 255 for c in GREEN])
    h1, s1, v1 = colorsys.rgb_to_hsv(*[c / 255 for c in RED])
    h1 -= 1
    r, g, b = colorsys.hsv_to_rgb((h0 + (h1 - h0) * t) % 1, s0 + (s1 - s0) * t, v0 + (v1 - v0) * t)
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def bar_t(i, n, u):
    """Gradient position for bar i of n at horizontal fraction u (0 = left edge, 1 = right edge).
    Each bar runs from its left neighbour's colour to its right neighbour's colour."""
    step = 1 / (n - 1)
    return min(max(i * step + (u - 0.5) * 2 * step, 0), 1)


def layout(size, w, gap, heights, x0):
    """Bars as (x0, x1, y0, y1) inclusive, vertically centred on the canvas (heights must match size parity)."""
    bars, x = [], x0
    for h in heights:
        y0 = (size - h) // 2
        bars.append((x, x + w - 1, y0, y0 + h - 1))
        x += w + gap
    return bars


NATIVE = {
    16: layout(16, 2, 1, [6, 10, 14, 10, 6], 1),
    24: layout(24, 3, 2, [8, 14, 22, 14, 8], 0),
    32: layout(32, 4, 2, [10, 18, 28, 18, 10], 2),
    48: layout(48, 6, 3, [16, 28, 42, 28, 16], 3),
}


def draw_native(size):
    bars = NATIVE[size]
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(bars)
    for i, (x0, x1, y0, y1) in enumerate(bars):
        for x in range(x0, x1 + 1):
            d.rectangle((x, y0, x, y1), fill=color_at(bar_t(i, n, (x - x0) / (x1 - x0))))
    return im


def draw_smooth(size):
    heights, w, gap = [300, 540, 860, 540, 300], 160, 50
    x = (SS - (len(heights) * w + (len(heights) - 1) * gap)) // 2
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    n = len(heights)
    for i, h in enumerate(heights):
        strip = Image.new("RGBA", (w + 1, 1))
        for px in range(w + 1):
            strip.putpixel((px, 0), color_at(bar_t(i, n, px / w)))
        bar = strip.resize((w + 1, h + 1), Image.NEAREST)
        mask = Image.new("L", (w + 1, h + 1), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=w // 2, fill=255)
        im.paste(bar, (x, (SS - h) // 2), mask)
        x += w + gap
    return im.resize((size, size), Image.LANCZOS)


order = [256, 128, 64, 48, 32, 24, 16]
images = [draw_native(s) if s in NATIVE else draw_smooth(s) for s in order]
images[0].save(OUT, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
print("sizes in ico:", sorted(Image.open(OUT).ico.sizes()))

dark = (32, 32, 32, 255)
sheet = Image.new("RGBA", (16 * 8 + 24 * 8 + 32 * 8 + 48 * 4 + 4 * 24 + 40 + 100, 48 * 4 + 90), dark)
x = 20
for s in (16, 24, 32):
    z = draw_native(s).resize((s * 8, s * 8), Image.NEAREST)
    sheet.paste(z, (x, 20), z)
    x += s * 8 + 24
z = draw_native(48).resize((48 * 4, 48 * 4), Image.NEAREST)
sheet.paste(z, (x, 20), z)
x = 20
for s in (16, 24, 32, 48):
    im = draw_native(s)
    sheet.paste(im, (x, 48 * 4 + 40), im)
    x += s + 20
big = draw_smooth(64)
sheet.paste(big, (x + 20, 48 * 4 + 20), big)
sheet.save(os.path.join(HERE, "preview.png"))
