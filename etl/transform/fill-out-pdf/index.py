from PyPDF2 import PdfReader, PdfWriter

def handler(inputs):
    pdf_path = inputs["pdf_template"]
    field_values = inputs.get("field_values", {})
    dry_run = inputs.get("dry_run", False)

    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    field_names = list(fields.keys()) if fields else []

    if dry_run:
        print("Dry run: Form fields found:", field_names)
        return {"form_fields": field_names}

    output_path = "/tmp/filled_output_named.pdf"
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.update_page_form_field_values(writer.pages[0], field_values)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    return {"filled_pdf": output_path, "form_fields": field_names}

# Example dry run:
# handler({
#     "pdf_template": "./test.pdf",
#     "dry_run": True
# })

# Example full fill:
# print(handler({
#     "pdf_template": "./test.pdf",
#     "field_values": {
#         "Adresse": "Musterstraße 1",
#         "Datum": "01.01.2025",
#         "Firma1": "Firma A",
#         "Firma2": "Firma B"
#     }
# }))
