import os
import fitz  # PyMuPDF
import time
import threading
from PIL import Image, ImageOps
from tkinter import Tk, Label, Button, filedialog, StringVar, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DPI = 300
BLEED_MM = 3
BLEED_PX = int(BLEED_MM / 25.4 * DPI)

class PDFProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder

    def add_mirror_bleed_pdf(self, pdf_path, output_path):
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()

        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=DPI)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Tambahkan bleed mirror
            bleed_img = ImageOps.expand(img, border=BLEED_PX, fill=None)
            bleed_img.paste(ImageOps.mirror(img.crop((0, 0, BLEED_PX, img.height))), (0, BLEED_PX))
            bleed_img.paste(ImageOps.mirror(img.crop((img.width - BLEED_PX, 0, img.width, img.height))), (BLEED_PX + img.width, BLEED_PX))
            bleed_img.paste(ImageOps.flip(img.crop((0, 0, img.width, BLEED_PX))), (BLEED_PX, 0))
            bleed_img.paste(ImageOps.flip(img.crop((0, img.height - BLEED_PX, img.width, img.height))), (BLEED_PX, BLEED_PX + img.height))

            # Simpan jadi PDF halaman
            temp_path = os.path.join(self.output_folder, f"_temp_page_{i}.pdf")
            bleed_img.save(temp_path, "PDF", resolution=DPI)
            new_page = fitz.open(temp_path)
            new_doc.insert_pdf(new_page)
            os.remove(temp_path)

        new_doc.save(output_path)
        new_doc.close()
        doc.close()

class FolderWatcher(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.lower().endswith('.pdf'):
            return
        filename = os.path.basename(event.src_path)
        output_path = os.path.join(self.processor.output_folder, filename)
        try:
            self.processor.add_mirror_bleed_pdf(event.src_path, output_path)
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"Error: {e}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hot Folder PDF - Mirror Bleed 3mm")

        self.input_folder = StringVar()
        self.output_folder = StringVar()

        Label(root, text="Input Folder:").grid(row=0, column=0, sticky="e")
        Label(root, textvariable=self.input_folder).grid(row=0, column=1)
        Button(root, text="Browse", command=self.select_input).grid(row=0, column=2)

        Label(root, text="Output Folder:").grid(row=1, column=0, sticky="e")
        Label(root, textvariable=self.output_folder).grid(row=1, column=1)
        Button(root, text="Browse", command=self.select_output).grid(row=1, column=2)

        self.status_label = Label(root, text="Status: Idle")
        self.status_label.grid(row=3, column=0, columnspan=3)

        self.start_button = Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.grid(row=4, column=0, columnspan=3)

    def select_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def start_monitoring(self):
        if not self.input_folder.get() or not self.output_folder.get():
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        processor = PDFProcessor(self.input_folder.get(), self.output_folder.get())
        event_handler = FolderWatcher(processor)
        observer = Observer()
        observer.schedule(event_handler, self.input_folder.get(), recursive=False)
        observer.start()

        self.status_label.config(text="Status: Monitoring...")

        def monitor_thread():
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        threading.Thread(target=monitor_thread, daemon=True).start()
        self.start_button.config(state='disabled')

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
