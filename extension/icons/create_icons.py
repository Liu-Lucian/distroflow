"""
Generate placeholder icons for DistroFlow extension
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon(size, filename):
    """Create a simple gradient icon with rocket emoji"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)

    # Draw gradient background (purple to blue)
    for y in range(size):
        # Interpolate between two colors
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Try to add text emoji (may not render well on all systems)
    try:
        # Attempt to use system font for emoji
        font_size = int(size * 0.6)
        try:
            # Try common emoji font locations
            font_paths = [
                '/System/Library/Fonts/Apple Color Emoji.ttc',  # macOS
                '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',  # Linux
                'C:\\Windows\\Fonts\\seguiemj.ttf',  # Windows
            ]
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break

            if font:
                text = "🚀"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((size - text_width) // 2, (size - text_height) // 2)
                draw.text(position, text, fill='white', font=font)
            else:
                # Fallback: draw a simple shape
                draw_simple_logo(draw, size)
        except Exception:
            # Fallback if font loading fails
            draw_simple_logo(draw, size)
    except Exception:
        draw_simple_logo(draw, size)

    # Save the image
    img.save(filename)
    print(f"Created {filename}")


def draw_simple_logo(draw, size):
    """Draw a simple rocket-like shape when emoji isn't available"""
    center_x = size // 2
    center_y = size // 2
    rocket_size = size // 3

    # Draw rocket body (triangle pointing up)
    points = [
        (center_x, center_y - rocket_size),  # Top
        (center_x - rocket_size // 2, center_y + rocket_size // 2),  # Bottom left
        (center_x + rocket_size // 2, center_y + rocket_size // 2),  # Bottom right
    ]
    draw.polygon(points, fill='white')

    # Draw rocket window (circle)
    window_radius = rocket_size // 4
    window_bbox = [
        center_x - window_radius,
        center_y - window_radius // 2,
        center_x + window_radius,
        center_y + window_radius // 2,
    ]
    draw.ellipse(window_bbox, fill=(102, 126, 234))


if __name__ == '__main__':
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create icons in different sizes
    sizes = [16, 48, 128]

    for size in sizes:
        filename = os.path.join(script_dir, f'icon{size}.png')
        create_icon(size, filename)

    print("\nIcons created successfully!")
    print("If emoji didn't render, you'll see a simple rocket shape instead.")
