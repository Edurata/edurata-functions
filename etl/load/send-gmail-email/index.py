import base64
import os
import requests
import mimetypes
from urllib.parse import quote
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.encoders import encode_base64

def handler(inputs):
    gmail_api_key = os.getenv("GMAIL_API_KEY")
    if not gmail_api_key:
        raise Exception("GMAIL_API_KEY not set")

    user_email = inputs.get("userEmail", "me")
    recipient = inputs["recipient"]
    subject = inputs["subject"]
    body = inputs["body"]
    attachments = inputs.get("attachments", [])
    thread_id = inputs.get("threadId")
    create_draft = inputs.get("createDraft", False)

    print(f"[INFO]: Creating email from '{user_email}' to '{recipient}' with subject '{subject}'")

    msg = EmailMessage()
    msg["From"] = user_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body, subtype="html")

    # Convert to mixed type only once if we have attachments
    if attachments:
        msg.make_mixed()

    for attachment_path in attachments:
        attachment_name = os.path.basename(attachment_path)
        print(f"[INFO]: Attaching file: {attachment_name} from {attachment_path}")

        if not os.path.exists(attachment_path):
            print(f"[ERROR]: Attachment file not found: {attachment_path}")
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")

        mime_type, _ = mimetypes.guess_type(attachment_path)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)

        with open(attachment_path, "rb") as f:
            file_data = f.read()

        encoded_name = quote(attachment_name)
        content_disposition = f'attachment; filename="{attachment_name}"; filename*=UTF-8\'\'{encoded_name}'

        part = MIMEBase(maintype, subtype)
        part.set_payload(file_data)
        encode_base64(part)
        part.add_header("Content-Disposition", content_disposition)

        msg.attach(part)

    print("[INFO]: Email composed, encoding to base64...")
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    headers = {
        "Authorization": f"Bearer {gmail_api_key}",
        "Content-Type": "application/json",
    }

    if create_draft:
        data = {"message": {"raw": raw_message}}
        if thread_id:
            data["message"]["threadId"] = thread_id
        url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
        print("[INFO]: Creating draft...")
    else:
        data = {"raw": raw_message}
        if thread_id:
            data["threadId"] = thread_id
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        print("[INFO]: Sending message...")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("[INFO]: Email sent successfully.")
        response_data = response.json()
        message_id = response_data.get("id")
        thread_id = response_data.get("threadId")
        
        print(f"[DEBUG]: Message ID: {message_id}")
        print(f"[DEBUG]: Thread ID: {thread_id}")
        
        if create_draft:
            draft_id = response_data.get("id")
            message_link = f"https://mail.google.com/mail/u/0/#drafts?compose={draft_id}"
        else:
            # Fetch the message metadata to get the proper Message-ID for the URL
            metadata_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=metadata&metadataHeaders=Message-ID"
            metadata_response = requests.get(metadata_url, headers=headers)
            
            if metadata_response.status_code == 200:
                metadata_data = metadata_response.json()
                payload = metadata_data.get("payload", {})
                headers = payload.get("headers", [])
                
                # Find the Message-ID header
                message_id_header = None
                for header in headers:
                    if header.get("name") == "Message-ID":
                        message_id_header = header.get("value")
                        break
                
                print(f"[DEBUG]: Message-ID header: {message_id_header}")
                
                if message_id_header:
                    # Extract the ID from the Message-ID header (remove < > and domain part)
                    # Message-ID format: <unique-id@example.com>
                    clean_message_id = message_id_header.strip("<>").split("@")[0]
                    message_link = f"https://mail.google.com/mail/u/0/#sent/{clean_message_id}"
                else:
                    # Fallback to using the Gmail message ID
                    message_link = f"https://mail.google.com/mail/u/0/#sent/{message_id}"
            else:
                print(f"[WARNING]: Failed to fetch message metadata: {metadata_response.status_code}")
                # Fallback to using the Gmail message ID
                message_link = f"https://mail.google.com/mail/u/0/#sent/{message_id}"

        return {
            "messageId": message_id,
            "threadId": thread_id,
            "messageLink": message_link
        }
    else:
        print(f"[ERROR]: Failed to send email: {response.status_code}, {response.text}")
        raise Exception(f"Failed to process email: {response.status_code}, {response.text}")

# Example usage:
# inputs = {
#     "userEmail": "your-email@gmail.com",
#     "recipient": "recipient-email@gmail.com",
#     "subject": "Your Subject Here",
#     "body": "The body of your email goes here.",
#     "attachments": ["/path/to/file1.pdf", "/path/to/file2.pdf"],
#     "threadId": "12345abc",  # Optional
#     "createDraft": True  # Set to True to save as a draft instead of sending
# }
# outputs = handler(inputs)
# print(outputs)
