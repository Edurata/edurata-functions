const axios = require("axios");

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";
const IS_REPLY_TO_PROPERTY_ID =
  "String {66f5a359-4659-4830-9070-00047ec6ac6e} Name isReplyTo";
const DRAFT_EXTENSION_NAME = "com.edurata.draftMetadata";

async function handler(inputs) {
  const token = process.env.OUTLOOK_API_KEY;
  if (!token) {
    throw new Error("OUTLOOK_API_KEY not set");
  }

  const {
    originalMessageId,
    body,
    categories = [],
    threadId: _threadId,
    extensionMetadata,
  } = inputs;

  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  // Create reply draft (saved to Drafts folder)
  const createReplyRes = await axios.post(
    `${GRAPH_BASE}/me/messages/${originalMessageId}/createReply`,
    {},
    { headers }
  );

  if (createReplyRes.status < 200 || createReplyRes.status >= 300) {
    throw new Error(
      `Failed to create reply draft: ${createReplyRes.status} ${createReplyRes.statusText}`
    );
  }

  const draft = createReplyRes.data;
  const draftId = draft.id;
  const conversationId = draft.conversationId || _threadId;

  // Update draft with body, categories, and singleValueExtendedProperty isReplyTo
  const updatePayload = {
    body: {
      contentType: "HTML",
      content: body,
    },
    categories: Array.isArray(categories) ? categories : [],
    singleValueExtendedProperties: [
      {
        id: IS_REPLY_TO_PROPERTY_ID,
        value: originalMessageId,
      },
    ],
  };

  const patchRes = await axios.patch(
    `${GRAPH_BASE}/me/messages/${draftId}`,
    updatePayload,
    { headers }
  );

  if (patchRes.status < 200 || patchRes.status >= 300) {
    throw new Error(
      `Failed to update draft: ${patchRes.status} ${patchRes.statusText}`
    );
  }

  const updated = patchRes.data;
  const webLink = updated.webLink || "https://outlook.office.com/mail/";

  // Optional: add open extension for metadata
  if (extensionMetadata && typeof extensionMetadata === "object" && Object.keys(extensionMetadata).length > 0) {
    const extensionPayload = {
      "@odata.type": "#microsoft.graph.openTypeExtension",
      extensionName: DRAFT_EXTENSION_NAME,
      ...extensionMetadata,
    };
    try {
      await axios.post(
        `${GRAPH_BASE}/me/messages/${draftId}/extensions`,
        extensionPayload,
        { headers }
      );
    } catch (err) {
      console.warn("Failed to add extension metadata to draft:", err.response?.data || err.message);
      // Non-fatal; draft and isReplyTo are already set
    }
  }

  return {
    draftId,
    threadId: conversationId,
    webLink,
  };
}

module.exports = { handler };
