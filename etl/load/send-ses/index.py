import boto3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate

def send_email(sender, to, subject, html_body, attachments):
    # The character encoding for the email.
    CHARSET = "UTF-8"
    print("Sending email to: " + to)

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=os.environ['AWS_REGION'])

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the HTML content.
    htmlpart = MIMEText(html_body, 'html', CHARSET)

    # Attach the HTML part to the child container.
    msg_body.attach(htmlpart)

    # Attach the multipart/alternative child container to the multipart/mixed parent container.
    msg.attach(msg_body)

    # Attach files
    for attachment in attachments:
        # Read the file content and guess its MIME type
        with open(attachment, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header(
                'Content-Disposition',
                'attachment',
                filename=os.path.basename(attachment)
            )
            msg.attach(part)

    # Send the email
    response = client.send_raw_email(
        Source=sender,
        Destinations=[to],
        RawMessage={
            'Data': msg.as_string(),
        }
    )

    print("Email sent! Message ID:", response['MessageId'])
    return response

def handler(inputs):
    if 'sender' not in inputs or 'to' not in inputs:
        raise Exception('required inputs not present')
    sender = inputs.get("sender")
    to = inputs.get("to")
    subject = inputs.get("subject", "")
    html_body = inputs.get("html_body", "")
    attachments = inputs.get("attachments", [])

    response = send_email(sender, to, subject, html_body, attachments)
    return {'status': True if response else False}

# Sample function call (commented out)
# inputs = {
#     "sender": "example@example.com",
#     "to": "recipient@example.com",
#     "subject": "Test Email",
#     "html_body": "<p>This is a test email.</p>",
#     "attachments": ["/path/to/attachment1.txt", "/path/to/attachment2.pdf"]
# }
# print(handler(inputs))
