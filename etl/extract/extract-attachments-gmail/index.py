import requests
import base64
import uuid
import os

def correct_base64url_padding(data):
    padding_needed = 4 - (len(data) % 4)
    if padding_needed and padding_needed < 4:
        data += '=' * padding_needed
    return data

def download_attachment(message_id, attachment_id, headers):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json().get("data")
    corrected_data = correct_base64url_padding(data)
    new_file = f"/tmp/{uuid.uuid4()}.pdf"
    with open(new_file, "wb") as f:
        f.write(base64.urlsafe_b64decode(corrected_data))
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
            parts = msg_resp.json().get("payload", {}).get("parts", [])
            for part in parts:
                body = part.get("body", {})
                att_id = body.get("attachmentId")
                if att_id:
                    new_files.append(download_attachment(message_id, att_id, headers))
    except Exception as e:
        print(f"Error downloading attachment(s): {e}")

    return {"new_files": new_files}

# Sample usage (commented out)
# handler({"message_id": "abc123"})
# handler({"message_id": "abc123", "attachment_id": "xyz456"})
