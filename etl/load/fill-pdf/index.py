from pypdf import PdfReader, PdfWriter

def fill_pdf_fields(pdf_path, fields_data):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    page = reader.pages[0]
    fields = reader.get_fields()

    writer.add_page(page)

    field_values = {field['field_name']: field['field_value'] for field in fields_data}
    writer.update_page_form_field_values(writer.pages[0], field_values)

    return writer

def handler(inputs):
    pdf_path = inputs['pdf_path']
    fields_data = inputs['fields_data']
    
    writer = fill_pdf_fields(pdf_path, fields_data)
    
    filled_pdf_path = 'filled_pdf.pdf'
    with open(filled_pdf_path, 'wb') as output_stream:
        writer.write(output_stream)
    
    outputs = {
        'filled_pdf_path': filled_pdf_path
    }
    
    return outputs

# Sample function call
# inputs = {
#     'pdf_path': 'example.pdf',
#     'fields_data': [
#         {'field_name': 'Name', 'field_value': 'John Doe'},
#         {'field_name': 'Date', 'field_value': '2024-06-17'}
#     ]
# }
# outputs = handler(inputs)
# print(outputs)
