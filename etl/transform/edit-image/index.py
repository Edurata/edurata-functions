import os
from PIL import Image
import numpy as np

def handler(inputs):
    image_path = inputs['image']
    crop_box = inputs.get('crop_box')
    color_range = inputs.get('color_range')

    # Open the image
    image = Image.open(image_path)

    # Crop the image if crop_box is defined
    if crop_box:
        image = image.crop((crop_box['left'], crop_box['upper'], crop_box['right'], crop_box['lower']))

    # Filter out the color range if color_range is defined
    if color_range:
        image_np = np.array(image)
        lower_bound = np.array(color_range['lower_bound'], dtype=np.uint8)
        upper_bound = np.array(color_range['upper_bound'], dtype=np.uint8)
        mask = cv2.inRange(image_np, lower_bound, upper_bound)
        image_np[mask != 0] = [0, 0, 0]  # Set filtered colors to black (or any other color)
        image = Image.fromarray(image_np)

    # Save the processed image
    processed_image_path = "processed_image.png"
    image.save(processed_image_path)

    outputs = {
        'processed_image': processed_image_path
    }
    
    return outputs

# Sample function call
# inputs = {
#     'image': 'path_to_image.jpg',
#     'crop_box': {'left': 100, 'upper': 100, 'right': 400, 'lower': 400},
#     'color_range': {'lower_bound': [0, 0, 0], 'upper_bound': [50, 50, 50]}
# }
# print(handler(inputs))
