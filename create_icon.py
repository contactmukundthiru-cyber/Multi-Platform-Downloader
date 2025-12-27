#!/usr/bin/env python3
"""
Flare Download - Icon Generator
Creates a professional fire-themed icon for the application.
"""

import os
import sys

def create_icon():
    """Generate a professional Flare Download icon."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        print("Pillow not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
        from PIL import Image, ImageDraw, ImageFont, ImageFilter

    # Icon sizes for Windows ICO (multiple resolutions)
    sizes = [256, 128, 64, 48, 32, 16]

    images = []

    for size in sizes:
        # Create base image with transparency
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle with gradient effect
        center = size // 2
        radius = int(size * 0.45)

        # Draw outer glow
        for i in range(10, 0, -1):
            glow_radius = radius + i * (size // 20)
            alpha = int(30 * (10 - i) / 10)
            glow_color = (255, 69, 0, alpha)  # Fire orange with fading alpha
            draw.ellipse(
                [center - glow_radius, center - glow_radius,
                 center + glow_radius, center + glow_radius],
                fill=glow_color
            )

        # Main circle - dark background
        draw.ellipse(
            [center - radius, center - radius,
             center + radius, center + radius],
            fill=(10, 10, 10, 255)
        )

        # Inner circle - slightly lighter
        inner_radius = int(radius * 0.85)
        draw.ellipse(
            [center - inner_radius, center - inner_radius,
             center + inner_radius, center + inner_radius],
            fill=(20, 20, 20, 255)
        )

        # Draw stylized flame/arrow pointing down
        flame_height = int(size * 0.5)
        flame_width = int(size * 0.35)

        # Flame points (stylized download arrow with fire effect)
        top_y = center - int(flame_height * 0.4)
        bottom_y = center + int(flame_height * 0.5)

        # Main flame body (download arrow shape)
        points = [
            (center, bottom_y),  # Bottom point
            (center - flame_width // 2, center - int(flame_height * 0.1)),  # Left
            (center - flame_width // 4, center - int(flame_height * 0.1)),  # Left inner
            (center - flame_width // 4, top_y),  # Left top
            (center + flame_width // 4, top_y),  # Right top
            (center + flame_width // 4, center - int(flame_height * 0.1)),  # Right inner
            (center + flame_width // 2, center - int(flame_height * 0.1)),  # Right
        ]

        # Draw fire gradient - multiple layers for depth
        # Outer fire (darker red)
        draw.polygon(points, fill=(180, 30, 0, 255))

        # Inner fire (bright orange)
        inner_scale = 0.8
        inner_points = [
            (center, bottom_y - int(flame_height * 0.1)),
            (center - int(flame_width * inner_scale) // 2, center - int(flame_height * 0.05)),
            (center - int(flame_width * inner_scale) // 4, center - int(flame_height * 0.05)),
            (center - int(flame_width * inner_scale) // 4, top_y + int(flame_height * 0.1)),
            (center + int(flame_width * inner_scale) // 4, top_y + int(flame_height * 0.1)),
            (center + int(flame_width * inner_scale) // 4, center - int(flame_height * 0.05)),
            (center + int(flame_width * inner_scale) // 2, center - int(flame_height * 0.05)),
        ]
        draw.polygon(inner_points, fill=(255, 69, 0, 255))

        # Core fire (bright yellow-orange)
        core_scale = 0.5
        core_points = [
            (center, bottom_y - int(flame_height * 0.2)),
            (center - int(flame_width * core_scale) // 2, center),
            (center - int(flame_width * core_scale) // 4, center),
            (center - int(flame_width * core_scale) // 4, top_y + int(flame_height * 0.2)),
            (center + int(flame_width * core_scale) // 4, top_y + int(flame_height * 0.2)),
            (center + int(flame_width * core_scale) // 4, center),
            (center + int(flame_width * core_scale) // 2, center),
        ]
        draw.polygon(core_points, fill=(255, 140, 0, 255))

        # Add small flame flickers at top
        flicker_size = max(2, size // 20)
        for offset in [-flame_width // 6, 0, flame_width // 6]:
            flicker_x = center + offset
            flicker_y = top_y - flicker_size
            draw.ellipse(
                [flicker_x - flicker_size, flicker_y - flicker_size,
                 flicker_x + flicker_size, flicker_y + flicker_size],
                fill=(255, 100, 0, 200)
            )

        images.append(img)

    # Save as ICO (Windows icon format)
    ico_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"Created: {ico_path}")

    # Also save as PNG for other uses
    png_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    images[0].save(png_path, format='PNG')
    print(f"Created: {png_path}")

    # Create a larger promotional image
    promo_size = 512
    promo = Image.new('RGBA', (promo_size, promo_size), (0, 0, 0, 255))
    promo_draw = ImageDraw.Draw(promo)

    # Paste the icon centered
    icon_large = images[0].resize((384, 384), Image.LANCZOS)
    promo.paste(icon_large, (64, 40), icon_large)

    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = font

    promo_draw.text((promo_size // 2, 450), "FLARE", fill=(255, 255, 255, 255),
                    font=font, anchor="mm")
    promo_draw.text((promo_size // 2, 485), "DOWNLOAD", fill=(136, 136, 136, 255),
                    font=small_font, anchor="mm")

    promo_path = os.path.join(os.path.dirname(__file__), 'icon_promo.png')
    promo.save(promo_path, format='PNG')
    print(f"Created: {promo_path}")

    return ico_path


if __name__ == "__main__":
    print("=" * 50)
    print("Flare Download - Icon Generator")
    print("=" * 50)
    print()

    icon_path = create_icon()

    print()
    print("=" * 50)
    print("Icons created successfully!")
    print("=" * 50)
    print()
    print("Files created:")
    print("  - icon.ico    (Windows application icon)")
    print("  - icon.png    (256x256 PNG icon)")
    print("  - icon_promo.png (512x512 promotional image)")
    print()
    print("Next steps:")
    print("  1. Run build_installer.bat to build with icon")
    print("  2. The installer will use the new icon")
