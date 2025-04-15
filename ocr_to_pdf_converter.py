import os
from pdf2image import convert_from_path
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Optional: Specify the tesseract executable path (especially on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Define directories
input_folder = 'answer_sheet'
output_folder = 'extracted_pdfs'

# Create output folder if not exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def ocr_pdf_to_text(pdf_path):
    """
    Converts each page of a scanned PDF to text using OCR.
    Returns a string with all extracted text.
    """
    print(f"Processing {pdf_path}")
    # Convert PDF pages to images
    pages = convert_from_path(pdf_path, dpi=300)
    extracted_text = ""
    for i, page in enumerate(pages):
        print(f"  OCR processing page {i+1}")
        # Run OCR on this page image
        text = pytesseract.image_to_string(page)
        extracted_text += f"\n\n--- Page {i+1} ---\n{text}"
    return extracted_text

def create_text_pdf(text, output_pdf_path):
    """
    Generates a PDF with the given text using ReportLab.
    """
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    width, height = letter

    # Set initial text position near the top of the page with margin
    margin = 40
    x_text = margin
    y_text = height - margin

    # Create a text object
    text_object = c.beginText(x_text, y_text)
    text_object.setFont("Helvetica", 10)
    
    # Wrap text lines using splitlines()
    for line in text.splitlines():
        # If the text reaches the bottom, add a new page
        if y_text <= margin:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(x_text, height - margin)
            y_text = height - margin
            text_object.setFont("Helvetica", 10)
        text_object.textLine(line)
        y_text -= 12  # Decrease y position (line spacing)
    
    c.drawText(text_object)
    c.save()

# Main loop: Process each PDF in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith('.pdf'):
        full_input_path = os.path.join(input_folder, filename)
        # Extract text using OCR
        extracted_text = ocr_pdf_to_text(full_input_path)
        
        # Define output PDF path
        output_pdf_name = os.path.splitext(filename)[0] + "_ocr.pdf"
        full_output_path = os.path.join(output_folder, output_pdf_name)
        
        # Create PDF with the extracted text
        create_text_pdf(extracted_text, full_output_path)
        print(f"Saved OCR output to {full_output_path}")
