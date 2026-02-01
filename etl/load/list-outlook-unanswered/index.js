const axios = require("axios");

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";
const IS_REPLY_TO_PROPERTY_ID =
  "String {66f5a359-4659-4830-9070-00047ec6ac6e} Name isReplyTo";

function encodeODataString(s) {
  return "'" + String(s).replace(/'/g, "''") + "'";
}

async function handler(inputs) {
  const token = process.env.OUTLOOK_API_KEY;
  if (!token) {
    throw new Error("OUTLOOK_API_KEY not set");
  }

  const { senderDomain, top = 50 } = inputs;
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  // 1) Get inbox messages from senders whose address contains senderDomain
  const domainFilter = `contains(from/emailAddress/address,${encodeODataString(senderDomain)})`;
  const inboxUrl = `${GRAPH_BASE}/me/mailFolders/inbox/messages`;
  const inboxParams = {
    $filter: domainFilter,
    $top: Math.min(Math.max(1, top), 100),
    $select:
      "id,subject,from,receivedDateTime,conversationId,bodyPreview,isRead",
    $orderby: "receivedDateTime desc",
  };

  const inboxRes = await axios.get(inboxUrl, { headers, params: inboxParams });
  if (inboxRes.status !== 200) {
    throw new Error(
      `Failed to get inbox: ${inboxRes.status} ${inboxRes.statusText}`
    );
  }

  const candidates = inboxRes.data.value || [];
  const unanswered = [];

  for (const msg of candidates) {
    const messageId = msg.id;
    const conversationId = msg.conversationId;
    const receivedDateTime = msg.receivedDateTime;

    // 2) Check if there is a draft with isReplyTo = this message id
    const draftFilter = `singleValueExtendedProperties/Any(ep: ep/id eq ${encodeODataString(IS_REPLY_TO_PROPERTY_ID)} and ep/value eq ${encodeODataString(messageId)})`;
    const draftsRes = await axios.get(
      `${GRAPH_BASE}/me/mailFolders/drafts/messages`,
      {
        headers,
        params: { $filter: draftFilter, $top: 1 },
      }
    );
    if (draftsRes.status !== 200) {
      console.warn("Draft check failed for message", messageId, draftsRes.status);
      continue;
    }
    const draftsWithReply = (draftsRes.data.value || []).length > 0;
    if (draftsWithReply) {
      continue; // has draft reply -> not unanswered
    }

    // 3) Check if there is a sent reply in the same conversation after this message
    const sentFilter = `conversationId eq ${encodeODataString(conversationId)} and sentDateTime gt ${encodeODataString(receivedDateTime)}`;
    const sentRes = await axios.get(
      `${GRAPH_BASE}/me/mailFolders/sentitems/messages`,
      {
        headers,
        params: { $filter: sentFilter, $top: 1 },
      }
    );
    if (sentRes.status !== 200) {
      console.warn("Sent check failed for message", messageId, sentRes.status);
      continue;
    }
    const hasSentReply = (sentRes.data.value || []).length > 0;
    if (hasSentReply) {
      continue; // already replied -> not unanswered
    }

    unanswered.push({
      id: msg.id,
      subject: msg.subject,
      from: msg.from?.emailAddress?.address || null,
      fromName: msg.from?.emailAddress?.name || null,
      receivedDateTime: msg.receivedDateTime,
      conversationId: msg.conversationId,
      bodyPreview: msg.bodyPreview || null,
      isRead: msg.isRead,
    });
  }

  return {
    messages: unanswered,
    count: unanswered.length,
  };
}

module.exports = { handler };
