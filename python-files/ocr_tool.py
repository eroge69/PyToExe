import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image
import pytesseract
import fitz
from pdf2image import convert_from_path
import easyocr
import io
import os
import re
import threading
from google.cloud import vision
import whisper  # Use openai-whisper
from pydub import AudioSegment

# ====================== CONFIGURATION ======================
# Set paths
pytesseract.pytesseract.tesseract_cmd = r'E:\hari\softwer\py_l\Tesseract-OCR\tesseract.exe'
poppler_path = r'E:\hari\softwer\py_l\poppler-24.08.0\Library\bin'

# Configure FFmpeg
ffmpeg_path = r'E:\hari\softwer\py_l\ffmpeg-7.1.1\bin'
ffmpeg_exe = os.path.join(ffmpeg_path, 'ffmpeg.exe')
ffprobe_exe = os.path.join(ffmpeg_path, 'ffprobe.exe')

# Verify FFmpeg and FFprobe existence
print(f"Checking FFmpeg path: {ffmpeg_exe}")
print(f"Checking FFprobe path: {ffprobe_exe}")
if not os.path.isfile(ffmpeg_exe):
    raise FileNotFoundError(f"FFmpeg not found at {ffmpeg_exe}")
if not os.path.isfile(ffprobe_exe):
    raise FileNotFoundError(f"FFprobe not found at {ffprobe_exe}")

# Set environment variables for FFmpeg
os.environ['FFMPEG_PATH'] = ffmpeg_exe
os.environ['FFPROBE_PATH'] = ffprobe_exe
os.environ['PATH'] += os.pathsep + ffmpeg_path

# Configure pydub
AudioSegment.converter = ffmpeg_exe
AudioSegment.ffprobe = ffprobe_exe
print(f"Set AudioSegment.converter to: {AudioSegment.converter}")
print(f"Set AudioSegment.ffprobe to: {AudioSegment.ffprobe}")

# Whisper model selection (default)
WHISPER_MODEL = "base"  # Default model

# ====================== OCR FUNCTIONS ======================
def image_to_text(file_path, lang):
    try:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang=lang, config='--psm 4')
    except Exception as e:
        messagebox.showerror("Image OCR Error", str(e))
        return ""

def image_to_text_easyocr(file_path, lang):
    try:
        if lang == "guj":
            raise ValueError("EasyOCR doesn't support Gujarati.")
        reader = easyocr.Reader(lang.split('+'), gpu=False)
        result = reader.readtext(file_path, detail=0, paragraph=False)
        return '\n'.join(result)
    except Exception as e:
        messagebox.showerror("EasyOCR Error", str(e))
        return ""

def image_to_text_googlevision(file_path):
    try:
        client = vision.ImageAnnotatorClient()
        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        text = ""
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                block_text = ""
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        block_text += ''.join([symbol.text for symbol in word.symbols]) + ' '
                    block_text += '\n'
                text += block_text + '\n'
        return text.strip()
    except Exception as e:
        messagebox.showerror("Google Vision Error", str(e))
        return ""

# ====================== PDF FUNCTIONS ======================
def pdf_to_text_pymupdf(file_path, lang):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc, 1):
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img, lang=lang, config='--psm 4')
            text += f"--- Page {page_num} ---\n{page_text}\n"
    except Exception as e:
        messagebox.showerror("PyMuPDF Error", str(e))
    return text.strip()

def pdf_to_text_pdf2image(file_path, lang):
    text = ""
    try:
        images = convert_from_path(file_path, poppler_path=poppler_path)
        for page_num, img in enumerate(images, 1):
            page_text = pytesseract.image_to_string(img, lang=lang, config='--psm 4')
            text += f"--- Page {page_num} ---\n{page_text}\n"
    except Exception as e:
        messagebox.showerror("pdf2image Error", str(e))
    return text.strip()

def pdf_to_text_easyocr(file_path, lang):
    text = ""
    try:
        if lang == "guj":
            raise ValueError("EasyOCR doesn't support Gujarati.")
        images = convert_from_path(file_path, poppler_path=poppler_path)
        reader = easyocr.Reader(lang.split('+'), gpu=False)
        for page_num, img in enumerate(images, 1):
            img_path = 'temp_img.jpg'
            img.save(img_path)
            result = reader.readtext(img_path, detail=0, paragraph=False)
            page_text = '\n'.join(result)
            text += f"--- Page {page_num} ---\n{page_text}\n"
            os.remove(img_path)
    except Exception as e:
        messagebox.showerror("EasyOCR PDF Error", str(e))
    return text.strip()

def pdf_to_text_googlevision(file_path):
    text = ""
    try:
        client = vision.ImageAnnotatorClient()
        images = convert_from_path(file_path, poppler_path=poppler_path)
        for page_num, img in enumerate(images, 1):
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            image = vision.Image(content=buf.getvalue())
            response = client.document_text_detection(image=image)
            page_text = ""
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            page_text += ''.join([symbol.text for symbol in word.symbols]) + ' '
                        page_text += '\n'
            text += f"--- Page {page_num} ---\n{page_text}\n"
    except Exception as e:
        messagebox.showerror("Google Vision PDF Error", str(e))
    return text.strip()

# ====================== AUDIO FUNCTIONS ======================
def audio_to_text_whisper(file_path, lang, model_name):
    try:
        status_label.config(text="Preparing audio file...")
        audio = AudioSegment.from_file(file_path)
        wav_path = 'temp_audio.wav'
        audio.export(wav_path, format='wav')
        
        status_label.config(text="Loading Whisper model...")
        model = whisper.load_model(model_name)
        
        # Improved language mapping with fallback
        lang_map = {
            "eng": "en", 
            "guj": "gu",
            "hin": "hi",
            "en": "en",
            "hi": "hi",
            "gu": "gu"
        }
        
        # Get Whisper language code or None (for auto-detection)
        whisper_lang = lang_map.get(lang.split('+')[0], None)
        
        # For small models, force English if Gujarati isn't working well
        if model_name in ["tiny", "base", "small"] and lang == "guj":
            messagebox.showwarning(
                "Model Limitation", 
                f"Small models ({model_name}) have poor Gujarati support. Trying with English instead."
            )
            whisper_lang = "en"
        
        status_label.config(text=f"Transcribing audio...")
        result = model.transcribe(
            wav_path, 
            language=whisper_lang,
            task="transcribe",  # Force transcription (not translation)
            initial_prompt="Transcribe the following Gujarati audio:" if lang == "guj" else None
        )
        
        detected_lang = result.get("language", "unknown")
        if detected_lang != whisper_lang and whisper_lang is not None:
            messagebox.showwarning(
                "Language Mismatch", 
                f"Detected language: {detected_lang}, but requested: {whisper_lang}"
            )
        
        os.remove(wav_path)
        return result["text"].strip()
    except Exception as e:
        messagebox.showerror("Whisper Audio Error", str(e))
        return ""

# ====================== TEXT PROCESSING ======================
def clean_ocr_text(text, lang, strict_lines=False):
    try:
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        if lang in ["guj", "hin", "eng+guj", "eng+hin", "guj+hin", "hin+guj", "eng+guj+hin", "hin+eng+guj"]:
            text = re.sub(r'[।|]\s*', '। ', text)
        if strict_lines:
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
        else:
            text = re.sub(r'\n\s*\n{2,}', '\n\n', text).strip()
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip() and not line.startswith('--- Page')]
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text or "No readable text found."
    except Exception as e:
        messagebox.showerror("Text Cleaning Error", str(e))
        return text

# ====================== GUI FUNCTIONS ======================
def browse_file():
    file_types = {
        "All Supported": [("All Files", "*.pdf *.png *.jpg *.jpeg *.tiff *.mp3 *.wav *.m4a")],
        "PDF Only": [("PDF Files", "*.pdf")],
        "Images Only": [("Image Files", "*.png *.jpg *.jpeg *.tiff")],
        "Audio Only": [("Audio Files", "*.mp3 *.wav *.m4a")]
    }
    selected_type = file_type_var.get()
    path = filedialog.askopenfilename(filetypes=file_types[selected_type])
    if path:
        file_var.set(path)

def browse_credentials():
    path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if path:
        credentials_var.set(path)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
        messagebox.showinfo("Credentials Updated", "Google Cloud credentials set successfully.")

def save_output_file(text):
    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        initialfile="extracted_text.txt"
    )
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}")
            return False
    return False

raw_text = ""  # Store raw OCR/audio output for toggling

def toggle_raw_cleaned():
    current_text = output_text.get(1.0, tk.END).strip()
    if current_text and current_text != raw_text:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, raw_text)
        toggle_button.config(text="Show Cleaned")
    elif raw_text:
        cleaned_text = clean_ocr_text(raw_text, lang_var.get(), strict_lines=strict_lines_var.get())
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, cleaned_text)
        toggle_button.config(text="Show Raw")
    else:
        messagebox.showwarning("No Text", "No raw text available.")

def copy_text():
    text = output_text.get(1.0, tk.END).strip()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("Copied", "Text copied to clipboard!")
    else:
        messagebox.showwarning("No Text", "No text to copy.")

def extract_text():
    global raw_text
    file_path = file_var.get()
    lang = lang_var.get()
    method = method_var.get()
    model_name = whisper_model_var.get() if method == "Whisper" else WHISPER_MODEL

    if not file_path:
        messagebox.showwarning("Missing File", "Please select a file.")
        return
    if method == "Google Vision" and not credentials_var.get():
        messagebox.showwarning("Missing Credentials", "Please select Google Cloud credentials for Google Vision.")
        return

    extract_button.config(state="disabled")
    clean_button.config(state="disabled")
    toggle_button.config(state="disabled")
    copy_button.config(state="disabled")
    status_label.config(text="Extracting text, please wait...")
    progress_bar.start()

    def run_extraction():
        global raw_text
        text = ""
        try:
            if file_path.lower().endswith((".mp3", ".wav", ".m4a")):
                if method != "Whisper":
                    raise ValueError("Please select Whisper for audio files.")
                text = audio_to_text_whisper(file_path, lang, model_name)
            elif file_path.lower().endswith(".pdf"):
                if method == "Whisper":
                    raise ValueError("Whisper is only for audio files.")
                if method == "PyMuPDF":
                    text = pdf_to_text_pymupdf(file_path, lang)
                elif method == "pdf2image":
                    text = pdf_to_text_pdf2image(file_path, lang)
                elif method == "EasyOCR":
                    text = pdf_to_text_easyocr(file_path, lang)
                elif method == "Google Vision":
                    text = pdf_to_text_googlevision(file_path)
            else:  # Image files
                if method == "Whisper":
                    raise ValueError("Whisper is only for audio files.")
                if method == "EasyOCR":
                    text = image_to_text_easyocr(file_path, lang)
                elif method == "Google Vision":
                    text = image_to_text_googlevision(file_path)
                else:
                    text = image_to_text(file_path, lang)

            raw_text = text
            cleaned_text = clean_ocr_text(text, lang, strict_lines=strict_lines_var.get())
            root.after(0, lambda: update_ui_after_extraction(cleaned_text))

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Extraction Error", str(e)))
            root.after(0, lambda: reset_ui())

    def update_ui_after_extraction(text):
        progress_bar.stop()
        status_label.config(text="Ready")
        extract_button.config(state="normal")
        clean_button.config(state="normal")
        toggle_button.config(state="normal")
        copy_button.config(state="normal")
        if text.strip() and text != "No readable text found.":
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, text)
            toggle_button.config(text="Show Raw")
            if save_output_file(text):
                messagebox.showinfo("Success", "Text extracted and saved successfully!")
            else:
                messagebox.showinfo("Success", "Text extracted but not saved.")
        else:
            messagebox.showinfo("No Text", "No text could be extracted.")
        reset_ui()

    def reset_ui():
        progress_bar.stop()
        status_label.config(text="Ready")
        extract_button.config(state="normal")
        clean_button.config(state="normal")
        toggle_button.config(state="normal")
        copy_button.config(state="normal")

    threading.Thread(target=run_extraction, daemon=True).start()

def clean_displayed_text():
    text = output_text.get(1.0, tk.END).strip()
    lang = lang_var.get()
    if text:
        cleaned_text = clean_ocr_text(text, lang, strict_lines=strict_lines_var.get())
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, cleaned_text)
        messagebox.showinfo("Cleaned", "Text has been reformatted.")
    else:
        messagebox.showwarning("No Text", "No text to clean.")

def update_conditional_options(event=None):
    method = method_var.get()
    
    # Clear conditional frame
    for widget in conditional_frame.winfo_children():
        widget.destroy()
    
    if method == "Whisper":
        tk.Label(conditional_frame, text="Whisper Model:", font=("Segoe UI", 10), bg="#ffffff").pack(side="left")
        whisper_model_combo = ttk.Combobox(conditional_frame, textvariable=whisper_model_var, state="readonly", width=10)
        whisper_model_combo['values'] = ["tiny", "base", "small", "medium", "large"]
        whisper_model_combo.set(WHISPER_MODEL)
        whisper_model_combo.pack(side="left", padx=10)
    elif method == "Google Vision":
        tk.Label(conditional_frame, text="Credentials:", font=("Segoe UI", 10), bg="#ffffff").pack(side="left")
        tk.Entry(conditional_frame, textvariable=credentials_var, width=30, font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        cred_button = tk.Button(conditional_frame, text="Browse", command=browse_credentials, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"), relief="flat")
        cred_button.pack(side="left")
        cred_button.bind("<Enter>", lambda e: on_enter(cred_button, "#45a049"))
        cred_button.bind("<Leave>", lambda e: on_leave(cred_button, "#4CAF50"))
        create_tooltip(cred_button, "Select Google Cloud JSON credentials file")

def update_language_options(event=None):
    method = method_var.get()
    lang_map = {
        "EasyOCR": ["en", "hi", "ta", "bn", "ml", "kn", "mr", "or", "pa", "te"],
        "Google Vision": ["eng", "hin", "guj"],
        "Whisper": ["en", "hi", "gu", "ta", "bn", "ml", "kn", "mr", "or", "pa", "te"],
        "default": ["eng", "guj", "hin", "eng+guj", "eng+hin", "guj+hin", "hin+guj", "eng+guj+hin", "hin+eng+guj"]
    }
    lang_combo['values'] = lang_map.get(method, lang_map["default"])
    lang_combo.set(lang_map.get(method, lang_map["default"])[0])
    update_conditional_options()

# ====================== GUI SETUP ======================
root = tk.Tk()
root.title("🧠 OCR & Audio Extractor Tool")
root.geometry("900x650")
root.minsize(800, 550)
root.configure(bg="#e8ecef")

style = ttk.Style()
style.theme_use('clam')

# Configure styles
style.configure("TCombobox", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"))
style.configure("Horizontal.TProgressbar", 
                troughcolor="#e0e0e0",
                background="#4CAF50",
                thickness=20,
                bordercolor="#e8ecef",
                lightcolor="#4CAF50",
                darkcolor="#4CAF50")

# Button hover effect
def on_enter(button, bg_color):
    button.config(bg=bg_color)

def on_leave(button, bg_color):
    button.config(bg=bg_color)

file_var = tk.StringVar()
lang_var = tk.StringVar()
method_var = tk.StringVar()
file_type_var = tk.StringVar(value="All Supported")
credentials_var = tk.StringVar()
strict_lines_var = tk.BooleanVar(value=True)
whisper_model_var = tk.StringVar(value=WHISPER_MODEL)

main_frame = tk.Frame(root, bg="#e8ecef")
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Input Section
input_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="flat")
input_frame.pack(fill="x", pady=(0, 10))
tk.Label(input_frame, text="📁 File Selection", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
file_input_frame = tk.Frame(input_frame, bg="#ffffff")
file_input_frame.pack(fill="x", padx=10, pady=5)
tk.Entry(file_input_frame, textvariable=file_var, width=50, font=("Segoe UI", 10)).pack(side="left", padx=(0, 5), fill="x", expand=True)
file_button = tk.Button(file_input_frame, text="Browse", command=browse_file, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"), relief="flat")
file_button.pack(side="left")
file_button.bind("<Enter>", lambda e: on_enter(file_button, "#45a049"))
file_button.bind("<Leave>", lambda e: on_leave(file_button, "#4CAF50"))
file_type_combo = ttk.Combobox(file_input_frame, textvariable=file_type_var, values=["All Supported", "PDF Only", "Images Only", "Audio Only"], state="readonly", width=15)
file_type_combo.pack(side="left", padx=(5, 0))

# Options Section
options_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="flat")
options_frame.pack(fill="x", pady=10)
tk.Label(options_frame, text="⚙️ OCR/Transcription Settings", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
settings_frame = tk.Frame(options_frame, bg="#ffffff")
settings_frame.pack(fill="x", padx=10, pady=5)

# Method selection
tk.Label(settings_frame, text="Method:", font=("Segoe UI", 10), bg="#ffffff").pack(side="left")
method_combo = ttk.Combobox(settings_frame, textvariable=method_var, state="readonly", width=20)
method_combo['values'] = ["PyMuPDF", "pdf2image", "EasyOCR", "Google Vision", "Whisper"]
method_combo.pack(side="left", padx=10)
method_combo.set("PyMuPDF")

# Language selection
tk.Label(settings_frame, text="Language:", font=("Segoe UI", 10), bg="#ffffff").pack(side="left")
lang_combo = ttk.Combobox(settings_frame, textvariable=lang_var, state="readonly", width=20)
lang_combo.pack(side="left", padx=10)

# Strict Line Preservation
tk.Checkbutton(settings_frame, text="Strict Line Preservation", variable=strict_lines_var, font=("Segoe UI", 10), bg="#ffffff").pack(side="left", padx=10)

# Conditional options (Whisper model or Google Vision credentials)
conditional_frame = tk.Frame(options_frame, bg="#ffffff")
conditional_frame.pack(fill="x", padx=10, pady=5)

# Call update_language_options after all widgets are defined
method_combo.bind("<<ComboboxSelected>>", update_language_options)
update_language_options()

# Progress and Extract
extract_frame = tk.Frame(main_frame, bg="#e8ecef")
extract_frame.pack(fill="x", pady=10)
status_label = tk.Label(extract_frame, text="Ready", font=("Segoe UI", 10, "bold"), bg="#e8ecef", fg="#333333")
status_label.pack(anchor="w", padx=10)
progress_bar = ttk.Progressbar(extract_frame, mode="indeterminate", style="Horizontal.TProgressbar")
progress_bar.pack(fill="x", padx=10, pady=5)
button_frame = tk.Frame(extract_frame, bg="#e8ecef")
button_frame.pack(pady=5)
extract_button = tk.Button(button_frame, text="🚀 Extract Text", command=extract_text, bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"), relief="flat")
extract_button.pack(side="left", padx=5)
extract_button.bind("<Enter>", lambda e: on_enter(extract_button, "#1e88e5"))
extract_button.bind("<Leave>", lambda e: on_leave(extract_button, "#2196F3"))
clean_button = tk.Button(button_frame, text="🧹 Clean Text", command=clean_displayed_text, bg="#FFC107", fg="black", font=("Segoe UI", 11, "bold"), relief="flat", state="disabled")
clean_button.pack(side="left", padx=5)
clean_button.bind("<Enter>", lambda e: on_enter(clean_button, "#ffb300"))
clean_button.bind("<Leave>", lambda e: on_leave(clean_button, "#FFC107"))
toggle_button = tk.Button(button_frame, text="Show Raw", command=toggle_raw_cleaned, bg="#9C27B0", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", state="disabled")
toggle_button.pack(side="left", padx=5)
toggle_button.bind("<Enter>", lambda e: on_enter(toggle_button, "#8e24aa"))
toggle_button.bind("<Leave>", lambda e: on_leave(toggle_button, "#9C27B0"))
copy_button = tk.Button(button_frame, text="📋 Copy Text", command=copy_text, bg="#FF5722", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", state="disabled")
copy_button.pack(side="left", padx=5)
copy_button.bind("<Enter>", lambda e: on_enter(copy_button, "#e64a19"))
copy_button.bind("<Leave>", lambda e: on_leave(copy_button, "#FF5722"))

# Output Section
output_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="flat")
output_frame.pack(fill="both", expand=True)
tk.Label(output_frame, text="📝 Extracted Text", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
output_text = ScrolledText(output_frame, height=15, wrap="word", font=("Consolas", 10), bg="#f9f9f9", spacing1=2, spacing2=2, spacing3=2)
output_text.pack(fill="both", padx=10, pady=(0, 10), expand=True)

# Tooltips
def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{widget.winfo_rootx()+20}+{widget.winfo_rooty()+20}")
    tk.Label(tooltip, text=text, bg="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9)).pack()
    tooltip.withdraw()
    def show_tooltip(event): tooltip.deiconify()
    def hide_tooltip(event): tooltip.withdraw()
    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

create_tooltip(file_type_combo, "Filter file types for selection")
create_tooltip(lang_combo, "Select the language for text extraction")
create_tooltip(method_combo, "Choose the OCR or transcription method")
create_tooltip(extract_button, "Start the text extraction process")
create_tooltip(clean_button, "Reformat the displayed text")
create_tooltip(toggle_button, "Toggle between raw and cleaned text output")
create_tooltip(copy_button, "Copy the extracted text to clipboard")

# Handle window close
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()