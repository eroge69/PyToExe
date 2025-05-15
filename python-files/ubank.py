import os
import re
import pandas as pd
from PyPDF2 import PdfReader

folder_path = r"C:\Users\Control 2\Desktop\PDF\Ubank"
output_excel = os.path.join(folder_path, "GEPCO_Record_And_Amount.xlsx")

data = []

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(folder_path, filename)
        print(f"\n📄 Reading: {filename}")

        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

            print("📝 Extracting from preview:")
            print(text[:500])

            # Count lines that begin with a serial number
            record_lines = re.findall(r"^\s*\d+\s+\d{2}/\d{2}/\d{4}", text, re.MULTILINE)
            record_count = len(record_lines)

            # Extract total amount at the end, e.g. "6,982.00Total"
            amount_match = re.search(r"([\d,]+\.\d{2})\s*Total", text, re.IGNORECASE)
            amount_paid = amount_match.group(1) if amount_match else "Not Found"

            data.append({
                "Filename": filename,
                "No of Records": record_count,
                "Amount Paid": amount_paid
            })

            print(f"✅ Found → Records: {record_count}, Amount: {amount_paid}")

        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")
            data.append({
                "Filename": filename,
                "No of Records": "Error",
                "Amount Paid": "Error"
            })

# Save to Excel
df = pd.DataFrame(data)
df.to_excel(output_excel, index=False)

print(f"\n✅ All done! Excel file saved to:\n{output_excel}")
