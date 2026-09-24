import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))


def make_preview():
    SS = 1024
    size = 512
    dark = (32, 32, 32, 255)
    sheet = Image.new("RGBA", (512 + 100, 512 + 100), dark)

    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    center_x, center_y = SS // 2, SS // 2

    # Ring
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

    # Microphone
    mic_w = 200
    mic_h = 320

    d.rounded_rectangle(
        (center_x - mic_w // 2, center_y - mic_h // 2,
         center_x + mic_w // 2, center_y + mic_h // 2 - 60),
        radius=100, fill=(240, 245, 250, 255)
    )

    d.rounded_rectangle(
        (center_x - 100, center_y + mic_h // 2 - 60,
         center_x + 100, center_y + mic_h // 2 + 40),
        radius=50, fill=(240, 245, 250, 255)
    )

    # Waves
    wave_color = (180, 40, 40, 255)
    wave_heights = [240, 380, 240]
    wave_x_offsets = [-80, 0, 80]

    for wx_off, wh in zip(wave_x_offsets, wave_heights):
        d.rounded_rectangle(
            (center_x + wx_off - 40, center_y - wh // 2,
             center_x + wx_off + 40, center_y + wh // 2),
            radius=30, fill=wave_color
        )

    im = im.resize((size, size), Image.LANCZOS)
    sheet.paste(im, (50, 50), im)
    sheet.save(os.path.join(HERE, "..", "icons", "Mic color ring.png"))
    print("Mic color ring preview created")


make_preview()
