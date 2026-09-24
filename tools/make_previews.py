"""Write a 64x64 PNG preview next to every icons/*.ico (the app shows these in its icon picker,
so it needs no imaging library at runtime)."""
import glob
import os

from PIL import Image

ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")

for path in sorted(glob.glob(os.path.join(ICONS_DIR, "*.ico"))):
    ico = Image.open(path)
    size = (64, 64) if (64, 64) in ico.ico.sizes() else max(ico.ico.sizes())
    frame = ico.ico.getimage(size).convert("RGBA")
    if frame.size != (64, 64):
        frame = frame.resize((64, 64), Image.LANCZOS)
    png = os.path.splitext(path)[0] + ".png"
    frame.save(png)
    print("preview", os.path.basename(png))
