import boto3
import os

def handler(inputs):
    # Extract environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    
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

    # Analyze the image
    response_labels = rekognition.detect_labels(Image={'Bytes': image_bytes})
    response_faces = rekognition.detect_faces(Image={'Bytes': image_bytes}, Attributes=['ALL'])
    response_text = rekognition.detect_text(Image={'Bytes': image_bytes})
    response_celebrities = rekognition.recognize_celebrities(Image={'Bytes': image_bytes})

    # Prepare the outputs
    outputs = {
        'labels': response_labels.get('Labels', []),
        'faces': response_faces.get('FaceDetails', []),
        'text': response_text.get('TextDetections', []),
        'celebrities': response_celebrities.get('CelebrityFaces', [])
    }

    return outputs

# Sample function call
# inputs = {
#     'image_file': 'path/to/your/image.jpg'
# }
# print(handler(inputs))
