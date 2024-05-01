import boto3
import os

def send_email(sender, to, subject, body):
    # The character encoding for the email.
    CHARSET = "UTF-8"
    print("Sending email to: " + to)

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=os.environ['AWS_REGION'])

    print("Sending email to: " + to)
    #Provide the contents of the email.
    response = client.send_email(
        Destination={
            'ToAddresses': [
                to,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': body.replaceAll("\n", "<br>")
                }
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject,
            },
        },
        Source=sender
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
    response = send_email(sender, to, subject, body)
    return response
