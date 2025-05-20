import pandas as pd
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageTk
import os
from datetime import datetime
import qrcode
import io


class StoneAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stone CSV Aggregator with PDF Export")

        self.files = []

        input_frame = tk.Frame(root)
        input_frame.pack(pady=5)

        srno_label = tk.Label(input_frame, text="Sr.no:", font=("Arial", 12))
        srno_label.pack(side=tk.LEFT, padx=(0,5))

        self.srno_entry = tk.Entry(input_frame, width=10, font=("Arial", 12))
        self.srno_entry.pack(side=tk.LEFT, padx=(0,15))
        self.srno_entry.insert(0, "1")

        top_label = tk.Label(input_frame, text="TOP:", font=("Arial", 12))
        top_label.pack(side=tk.LEFT, padx=(0,5))

        self.top_entry = tk.Entry(input_frame, width=20, font=("Arial", 12))
        self.top_entry.pack(side=tk.LEFT, padx=(0,5))
        self.top_entry.insert(0, "")

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.select_btn = tk.Button(btn_frame, text="Select CSV Files", command=self.select_files)
        self.select_btn.grid(row=0, column=0, padx=5)
        self.process_btn = tk.Button(btn_frame, text="Process and Aggregate", command=self.process_files, state=tk.DISABLED)
        self.process_btn.grid(row=0, column=1, padx=5)
        self.pdf_btn = tk.Button(btn_frame, text="Export to PDF", command=self.export_pdf, state=tk.DISABLED)
        self.pdf_btn.grid(row=0, column=2, padx=5)
        self.clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_all)
        self.clear_btn.grid(row=0, column=3, padx=5)

        self.output_text = scrolledtext.ScrolledText(root, width=40, height=15, font=("Consolas", 12))
        self.output_text.pack(padx=0, pady=10)
        self.output_text.config(state=tk.NORMAL)

        self.qr_label = None
        self.qr_image = None
        self.qr_pil_image = None

        self.pdf_filename = "Stone_Aggregation_Output.pdf"

    def clear_all(self):
        self.srno_entry.delete(0, tk.END)
        self.srno_entry.insert(0, "")
        self.top_entry.delete(0, tk.END)

        self.files = []

        self.process_btn.config(state=tk.DISABLED)
        self.pdf_btn.config(state=tk.DISABLED)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

        if self.qr_label:
            self.qr_label.destroy()
            self.qr_label = None
            self.qr_image = None
            self.qr_pil_image = None

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select CSV files",
            filetypes=[("CSV Files", "*.csv;*.CSV")]
        )
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)

        if self.qr_label:
            self.qr_label.destroy()
            self.qr_label = None
            self.qr_image = None
            self.qr_pil_image = None

        if file_paths:
            self.files = list(file_paths)
            self.process_btn.config(state=tk.NORMAL)
            self.pdf_btn.config(state=tk.DISABLED)
            self.output_text.insert(tk.END, f"Selected {len(self.files)} files:\n")
            for f in self.files:
                self.output_text.insert(tk.END, f" - {f}\n")
        else:
            self.files = []
            self.process_btn.config(state=tk.DISABLED)
            self.pdf_btn.config(state=tk.DISABLED)
            self.output_text.insert(tk.END, "No files selected.\n")

        self.output_text.config(state=tk.DISABLED)

    def process_files(self):
        if not self.files:
            messagebox.showwarning("No files", "Please select CSV files first.")
            return

        total_rw_max_sum = 0.0
        total_mk = 0
        total_pw = 0.0
        all_mk_count = 0
        total_all_mk = 0
        total_pcs = len(self.files)
        first_valid_user_name = None
        first_valid_pc_name = None

        try:
            for file_path in self.files:
                df = pd.read_csv(file_path)
                df = df.dropna(how='all')
                df.columns = df.columns.str.strip()

                if 'R.w' in df.columns and not df['R.w'].dropna().empty:
                    max_rw = df['R.w'].max()
                else:
                    max_rw = 0.0

                mk_count = df.loc[df['Pw'].notnull(), 'Mk.Wt'].count() if 'Mk.Wt' in df.columns else 0
                all_mk_count = df['Mk.Wt'].count() if 'Mk.Wt' in df.columns else 0
                pw_sum = df['Pw'].sum() if 'Pw' in df.columns else 0.0

                if first_valid_user_name is None and 'User Name' in df.columns:
                    user_series = df['User Name'].dropna()
                    if not user_series.empty:
                        first_valid_user_name = user_series.iloc[0]

                if first_valid_pc_name is None and 'Pc Name' in df.columns:
                    pc_series = df['Pc Name'].dropna()
                    if not pc_series.empty:
                        first_valid_pc_name = pc_series.iloc[0]

                total_rw_max_sum += max_rw
                total_mk += mk_count
                total_pw += pw_sum
                total_all_mk += all_mk_count

            try:
                Sr_no = int(self.srno_entry.get())
            except ValueError:
                Sr_no = 1

            TOP = self.top_entry.get().strip()
            if not TOP:
                TOP = "-"

            TOP = TOP.upper()
            pc_name_upper = first_valid_pc_name.upper() if first_valid_pc_name else ""

            first_file_name = os.path.basename(self.files[0])
            CUT = first_file_name.split('-')[0]
            now = datetime.now()
            D_T = now.strftime("%d/%m/%y")
            RJ = total_all_mk - total_mk
            TOTAL = total_all_mk

            user_name_line = f"User Name\t{first_valid_user_name}" if first_valid_user_name else ""

            output_lines = [
                f"CUT\t{CUT}\tSr.no\t{Sr_no}",
                f"PCS\t{total_pcs}\tMK\t{total_mk}",
                f"RW\t{round(total_rw_max_sum,3)}\tRJ\t{RJ}",
                f"PW\t{round(total_pw,3)}\tTOTAL\t{TOTAL}",
                f"TOP.\t{TOP}\tP.C\t{pc_name_upper}",
                f"D & T\t{D_T}",
            ]

            if user_name_line:
                output_lines.append(user_name_line)

            qr_data = f"{CUT},{Sr_no},{total_pcs},{total_mk},{total_rw_max_sum},{total_pw},{CUT},{TOTAL},{TOP},{pc_name_upper},{D_T},{user_name_line}" 

            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            qr_image = Image.open(buf)
            self.qr_image = ImageTk.PhotoImage(qr_image)
            self.qr_pil_image = qr_image.convert("RGB")  # Ensure RGB mode

            if self.qr_label is None:
                self.qr_label = tk.Label(self.root, image=self.qr_image, borderwidth=2, relief="sunken")
                self.qr_label.pack(pady=10)
            else:
                self.qr_label.configure(image=self.qr_image)
                self.qr_label.image = self.qr_image

            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, '\n'.join(output_lines))
            self.pdf_btn.config(state=tk.NORMAL)
            self.output_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error processing files: {e}")

    def export_pdf(self):
        output = self.output_text.get("1.0", tk.END).strip()
        if not output:
            messagebox.showwarning("No Output", "No data to export to PDF.")
            return

        try:
            pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
            pdfmetrics.registerFont(TTFont('Calibri-Bold', 'calibrib.ttf'))

            page_width = 144   # 2 inch width
            page_height = 72   # 1 inch height
            c = canvas.Canvas(self.pdf_filename, pagesize=(page_width, page_height))

            margin_x = 1
            margin_y = 1
            y_start = page_height - margin_y
            line_height = 7  # smaller line height for fit
            cell_padding = 1

            # Removed gap between QR and data:
            gap_between_qr_and_data = 0

            lines = output.splitlines()
            rows = [line.split('\t') for line in lines]

            max_cols = max(len(row) for row in rows)

            font_name = "Calibri"
            header_font_size = 5
            text_font_size = 3  # Reduced font size for table text for clarity

            c.setFont(font_name, text_font_size)

            qr_box_size = 60  # Larger QR box for better clarity

            reserved_for_qr = qr_box_size + gap_between_qr_and_data

            # Calculate max widths of columns
            col_widths = [0] * max_cols
            for row_index, row in enumerate(rows):
                if row_index == 0:
                    font_used = "Calibri-Bold"
                    size_used = header_font_size
                else:
                    font_used = font_name
                    size_used = text_font_size

                c.setFont(font_used, size_used)
                for i, cell in enumerate(row):
                    max_w_allowed = page_width - 2 * margin_x
                    if row_index == 0:
                        max_w_allowed -= reserved_for_qr
                    width = c.stringWidth(cell, font_used, size_used)
                    if width > col_widths[i]:
                        col_widths[i] = width
                c.setFont(font_name, text_font_size)

            col_widths = [w + 2*cell_padding for w in col_widths]

            total_w_first_row = sum(col_widths)
            max_w_first_row = page_width - 2 * margin_x - reserved_for_qr
            if total_w_first_row > max_w_first_row:
                scale = max_w_first_row / total_w_first_row
                col_widths = [w * scale for w in col_widths]

            total_w_others = sum(col_widths)
            max_w_others = page_width - 2 * margin_x
            if total_w_others > max_w_others:
                scale = max_w_others / total_w_others
                col_widths = [w * scale for w in col_widths]

            y = y_start

            # Draw first row (header)
            if len(rows) > 0:
                first_row = rows[0]
                x = margin_x
                row_height = line_height
                c.setFont("Calibri-Bold", header_font_size)
                for i in range(max_cols):
                    cell_text = first_row[i] if i < len(first_row) else ""
                    cell_w = col_widths[i]
                    c.rect(x, y - row_height, cell_w, row_height, stroke=1, fill=0)
                    text_w = c.stringWidth(cell_text, "Calibri-Bold", header_font_size)
                    text_x = x + (cell_w - text_w) / 2 if cell_w > 0 else x
                    text_y = y - row_height + (row_height - header_font_size) / 2
                    if cell_w > 0:
                        c.drawString(text_x, text_y, cell_text)
                    x += cell_w

                y -= row_height

                # Draw white background for QR code
                if self.qr_pil_image:
                    qr_x = margin_x + sum(col_widths) + gap_between_qr_and_data
                    qr_y = y - qr_box_size + (row_height - qr_box_size) / 2
                    if qr_y < margin_y:
                        qr_y = margin_y
                    c.setFillColorRGB(1,1,1)
                    c.rect(qr_x - 1, qr_y - 1, qr_box_size + 2, qr_box_size + 2, fill=1, stroke=0)
                    c.setFillColorRGB(0,0,0)

                    try:
                        qr_img_resized = self.qr_pil_image.resize((qr_box_size, qr_box_size), Image.LANCZOS)
                        qr_img_buf = io.BytesIO()
                        qr_img_resized.save(qr_img_buf, format='PNG')
                        qr_img_buf.seek(0)
                        qr_img_reader = ImageReader(qr_img_buf)
                        c.drawImage(qr_img_reader, qr_x, qr_y, width=qr_box_size, height=qr_box_size)
                    except Exception as e:
                        messagebox.showerror("QR Code Error", f"Failed to draw QR code in PDF: {e}")

            # Draw remaining rows (small font)
            c.setFont(font_name, text_font_size)
            for row in rows[1:]:
                x = margin_x
                row_height = line_height
                for i in range(max_cols):
                    cell_text = row[i] if i < len(row) else ""
                    cell_w = col_widths[i]
                    c.rect(x, y - row_height, cell_w, row_height, stroke=1, fill=0)
                    text_w = c.stringWidth(cell_text, font_name, text_font_size)
                    text_x = x + (cell_w - text_w) / 2 if cell_w > 0 else x
                    text_y = y - row_height + (row_height - text_font_size) / 2
                    if cell_w > 0:
                        c.drawString(text_x, text_y, cell_text)
                    x += cell_w
                y -= row_height
                if y - row_height < margin_y:
                    break

            c.save()
            messagebox.showinfo("PDF Exported", f"Output successfully exported to:\n{os.path.abspath(self.pdf_filename)}")

        except Exception as e:
            messagebox.showerror("PDF Export Error", f"Failed to export PDF: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StoneAggregatorApp(root)
    root.mainloop()

