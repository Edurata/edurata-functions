const puppeteer = require("puppeteer");
const fs = require("fs");

async function handler(inputs) {
  const htmlFile = inputs.html_file;

  if (!htmlFile || !fs.existsSync(htmlFile)) {
    throw new Error("Invalid or missing HTML file.");
  }

  const outputPdf = htmlFile.replace(".html", ".pdf");

  try {
    const browser = await puppeteer.launch({ headless: "new" }); // Runs in headless mode
    const page = await browser.newPage();
    const htmlContent = fs.readFileSync(htmlFile, "utf-8");

    await page.setContent(htmlContent, { waitUntil: "load" }); // Load HTML fully
    await page.pdf({
      path: outputPdf,
      format: "A4",
      printBackground: true, // Ensures background colors/images are printed
    });

    await browser.close();
  } catch (error) {
    throw new Error(`Failed to generate PDF: ${error.message}`);
  }

  return { pdf_file: outputPdf };
}

module.exports = { handler };

// Example function call (Commented Out)
// handler({ html_file: "example.html" }).then(console.log).catch(console.error);
