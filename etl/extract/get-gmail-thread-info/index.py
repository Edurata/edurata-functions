import os
import re
import requests

def extract_message_id(input_str):
    match = re.search(r'(?:#(?:inbox|sent|all|drafts|search)/)?([a-fA-F0-9]{16,})', input_str)
    return match.group(1) if match else input_str

def handler(inputs):
    gmail_api_key = os.getenv("GMAIL_API_KEY")
    if not gmail_api_key:
        raise Exception("GMAIL_API_KEY not set in environment")

    raw_input = inputs["messageInput"]
    message_id = extract_message_id(raw_input)

    headers = {
        "Authorization": f"Bearer {gmail_api_key}",
        "Accept": "application/json",
    }

    # Get message info
    msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full"
    msg_response = requests.get(msg_url, headers=headers)
    if msg_response.status_code != 200:
        raise Exception(f"Failed to fetch message: {msg_response.status_code}, {msg_response.text}")

    msg_data = msg_response.json()
    snippet = msg_data.get("snippet", "")
    thread_id = msg_data.get("threadId")

    message_link = f"https://mail.google.com/mail/u/0/#all/{message_id}"

    # Default return structure
    result = {
        "messageId": message_id,
        "messageLink": message_link,
        "messageCount": 1,
        "messageSnippets": [{"messageIndex": 0, "messageId": message_id, "snippet": snippet}]
    }

    # Get thread info
    if thread_id:
        thread_url = f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{thread_id}"
        thread_response = requests.get(thread_url, headers=headers)
        if thread_response.status_code == 200:
            thread_data = thread_response.json()
            messages = thread_data.get("messages", [])
            result["messageCount"] = len(messages)
            
            # Collect snippets for each message
            result["messageSnippets"] = [
                {
                    "messageIndex": i,
                    "messageId": msg.get("id"),
                    "snippet": msg.get("snippet", "")
                }
                for i, msg in enumerate(messages) if msg.get("id")
            ]

    return result

# Example usage:
# inputs = {"messageInput": "https://mail.google.com/mail/u/0/#inbox/197bbafa404afec3"}
# result = handler(inputs)
# print(f"Result: {result}")
