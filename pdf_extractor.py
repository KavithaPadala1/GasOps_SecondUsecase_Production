
import base64
import os
import pdfplumber # type: ignore
from pdf2image import convert_from_path  # type: ignore
import pytesseract  # type: ignore

def save_pdf_from_binary(binary_data, output_path):
    """
    Saves binary PDF data to a file.
    :param binary_data: bytes or base64-encoded string representing the PDF
    :param output_path: path to save the PDF file
    :return: output_path if successful, else None
    """
    # If the data is base64-encoded, decode it
    if isinstance(binary_data, str):
        try:
            binary_data = base64.b64decode(binary_data)
        except Exception:
            pass  # Assume it's already bytes if decoding fails
    try:

        with open(output_path, 'wb') as f:
            f.write(binary_data)
        return output_path
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return None

# Example usage:
# save_pdf_from_binary(binary_string, 'output.pdf')



# Function to extract text from a PDF file using pdfplumber
import sys
def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file using pdfplumber. If no text is found, uses OCR (pytesseract).
    :param pdf_path: Path to the PDF file
    :return: Extracted text as a string, or None if error
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or '' for page in pdf.pages)
        if text.strip():
            print(f"Printing extracted text: {text}")
            return text
        else:
            print("No text found with pdfplumber, attempting OCR...")
    except Exception as e:
        print(f"Error extracting text from PDF with pdfplumber: {e}")

    # OCR fallback
    # try:
    #     if sys.platform.startswith("win"):
    #         poppler_path = r"C:\\Program Files\\poppler-24.08.0\\Library\\bin"
    #         images = convert_from_path(pdf_path, poppler_path=poppler_path)
    #     else:
    #         images = convert_from_path(pdf_path)
    #     ocr_text = []
    #     for i, image in enumerate(images):
    #         page_text = pytesseract.image_to_string(image)
    #         ocr_text.append(page_text)
    #     full_ocr_text = "\n".join(ocr_text)
    #     print(f"Printing OCR extracted text: {full_ocr_text}")
    #     return full_ocr_text
    # except Exception as e:
    #     print(f"Error extracting text from PDF with OCR: {e}")
    #     return None
    
    
    # OCR fallback
    try:
        # No need for poppler_path when running in Docker with poppler-utils installed
        images = convert_from_path(pdf_path)

        ocr_text = []
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            ocr_text.append(page_text)

        full_ocr_text = "\n".join(ocr_text)

        print(f"Printing OCR extracted text: {full_ocr_text}")
        return full_ocr_text

    except Exception as e:
        print(f"Error extracting text from PDF with OCR: {e}")
        return None


# Function to save extracted text to a file
def save_text_to_file(text, output_path):
    """
    Saves extracted text to a file.
    :param text: The text to save
    :param output_path: Path to save the text file
    :return: output_path if successful, else None
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error saving text: {e}")
        return None


