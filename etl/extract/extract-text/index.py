import os
import fitz  # PyMuPDF for PDF handling
import docx  # for handling Word documents
from bs4 import BeautifulSoup  # for HTML parsing

def extract_text_from_pdf(file_path):
    try:
        text = ""
        with fitz.open(file_path) as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
        return text
    except Exception:
        return None

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception:
        return None

def extract_text_from_html(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            return soup.get_text()
    except Exception:
        return None

def extract_text_from_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception:
        return None

def handler(inputs):
    input_file = inputs["input_file"]

    extractors = [
        extract_text_from_txt,
        extract_text_from_pdf,
        extract_text_from_docx,
        extract_text_from_html
    ]

    for extractor in extractors:
        extracted_text = extractor(input_file)
        if extracted_text:
            return {"extracted_text": extracted_text}

    raise ValueError("Could not extract text: unsupported or unreadable file format")

# Sample function call (commented out):
# inputs = {"input_file": "path_to_your_file"} 
# print(handler(inputs))
