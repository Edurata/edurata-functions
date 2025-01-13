import base64
import os
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def handler(inputs):
    """
    Sends an email via the Gmail API with customizable subject, body, and attachments.
    Can send the email as part of an existing thread if threadId is provided.

    Args:
        inputs (dict): A dictionary containing:
            - userEmail (str): The sender's email address.
            - recipient (str): The recipient's email address.
            - subject (str): The subject of the email.
            - body (str): The body text of the email.
            - attachments (list): List of file paths to attach (optional).
            - threadId (str): Optional. The thread ID to include the email in an existing thread.

    Returns:
        dict: A dictionary containing:
            - messageId (str): The ID of the sent email.
            - threadId (str): The thread ID of the email conversation.
    """
    # Check if the Gmail API key is defined
    gmail_api_key = os.getenv("GMAIL_API_KEY")
    if not gmail_api_key:
        raise Exception("The Gmail API key is not defined. Please set the GMAIL_API_KEY environment variable.")

    user_email = inputs['userEmail']
    recipient = inputs['recipient']
    subject = inputs['subject']
    body = inputs['body']
    attachments = inputs.get('attachments', [])
    thread_id = inputs.get('threadId', None)

    # Create email
    msg = MIMEMultipart()
    msg['From'] = user_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach files if provided
    for attachment_path in attachments:
        attachment_name = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_name}'
            )
            msg.attach(part)

    # Encode email as base64
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    # Send email using Gmail API
    headers = {
        'Authorization': f'Bearer {gmail_api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'raw': raw_message,
    }
    if thread_id:
        data['threadId'] = thread_id

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        return {
            "messageId": response_data.get("id"),
            "threadId": response_data.get("threadId")
        }
    else:
        raise Exception(f"Failed to send email: {response.status_code}, {response.text}")

# Example usage
# inputs = {
#     "userEmail": "your-email@gmail.com",
#     "recipient": "recipient-email@gmail.com",
#     "subject": "Your Subject Here",
#     "body": "The body of your email goes here.",
#     "attachments": ["/path/to/file1.pdf", "/path/to/file2.pdf"],
#     "threadId": "12345abc"  # Optional
# }
# outputs = handler(inputs)
# print(outputs)
