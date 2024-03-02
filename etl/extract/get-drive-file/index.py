from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import os

def handler(inputs):
    service_account_file = inputs["serviceAccountFile"]
    fileId = inputs["fileId"]

    # Load the service account credentials from the JSON key file
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # Create a service object for interacting with the Google Drive API
    drive_service = build('drive', 'v3', credentials=credentials)

    # Prepare the file download
    request = drive_service.files().get_media(fileId=fileId)
    fileName = drive_service.files().get(fileId=fileId).execute().get('name')
    filePath = os.path.join(os.getcwd(), fileName)  # Use the current working directory

    # Download the file
    with open(filePath, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

    downloadPath = filePath

    return {
        "file": downloadPath
    }

# Sample function call (commented out)
print(handler({
    "serviceAccountFile": ".token.json",
    "fileId": "1ScXVYF78vu3gcrVDk462NG7Cut05eESN"
}))
