import boto3
import os

def handler(inputs):
    # Extract environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    types = inputs['types']
    
    # Initialize the Rekognition client
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )

    # Read the image file
    with open(inputs['image_file'], 'rb') as image:
        image_bytes = image.read()
    
    response_labels = []
    response_faces = []
    response_text = []
    response_celebrities = []
    
    # Check if 'labels' is in types
    if "labels" in types:
        response_labels = rekognition.detect_labels(Image={'Bytes': image_bytes})
    if "faces" in types:
        response_faces = rekognition.detect_faces(Image={'Bytes': image_bytes}, Attributes=['ALL'])
    if "text" in types:
        response_text = rekognition.detect_text(Image={'Bytes': image_bytes})
    if "celebrities" in types:
        response_celebrities = rekognition.recognize_celebrities(Image={'Bytes': image_bytes})
    
    return {
        "labels": response_labels["Labels"] if "Labels" in response_labels else [],
        "faces": response_faces["FaceDetails"] if "FaceDetails" in response_faces else [],
        "text": response_text["TextDetections"] if "TextDetections" in response_text else [],
        "celebrities": response_celebrities["CelebrityFaces"] if "CelebrityFaces" in response_celebrities else []
    }

# Sample function call
# inputs = {
#     'image_file': 'path/to/your/image.jpg'
# }
# print(handler(inputs))
