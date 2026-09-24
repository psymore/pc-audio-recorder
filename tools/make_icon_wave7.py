import colorsys
import os

from PIL import Image, ImageDraw

GREEN = (47, 179, 68)     # COLOR_READY      #2fb344  (first bar)
YELLOW = (250, 204, 21)   #                  #facc15  (middle bar)
RED = (229, 72, 77)       # COLOR_RECORDING  #e5484d  (last bar)
SS = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Wave 7 bars.ico")
BARS = 7


def color_at(t):
    """Green -> yellow -> red; hue sweeps downward through lime and orange, so every step stays vivid."""
    stops = [(0.0, GREEN), (0.5, YELLOW), (1.0, RED)]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            h0, s0, v0 = colorsys.rgb_to_hsv(*[c / 255 for c in c0])
            h1, s1, v1 = colorsys.rgb_to_hsv(*[c / 255 for c in c1])
            if h1 > h0:
                h1 -= 1
            r, g, b = colorsys.hsv_to_rgb((h0 + (h1 - h0) * u) % 1, s0 + (s1 - s0) * u, v0 + (v1 - v0) * u)
            return (round(r * 255), round(g * 255), round(b * 255), 255)


BAR_COLORS = [color_at(i / (BARS - 1)) for i in range(BARS)]  # one flat colour per bar


def layout(size, w, gap, heights, x0):
    """Equal-width bars as (x0, x1, y0, y1) inclusive, centred vertically."""
    bars, x = [], x0
    for h in heights:
        y0 = (size - h) // 2
        bars.append((x, x + w - 1, y0, y0 + h - 1))
        x += w + gap
    return bars


# Pixel-grid layouts, all coordinates integer. Heights must be even (canvas sizes are even).
# At 16 px seven 1 px bars cannot be centred exactly (odd total width), so that one sits half a pixel left.
NATIVE = {
    16: layout(16, 1, 1, [4, 6, 10, 14, 10, 6, 4], 1),
    24: layout(24, 2, 1, [6, 10, 16, 22, 16, 10, 6], 2),
    32: layout(32, 2, 2, [8, 14, 20, 30, 20, 14, 8], 3),
    48: layout(48, 4, 2, [12, 20, 30, 42, 30, 20, 12], 4),
}


def draw_native(size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for (x0, x1, y0, y1), color in zip(NATIVE[size], BAR_COLORS):
        d.rectangle((x0, y0, x1, y1), fill=color)
    return im


def draw_smooth(size):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    heights, w, gap = [260, 420, 600, 860, 600, 420, 260], 90, 50
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
sheet.save(os.path.join(HERE, "preview_wave7.png"))
