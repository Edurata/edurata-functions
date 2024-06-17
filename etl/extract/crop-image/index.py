from PIL import Image
import os

def handler(inputs):
    image_path = inputs['image_path']
    coords = inputs['coordinates']
    
    left = coords['left']
    top = coords['top']
    right = coords['right']
    bottom = coords['bottom']
    
    with Image.open(image_path) as img:
        cropped_img = img.crop((left, top, right, bottom))
        cropped_image_path = 'cropped_image.png'
        cropped_img.save(cropped_image_path)
    
    outputs = {
        'cropped_image_path': cropped_image_path
    }
    
    return outputs

# Sample function call
# inputs = {
#     'image_path': 'example.png',
#     'coordinates': {
#         'left': 100,
#         'top': 100,
#         'right': 400,
#         'bottom': 400
#     }
# }
# outputs = handler(inputs)
# print(outputs)
