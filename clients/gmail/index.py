import os
import base64
import json
import requests

def handler(inputs):
    operation = inputs.get('operation')
    user_id = inputs.get('user_id')
    oauth_token = inputs.get('oauth_token')
    query = inputs.get('query')
    email = inputs.get('email')

    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    if operation == 'read':
        if not query:
            raise ValueError("Query is required for read operation")

        url = f'https://www.googleapis.com/gmail/v1/users/{user_id}/messages?q={query}'
        response = requests.get(url, headers=headers)

    elif operation == 'send':
        if not email:
            raise ValueError("Email content is required for send operation")

        url = f'https://www.googleapis.com/gmail/v1/users/{user_id}/messages/send'
        message = {
            'raw': base64.urlsafe_b64encode(f"To: {email['to']}\r\nSubject: {email['subject']}\r\n\r\n{email['body']}".encode('utf-8')).decode('utf-8')
        }
        response = requests.post(url, headers=headers, json=message)

    else:
        raise ValueError("Invalid operation. Use 'read' or 'send'.")

    if response.status_code in (200, 201):
        return {'response': response.json()}
    else:
        response.raise_for_status()

# Example function call
# inputs = {
#     'operation': 'send',
#     'user_id': 'me',
#     'oauth_token': 'your_oauth_token',
#     'email': {
#         'to': 'recipient@example.com',
#         'subject': 'Test Email',
#         'body': 'This is a test email.'
#     }
# }
# print(handler(inputs))
