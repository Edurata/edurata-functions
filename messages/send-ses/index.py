import boto3

def send_email(sender, to, subject, body, region_name="eu-west-1"):
    # The character encoding for the email.
    CHARSET = "UTF-8"
    print("Sending email to: " + to)

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=region_name)

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
                'Text': {
                    'Charset': CHARSET,
                    'Data': body,
                },
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
    return True

def handler(inputs):
    if 'sender' not in inputs or 'to' not in inputs:
        raise Exception('required inputs not present')
    sender = inputs.get("sender")
    to = inputs.get("to")
    subject = inputs.get("subject","")
    body = inputs.get("body", "")
    send_email(sender, to, subject, body)
