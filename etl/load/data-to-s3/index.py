import boto3
from botocore.exceptions import NoCredentialsError

def download_file_from_s3(bucket_name, s3_file_key, local_file_path):
    # Create an S3 client
    s3 = boto3.client('s3')
    local_file_path = local_file_path if local_file_path else "tmp/" + s3_file_key
    try:
        # Download the file
        s3.download_file(Bucket=bucket_name, Key=s3_file_key, Filename=local_file_path)
        print(f"File downloaded successfully: {local_file_path}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"An error occurred: {e}")

def handler(inputs):
    # Example usage
    bucket_name = inputs.bucket_name
    s3_file_key = inputs.s3_file_key
    local_file_path = inputs.local_file_path if inputs.local_file_path else "tmp/" + s3_file_key
    is_json = inputs.is_json

    download_file_from_s3(bucket_name, s3_file_key, local_file_path)
    content = open(local_file_path, 'r').read()

    return {
        file: local_file_path
        content: json.loads(content) if is_json else content
    }
