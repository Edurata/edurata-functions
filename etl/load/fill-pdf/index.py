import PyPDF2
from PyPDF2.generic import NameObject, TextStringObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def handler(inputs):
    pdf_path = inputs['pdf_path']
    field_name = inputs['field_data']['field_name']
    field_value = inputs['field_data']['field_value']
    
    # Read the existing PDF
    pdf_reader = PyPDF2.PdfFileReader(pdf_path)
    pdf_writer = PyPDF2.PdfFileWriter()
    
    # Create a new PDF to overlay
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Assuming a simple fixed position for demonstration purposes
    can.drawString(100, 750, field_value)
    can.save()
    
    packet.seek(0)
    overlay_pdf = PyPDF2.PdfFileReader(packet)
    
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        
        if page_num == 0:  # Add overlay only to the first page for demonstration
            page.mergePage(overlay_pdf.getPage(0))
        
        pdf_writer.addPage(page)
    
    filled_pdf_path = 'filled_pdf.pdf'
    with open(filled_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    
    outputs = {
        'filled_pdf_path': filled_pdf_path
    }
    
    return outputs

# Sample function call
# inputs = {
#     'pdf_path': 'example.pdf',
#     'field_data': {
#         'field_name': 'Name',
#         'field_value': 'John Doe'
#     }
# }
# outputs = handler(inputs)
# print(outputs)
