import os

from PIL import Image, ImageDraw

SS = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Mic color ring.ico")


def draw_smooth(size):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    center_x, center_y = SS // 2, SS // 2

    # Colorful ring
    ring_radius = 380
    ring_width = 80

    d.arc((center_x - ring_radius, center_y - ring_radius,
           center_x + ring_radius, center_y + ring_radius),
          45, 135, fill=(76, 175, 80, 255), width=ring_width)  # Green
    d.arc((center_x - ring_radius, center_y - ring_radius,
           center_x + ring_radius, center_y + ring_radius),
          135, 225, fill=(66, 165, 245, 255), width=ring_width)  # Blue
    d.arc((center_x - ring_radius, center_y - ring_radius,
           center_x + ring_radius, center_y + ring_radius),
          225, 315, fill=(255, 152, 0, 255), width=ring_width)  # Orange
    d.arc((center_x - ring_radius, center_y - ring_radius,
           center_x + ring_radius, center_y + ring_radius),
          315, 45, fill=(255, 87, 87, 255), width=ring_width)  # Red

    # White microphone capsule
    mic_w = 200
    mic_h = 320

    # Capsule
    d.rounded_rectangle(
        (center_x - mic_w // 2, center_y - mic_h // 2,
         center_x + mic_w // 2, center_y + mic_h // 2 - 60),
        radius=100, fill=(240, 245, 250, 255)
    )

    # Stand
    d.rounded_rectangle(
        (center_x - 100, center_y + mic_h // 2 - 60,
         center_x + 100, center_y + mic_h // 2 + 40),
        radius=50, fill=(240, 245, 250, 255)
    )

    # Dark red sound waves inside capsule
    wave_color = (180, 40, 40, 255)
    wave_heights = [240, 380, 240]
    wave_x_offsets = [-80, 0, 80]

    for wx_off, wh in zip(wave_x_offsets, wave_heights):
        d.rounded_rectangle(
            (center_x + wx_off - 40, center_y - wh // 2,
             center_x + wx_off + 40, center_y + wh // 2),
            radius=30, fill=wave_color
        )

    return im.resize((size, size), Image.LANCZOS)


# Generate all sizes
order = [256, 128, 64, 48, 32, 24, 16]
images = [draw_smooth(s) for s in order]
images[0].save(OUT, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
print("Mic color ring created:", OUT)
