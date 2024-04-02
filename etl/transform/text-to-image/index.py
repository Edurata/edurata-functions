from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji
import os
import emoji

def create_gradient(size, color):
    """Create a vertical linear gradient from dark to light of the given color."""
    gradient = Image.new('RGB', size)
    for y in range(size[1]):
        brightness = int(255 * (1 - y / size[1]))  # Dark to light
        line_color = tuple(min(c + brightness, 255) for c in color)
        for x in range(size[0]):
            gradient.putpixel((x, y), line_color)
    return gradient

def estimate_text_size(text, font):
    """Estimates the width of text."""
    return font.getsize(text)

def adjust_font_size(image_width, text, font_path, padding):
    """Adjusts the font size so that the text fits within the image width along with padding."""
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    
    # Find the maximum font size that fits the text within the image width along with padding
    while True:
        font = ImageFont.truetype(font_path, font_size)
        max_line_width = max(estimate_text_size(line, font)[0] for line in text.split('\n'))
        if max_line_width + 2 * padding >= image_width:
            break
        font_size += 1
    
    return ImageFont.truetype(font_path, font_size)

def render_text_centered_with_emojis(image, text, font_path, text_color, vertical_padding=30, horizontal_padding=30):
    """Renders text centered on the image with automatic line wrapping and emoji support."""
    image_width, image_height = image.size
    font = adjust_font_size(image_width, text, font_path, horizontal_padding)
    draw = ImageDraw.Draw(image)
    
    # Calculate line width and wrap text
    max_line_width = image_width - (2 * horizontal_padding)
    lines = text.split('\n')
    
    # Estimate total text height for vertical centering
    total_text_height = sum(estimate_text_size(line, font)[1] for line in lines)
    total_text_height_with_padding = total_text_height + vertical_padding * (len(lines) - 1)  # Add padding between lines
    
    # Start position for vertical centering
    y = (image_height - total_text_height_with_padding) // 2
    
    with Pilmoji(image) as pilmoji:
        for line in lines[:-1]:  # Skip the last line
            line_width, line_height = estimate_text_size(line, font)
            x = (image_width - line_width) // 2
            pilmoji.text((x, y), line, fill=text_color, font=font)
            y += line_height  # Ensure y increment is an integer
            y += vertical_padding  # Add vertical padding between lines
        
        # Render the last line without vertical padding
        line = lines[-1]
        line_width, line_height = estimate_text_size(line, font)
        x = (image_width - line_width) // 2
        pilmoji.text((x, y), line, fill=text_color, font=font)

def handler(inputs):
    image_type = inputs["type"]
    text = inputs["text"].strip()
    text_color = inputs.get("textColor", "black")
    color = inputs.get("color", (0, 0, 128))  # Default: navy
    vertical_padding = inputs.get("verticalPadding", 30)  # Default vertical padding: 30
    horizontal_padding = inputs.get("horizontalPadding", 30)  # Default horizontal padding: 30

    size = (1080, 1080) if image_type == "feed" else (1080, 1920)
    image = create_gradient(size, color)

    font_path = "./arial.ttf"  # Ensure this path is correct
    
    # Render centered text with emoji support
    render_text_centered_with_emojis(image, text, font_path, text_color, vertical_padding, horizontal_padding)

    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"{image_type}_image.png")
    image.save(image_path)

    return {"imagePath": image_path}

# Example function call
# post = """
# 🏠 Exciting Update! 
# 🎉 Check out our latest additions on our Airbnb-style app:

# 🌟 Charming Cottage Retreat
# 🌆 Stylish Urban Loft
# 🏖️ Beachfront Bungalow
# 🏞️ Tranquil Mountain Cabin

# Start planning your next getaway now! 


# #Travel #Airbnb #NewListings 🌟✈️🛏️
# """
# print(handler({"type": "story", "text": post, "textColor": "black", "color": (0, 128, 128), "verticalPadding": 20, "horizontalPadding": 40}))

