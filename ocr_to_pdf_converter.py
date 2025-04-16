import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from google.cloud import vision
from google.oauth2 import service_account

# ---------- CONFIGURATION ----------
input_folder = 'answer_sheet'
output_folder = 'extracted_pdfs'
google_key_path = 'google-credentials.json'
dpi = 300

# ---------- GOOGLE VISION SETUP ----------
credentials = service_account.Credentials.from_service_account_file(google_key_path)
client = vision.ImageAnnotatorClient(credentials=credentials)

# ---------- OCR FUNCTION ----------
def google_ocr_from_cv2_image(cv2_image):
    is_success, buffer = cv2.imencode(".png", cv2_image)
    byte_image = buffer.tobytes()
    image = vision.Image(content=byte_image)
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text if response.full_text_annotation.text else "[No text found]"

# ---------- MAIN PROCESSING FUNCTION ----------
def process_all_pdfs():
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            input_pdf_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_pdf_path = os.path.join(output_folder, base_name + "_ocr.pdf")

            print(f"📄 Processing: {filename}")
            pages = convert_from_path(input_pdf_path, dpi=dpi)

            pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=letter)
            width, height = letter

            for idx, page in enumerate(pages):
                print(f"🔍 OCR page {idx + 1} of {filename}...")
                
                # Convert PIL image to OpenCV
                cv_image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 3)
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                extracted_text = google_ocr_from_cv2_image(gray)

                text_obj = pdf_canvas.beginText(40, height - 40)
                text_obj.setFont("Helvetica", 10)
                text_obj.textLine(f"--- Page {idx + 1} ---")
                for line in extracted_text.split('\n'):
                    if text_obj.getY() < 40:
                        pdf_canvas.drawText(text_obj)
                        pdf_canvas.showPage()
                        text_obj = pdf_canvas.beginText(40, height - 40)
                        text_obj.setFont("Helvetica", 10)
                    text_obj.textLine(line)

                pdf_canvas.drawText(text_obj)
                pdf_canvas.showPage()

            pdf_canvas.save()
            print(f"✅ Saved: {output_pdf_path}\n")

# ---------- RUN ----------
if __name__ == "__main__":
    process_all_pdfs()
