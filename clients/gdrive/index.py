import os
import uuid
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Initialize Google Drive API
def init_drive_api():
    oauth_token = os.getenv('OAUTH_TOKEN')
    if not oauth_token:
        raise ValueError("OAUTH_TOKEN environment variable is not set")
    
    credentials = Credentials(token=oauth_token)
    service = build('drive', 'v3', credentials=credentials)
    return service

# Download a file from Google Drive
def download_file(service, file_id):
    file_path = f"/tmp/{uuid.uuid4()}"
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return file_path

# Upload a file to Google Drive
def upload_file(service, file_path, upload_file_name):
    file_metadata = {'name': upload_file_name}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def handler(inputs):
    action = inputs['action']
    file_path = inputs.get('file_path')
    drive_file_id = inputs.get('drive_file_id')
    upload_file_name = inputs.get('upload_file_name')

    service = init_drive_api()

    if action == 'download':
        if not drive_file_id:
            return {'message': 'drive_file_id is required for downloading'}
        download_file_path = download_file(service, drive_file_id)
        return {'download_file_path': download_file_path}
    elif action == 'upload':
        if not file_path or not upload_file_name:
            return {'message': 'file_path and upload_file_name are required for uploading'}
        uploaded_file_id = upload_file(service, file_path, upload_file_name)
        return {'drive_file_id': uploaded_file_id}
    else:
        return {'message': 'Invalid action. Please specify "upload" or "download".'}

# Sample function call
# os.environ['OAUTH_TOKEN'] = 'your_oauth_token'
# inputs = {
#     'action': 'download',
#     'drive_file_id': 'your_drive_file_id'
# }
# print(handler(inputs))

# inputs = {
#     'action': 'upload',
#     'file_path': '/path/to/local/file',
#     'upload_file_name': 'uploaded_file_name'
# }
# print(handler(inputs))
