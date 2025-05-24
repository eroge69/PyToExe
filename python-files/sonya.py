import tkinter as tk
from tkinter import filedialog
from docx import Document

def select_and_read_word_file():
    # Initialize tkinter root
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open file dialog to select a .docx file
    file_path = filedialog.askopenfilename(
        title="Select a Word document",
        filetypes=[("Word Documents", "*.docx")]
    )

    if not file_path:
        print("No file selected.")
        return

    try:
        # Load the document
        doc = Document(file_path)

        # Read and print all paragraphs
        print(f"\nContent of '{file_path}':\n")
        for para in doc.paragraphs:
            print(para.text)
    except Exception as e:
        print(f"Error reading the document: {e}")

if __name__ == "__main__":
    select_and_read_word_file()
