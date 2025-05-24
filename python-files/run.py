# bom_dragdrop.py
import xlwt
import re
import sys
import os

def convert_txt_to_bom_format(txt_path, xls_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    part_lines = [line for line in lines if "Part" in line and line.strip().startswith(tuple("0123456789"))]

    bom_rows = []
    for line in part_lines:
        match = re.match(r"\s*(\d+)\s+Part\s+(.*)", line)
        if match:
            qty = int(match.group(1))
            part_number = match.group(2).strip()
            bom_rows.append((part_number, "", qty))

    wb = xlwt.Workbook()
    ws = wb.add_sheet('BOM')

    headers = ["Item", "Part Number", "Description", "Qty"]
    for col, header in enumerate(headers):
        ws.write(0, col, header)

    for idx, (part_number, desc, qty) in enumerate(bom_rows, start=1):
        ws.write(idx, 0, idx)
        ws.write(idx, 1, part_number)
        ws.write(idx, 2, desc)
        ws.write(idx, 3, qty)

    wb.save(xls_path)
    print(f"轉換完成：{xls_path}")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        for txt_path in sys.argv[1:]:
            if os.path.isfile(txt_path) and txt_path.lower().endswith('.txt'):
                base = os.path.splitext(txt_path)[0]
                xls_path = base + ".xls"
                convert_txt_to_bom_format(txt_path, xls_path)
    else:
        print("請拖拉 .txt 檔案到此程式上")
