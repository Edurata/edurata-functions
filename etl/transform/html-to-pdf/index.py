from xhtml2pdf import pisa
import os

def handler(inputs):
    html_file = inputs.get("html_file")
    
    if not html_file or not os.path.exists(html_file):
        raise ValueError("Invalid or missing HTML file.")

    output_pdf = html_file.replace(".html", ".pdf")

    try:
        with open(html_file, "r", encoding="utf-8") as html_source:
            with open(output_pdf, "wb") as pdf_output:
                pisa_status = pisa.CreatePDF(html_source, dest=pdf_output)
                if pisa_status.err:
                    raise RuntimeError("Failed to generate PDF")
    except Exception as e:
        raise RuntimeError(f"PDF generation error: {str(e)}")
    
    return {"pdf_file": output_pdf}

# Example function call (Commented Out)
# inputs = {"html_file": "example.html"}
# print(handler(inputs))
