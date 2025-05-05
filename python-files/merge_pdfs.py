
from PyPDF2 import PdfMerger
import sys
import os
import subprocess

def merge_pdfs(pdf_paths, output_path):
    merger = PdfMerger()
    for pdf in pdf_paths:
        if pdf.lower().endswith('.pdf') and os.path.exists(pdf):
            merger.append(pdf)
    merger.write(output_path)
    merger.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_files = sys.argv[1:]
        first_pdf_dir = os.path.dirname(pdf_files[0])
        output_file = os.path.join(first_pdf_dir, "merged.pdf")
        merge_pdfs(pdf_files, output_file)
        subprocess.run(["start", output_file], shell=True)
    else:
        print("No PDF files provided.")
