import os
import re
import base64
import requests


def _decode_base64url(data):
    if not data:
        return ""
    s = str(data).strip()
    padding = (4 - len(s) % 4) % 4
    s += "=" * padding
    try:
        return base64.urlsafe_b64decode(s.encode("utf-8")).decode("utf-8", errors="replace")
    except Exception:
        return ""


def _html_to_text(html):
    if not html:
        return ""
    text = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.IGNORECASE)
    text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|br|tr|li|h[1-6])>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _header(msg, name):
    payload = msg.get("payload") or {}
    headers = payload.get("headers") or []
    needle = str(name or "").strip().lower()
    for h in headers:
        if (h.get("name") or "").strip().lower() == needle:
            return h.get("value")
    return None


def _first_body_content(payload):
    if not payload:
        return ""
    mime = (payload.get("mimeType") or "").lower()
    body = payload.get("body") or {}
    data = body.get("data")
    if mime == "text/plain" and data:
        return _decode_base64url(data)
    if mime == "text/html" and data:
        return _html_to_text(_decode_base64url(data))

    for part in payload.get("parts") or []:
        found = _first_body_content(part)
        if found:
            return found

    if data:
        raw = _decode_base64url(data)
        return _html_to_text(raw) if "<" in raw and ">" in raw else raw.strip()
    return ""


def handler(inputs):
    token = os.getenv("GMAIL_API_KEY")
    if not token:
        raise Exception("GMAIL_API_KEY not set")

    thread_id = (inputs.get("threadId") or "").strip()
    if not thread_id:
        raise Exception("threadId is required")

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    res = requests.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{thread_id}",
        headers=headers,
        params={"format": "full"},
        timeout=30,
    )
    if res.status_code != 200:
        raise Exception(f"Failed to fetch thread: {res.status_code}, {res.text}")

    data = res.json()
    messages = data.get("messages") or []
    out = []
    for msg in messages:
        payload = msg.get("payload") or {}
        from_header = _header(msg, "From") or ""
        out.append(
            {
                "id": msg.get("id"),
                "subject": _header(msg, "Subject"),
                "from": {"address": from_header, "name": None},
                "receivedDateTime": msg.get("internalDate"),
                "sentDateTime": msg.get("internalDate"),
                "threadId": msg.get("threadId"),
                "body": {
                    "contentType": payload.get("mimeType") or "text/plain",
                    "content": _first_body_content(payload),
                },
            }
        )

    out.sort(key=lambda m: int(m.get("receivedDateTime") or 0))
    return {"threadId": thread_id, "count": len(out), "messages": out}
