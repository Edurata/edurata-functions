const fs = require("fs");
const readline = require("readline-promise").default;
const { google } = require("googleapis");
require("dotenv").config();

const SCOPES = ["https://www.googleapis.com/auth/gmail.modify"];
const LABEL_ID = "INBOX";
const RECIPIENT_EMAIL = "recipient@example.com";

async function main() {
  // Load credentials from .env file
  const TOKEN = process.env.GMAIL_API_TOKEN;
  if (!TOKEN) {
    console.error("GMAIL_API_TOKEN environment variable is not set.");
    return;
  }

  // Authorize the client
  const oAuth2Client = new google.auth.OAuth2();
  oAuth2Client.setCredentials(JSON.parse(TOKEN));

  // Create a Gmail client
  const gmail = google.gmail({ version: "v1", auth: oAuth2Client });

  // Search for emails with attachments and 'invoice' in the subject
  const query = `label:${LABEL_ID} has:attachment subject:invoice`;
  const messages = await searchMessages(gmail, query);

  for (const message of messages) {
    // Get the message
    const msg = await getMessage(gmail, message.id);

    // Check if the message has any attachments
    if (msg.payload.parts) {
      for (const part of msg.payload.parts) {
        if (part.filename) {
          const filename = part.filename;
          // Check if the filename contains 'invoice'
          if (filename.toLowerCase().includes("invoice")) {
            // Forward the message to the recipient email
            await forwardMessage(gmail, msg.id, RECIPIENT_EMAIL);
            console.log(
              `Forwarded email with invoice attachment to ${RECIPIENT_EMAIL}`
            );
          }
        }
      }
    }
  }
}

async function searchMessages(gmail, query) {
  const res = await gmail.users.messages.list({
    userId: "me",
    q: query,
  });
  return res.data.messages || [];
}

async function getMessage(gmail, messageId) {
  const res = await gmail.users.messages.get({
    userId: "me",
    id: messageId,
  });
  return res.data;
}

async function forwardMessage(gmail, messageId, recipient) {
  await gmail.users.messages.send({
    userId: "me",
    requestBody: {
      raw: await getRawMessage(gmail, messageId, recipient),
    },
  });
}

async function getRawMessage(gmail, messageId, recipient) {
  const res = await gmail.users.messages.get({
    userId: "me",
    id: messageId,
  });
  const message = res.data;

  let email = "";
  for (const header of message.payload.headers) {
    if (header.name === "To") {
      email = header.value;
      break;
    }
  }

  message.payload.headers.push({ name: "To", value: recipient });
  return Buffer.from(JSON.stringify(message)).toString("base64");
}

main().catch(console.error);
