import os
from PIL import Image, ImageDraw, ImageFont

def generate_icon(size, filename):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background with gradient effect
    padding = size // 16
    rect = [padding, padding, size - padding, size - padding]
    corner_radius = size // 5
    
    # Background teal gradient simulation
    bg_color = (13, 148, 136, 255) # Teal #0d9488
    draw.rounded_rectangle(rect, corner_radius, fill=bg_color)
    
    # Draw inner heart/pulse design symbol
    center = size // 2
    heart_scale = size / 512.0
    
    # Simple crisp pulse line + heart symbol using vector shapes
    draw.ellipse(
        [center - int(70 * heart_scale), center - int(80 * heart_scale),
         center - int(10 * heart_scale), center - int(20 * heart_scale)],
        fill=(255, 255, 255, 255)
    )
    draw.ellipse(
        [center + int(10 * heart_scale), center - int(80 * heart_scale),
         center + int(70 * heart_scale), center - int(20 * heart_scale)],
        fill=(255, 255, 255, 255)
    )
    points = [
        (center - int(74 * heart_scale), center - int(45 * heart_scale)),
        (center + int(74 * heart_scale), center - int(45 * heart_scale)),
        (center, center + int(80 * heart_scale))
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # Pulse accent line across center
    line_y = center + int(100 * heart_scale)
    line_width = int(24 * heart_scale)
    if line_width < 2:
        line_width = 2
        
    draw.line(
        [(center - int(140 * heart_scale), line_y),
         (center - int(40 * heart_scale), line_y),
         (center - int(10 * heart_scale), line_y - int(30 * heart_scale)),
         (center + int(20 * heart_scale), line_y + int(30 * heart_scale)),
         (center + int(50 * heart_scale), line_y - int(15 * heart_scale)),
         (center + int(70 * heart_scale), line_y),
         (center + int(140 * heart_scale), line_y)],
        fill=(56, 189, 248, 255), width=line_width
    )
    
    out_dir = os.path.join("app", "static", "img")
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)
    img.save(filepath)
    print(f"Generated {filepath} ({size}x{size})")

if __name__ == '__main__':
    generate_icon(192, "icon-192.png")
    generate_icon(512, "icon-512.png")
    generate_icon(180, "apple-touch-icon.png")
    generate_icon(64, "favicon.ico")
