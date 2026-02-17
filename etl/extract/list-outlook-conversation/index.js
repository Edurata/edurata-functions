const axios = require("axios");

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";

function encodeODataString(s) {
  return "'" + String(s).replace(/'/g, "''") + "'";
}

// super simple HTML -> Text (ohne DOM). Für “nur Inhalt” meistens ok.
function htmlToText(html) {
  if (!html) return "";
  return String(html)
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<\/(p|div|br|tr|li|h[1-6])>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\r/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function msgSortKey(m) {
  // for ordering: sentDateTime preferred, else receivedDateTime
  return m.sentDateTime || m.receivedDateTime || "";
}

async function fetchAllPages(initialUrl, { headers, params }) {
  const items = [];
  let url = initialUrl;
  let first = true;

  while (url) {
    let res;
    try {
      res = await axios.get(url, {
        headers,
        // params nur beim ersten Request; nextLink enthält bereits alles
        params: first ? params : undefined,
      });
    } catch (err) {
      console.error("[graph] request failed:", err.message, err.response?.status, err.response?.data);
      throw err;
    }

    if (res.status !== 200) {
      throw new Error(`Graph failed: ${res.status} ${res.statusText}`);
    }

    const value = res.data.value || [];
    items.push(...value);

    url = res.data["@odata.nextLink"] || null;
    first = false;
  }

  return items;
}

/**
 * Holt alle Messages einer Konversation aus Inbox + SentItems
 * und gibt sie chronologisch (alt -> neu) zurück.
 */
async function handler(inputs) {
  console.log("[list-outlook-conversation] inputs:", JSON.stringify(inputs));

  const token = process.env.OUTLOOK_API_KEY;
  if (!token) throw new Error("OUTLOOK_API_KEY not set");

  const { conversationId, top = 200, includePlainText = true } = inputs || {};
  if (!conversationId || String(conversationId).trim() === "") {
    throw new Error("conversationId is required");
  }

  const conv = String(conversationId).trim();
  const n = Math.min(Math.max(1, Number(top) || 200), 500); // du kannst das Limit erhöhen, paging macht’s möglich

  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  // WICHTIG: kein $orderby -> Graph soll nicht “kompliziert” werden
  const filter = `conversationId eq ${encodeODataString(conv)}`;
  const select =
    "id,subject,from,toRecipients,receivedDateTime,sentDateTime,conversationId,body,isRead,parentFolderId";

  const params = {
    $filter: filter,
    $select: select,
    $top: 50, // page size (Graph cap variiert; 25/50/100 – 50 ist oft safe)
  };

  const inboxUrl = `${GRAPH_BASE}/me/mailFolders/Inbox/messages`;
  const sentUrl = `${GRAPH_BASE}/me/mailFolders/SentItems/messages`;

  console.log("[list-outlook-conversation] fetching Inbox pages…");
  const inboxMsgs = await fetchAllPages(inboxUrl, { headers, params });

  console.log("[list-outlook-conversation] fetching SentItems pages…");
  const sentMsgs = await fetchAllPages(sentUrl, { headers, params });

  // merge + dedupe by id
  const byId = new Map();
  for (const m of [...inboxMsgs, ...sentMsgs]) {
    if (m?.id && !byId.has(m.id)) byId.set(m.id, m);
  }

  let all = Array.from(byId.values());
  console.log("[list-outlook-conversation] merged unique messages:", all.length);

  // sort oldest -> newest
  all.sort((a, b) => {
    const ka = msgSortKey(a);
    const kb = msgSortKey(b);
    if (ka === kb) return 0;
    return ka < kb ? -1 : 1;
  });

  // wenn du wirklich nur “letzte N” willst: tail nehmen, aber Reihenfolge beibehalten
  if (all.length > n) {
    all = all.slice(all.length - n);
  }

  const messages = all.map((msg) => {
    const body = msg.body ? { contentType: msg.body.contentType, content: msg.body.content } : null;
    const bodyText =
      includePlainText && body?.content
        ? body.contentType?.toLowerCase() === "html"
          ? htmlToText(body.content)
          : String(body.content).trim()
        : null;

    return {
      id: msg.id,
      subject: msg.subject || null,
      from: {
        address: msg.from?.emailAddress?.address || null,
        name: msg.from?.emailAddress?.name || null,
      },
      toRecipients: (msg.toRecipients || []).map((r) => ({
        address: r.emailAddress?.address || null,
        name: r.emailAddress?.name || null,
      })),
      receivedDateTime: msg.receivedDateTime || null,
      sentDateTime: msg.sentDateTime || null,
      conversationId: msg.conversationId || null,
      body, // original body (HTML/Text)
      // bodyText, // plain text extraction (optional)
      isRead: msg.isRead,
      parentFolderId: msg.parentFolderId,
    };
  });

  return {
    conversationId: conv,
    count: messages.length,
    messages, // alt -> neu
  };
}

module.exports = { handler };
