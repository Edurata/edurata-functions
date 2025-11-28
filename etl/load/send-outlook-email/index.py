import os
import base64
import mimetypes
import requests
from typing import List, Dict, Any


def _build_attachments(attachment_paths: List[str]) -> List[Dict[str, Any]]:
    attachments: List[Dict[str, Any]] = []
    for path in attachment_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Attachment not found: {path}")
        filename = os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(path)
        content_type = mime_type or "application/octet-stream"
        with open(path, "rb") as f:
            content_bytes = base64.b64encode(f.read()).decode("utf-8")
        attachments.append({
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": filename,
            "contentType": content_type,
            "contentBytes": content_bytes,
        })
    return attachments


def handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    token = os.getenv("OUTLOOK_API_KEY")
    if not token:
        raise Exception("OUTLOOK_API_KEY not set")

    sender = inputs.get("userEmail")
    recipients = inputs["recipients"]
    cc = inputs.get("cc", [])
    bcc = inputs.get("bcc", [])
    subject = inputs["subject"]
    body_html = inputs["body"]
    attachments_paths = inputs.get("attachments", [])
    create_draft = bool(inputs.get("createDraft", False))

    print(f"[INFO]: Preparing Outlook email to {recipients} (cc: {cc}, bcc: {bcc}) with subject '{subject}'")

    message: Dict[str, Any] = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": body_html,
        },
        "toRecipients": [
            {"emailAddress": {"address": addr}} for addr in recipients
        ],
    }

    if cc:
        message["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]
    if bcc:
        message["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]

    if sender:
        message["from"] = {"emailAddress": {"address": sender}}

    if attachments_paths:
        message["attachments"] = _build_attachments(attachments_paths)

    base_url = "https://graph.microsoft.com/v1.0"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Create the message first to obtain stable IDs and webLink
    create_resp = requests.post(f"{base_url}/me/messages", headers=headers, json=message)
    if create_resp.status_code not in (200, 201):
        raise Exception(f"Failed to create Outlook message: {create_resp.status_code}, {create_resp.text}")

    created = create_resp.json()
    message_id = created.get("id")

    # Fetch webLink and conversationId
    get_resp = requests.get(
        f"{base_url}/me/messages/{message_id}?$select=webLink,conversationId,internetMessageId",
        headers=headers,
    )
    if get_resp.status_code != 200:
        raise Exception(f"Failed to fetch message metadata: {get_resp.status_code}, {get_resp.text}")

    meta = get_resp.json()
    web_link = meta.get("webLink")
    conversation_id = meta.get("conversationId")

    if create_draft:
        print("[INFO]: Draft created successfully.")
        return {
            "messageId": message_id,
            "threadId": conversation_id,
            "messageLink": web_link or "https://outlook.office.com/mail/",
        }

    # Send the created message
    send_resp = requests.post(f"{base_url}/me/messages/{message_id}/send", headers=headers)
    if send_resp.status_code not in (200, 202):
        raise Exception(f"Failed to send Outlook message: {send_resp.status_code}, {send_resp.text}")

    print("[INFO]: Email sent successfully via Outlook.")

    return {
        "messageId": message_id,
        "threadId": conversation_id,
        "messageLink": web_link or "https://outlook.office.com/mail/",
    }
