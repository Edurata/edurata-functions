import boto3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate

def send_email(sender, to, subject, body, attachments):
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

    # Encode the HTML and plain text content.
    textpart = MIMEText(body.replace("\\n", "\n"), 'plain', CHARSET)
    htmlpart = MIMEText(body.replace("\n", "<br>"), 'html', CHARSET)

    # Attach the text and HTML parts to the child container.
    msg_body.attach(textpart)
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

    print("Email sent! Message ID:"),
    print(response['MessageId'])
    return response

def handler(inputs):
    if 'sender' not in inputs or 'to' not in inputs:
        raise Exception('required inputs not present')
    sender = inputs.get("sender")
    to = inputs.get("to")
    subject = inputs.get("subject","")
    body = inputs.get("body", "")
    attachments = inputs.get("attachments", [])

    response = send_email(sender, to, subject, body, attachments)
    return {'status': True if response else False}

# Sample function call (commented out)
# inputs = {
#     "sender": "example@example.com",
#     "to": "recipient@example.com",
#     "subject": "Test Email",
#     "body": "This is a test email.",
#     "attachments": ["/path/to/attachment1.txt", "/path/to/attachment2.pdf"]
# }
# print(handler(inputs))
