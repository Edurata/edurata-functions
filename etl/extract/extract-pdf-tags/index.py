import os
import PyPDF2
import re
import pandas as pd
import json

def handler(inputs):
    folder_path = inputs["folder_path"]
    extracted_data = []
    example_file_written = False

    # Define regex patterns
    laketyre_url_pattern = r"https://laketyre\.de/product/(\d+)"  # Match Laketyre URLs with at least two digits in the product number
    filename_rechnungsnr_pattern = r"Einnahme_(\d+)"  # Extract Rechnungsnr from filename after "Einnahme_"

    print(f"Starting scan of folder: {folder_path}")
    
    # Walk through all subdirectories and files in the folder path
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                print(f"Processing PDF file: {pdf_path}")

                # Extract Rechnungsnr from filename
                rechnungsnr_match = re.search(filename_rechnungsnr_pattern, filename)
                rechnungsnr = rechnungsnr_match.group(1) if rechnungsnr_match else None
                print(f"Extracted Rechnungsnr from filename: {rechnungsnr}")

                # Extract text from the PDF
                pdf_text = ""
                try:
                    with open(pdf_path, "rb") as file:
                        reader = PyPDF2.PdfReader(file)
                        for page in reader.pages:
                            pdf_text += page.extract_text() or ""
                except Exception as e:
                    print(f"Error reading {pdf_path}: {e}")
                    continue

                print(f"Extracted text from {pdf_path}")

                # Find all Laketyre URLs in the PDF content
                laketyre_urls = []
                for match in re.finditer(laketyre_url_pattern, pdf_text):
                    product_number = match.group(1)  # Extract the numeric part of the URL
                    full_url = f"https://laketyre.de/product/{product_number}"
                    laketyre_urls.append(full_url)
                print(f"Found Laketyre URLs: {laketyre_urls}")

                # Store the extracted data
                data = {
                    "file": pdf_path,
                    "Rechnungsnr": rechnungsnr,
                    "Laketyre URLs": laketyre_urls
                }
                
                extracted_data.append(data)

                # Write the content of the first processed file to an example file
                if not example_file_written:
                    with open("example_file_output.txt", "w") as example_file:
                        example_file.write(f"Example content from: {pdf_path}\n\n")
                        example_file.write(pdf_text)  # Write entire text content of the first PDF
                        example_file.write("\n\nExtracted Data:\n\n")
                        example_file.write(f"Rechnungsnr: {data['Rechnungsnr']}\n")
                        example_file.write("Laketyre URLs:\n")
                        for url in data["Laketyre URLs"]:
                            example_file.write(f"{url}\n")
                    print(f"Example output written to 'example_file_output.txt' for {pdf_path}")
                    example_file_written = True  # Mark that the example file has been written

    print("Processing complete.")
    
    # Save the results to an Excel file
    df = pd.DataFrame(extracted_data)
    df.to_excel("results_output.xlsx", index=False)
    print("Results have been written to 'results_output.xlsx'")

    # Save the results to a JSON file
    with open("results_output.json", "w") as result_file:
        json.dump(extracted_data, result_file, indent=4)
    print("Results have been written to 'results_output.json'")

    # Return the results
    outputs = {
        "extracted_data": extracted_data
    }
    return outputs

# Example call to the handler function
inputs = {
    "folder_path": "belege"
}
print(handler(inputs))
