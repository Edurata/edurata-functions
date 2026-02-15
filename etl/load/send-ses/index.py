import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def handler(inputs):
    sender = inputs['sender']
    recipient = inputs['to']
    subject = inputs['subject']
    html_body = inputs['html_body'].replace('\\n', '<br>').replace('\n', '<br>')
    attachments = inputs.get('attachments', [])

    if not sender or not recipient or not subject:
        return {'status': False, 'error': 'sender, to, and subject are required'}

    aws_region = os.getenv('AWS_REGION', 'eu-central-1')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    client = boto3.client(
        'ses',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')
    textpart = "This email requires an HTML-compatible email client."
    htmlpart = html_body

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEBase('text', 'plain')
    part1.set_payload(textpart)
    part2 = MIMEBase('text', 'html')
    part2.set_payload(htmlpart)

    # Attach parts into message container.
    msg_body.attach(part1)
    msg_body.attach(part2)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Attach files
    for file_path in attachments:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as attachment:
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(file_path)}',
        )
        msg.attach(part)

    try:
        # Provide the contents of the email.
        response = client.send_raw_email(
            Source=sender,
            Destinations=[
                recipient,
            ],
            RawMessage={
                'Data': msg.as_string(),
            },
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'status': False, 'error': e.response['Error']['Message']}
    else:
        return {'status': True}

# Sample function call
# inputs = {
#     'sender': 'sender@example.com',
#     'to': 'recipient@example.com',
#     'subject': 'Test Email',
#     'html_body': '<h1>Test Email</h1><p>This is a test email.</p>',
#     'attachments': ['/path/to/attachment1', '/path/to/attachment2']
# }
# os.environ['AWS_ACCESS_KEY_ID'] = 'your_access_key_id'
# os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_secret_access_key'
# os.environ['AWS_REGION'] = 'eu-central-1'
# print(handler(inputs))
