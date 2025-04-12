import base64
import os
import requests
from email.message import EmailMessage
from urllib.parse import quote
import mimetypes

def handler(inputs):
    """
    Sends an email via the Gmail API with customizable subject, body, and attachments.
    Can send the email as part of an existing thread if threadId is provided.
    Can create a draft instead of sending the email if createDraft is set to True.

    Args:
        inputs (dict): A dictionary containing:
            - userEmail (str): The sender's email address.
            - recipient (str): The recipient's email address.
            - subject (str): The subject of the email.
            - body (str): The body text of the email (HTML supported).
            - attachments (list): List of file paths to attach (optional).
            - threadId (str): Optional. The thread ID to include the email in an existing thread.
            - createDraft (bool): Optional. If True, the email will be saved as a draft instead of being sent.

    Returns:
        dict: A dictionary containing:
            - messageId (str): The ID of the sent email or draft.
            - threadId (str): The thread ID of the email conversation.
    """

    # Check if the Gmail API key is defined
    gmail_api_key = os.getenv("GMAIL_API_KEY")
    if not gmail_api_key:
        raise Exception("The Gmail API key is not defined. Please set the GMAIL_API_KEY environment variable.")

    user_email = inputs.get("userEmail", "me")
    recipient = inputs["recipient"]
    subject = inputs["subject"]
    body = inputs["body"]
    attachments = inputs.get("attachments", [])
    thread_id = inputs.get("threadId")
    create_draft = inputs.get("createDraft", False)

    # Create the EmailMessage object
    msg = EmailMessage()
    msg["From"] = user_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body, subtype="html")

    # Attach files
    for attachment_path in attachments:
        attachment_name = os.path.basename(attachment_path)
        print(f"Attaching file: {attachment_name} from {attachment_path}")

        # Guess the MIME type or fallback to octet-stream
        mime_type, _ = mimetypes.guess_type(attachment_path)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)

        with open(attachment_path, "rb") as attachment_file:
            file_data = attachment_file.read()

        # Encode the filename for Content-Disposition
        encoded_name = quote(attachment_name)
        content_disposition = f'attachment; filename="{attachment_name}"; filename*=UTF-8\'\'{encoded_name}'

        # Attach with custom header
        msg.add_attachment(
            file_data,
            maintype=maintype,
            subtype=subtype,
            headers=[f"Content-Disposition: {content_disposition}"]
        )
    # print msg
    print(msg)
    # Encode the message in base64
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
    else:
        data = {"raw": raw_message}
        if thread_id:
            data["threadId"] = thread_id
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

    # Send request to Gmail API
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        return {
            "messageId": response_data.get("id"),
            "threadId": response_data.get("threadId")
        }
    else:
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
