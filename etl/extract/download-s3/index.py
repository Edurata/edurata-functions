import os
import json
import boto3
import tempfile

def handler(inputs):
    # Extracting environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'eu-central-1')

    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )

    bucket_name = inputs['bucket_name']
    file_requests = inputs['files']

    output_files = []

    for file_request in file_requests:
        key = file_request['key']
        as_raw = file_request.get('as_raw', False)
        as_json = file_request.get('as_json', False)
        path = file_request.get('path', tempfile.mktemp())

        # Download the file
        s3_client.download_file(bucket_name, key, path)

        data = ''
        if as_raw or as_json:
            with open(path, 'r') as file:
                if as_json:
                    data = json.loads(file.read())
                else:
                    data = file.read()

        output_files.append({
            'path': path,
            'data': data
        })

    return {'files': output_files}

# For demonstration purposes, this call is a placeholder
# actual_inputs = {"bucket_name": "example_bucket", "files": [{"key": "file1.txt"}]}
# print(handler(actual_inputs))
