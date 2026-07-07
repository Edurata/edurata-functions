const axios = require("axios");

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";
const LOG_PREFIX = "[list-outlook-unanswered]";

function normalizeGraphAccessToken(raw) {
  if (raw == null || typeof raw !== "string") return raw;
  let t = raw.trim();
  if ((t.startsWith('"') && t.endsWith('"')) || (t.startsWith("'") && t.endsWith("'"))) {
    t = t.slice(1, -1).trim();
  }
  if (/^bearer\s+/i.test(t)) {
    t = t.replace(/^bearer\s+/i, "").trim();
  }
  return t;
}

function encodeODataString(s) {
  return "'" + String(s).replace(/'/g, "''") + "'";
}

function normalizeDomainList(value) {
  if (value == null) return [];
  const raw = Array.isArray(value) ? value : [value];
  return raw
    .map((item) => String(item || "").trim())
    .filter(Boolean);
}

function resolveSenderDomains(inputs) {
  const includeDomains = normalizeDomainList(inputs?.senderDomains);
  const excludeDomains = normalizeDomainList(inputs?.excludeDomains);
  return { includeDomains, excludeDomains };
}

function normalizeFolderList(value) {
  return normalizeDomainList(value);
}

/** OData filter for inbound rows, optionally scoped by time window and sender domain. */
function buildInboundSenderFilter(sinceIso, includeDomains, excludeDomains = []) {
  const clauses = [];
  if (sinceIso) {
    clauses.push(`receivedDateTime ge ${sinceIso}`);
  }

  if (includeDomains.length) {
    const includeClause =
      includeDomains.length === 1
        ? `contains(from/emailAddress/address,${encodeODataString(includeDomains[0])})`
        : "(" +
          includeDomains
            .map((domain) => `contains(from/emailAddress/address,${encodeODataString(domain)})`)
            .join(" or ") +
          ")";
    clauses.push(includeClause);
  }

  for (const domain of excludeDomains) {
    clauses.push(`not contains(from/emailAddress/address,${encodeODataString(domain)})`);
  }

  return clauses.join(" and ");
}

const MAIL_FOLDER_ID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

/** Lowercase well-known folder segment accepted by /me/mailFolders/{name}/messages */
const WELL_KNOWN_MAIL_FOLDER = new Map(
  [
    ["inbox", "inbox"],
    ["sentitems", "sentitems"],
    ["sent items", "sentitems"],
    ["drafts", "drafts"],
    ["junk email", "junkemail"],
    ["junkemail", "junkemail"],
    ["junk", "junkemail"],
    ["deleted items", "deleteditems"],
    ["deleteditems", "deleteditems"],
    ["archive", "archive"],
  ].map(([k, v]) => [k.toLowerCase(), v])
);

/**
 * Resolves inbound folder specs to Graph URL segments `mailFolders/{id|wellKnown}`.
 * Accepts: inbox (default); GUID; well-known shortcut (inbox, junk, …);
 * otherwise treats value as display name and looks up via Graph (mailbox root, then Inbox children).
 */
async function resolveInboundMailFolderSegment(headers, inboundMailFolderSpec) {
  const raw = String(inboundMailFolderSpec || "inbox").trim() || "inbox";

  if (MAIL_FOLDER_ID_RE.test(raw)) {
    return `mailFolders/${encodeURIComponent(raw)}`;
  }

  const wellKnown = WELL_KNOWN_MAIL_FOLDER.get(raw.toLowerCase());
  if (wellKnown) {
    return `mailFolders/${wellKnown}`;
  }

  // Allow passing Graph well-known literal directly (e.g. junkemail)
  if (/^(inbox|sentitems|drafts|junkemail|deleteditems|archive)$/i.test(raw)) {
    return `mailFolders/${raw.toLowerCase()}`;
  }

  const nameEq = `displayName eq ${encodeODataString(raw)}`;
  const listParams = {
    $filter: nameEq,
    $select: "id,displayName",
    $top: 10,
  };

  const lookups = [
    { label: "mailbox root", url: `${GRAPH_BASE}/me/mailFolders` },
    { label: "Inbox children", url: `${GRAPH_BASE}/me/mailFolders/inbox/childFolders` },
  ];

  for (const { label, url } of lookups) {
    const res = await axios.get(url, { headers, params: listParams });
    const folders = res.data?.value || [];
    if (folders.length === 1) {
      console.log(
        `${LOG_PREFIX} resolved inbound folder by displayName='${raw}' (${label}) → id=${folders[0].id}`
      );
      return `mailFolders/${encodeURIComponent(folders[0].id)}`;
    }
    if (folders.length > 1) {
      throw new Error(
        `mailFolderNames: displayName '${raw}' matched ${folders.length} folders under ${label}; use folder GUID`
      );
    }
  }

  throw new Error(
    `mailFolderNames: no folder with displayName '${raw}' at mailbox root or as direct child of Inbox; pass a folder GUID or move the folder`
  );
}

async function resolveInboundMailFolderSegments(headers, mailFolderNames) {
  const specs = normalizeFolderList(mailFolderNames);
  const folderSpecs = specs.length ? specs : ["inbox"];
  const segments = [];
  const seen = new Set();
  for (const spec of folderSpecs) {
    const seg = await resolveInboundMailFolderSegment(headers, spec);
    if (!seen.has(seg)) {
      seen.add(seg);
      segments.push(seg);
    }
  }
  return segments;
}
function chunkArray(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}
function buildOrEquals(field, values) {
  return "(" + values.map((v) => `${field} eq ${encodeODataString(v)}`).join(" or ") + ")";
}
function toMs(dt) {
  const t = Date.parse(dt);
  return Number.isFinite(t) ? t : NaN;
}
function subtractHoursIso(hours) {
  const d = new Date(Date.now() - hours * 60 * 60 * 1000);
  return d.toISOString();
}

function resolveWindowHours(inputs) {
  const raw = inputs?.windowHours;
  if (raw == null || raw === "") return 0;
  const n = Number(raw);
  return Number.isFinite(n) ? n : 0;
}

async function pagedGet({ url, headers, params, maxPages }) {
  const pages = [];
  let next = null;
  let page = 0;

  do {
    page++;
    const res = next
      ? await axios.get(next, { headers })
      : await axios.get(url, { headers, params });

    pages.push(res);
    next = res.data?.["@odata.nextLink"] || null;
  } while (next && page < maxPages);

  return pages;
}

async function handler(inputs) {
  const token = normalizeGraphAccessToken(process.env.OUTLOOK_API_KEY);
  if (!token) throw new Error("OUTLOOK_API_KEY not set");

  const { includeDomains, excludeDomains } = resolveSenderDomains(inputs);

  const {
    mailFolderNames,
    pageSize = 100,
    maxInboxPages = 3,
    maxSentPages = 3,
    draftChunkSize = 15,
    onlyEdurataDrafts = false,
    maxUnanswered = 10,
  } = inputs || {};

  const windowHours = resolveWindowHours(inputs);
  const sinceDateTime = windowHours > 0 ? subtractHoursIso(windowHours) : null;

  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const inboundFolderSegs = await resolveInboundMailFolderSegments(headers, mailFolderNames);
  console.log(
    `${LOG_PREFIX} start senderDomains=${includeDomains.join(",") || "(all)"} excludeDomains=${excludeDomains.join(",") || "(none)"} inboundFolders=${inboundFolderSegs.join(",")} windowHours=${windowHours || "unlimited"} sinceUsed=${sinceDateTime || "(unlimited)"} maxUnanswered=${maxUnanswered}`
  );

  /* ===============================
     1) INBOX BULK PULL
  =============================== */

  const inboxMsgs = [];
  for (const inboundFolderSeg of inboundFolderSegs) {
    const inboundFilter = buildInboundSenderFilter(sinceDateTime, includeDomains, excludeDomains);
    const inboxPages = await pagedGet({
      url: `${GRAPH_BASE}/me/${inboundFolderSeg}/messages`,
      headers,
      params: {
        ...(inboundFilter ? { $filter: inboundFilter } : {}),
        $top: Math.min(pageSize, 100),
        $select: "id,receivedDateTime,conversationId",
        $orderby: "receivedDateTime desc",
      },
      maxPages: maxInboxPages,
    });
    inboxMsgs.push(...inboxPages.flatMap((p) => p.data?.value || []));
  }

  console.log(
    `${LOG_PREFIX} inbox: ${inboxMsgs.length} message(s) from domain across ${inboundFolderSegs.length} folder(s)`
  );

  // Latest inbound per conversation
  const latestInboundByCid = new Map();
  for (const m of inboxMsgs) {
    if (!m.conversationId || !m.receivedDateTime) continue;
    const cur = latestInboundByCid.get(m.conversationId);
    if (!cur || m.receivedDateTime > cur.receivedDateTime) {
      latestInboundByCid.set(m.conversationId, {
        id: m.id,
        receivedDateTime: m.receivedDateTime,
      });
    }
  }

  const allConversationIds = Array.from(latestInboundByCid.keys());
  console.log(
    `${LOG_PREFIX} inbox: ${allConversationIds.length} unique conversation(s) (latest inbound per cid)`
  );
  if (allConversationIds.length === 0) {
    console.log(`${LOG_PREFIX} early return: no conversations in window`);
    return {
      unansweredConversationIds: [],
      answeredConversationIds: [],
      countUnanswered: 0,
      countAnswered: 0,
      sinceUsed: sinceDateTime || "",
    };
  }

  /* ===============================
     2) SENT ITEMS BULK PULL
  =============================== */

  const sentPages = await pagedGet({
    url: `${GRAPH_BASE}/me/mailFolders/sentitems/messages`,
    headers,
    params: {
      ...(sinceDateTime ? { $filter: `sentDateTime ge ${sinceDateTime}` } : {}),
      $top: Math.min(pageSize, 100),
      $select: "conversationId,sentDateTime",
      $orderby: "sentDateTime desc",
    },
    maxPages: maxSentPages,
  });

  const sentMsgs = sentPages.flatMap((p) => p.data?.value || []);
  console.log(
    `${LOG_PREFIX} sent: ${sentPages.length} page(s), ${sentMsgs.length} message(s) in window`
  );

  const latestSentByCid = new Map();
  for (const s of sentMsgs) {
    if (!s.conversationId || !s.sentDateTime) continue;
    if (!latestInboundByCid.has(s.conversationId)) continue;
    const cur = latestSentByCid.get(s.conversationId);
    if (!cur || s.sentDateTime > cur) {
      latestSentByCid.set(s.conversationId, s.sentDateTime);
    }
  }
  const cidsWithSent = [...latestSentByCid.keys()].filter((cid) =>
    allConversationIds.includes(cid)
  ).length;
  console.log(
    `${LOG_PREFIX} sent: ${cidsWithSent} of ${allConversationIds.length} conversation(s) have sent message in window`
  );

  /* ===============================
     3) DRAFT BULK CHECK
  =============================== */

  const newestDraftByCid = new Map();
  const chunks = chunkArray(allConversationIds, draftChunkSize);

  for (const chunk of chunks) {
    let filter = `isDraft eq true and ${buildOrEquals("conversationId", chunk)}`;
    if (onlyEdurataDrafts) {
      filter += ` and categories/any(c: c eq ${encodeODataString("EdurataDraft")})`;
    }

    const res = await axios.get(`${GRAPH_BASE}/me/mailFolders/drafts/messages`, {
      headers,
      params: {
        $filter: filter,
        $top: 200,
        $select: "id,conversationId,lastModifiedDateTime",
      },
    });

    const drafts = res.data?.value || [];
    for (const d of drafts) {
      const cur = newestDraftByCid.get(d.conversationId);
      if (!cur || d.lastModifiedDateTime > cur.lastModifiedDateTime) {
        newestDraftByCid.set(d.conversationId, {
          id: d.id,
          lastModifiedDateTime: d.lastModifiedDateTime,
        });
      }
    }
  }
  const totalDrafts = newestDraftByCid.size;
  console.log(
    `${LOG_PREFIX} drafts: ${totalDrafts} conversation(s) have draft(s) (onlyEdurataDrafts=${onlyEdurataDrafts})`
  );

  /* ===============================
     4) CLASSIFICATION
  =============================== */

  const unansweredConversationIds = [];
  const answeredConversationIds = [];

  for (const cid of allConversationIds) {
    const inbound = latestInboundByCid.get(cid);
    const inboundMs = toMs(inbound.receivedDateTime);
    const sentMs = toMs(latestSentByCid.get(cid));

    const isAnswered =
      Number.isFinite(sentMs) &&
      Number.isFinite(inboundMs) &&
      sentMs > inboundMs;

    if (isAnswered) {
      answeredConversationIds.push(cid);
      continue;
    }

    const draft = newestDraftByCid.get(cid);
    if (!draft) {
      unansweredConversationIds.push(cid);
      continue;
    }

    const draftMs = toMs(draft.lastModifiedDateTime);
    const isOutdated =
      Number.isFinite(draftMs) &&
      Number.isFinite(inboundMs) &&
      draftMs < inboundMs;

    if (isOutdated) {
      unansweredConversationIds.push(cid);
    }
  }

  const limit = Math.max(0, Number(maxUnanswered) || 0);
  const cappedIds = limit > 0 ? unansweredConversationIds.slice(0, limit) : unansweredConversationIds;

  console.log(
    `${LOG_PREFIX} classification: answered=${answeredConversationIds.length} unanswered=${unansweredConversationIds.length} (returning ${cappedIds.length} after maxUnanswered=${limit})`
  );

  return {
    unansweredConversationIds: cappedIds,
    answeredConversationIds,
    countUnanswered: unansweredConversationIds.length,
    countAnswered: answeredConversationIds.length,
    sinceUsed: sinceDateTime || "",
  };
}

module.exports = { handler };
