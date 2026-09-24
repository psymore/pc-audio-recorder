import math
import os

from PIL import Image, ImageDraw

SS = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "icons", "Mic ring.ico")


def draw_smooth(size):
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Dark navy background with rounded corners
    bg_color = (12, 20, 45, 255)  # Very dark navy
    d.rounded_rectangle((0, 0, SS, SS), radius=160, fill=bg_color)

    # Microphone: white mic body with red sound waves
    mic_x, mic_y = SS // 2, SS // 2
    mic_w, mic_h = 180, 340

    # Mic capsule (rounded rectangle)
    mic_color = (240, 245, 250, 255)  # White
    d.rounded_rectangle(
        (mic_x - mic_w // 2, mic_y - mic_h // 2,
         mic_x + mic_w // 2, mic_y + mic_h // 2 - 80),
        radius=90, fill=mic_color
    )

    # Mic stand
    stand_w = 120
    d.rounded_rectangle(
        (mic_x - stand_w // 2, mic_y + mic_h // 2 - 80,
         mic_x + stand_w // 2, mic_y + mic_h // 2 + 40),
        radius=60, fill=mic_color
    )

    # Red sound waves on mic capsule
    wave_color = (240, 80, 80, 255)  # Red
    wave_y_positions = [mic_y - 80, mic_y - 10, mic_y + 60]
    wave_w = 100
    for wy in wave_y_positions:
        d.rounded_rectangle(
            (mic_x - wave_w // 2, wy - 30,
             mic_x + wave_w // 2, wy + 30),
            radius=30, fill=wave_color
        )

    # Colorful ring around microphone (green, blue, orange, red)
    ring_radius = 420
    ring_width = 70
    center_x, center_y = SS // 2, SS // 2

    # Ring colors: green (top-left), blue (bottom-left), orange (bottom-right), red (top-right)
    ring_colors = [
        (76, 175, 80, 255),      # Green
        (66, 165, 245, 255),     # Blue
        (255, 152, 0, 255),      # Orange
        (255, 87, 87, 255),      # Red
    ]

    # Draw ring in quarters
    steps_per_quarter = 256
    for quarter in range(4):
        color = ring_colors[quarter]
        start_angle = quarter * 90
        end_angle = (quarter + 1) * 90

        for angle in range(start_angle, end_angle, 1):
            rad = math.radians(angle)
            x = center_x + ring_radius * math.cos(rad)
            y = center_y + ring_radius * math.sin(rad)

            # Draw a small arc segment
            d.arc(
                (x - ring_width // 2, y - ring_width // 2,
                 x + ring_width // 2, y + ring_width // 2),
                0, 360, fill=color, width=ring_width
            )

    # Actually, simpler approach - draw curved segments
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        45, 135, fill=(76, 175, 80, 255), width=ring_width
    )  # Green (top-left)
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        135, 225, fill=(66, 165, 245, 255), width=ring_width
    )  # Blue (bottom-left)
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        225, 315, fill=(255, 152, 0, 255), width=ring_width
    )  # Orange (bottom-right)
    d.arc(
        (center_x - ring_radius, center_y - ring_radius,
         center_x + ring_radius, center_y + ring_radius),
        315, 45, fill=(255, 87, 87, 255), width=ring_width
    )  # Red (top-right)

    return im.resize((size, size), Image.LANCZOS)


order = [256, 128, 64, 48, 32, 24, 16]
images = [draw_smooth(s) for s in order]
images[0].save(OUT, format="ICO", sizes=[(s, s) for s in order], append_images=images[1:])
print("Mic ring created:", OUT)
