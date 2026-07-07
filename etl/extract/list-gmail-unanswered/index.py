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


def _normalize_domain_list(value):
    if value is None:
        return []
    raw = value if isinstance(value, list) else [value]
    return [str(item or "").strip() for item in raw if str(item or "").strip()]


def _resolve_sender_domains(inputs):
    include_domains = _normalize_domain_list(inputs.get("senderDomains"))
    exclude_domains = _normalize_domain_list(inputs.get("excludeDomains"))
    return include_domains, exclude_domains


GMAIL_WELL_KNOWN_FOLDERS = {
    "inbox": "in:inbox",
    "spam": "in:spam",
    "junk": "in:spam",
    "trash": "in:trash",
    "drafts": "in:drafts",
    "sent": "in:sent",
    "important": "is:important",
    "starred": "is:starred",
    "all": "in:anywhere",
}


def _gmail_labels_by_name(token):
    data = _gmail_get("https://gmail.googleapis.com/gmail/v1/users/me/labels", token)
    out = {}
    for label in data.get("labels", []) or []:
        name = (label.get("name") or "").strip()
        if name:
            out[name.lower()] = name
    return out


def _resolve_gmail_folder_clause(token, folder_name, labels_by_name):
    raw = str(folder_name or "").strip()
    if not raw:
        raw = "inbox"
    well_known = GMAIL_WELL_KNOWN_FOLDERS.get(raw.lower())
    if well_known:
        return well_known
    exact = labels_by_name.get(raw.lower())
    if not exact:
        raise Exception(
            f"mailFolderNames: no Gmail system folder or label matching '{raw}'"
        )
    if " " in exact or '"' in exact:
        escaped = exact.replace('"', '\\"')
        return f'label:"{escaped}"'
    return f"label:{exact}"


def _resolve_gmail_folder_clauses(token, mail_folder_names):
    names = _normalize_domain_list(mail_folder_names)
    folder_names = names or ["inbox"]
    labels_by_name = None
    clauses = []
    for name in folder_names:
        if labels_by_name is None and name.lower() not in GMAIL_WELL_KNOWN_FOLDERS:
            labels_by_name = _gmail_labels_by_name(token)
        clause = _resolve_gmail_folder_clause(token, name, labels_by_name or {})
        if clause not in clauses:
            clauses.append(clause)
    if len(clauses) == 1:
        return clauses[0]
    return "(" + " OR ".join(clauses) + ")"


def _address_matches_include_domains(from_header, include_domains):
    if not include_domains:
        return True
    lowered = (from_header or "").lower()
    return any(f"@{domain.lower()}" in lowered for domain in include_domains)


def _address_matches_exclude_domains(from_header, exclude_domains):
    lowered = (from_header or "").lower()
    return any(f"@{domain.lower()}" in lowered for domain in exclude_domains)


def _resolve_window_hours(inputs):
    raw = inputs.get("windowHours")
    if raw is None or raw == "":
        return 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def _build_inbound_query(since_ts, include_domains, exclude_domains, folder_clause):
    parts = []
    if since_ts is not None:
        parts.append(f"after:{since_ts}")
    parts.append(folder_clause)
    if include_domains:
        include_clause = " OR ".join(f"from:*@{domain}" for domain in include_domains)
        if len(include_domains) > 1:
            include_clause = f"({include_clause})"
        parts.append(include_clause)
    exclude_clause = " ".join(f"-from:*@{domain}" for domain in exclude_domains)
    if exclude_clause:
        parts.append(exclude_clause)
    return " ".join(parts)


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

    include_domains, exclude_domains = _resolve_sender_domains(inputs)
    mail_folder_names = inputs.get("mailFolderNames")

    listener_email = (inputs.get("listenerEmail") or "").strip().lower()
    window_hours = _resolve_window_hours(inputs)
    max_unanswered = int(inputs.get("maxUnanswered") or 10)
    max_inbox_pages = int(inputs.get("maxInboxPages") or 3)
    max_sent_pages = int(inputs.get("maxSentPages") or 3)
    page_size = min(max(1, int(inputs.get("pageSize") or 100)), 500)

    since_dt = None
    since_ts = None
    if window_hours > 0:
        since_dt = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        since_ts = int(since_dt.timestamp())

    folder_clause = _resolve_gmail_folder_clauses(token, mail_folder_names)

    print(
        f"{LOG_PREFIX} start senderDomains={','.join(include_domains) or '(all)'} "
        f"excludeDomains={','.join(exclude_domains) or '(none)'} "
        f"mailFolders={folder_clause} windowHours={window_hours or 'unlimited'} "
        f"since={since_dt.isoformat() if since_dt else '(unlimited)'} maxUnanswered={max_unanswered}"
    )

    inbox_query = _build_inbound_query(since_ts, include_domains, exclude_domains, folder_clause)
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
        from_header = _find_header(msg, "From") or ""
        if not _address_matches_include_domains(from_header, include_domains):
            continue
        if _address_matches_exclude_domains(from_header, exclude_domains):
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
            "sinceUsed": since_dt.isoformat() if since_dt else "",
        }

    sent_query = f"in:sent after:{since_ts}" if since_ts is not None else "in:sent"
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
        "sinceUsed": since_dt.isoformat() if since_dt else "",
    }
