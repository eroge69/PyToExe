import fitz  # PyMuPDF
import os
import shutil
import zipfile

input_pdf = 'yourfile.pdf'  # You can later make this an argument
output_folder = 'output_pages'
zip_filename = 'output_pages.zip'

# Delete output folder if it exists
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)

# Create output folder
os.makedirs(output_folder, exist_ok=True)

# Open the big PDF
doc = fitz.open(input_pdf)

for page_number in range(len(doc)):
    page = doc.load_page(page_number)  # Load each page
    full_text = page.get_text()
    lines = full_text.splitlines()

    customer_name = ""
    date_string = ""

    for i, line in enumerate(lines):
        line = line.strip()

        # Extract Date String (after Serial No.)
        if "Serial No." in line:
            next_line = lines[i+1].strip() if i+1 < len(lines) else ''
            next_next_line = lines[i+2].strip() if i+2 < len(lines) else ''

            if next_line == ":":
                date_string = next_next_line
            else:
                date_string = next_line

        # Extract Customer Name (after Date :)
        if "Date" in line:
            next_line = lines[i+1].strip() if i+1 < len(lines) else ''
            next_next_line = lines[i+2].strip() if i+2 < len(lines) else ''

            if next_line == ":":
                customer_name = next_next_line
            else:
                customer_name = next_line

    if customer_name and date_string:
        # Clean filename
        filename = f"{customer_name} - {date_string}.pdf"
        safe_filename = "".join(c for c in filename if c.isalnum() or c in " -().").rstrip()

        # Create new PDF with just this page
        new_doc = fitz.open()  # New empty PDF
        new_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)
        
        output_path = os.path.join(output_folder, safe_filename)
        new_doc.save(output_path)
        new_doc.close()

        print(f"Saved: {safe_filename}")

    else:
        print(f"Failed to extract info on page {page_number + 1}")

doc.close()

# Create a ZIP file of all output PDFs
print("Zipping the output folder...")

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, output_folder)
            zipf.write(file_path, arcname)

print(f"✅ All done! Zipped file created: {zip_filename}")