const axios = require("axios");

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";

function encodeODataString(s) {
  return "'" + String(s).replace(/'/g, "''") + "'";
}

/**
 * Fetches the last n messages in an Outlook conversation by conversationId.
 * Uses Microsoft Graph /me/messages filtered by conversationId, ordered by
 * sentDateTime desc, so "last n" means the n most recent messages in the thread.
 */
async function handler(inputs) {
  console.log("[list-outlook-conversation] handler invoked, inputs:", JSON.stringify(inputs));

  const token = process.env.OUTLOOK_API_KEY;
  if (!token) {
    console.error("[list-outlook-conversation] OUTLOOK_API_KEY not set");
    throw new Error("OUTLOOK_API_KEY not set");
  }

  const { conversationId, top = 20 } = inputs;
  if (!conversationId || String(conversationId).trim() === "") {
    throw new Error("conversationId is required");
  }

  const n = Math.min(Math.max(1, Number(top) || 20), 100);
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const url = `${GRAPH_BASE}/me/messages`;
  const filter = `conversationId eq ${encodeODataString(String(conversationId).trim())}`;
  const params = {
    $filter: filter,
    $top: n,
    $orderby: "sentDateTime desc",
    $select:
      "id,subject,from,toRecipients,receivedDateTime,sentDateTime,conversationId,bodyPreview,body,isRead,parentFolderId",
  };

  console.log("[list-outlook-conversation] fetching url:", url, "params:", JSON.stringify(params));
  let res;
  try {
    res = await axios.get(url, { headers, params });
  } catch (err) {
    console.error("[list-outlook-conversation] request failed:", err.message, "response:", err.response?.status, err.response?.data);
    throw err;
  }

  if (res.status !== 200) {
    console.error("[list-outlook-conversation] unexpected status:", res.status, res.statusText, res.data);
    throw new Error(`Failed to get conversation: ${res.status} ${res.statusText}`);
  }

  const value = res.data.value || [];
  console.log("[list-outlook-conversation] got", value.length, "messages");

  // Return oldest-first so downstream "last entry = newest message" holds
  const raw = value.map((msg) => ({
    id: msg.id,
    subject: msg.subject,
    from: {
      emailAddress: {
        address: msg.from?.emailAddress?.address || null,
        name: msg.from?.emailAddress?.name || null,
      },
    },
    toRecipients: (msg.toRecipients || []).map((r) => ({
      address: r.emailAddress?.address || null,
      name: r.emailAddress?.name || null,
    })),
    receivedDateTime: msg.receivedDateTime,
    sentDateTime: msg.sentDateTime,
    conversationId: msg.conversationId,
    bodyPreview: msg.bodyPreview || null,
    body: msg.body ? { contentType: msg.body.contentType, content: msg.body.content } : null,
    isRead: msg.isRead,
    parentFolderId: msg.parentFolderId,
  }));
  const messages = raw.reverse();

  return {
    conversationId: String(conversationId).trim(),
    messages,
    count: messages.length,
  };
}

module.exports = { handler };
