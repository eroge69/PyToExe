# How to run: C:\Users\Saurabh.Agashe\AppData\Local\Programs\Python\Python313\python.exe flatten_pdfs_recursive.py "D:\VS_Projects\repos\PdfSigner\input" "D:\VS_Projects\repos\PdfSigner\output"

# It goes recursively in source folder and creates exactly same structure in destination folder and converts all pdf with invalid signature
# error to image pdf

import os
import fitz  # PyMuPDF
from PIL import Image
import io
import argparse

def flatten_pdf(input_path, output_path):
    pdf_document = fitz.open(input_path)
    pdf_writer = fitz.open()

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=100)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=75)
        img_byte_arr = img_byte_arr.getvalue()

        img_rect = fitz.Rect(0, 0, pix.width, pix.height)
        new_page = pdf_writer.new_page(width=pix.width, height=pix.height)
        new_page.insert_image(img_rect, stream=img_byte_arr)

    pdf_writer.save(output_path)
    pdf_writer.close()
    pdf_document.close()

def process_pdfs(input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                input_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                flatten_pdf(input_path, output_path)
                print(f"Processed and saved: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flatten PDFs recursively and preserve folder structure.")
    parser.add_argument("input_directory", help="Path to the master input directory containing PDFs.")
    parser.add_argument("output_directory", help="Path to the master output directory to save flattened PDFs.")
    args = parser.parse_args()

    process_pdfs(args.input_directory, args.output_directory)
