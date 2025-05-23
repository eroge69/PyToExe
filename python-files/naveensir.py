import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cv2
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)

def main():
    print("KEESARA - PDF and Image to Text Converter")
    print("1. Convert PDF")
    print("2. Convert Image")
    choice = input("Enter choice (1/2): ")

    file_path = input("Enter file path: ")

    if not os.path.exists(file_path):
        print("File not found!")
        return

    if choice == '1':
        text = extract_text_from_pdf(file_path)
    elif choice == '2':
        text = extract_text_from_image(file_path)
    else:
        print("Invalid choice.")
        return

    output_file = "output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\n✅ Text saved to {output_file}")

if __name__ == "__main__":
    main()
