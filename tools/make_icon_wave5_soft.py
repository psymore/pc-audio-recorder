import colorsys
import os

from PIL import Image, ImageDraw

GREEN = (47, 179, 68)     # COLOR_READY      #2fb344  (outer blocks)
RED = (229, 72, 77)       # COLOR_RECORDING  #e5484d  (center block)
SS = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Wave 5 soft.ico")
BARS = 5


def draw_smooth(size):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # 5 blocks: green, green, red, green, green
    colors = [GREEN, GREEN, RED, GREEN, GREEN]
    heights = [320, 560, 860, 560, 320]
    w, gap = 140, 60
    x = (SS - (BARS * w + (BARS - 1) * gap)) // 2
    for h, color in zip(heights, colors):
        d.rounded_rectangle((x, (SS - h) // 2, x + w, (SS + h) // 2), radius=w // 2, fill=color)
        x += w + gap
    return im.resize((size, size), Image.LANCZOS)


order = [256, 128, 64, 48, 32, 24, 16]
images = [draw_smooth(s) for s in order]
images[0].save(OUT, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
print("Wave 5 soft created:", OUT)
