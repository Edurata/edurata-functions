const axios = require("axios");

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";
// default for draft messages
const IS_REPLY_TO_PROPERTY_ID =
  "String {66f5a359-4659-4830-9070-00047ec6ac6e} Name isReplyTo";

function encodeODataString(s) {
  return "'" + String(s).replace(/'/g, "''") + "'";
}

async function handler(inputs) {
  console.log("[list-outlook-unanswered] handler invoked, inputs:", JSON.stringify(inputs));

  const token = process.env.OUTLOOK_API_KEY;
  if (!token) {
    console.error("[list-outlook-unanswered] OUTLOOK_API_KEY not set");
    throw new Error("OUTLOOK_API_KEY not set");
  }
  console.log("[list-outlook-unanswered] token present, length:", token.length);

  const DEFAULT_SINCE = "1900-01-01T00:00:00Z";
  const { senderDomain, top = 50, since } = inputs;
  const sinceDateTime = since != null && String(since).trim() !== "" ? String(since).trim() : DEFAULT_SINCE;
  console.log("[list-outlook-unanswered] senderDomain:", senderDomain, "top:", top, "since:", sinceDateTime);

  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  // 1) Get inbox messages from senders whose address contains senderDomain.
  // Graph API requires: fields in $orderby must appear in $filter, in the same order;
  // other filter fields must come after. So we filter on receivedDateTime first, then domain.
  const inboxUrl = `${GRAPH_BASE}/me/mailFolders/inbox/messages`;
  const inboxFilter =
    `receivedDateTime ge ${sinceDateTime} and contains(from/emailAddress/address,${encodeODataString(senderDomain)})`;
  console.log("[list-outlook-unanswered] inbox filter:", inboxFilter);
  const inboxParams = {
    $filter: inboxFilter,
    $top: Math.min(Math.max(1, top), 100),
    $select:
      "id,subject,from,receivedDateTime,conversationId,bodyPreview,isRead",
    $orderby: "receivedDateTime desc",
  };

  console.log("[list-outlook-unanswered] fetching inbox, url:", inboxUrl, "params:", JSON.stringify(inboxParams));
  let inboxRes;
  try {
    inboxRes = await axios.get(inboxUrl, { headers, params: inboxParams });
  } catch (err) {
    console.error("[list-outlook-unanswered] inbox request failed:", err.message, "response:", err.response?.status, err.response?.data);
    throw err;
  }
  console.log("[list-outlook-unanswered] inbox response status:", inboxRes.status, "data.value length:", inboxRes.data?.value?.length);

  if (inboxRes.status !== 200) {
    console.error("[list-outlook-unanswered] unexpected inbox status:", inboxRes.status, inboxRes.statusText, inboxRes.data);
    throw new Error(
      `Failed to get inbox: ${inboxRes.status} ${inboxRes.statusText}`
    );
  }

  const candidates = inboxRes.data.value || [];
  console.log("[list-outlook-unanswered] candidates count:", candidates.length);

  const unanswered = [];

  for (let i = 0; i < candidates.length; i++) {
    const msg = candidates[i];
    const messageId = msg.id;
    const conversationId = msg.conversationId;
    const receivedDateTime = msg.receivedDateTime;
    console.log("[list-outlook-unanswered] processing candidate", i + 1, "/", candidates.length, "id:", messageId, "subject:", msg.subject?.substring(0, 50));

    // 2) Check if there is a draft with isReplyTo = this message id
    const draftFilter = `singleValueExtendedProperties/Any(ep: ep/id eq ${encodeODataString(IS_REPLY_TO_PROPERTY_ID)} and ep/value eq ${encodeODataString(messageId)})`;
    console.log("[list-outlook-unanswered] draft filter for", messageId, ":", draftFilter);
    let draftsRes;
    try {
      draftsRes = await axios.get(
        `${GRAPH_BASE}/me/mailFolders/drafts/messages`,
        {
          headers,
          params: { $filter: draftFilter, $top: 1 },
        }
      );
    } catch (draftErr) {
      console.error("[list-outlook-unanswered] draft request failed for", messageId, ":", draftErr.message, "response:", draftErr.response?.status, draftErr.response?.data);
      continue;
    }
    console.log("[list-outlook-unanswered] draft response for", messageId, "status:", draftsRes.status, "matches:", (draftsRes.data?.value || []).length);
    if (draftsRes.status !== 200) {
      console.warn("[list-outlook-unanswered] draft check failed for message", messageId, draftsRes.status);
      continue;
    }
    const draftsWithReply = (draftsRes.data.value || []).length > 0;
    if (draftsWithReply) {
      console.log("[list-outlook-unanswered] skipping", messageId, "- has draft reply");
      continue; // has draft reply -> not unanswered
    }

    // 3) Check if there is a sent reply in the same conversation after this message
    const sentFilter = `conversationId eq ${encodeODataString(conversationId)} and sentDateTime gt ${encodeODataString(receivedDateTime)}`;
    console.log("[list-outlook-unanswered] sent filter for", messageId, ":", sentFilter);
    let sentRes;
    try {
      sentRes = await axios.get(
        `${GRAPH_BASE}/me/mailFolders/sentitems/messages`,
        {
          headers,
          params: { $filter: sentFilter, $top: 1 },
        }
      );
    } catch (sentErr) {
      console.error("[list-outlook-unanswered] sent request failed for", messageId, ":", sentErr.message, "response:", sentErr.response?.status, sentErr.response?.data);
      continue;
    }
    console.log("[list-outlook-unanswered] sent response for", messageId, "status:", sentRes.status, "matches:", (sentRes.data?.value || []).length);
    if (sentRes.status !== 200) {
      console.warn("[list-outlook-unanswered] sent check failed for message", messageId, sentRes.status);
      continue;
    }
    const hasSentReply = (sentRes.data.value || []).length > 0;
    if (hasSentReply) {
      console.log("[list-outlook-unanswered] skipping", messageId, "- has sent reply");
      continue; // already replied -> not unanswered
    }

    console.log("[list-outlook-unanswered] adding to unanswered:", messageId, msg.subject?.substring(0, 50));
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

  console.log("[list-outlook-unanswered] done, unanswered count:", unanswered.length);
  const result = {
    messages: unanswered,
    count: unanswered.length,
  };
  console.log("[list-outlook-unanswered] returning result");
  return result;
}

module.exports = { handler };
