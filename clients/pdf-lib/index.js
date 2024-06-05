const fs = require("fs");
const { PDFDocument } = require("pdf-lib");

async function handler(inputs) {
  const { action, pdfFilePath, formData } = inputs;
  const existingPdfBytes = fs.readFileSync(pdfFilePath);

  // Load a PDFDocument from the existing PDF bytes
  const pdfDoc = await PDFDocument.load(existingPdfBytes);

  // Get the form from the PDF
  const form = pdfDoc.getForm();

  if (action === "fill") {
    // Fill in the form fields with the provided data
    for (const [fieldName, fieldValue] of Object.entries(formData)) {
      const field = form.getTextField(fieldName);
      if (field) {
        field.setText(fieldValue);
      }
    }

    // Serialize the PDFDocument to bytes (a Uint8Array)
    const pdfBytes = await pdfDoc.save();
    const outputFilePath = "output.pdf";

    // Write the PDF to a file
    fs.writeFileSync(outputFilePath, pdfBytes);

    return { outputFilePath };
  } else if (action === "read") {
    // Read the form fields and their current values
    const formFields = {};
    const fields = form.getFields();
    fields.forEach((field) => {
      const name = field.getName();
      const value = field.getText();
      formFields[name] = value;
    });

    return { formFields };
  } else {
    throw new Error('Invalid action. Must be "fill" or "read".');
  }
}

// Example usage for filling the form:
// const inputs = {
//   action: 'fill',
//   pdfFilePath: 'path/to/your/input.pdf',
//   formData: {
//     'FieldName1': 'Value1',
//     'FieldName2': 'Value2',
//   },
// };
// handler(inputs).then((outputs) => console.log(outputs));

// Example usage for reading the form:
// const inputs = {
//   action: 'read',
//   pdfFilePath: 'path/to/your/input.pdf',
// };
// handler(inputs).then((outputs) => console.log(outputs));

module.exports = { handler };
