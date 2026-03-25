import os
import requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime


LOG_PREFIX = "[list-gmail-unanswered]"


def _to_epoch(dt_value):
    if not dt_value:
        return None
    if isinstance(dt_value, (int, float)):
        return float(dt_value)
    s = str(dt_value).strip()
    if not s:
        return None
    if s.isdigit():
        # Gmail internalDate is in milliseconds.
        return int(s) / 1000.0
    try:
        # RFC2822 date header.
        return parsedate_to_datetime(s).timestamp()
    except Exception:
        return None


def _gmail_get(url, token, params=None):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    res = requests.get(url, headers=headers, params=params, timeout=30)
    if res.status_code != 200:
        raise Exception(f"Gmail GET failed: {res.status_code} {res.text}")
    return res.json()


def _list_messages_by_query(token, query, max_pages, page_size):
    out = []
    page_token = None
    pages = 0
    while pages < max_pages:
        pages += 1
        params = {"q": query, "maxResults": page_size}
        if page_token:
            params["pageToken"] = page_token
        data = _gmail_get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            token,
            params=params,
        )
        out.extend(data.get("messages", []) or [])
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return out


def _find_header(msg, name):
    payload = msg.get("payload") or {}
    headers = payload.get("headers") or []
    target = str(name or "").strip().lower()
    for h in headers:
        if (h.get("name") or "").strip().lower() == target:
            return h.get("value")
    return None


def _latest_draft_updated_per_thread(token):
    out = {}
    page_token = None
    while True:
        params = {"maxResults": 500}
        if page_token:
            params["pageToken"] = page_token
        data = _gmail_get(
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
            token,
            params=params,
        )
        drafts = data.get("drafts") or []
        for d in drafts:
            msg = d.get("message") or {}
            thread_id = (msg.get("threadId") or "").strip()
            updated = _to_epoch(msg.get("internalDate"))
            if not thread_id or updated is None:
                continue
            cur = out.get(thread_id)
            if cur is None or updated > cur:
                out[thread_id] = updated
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return out


def handler(inputs):
    token = os.getenv("GMAIL_API_KEY")
    if not token:
        raise Exception("GMAIL_API_KEY not set")

    sender_domain = (inputs.get("senderDomain") or "").strip()
    if not sender_domain:
        raise Exception("senderDomain is required")

    listener_email = (inputs.get("listenerEmail") or "").strip().lower()
    window_hours = int(inputs.get("windowHours") or 72)
    max_unanswered = int(inputs.get("maxUnanswered") or 10)
    max_inbox_pages = int(inputs.get("maxInboxPages") or 3)
    max_sent_pages = int(inputs.get("maxSentPages") or 3)
    page_size = min(max(1, int(inputs.get("pageSize") or 100)), 500)

    since_dt = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    since_ts = int(since_dt.timestamp())

    print(
        f"{LOG_PREFIX} start senderDomain={sender_domain} windowHours={window_hours} "
        f"since={since_dt.isoformat()} maxUnanswered={max_unanswered}"
    )

    inbox_query = f"in:inbox after:{since_ts} from:*@{sender_domain}"
    inbox_hits = _list_messages_by_query(token, inbox_query, max_inbox_pages, page_size)
    print(f"{LOG_PREFIX} inbox hits={len(inbox_hits)}")

    latest_inbound_by_thread = {}
    for hit in inbox_hits:
        msg_id = (hit.get("id") or "").strip()
        if not msg_id:
            continue
        msg = _gmail_get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
            token,
            params={"format": "metadata", "metadataHeaders": ["From", "Date", "Subject"]},
        )
        thread_id = (msg.get("threadId") or "").strip()
        if not thread_id:
            continue
        internal_epoch = _to_epoch(msg.get("internalDate"))
        from_header = (_find_header(msg, "From") or "").lower()
        if f"@{sender_domain.lower()}" not in from_header:
            continue
        cur = latest_inbound_by_thread.get(thread_id)
        if cur is None or (internal_epoch or 0) > (cur.get("epoch") or 0):
            latest_inbound_by_thread[thread_id] = {
                "messageId": msg_id,
                "epoch": internal_epoch or 0,
            }

    thread_ids = list(latest_inbound_by_thread.keys())
    print(f"{LOG_PREFIX} candidate threads={len(thread_ids)}")
    if not thread_ids:
        return {
            "unansweredThreadIds": [],
            "answeredThreadIds": [],
            "countUnanswered": 0,
            "countAnswered": 0,
            "sinceUsed": since_dt.isoformat(),
        }

    sent_query = f"in:sent after:{since_ts}"
    sent_hits = _list_messages_by_query(token, sent_query, max_sent_pages, page_size)
    print(f"{LOG_PREFIX} sent hits={len(sent_hits)}")
    latest_sent_by_thread = {}
    for hit in sent_hits:
        msg_id = (hit.get("id") or "").strip()
        if not msg_id:
            continue
        msg = _gmail_get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
            token,
            params={"format": "metadata", "metadataHeaders": ["From", "Date"]},
        )
        thread_id = (msg.get("threadId") or "").strip()
        if not thread_id or thread_id not in latest_inbound_by_thread:
            continue
        sender_header = (_find_header(msg, "From") or "").lower()
        if listener_email and listener_email not in sender_header:
            continue
        sent_epoch = _to_epoch(msg.get("internalDate")) or 0
        cur = latest_sent_by_thread.get(thread_id)
        if cur is None or sent_epoch > cur:
            latest_sent_by_thread[thread_id] = sent_epoch

    newest_draft_by_thread = _latest_draft_updated_per_thread(token)
    print(f"{LOG_PREFIX} threads with drafts={len(newest_draft_by_thread)}")

    unanswered = []
    answered = []
    for tid in thread_ids:
        inbound_epoch = latest_inbound_by_thread[tid]["epoch"]
        sent_epoch = latest_sent_by_thread.get(tid)
        is_answered = sent_epoch is not None and sent_epoch > inbound_epoch
        if is_answered:
            answered.append(tid)
            continue

        draft_epoch = newest_draft_by_thread.get(tid)
        is_outdated = draft_epoch is not None and draft_epoch < inbound_epoch
        if draft_epoch is None or is_outdated:
            unanswered.append(tid)

    if max_unanswered > 0:
        unanswered = unanswered[:max_unanswered]

    print(
        f"{LOG_PREFIX} classification answered={len(answered)} unanswered={len(unanswered)}"
    )
    return {
        "unansweredThreadIds": unanswered,
        "answeredThreadIds": answered,
        "countUnanswered": len(unanswered),
        "countAnswered": len(answered),
        "sinceUsed": since_dt.isoformat(),
    }
