import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import pandas as pd
import re
import os

def extract_claim_data(pdf_path):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        text = ''.join(page.extract_text() or '' for page in pdf.pages)

    claims = text.split("__________________________________________________________________________________________________________________")

    for claim in claims:
        if "NAME" not in claim:
            continue
        try:
            name = re.search(r'NAME\s+([A-Z ,]+)', claim)
            hic = re.search(r'HIC\s+(\d+)', claim)
            acnt = re.search(r'ACNT\s+(\d+)', claim)
            icn = re.search(r'ICN\s+(\d+)', claim)
            billed = re.search(r'CLAIM TOTALS\s+([\d\.]+)', claim)
            rc_amt = re.search(r'CO-23\s+([\d\.]+)', claim)
            prov_pd = re.search(r'CO-23\s+[\d\.]+\s+([\d\.]+)', claim)
            net = re.search(r'NET\s+([\d\.]+)', claim)
            status = re.search(r'STATUS CODE\s+(\d)', claim)

            record = {
                "File": os.path.basename(pdf_path),
                "Name": name.group(1).strip() if name else None,
                "HIC": hic.group(1) if hic else None,
                "ACNT": acnt.group(1) if acnt else None,
                "ICN": icn.group(1) if icn else None,
                "Billed": billed.group(1) if billed else None,
                "RC-AMT": rc_amt.group(1) if rc_amt else None,
                "Prov PD": prov_pd.group(1) if prov_pd else None,
                "Net": net.group(1) if net else None,
                "Status Code": status.group(1) if status else None
            }

            records.append(record)
        except Exception as e:
            print(f"Error processing claim: {e}")
    return records


def select_pdfs():
    files = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
    if files:
        all_data = []
        for f in files:
            all_data.extend(extract_claim_data(f))
        if all_data:
            df = pd.DataFrame(all_data)
            output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
            if output_path:
                df.to_excel(output_path, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{output_path}")
        else:
            messagebox.showwarning("No Data", "No claims found in selected PDFs.")

# Build GUI
root = tk.Tk()
root.title("PDF Claims Extractor")

tk.Label(root, text="PDF Claims to Excel Converter", font=('Helvetica', 14, 'bold')).pack(pady=10)
tk.Button(root, text="Select PDF Files and Export", command=select_pdfs, width=30, height=2).pack(pady=20)

root.mainloop()