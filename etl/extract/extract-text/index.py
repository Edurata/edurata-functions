import os
import fitz  # PyMuPDF for PDF handling
import docx  # for handling Word documents
from bs4 import BeautifulSoup  # for HTML parsing

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        text = soup.get_text()
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def handler(inputs):
    input_file = inputs["input_file"]

    # Get file extension
    file_extension = os.path.splitext(input_file)[1].lower()

    if file_extension == ".pdf":
        extracted_text = extract_text_from_pdf(input_file)
    elif file_extension == ".docx":
        extracted_text = extract_text_from_docx(input_file)
    elif file_extension == ".html":
        extracted_text = extract_text_from_html(input_file)
    elif file_extension == ".txt":
        extracted_text = extract_text_from_txt(input_file)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    outputs = {
        "extracted_text": extracted_text
    }
    return outputs

# Sample function call (commented out):
# inputs = {"input_file": {"path": "path_to_your_file.pdf"}}
# print(handler(inputs))
