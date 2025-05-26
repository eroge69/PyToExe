
import sys
import os
from pdf2image import convert_from_path
from fpdf import FPDF

def pdf_to_images_and_back(pdf_path):
    if not pdf_path.lower().endswith(".pdf"):
        print("Not a PDF file.")
        return

    print(f"Processing: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)

    output_path = pdf_path.replace(".pdf", "_image.pdf")
    pdf = FPDF(unit="pt", format=[img.width, img.height])

    for img in images:
        pdf.add_page()
        img_path = "temp_page.jpg"
        img.save(img_path, "JPEG")
        pdf.image(img_path, 0, 0)
        os.remove(img_path)

    pdf.output(output_path, "F")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            pdf_to_images_and_back(path)
    else:
        print("Drag and drop a PDF file onto this tool.")
