import colorsys
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(HERE, "..", "icons")
SS = 1024

FRAME_BLUE = (31, 111, 235, 255)
RED = (229, 72, 77, 255)      # COLOR_RECORDING
GREEN = (47, 179, 68)         # COLOR_READY

# name -> (frame colour, screen colour, "flat" red bars or "gradient" green->red bars)
VARIANTS = {
    "Monitor navy": (FRAME_BLUE, (11, 27, 61, 255), "flat"),
    "Monitor white": (FRAME_BLUE, (238, 244, 255, 255), "flat"),
    "Monitor sky": (FRAME_BLUE, (138, 212, 255, 255), "flat"),
    "Monitor gradient": ((24, 99, 233, 255), (13, 29, 66, 255), "gradient"),
}

# Pixel-grid layouts (integer coordinates): body/screen/neck/base = (x0, y0, x1, y1), bars = (x0, x1, y0, y1).
NATIVE = {
    16: dict(body=(0, 0, 15, 12), body_r=1, screen=(2, 2, 13, 10), screen_r=0,
             bars=[(3, 4, 4, 8), (7, 8, 3, 9), (11, 12, 4, 8)], neck=(7, 13, 8, 14), base=(4, 15, 11, 15), base_r=0),
    24: dict(body=(0, 0, 23, 20), body_r=2, screen=(2, 2, 21, 18), screen_r=1,
             bars=[(4, 7, 6, 14), (10, 13, 4, 16), (16, 19, 6, 14)], neck=(10, 21, 13, 21), base=(6, 22, 17, 23), base_r=0),
    32: dict(body=(0, 0, 31, 26), body_r=3, screen=(3, 3, 28, 23), screen_r=2,
             bars=[(5, 10, 8, 18), (13, 18, 5, 21), (21, 26, 8, 18)], neck=(13, 27, 18, 28), base=(8, 29, 23, 31), base_r=0),
    48: dict(body=(0, 0, 47, 39), body_r=5, screen=(4, 4, 43, 35), screen_r=2,
             bars=[(10, 13, 15, 24), (16, 19, 11, 28), (22, 25, 8, 31), (28, 31, 11, 28), (34, 37, 15, 24)],
             neck=(20, 40, 27, 43), base=(12, 44, 35, 47), base_r=0),
}


def bar_colors(n, mode):
    if mode == "flat":
        return [RED] * n
    h0, s0, v0 = colorsys.rgb_to_hsv(*[c / 255 for c in GREEN])
    h1, s1, v1 = colorsys.rgb_to_hsv(229 / 255, 72 / 255, 77 / 255)
    h1 -= 1  # sweep through yellow
    out = []
    for i in range(n):
        t = i / (n - 1)
        r, g, b = colorsys.hsv_to_rgb((h0 + (h1 - h0) * t) % 1, s0 + (s1 - s0) * t, v0 + (v1 - v0) * t)
        out.append((round(r * 255), round(g * 255), round(b * 255), 255))
    return out


def draw_native(size, frame, screen, mode):
    p = NATIVE[size]
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(p["body"], radius=p["body_r"], fill=frame)
    d.rounded_rectangle(p["screen"], radius=p["screen_r"], fill=screen)
    d.rectangle(p["neck"], fill=frame)
    d.rounded_rectangle(p["base"], radius=p["base_r"], fill=frame)
    for (x0, x1, y0, y1), color in zip(p["bars"], bar_colors(len(p["bars"]), mode)):
        d.rectangle((x0, y0, x1, y1), fill=color)
    return im


def draw_smooth(size, frame, screen, mode):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16, 48, 1008, 800), radius=110, fill=frame)
    d.rounded_rectangle((104, 136, 920, 712), radius=52, fill=screen)
    d.rectangle((424, 796, 600, 904), fill=frame)
    d.rounded_rectangle((224, 892, 800, 984), radius=46, fill=frame)
    heights, w, gap = [200, 340, 470, 340, 200], 100, 54
    x = 512 - (len(heights) * w + (len(heights) - 1) * gap) // 2
    for h, color in zip(heights, bar_colors(len(heights), mode)):
        d.rounded_rectangle((x, 424 - h // 2, x + w, 424 + h // 2), radius=w // 2, fill=color)
        x += w + gap
    return im.resize((size, size), Image.LANCZOS)


order = [256, 128, 64, 48, 32, 24, 16]
os.makedirs(ICONS_DIR, exist_ok=True)
for name, (frame, screen, mode) in VARIANTS.items():
    images = [draw_native(s, frame, screen, mode) if s in NATIVE else draw_smooth(s, frame, screen, mode) for s in order]
    out = os.path.join(ICONS_DIR, name + ".ico")
    images[0].save(out, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
    print("wrote", os.path.basename(out))
