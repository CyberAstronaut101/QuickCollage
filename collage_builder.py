import os
import sys
from PIL import Image, ImageDraw, ImageFont

FONT_SIZE = 70 # Font Size px for file names
FONT_BOTTOM_MARGIN = 100 # Space for text at the bottom of the image
UPSCALE_SMALL_IMAGES = 0.75 # Percentage of max width or height to upscale small images

def draw_text_with_border(draw, text, position, font, text_color="white", border_color="black", border_size=2):
    # Draw text with border
    x, y = position
    draw.text((x - border_size, y - border_size), text, font=font, fill=border_color)
    draw.text((x + border_size, y - border_size), text, font=font, fill=border_color)
    draw.text((x - border_size, y + border_size), text, font=font, fill=border_color)
    draw.text((x + border_size, y + border_size), text, font=font, fill=border_color)
    # Draw the main text (white)
    draw.text((x, y), text, font=font, fill=text_color)

def scale_to_min_size(image, max_width, max_height, scale_ratio=0.75):
    """Upscales the image if it's smaller than 75% of the max width or height."""
    min_width = int(max_width * scale_ratio)
    min_height = int(max_height * scale_ratio)

    img_width, img_height = image.size

    if img_width < min_width or img_height < min_height:
        # Maintain aspect ratio while scaling
        scale_factor = min(min_width / img_width, min_height / img_height)
        new_size = (int(img_width * scale_factor), int(img_height * scale_factor))
        # return image.resize(new_size, Image.ANTIALIAS)
        return image.resize(new_size, Image.Resampling.LANCZOS)

    return image

def create_image_collage(input_folder, output_image, images_per_row=3, margin=10, background_color=(0, 0, 0)):
    # Get list of images in the folder
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    image_files.sort()  # Sort files alphabetically

    if not image_files:
        print("No images found in the folder.")
        return

    # Load images and find the max width and height for layout purposes
    images = [Image.open(os.path.join(input_folder, file)) for file in image_files]
    max_width = max(image.width for image in images)
    max_height = max(image.height for image in images)

    # Calculate number of rows and columns
    num_images = len(images)
    num_rows = (num_images + images_per_row - 1) // images_per_row

    # Create the final image size, with a black background
    collage_width = images_per_row * (max_width + margin) - margin
    collage_height = num_rows * (max_height + margin)  # Adjusted the height
    collage_image = Image.new('RGB', (collage_width, collage_height), background_color)

    # Optional: Load a font for the text
    try:
        font = ImageFont.truetype("arial.ttf", FONT_SIZE)  # You can use other fonts available on your system
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(collage_image)

    # Iterate through the images and place them in the collage
    for i, image in enumerate(images):
        row = i // images_per_row
        col = i % images_per_row

        # Calculate the position of the image in the grid
        x = col * (max_width + margin)
        y = row * (max_height + margin)

        # Upscale the image if it's smaller than 75% of the bounding box
        image = scale_to_min_size(image, max_width, max_height, scale_ratio=UPSCALE_SMALL_IMAGES)

        # Center the image in the bounding box (center it in max_width x max_height)
        offset_x = (max_width - image.width) // 2
        offset_y = (max_height - image.height) // 2

        # Paste the image with calculated offsets to center it in the grid
        collage_image.paste(image, (x + offset_x, y + offset_y))

        # Draw the file name at the bottom of the image
        file_name = os.path.basename(image_files[i])
        
        # Get the text bounding box to calculate the text position
        bbox = draw.textbbox((0, 0), file_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (max_width - text_width) // 2
        text_y = y + max_height - FONT_BOTTOM_MARGIN  # Place text above the bottom margin

        # Draw the text with a black border and white fill
        draw_text_with_border(draw, file_name, (text_x, text_y), font)

    # Save the final collage image
    collage_image.save(output_image)
    print(f"Collage saved as {output_image}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_folder> <output_image>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_image = sys.argv[2]

    create_image_collage(input_folder, output_image)
