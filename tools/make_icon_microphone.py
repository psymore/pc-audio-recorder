import os

from PIL import Image, ImageDraw

SS = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Microphone.ico")


def draw_native(size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    center_x, center_y = size // 2, size // 2

    # White microphone
    mic_w = max(2, size // 5)
    mic_h = max(4, size // 3)

    # Capsule (rounded oval)
    d.rounded_rectangle(
        (center_x - mic_w // 2, center_y - mic_h // 2,
         center_x + mic_w // 2, center_y + mic_h // 2 - size // 8),
        radius=mic_w // 2, fill=(240, 245, 250, 255)
    )

    # Stand
    stand_w = max(1, size // 8)
    d.rounded_rectangle(
        (center_x - stand_w // 2, center_y + mic_h // 2 - size // 8,
         center_x + stand_w // 2, center_y + mic_h // 2 + size // 20),
        radius=max(1, stand_w // 2), fill=(240, 245, 250, 255)
    )

    # Red sound waves
    wave_color = (229, 72, 77, 255)
    wave_w = max(1, size // 12)
    for offset in [-size // 6, 0, size // 6]:
        d.rounded_rectangle(
            (center_x + offset - wave_w // 2, center_y - size // 6,
             center_x + offset + wave_w // 2, center_y + size // 6),
            radius=max(1, wave_w // 3), fill=wave_color
        )

    return im


def draw_smooth(size):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    center_x, center_y = SS // 2, SS // 2

    # White microphone capsule
    mic_w = 180
    mic_h = 320

    d.rounded_rectangle(
        (center_x - mic_w // 2, center_y - mic_h // 2,
         center_x + mic_w // 2, center_y + mic_h // 2 - 60),
        radius=90, fill=(240, 245, 250, 255)
    )

    # Stand
    d.rounded_rectangle(
        (center_x - 90, center_y + mic_h // 2 - 60,
         center_x + 90, center_y + mic_h // 2 + 30),
        radius=45, fill=(240, 245, 250, 255)
    )

    # Red sound waves
    wave_color = (229, 72, 77, 255)
    for offset in [-100, 0, 100]:
        d.rounded_rectangle(
            (center_x + offset - 50, center_y - 200,
             center_x + offset + 50, center_y + 200),
            radius=25, fill=wave_color
        )

    return im.resize((size, size), Image.LANCZOS)


# Pixel-perfect native sizes
NATIVE = {
    16: draw_native(16),
    24: draw_native(24),
    32: draw_native(32),
    48: draw_native(48),
}

order = [256, 128, 64, 48, 32, 24, 16]
images = [NATIVE[s] if s in NATIVE else draw_smooth(s) for s in order]
images[0].save(OUT, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
print("Microphone icon created:", OUT)
