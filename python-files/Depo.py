Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import json
import whisper
import xml.etree.ElementTree as ET
from xml.dom import minidom
import fitz  # PyMuPDF
import datetime
import subprocess

# Load users from local JSON
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    else:
        return {}

# Save users back to file
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# Login Window
class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("DepoSync Login")
        self.master.geometry("300x180")

        tk.Label(master, text="Username:").pack(pady=(10, 0))
        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        tk.Label(master, text="Password:").pack()
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        tk.Button(master, text="Login", command=self.login).pack(pady=10)
        self.status_label = tk.Label(master, text="")
        self.status_label.pack()

    def login(self):
        users = load_users()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in users and users[username]["password"] == password:
            self.master.destroy()
            root = tk.Tk()
            app = DepoSyncApp(root, username, users[username]["role"])
            root.mainloop()
        else:
            self.status_label.config(text="Invalid login", fg="red")
class DepoSyncApp:
    def __init__(self, root, username, role):
        self.root = root
        self.root.title("DepoSync Pro")
        self.username = username
        self.role = role
        self.transcript_lines = []
        self.cleaned_lines = []
        self.model = whisper.load_model("base")
        self.video_duration = 0

        self.transcript_path = ""
        self.video_path = ""

        self.setup_gui()

    def setup_gui(self):
        self.logo_img = tk.PhotoImage(file="logo.png") if os.path.exists("logo.png") else None
        if self.logo_img:
            tk.Label(self.root, image=self.logo_img).pack()

        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Upload section
        upload_frame = tk.LabelFrame(frame, text="Upload Files")
        upload_frame.pack(fill="x", pady=5)

        tk.Button(upload_frame, text="Browse Transcript (.txt or .pdf)", command=self.load_transcript).pack(pady=2)
        tk.Button(upload_frame, text="Browse Video (.mp4)", command=self.load_video).pack(pady=2)

        self.cleanup_var = tk.BooleanVar()
        tk.Checkbutton(upload_frame, text="Clean up transcript formatting", variable=self.cleanup_var).pack()

        # Job Tracking Info
        job_frame = tk.LabelFrame(frame, text="Job Tracking Information")
        job_frame.pack(fill="x", pady=5)

        self.first_name = tk.Entry(job_frame)
        self.last_name = tk.Entry(job_frame)
        self.date_entry = tk.Entry(job_frame)
        self.case_caption = tk.Entry(job_frame)

        for label, entry in [("Deponent First Name:", self.first_name),
                             ("Deponent Last Name:", self.last_name),
                             ("Deposition Date:", self.date_entry),
                             ("Case Caption:", self.case_caption)]:
            tk.Label(job_frame, text=label).pack(anchor="w")
            entry.pack(fill="x", padx=5)
        # Action buttons
        tk.Button(frame, text="Preview Transcript", command=self.preview_transcript).pack(pady=5)
        tk.Button(frame, text="Sync & Export", command=self.sync_and_export).pack(pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        self.status_bar = tk.Label(frame, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        self.status_bar.pack(fill="x", pady=5)

        # Log output
        self.log_box = scrolledtext.ScrolledText(frame, height=8)
        self.log_box.pack(fill="both", expand=True)

    def load_transcript(self):
        file = filedialog.askopenfilename(filetypes=[("Transcript files", "*.txt *.pdf")])
        if not file:
            return
        self.transcript_path = file
        try:
            if file.endswith(".pdf"):
                doc = fitz.open(file)
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
            else:
                with open(file, "r", encoding="utf-8") as f:
                    full_text = f.read()

            lines = full_text.splitlines()
            self.cleaned_lines = [l.strip() for l in lines if l.strip()] if self.cleanup_var.get() else lines
            self.status_var.set("Transcript loaded.")
            self.log("Transcript loaded successfully.")
        except Exception as e:
            self.log(f"Error loading transcript: {e}")

    def load_video(self):
        file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if not file:
            return
        self.video_path = file
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", file
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.video_duration = float(result.stdout)
            self.status_var.set(f"Video loaded. Duration: {self.video_duration:.2f} seconds.")
            self.log(f"Video loaded: {file} ({self.video_duration:.2f} sec)")
        except Exception as e:
            self.log(f"Error reading video duration: {e}")
    def preview_transcript(self):
        if not self.cleaned_lines:
            messagebox.showwarning("Missing Transcript", "Please load a transcript first.")
            return
        preview = tk.Toplevel(self.root)
        preview.title("Transcript Preview")
        box = scrolledtext.ScrolledText(preview, width=100, height=30)
        box.pack(fill="both", expand=True)
        box.insert(tk.END, "\n".join(self.cleaned_lines))

    def sync_and_export(self):
        if not self.video_path or not self.cleaned_lines:
            messagebox.showwarning("Missing Input", "Transcript and video are both required.")
            return
        try:
            self.status_var.set("Transcribing video with Whisper...")
            self.root.update()
            result = self.model.transcribe(self.video_path)
            segments = result["segments"]
            export_data = []

            for i, line in enumerate(self.cleaned_lines):
                if i < len(segments):
                    export_data.append({
                        "start": segments[i]["start"],
                        "end": segments[i]["end"],
                        "text": line
                    })

            self.status_var.set("Building XML export...")
            self.root.update()

            root = ET.Element("onCue")
            depo = ET.SubElement(root, "deposition", {
                "mediaId": "",
                "depoFirstName": self.first_name.get(),
                "depoLastName": self.last_name.get(),
                "date": self.date_entry.get(),
                "linesPerPage": "25"
            })

            depoVideo = ET.SubElement(depo, "depoVideo", {
                "ID": "1",
                "filename": os.path.basename(self.video_path),
                "startTime": "0",
                "stopTime": str(export_data[-1]["end"]),
                "firstPGLN": "10001",
                "lastPGLN": str(10000 + len(export_data)),
                "startTuned": "no",
                "stopTuned": "no"
            })

            for i, seg in enumerate(export_data):
                page = 100 + (i // 25)
                line = (i % 25) + 1
                pgLN = page * 100 + line
                ET.SubElement(depoVideo, "depoLine", {
                    "prefix": "",
                    "text": seg["text"],
                    "page": str(page),
                    "line": str(line),
                    "pgLN": str(pgLN),
                    "videoID": "1",
                    "videoStart": f"{seg['start']:.3f}",
                    "videoStop": f"{seg['end']:.3f}",
                    "isEdited": "no",
                    "isSynched": "yes",
                    "isRedacted": "no"
                })

            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            xml_out = os.path.join(os.path.dirname(self.video_path), "synced_transcript_export.xml")
            with open(xml_out, "w", encoding="utf-8") as f:
                f.write(xml_str)
            self.log(f"XML exported to {xml_out}")

            self.generate_invoice()
            self.status_var.set("Export complete.")
...         except Exception as e:
...             self.log(f"Sync/export error: {e}")
... 
...     def generate_invoice(self):
...         try:
...             mins = self.video_duration / 60
...             total = mins * 15.00
...             invoice = f"""
... DepoSync Invoice
... =======================
... Deponent: {self.first_name.get()} {self.last_name.get()}
... Case: {self.case_caption.get()}
... Deposition Date: {self.date_entry.get()}
... Processed By: {self.username}
... 
... Video File: {os.path.basename(self.video_path)}
... Duration: {self.video_duration:.2f} seconds ({mins:.2f} minutes)
... Rate: $15.00/minute
... 
... Total Due: ${total:.2f}
... Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
... """
...             invoice_path = os.path.join(os.path.dirname(self.video_path), "DepoSync_Invoice.txt")
...             with open(invoice_path, "w") as f:
...                 f.write(invoice)
...             self.log(f"Invoice exported to {invoice_path}")
...         except Exception as e:
...             self.log(f"Invoice error: {e}")
... 
...     def log(self, message):
...         self.log_box.insert(tk.END, message + "\n")
...         self.log_box.see(tk.END)
... 
... # Start the app with login
... if __name__ == "__main__":
...     login = tk.Tk()
...     LoginWindow(login)
...     login.mainloop()
