#!/usr/bin/env node
/** One-off local runner; delete after use if you prefer. */
const fs = require("fs");
const path = require("path");

const logPath = path.join(__dirname, "list-outlook-run-log.txt");

function log(line) {
  fs.appendFileSync(logPath, line + "\n");
  console.log(line);
}

(async () => {
  fs.writeFileSync(logPath, "");
  const { handler } = require("./index.js");

  const payload = {
    senderDomains: ["mail.kleinanzeigen.de"],
    mailFolderNames: ["Kleinanzeigen konvo"],
    maxUnanswered: 10,
    windowHours: 0,
  };

  log("OUTLOOK_API_KEY set: " + Boolean(process.env.OUTLOOK_API_KEY));
  if (!process.env.OUTLOOK_API_KEY) {
    log("ERROR: Export OUTLOOK_API_KEY (Bearer token) then re-run.");
    process.exit(1);
  }

  try {
    const result = await handler(payload);
    log(JSON.stringify(result, null, 2));
  } catch (e) {
    if (e && e.response) {
      log(`Graph HTTP ${e.response.status} ${e.response.statusText || ""}`);
      if (e.response.data !== undefined) {
        log(typeof e.response.data === "string" ? e.response.data : JSON.stringify(e.response.data, null, 2));
      }
    }
    log(String(e && e.stack ? e.stack : e));
    process.exit(1);
  }
})();
