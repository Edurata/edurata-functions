import requests
import base64
import uuid
import os
import mimetypes

def correct_base64url_padding(data):
    padding_needed = 4 - (len(data) % 4)
    if padding_needed and padding_needed < 4:
        data += '=' * padding_needed
    return data

def get_attachment_info(message_id, attachment_id, headers):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def download_attachment(message_id, attachment_id, headers, filename=None):
    # Get attachment metadata
    attachment_info = get_attachment_info(message_id, attachment_id, headers)
    data = attachment_info.get("data")
    
    if not data:
        raise ValueError("No data found in attachment")
        
    corrected_data = correct_base64url_padding(data)
    decoded_data = base64.urlsafe_b64decode(corrected_data)
    
    # If filename not provided, generate one with appropriate extension
    if not filename:
        # Try to determine file extension from content type
        content_type = attachment_info.get("mimeType", "application/octet-stream")
        extension = mimetypes.guess_extension(content_type) or ".bin"
        filename = f"{uuid.uuid4()}{extension}"
    
    new_file = f"/tmp/{filename}"
    with open(new_file, "wb") as f:
        f.write(decoded_data)
    return new_file

def handler(inputs):
    GMAIL_API_KEY = os.getenv("GMAIL_API_KEY")
    headers = {
        "Authorization": f"Bearer {GMAIL_API_KEY}"
    }

    message_id = inputs["message_id"]
    attachment_id = inputs.get("attachment_id")

    new_files = []

    try:
        if attachment_id:
            # Single attachment
            new_files.append(download_attachment(message_id, attachment_id, headers))
        else:
            # Fetch all attachments from the message
            msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
            msg_resp = requests.get(msg_url, headers=headers)
            msg_resp.raise_for_status()
            
            # Get message details to find attachment filenames
            message_data = msg_resp.json()
            parts = message_data.get("payload", {}).get("parts", [])
            
            for part in parts:
                body = part.get("body", {})
                att_id = body.get("attachmentId")
                if att_id:
                    # Get filename from headers if available
                    filename = None
                    headers_list = part.get("headers", [])
                    for header in headers_list:
                        if header.get("name", "").lower() == "content-disposition":
                            # Parse filename from Content-Disposition header
                            content_disp = header.get("value", "")
                            if "filename=" in content_disp:
                                filename = content_disp.split("filename=")[1].strip('"')
                                break
                    
                    new_files.append(download_attachment(message_id, att_id, headers, filename))
    except Exception as e:
        print(f"Error downloading attachment(s): {e}")

    return {"new_files": new_files}

# Sample usage (commented out)
# handler({"message_id": "abc123"})
# handler({"message_id": "abc123", "attachment_id": "xyz456"})
