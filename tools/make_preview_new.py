import math
import os

from PIL import Image, ImageDraw

# Wave 5 soft preview
def make_wave5_soft_preview():
    GREEN = (47, 179, 68)
    RED = (229, 72, 77)

    dark = (32, 32, 32, 255)
    size = 512
    sheet = Image.new("RGBA", (512 + 100, 512 + 100), dark)

    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    colors = [GREEN, GREEN, RED, GREEN, GREEN]
    heights = [260, 420, 600, 420, 260]
    w, gap = 80, 35
    x = (512 - (5 * w + 4 * gap)) // 2

    for h, color in zip(heights, colors):
        d.rounded_rectangle(
            (x, (512 - h) // 2, x + w, (512 + h) // 2),
            radius=w // 2, fill=color
        )
        x += w + gap

    sheet.paste(im, (50, 50), im)
    sheet.save(os.path.join(os.path.dirname(__file__), "..", "icons", "Wave 5 soft.png"))
    print("Wave 5 soft preview created")


# Mic ring preview
def make_mic_ring_preview():
    size = 512
    dark = (32, 32, 32, 255)
    sheet = Image.new("RGBA", (512 + 100, 512 + 100), dark)

    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Dark navy background
    bg_color = (12, 20, 45, 255)
    d.rounded_rectangle((0, 0, 512, 512), radius=90, fill=bg_color)

    # Microphone
    mic_x, mic_y = 256, 256
    mic_w, mic_h = 100, 180
    mic_color = (240, 245, 250, 255)

    d.rounded_rectangle(
        (mic_x - mic_w // 2, mic_y - mic_h // 2,
         mic_x + mic_w // 2, mic_y + mic_h // 2 - 40),
        radius=50, fill=mic_color
    )

    # Mic stand
    d.rounded_rectangle(
        (mic_x - 60, mic_y + mic_h // 2 - 40,
         mic_x + 60, mic_y + mic_h // 2 + 20),
        radius=30, fill=mic_color
    )

    # Red waves
    wave_color = (240, 80, 80, 255)
    for wy in [mic_y - 40, mic_y + 10, mic_y + 60]:
        d.rounded_rectangle(
            (mic_x - 55, wy - 15, mic_x + 55, wy + 15),
            radius=15, fill=wave_color
        )

    # Ring
    center_x, center_y = 256, 256
    ring_radius = 230
    ring_width = 40

    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        45, 135, fill=(76, 175, 80, 255), width=ring_width
    )
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        135, 225, fill=(66, 165, 245, 255), width=ring_width
    )
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        225, 315, fill=(255, 152, 0, 255), width=ring_width
    )
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        315, 45, fill=(255, 87, 87, 255), width=ring_width
    )

    sheet.paste(im, (25, 25), im)
    sheet.save(os.path.join(os.path.dirname(__file__), "..", "icons", "Mic ring.png"))
    print("Mic ring preview created")


make_wave5_soft_preview()
make_mic_ring_preview()
