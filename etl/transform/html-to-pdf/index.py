import pdfkit
import os

def handler(inputs):
    html_file = inputs.get("html_file")
    
    if not html_file or not os.path.exists(html_file):
        raise ValueError("Invalid or missing HTML file.")

    output_pdf = html_file.replace(".html", ".pdf")

    try:
        pdfkit.from_file(html_file, output_pdf)
    except Exception as e:
        raise RuntimeError(f"Failed to convert HTML to PDF: {str(e)}")
    
    outputs = {"pdf_file": output_pdf}
    return outputs

# Example function call (Commented Out)
# inputs = {"html_file": "example.html"}
# print(handler(inputs))
