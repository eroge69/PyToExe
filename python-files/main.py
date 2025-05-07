import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
import os
import json
import datetime
import threading

# ---------- Timestamp Formatter ----------
def format_timestamp(seconds: float) -> str:
    return str(datetime.timedelta(seconds=int(seconds))).zfill(8).replace(".", ",") + ",000"

# ---------- Translations ----------
translations = {
    "en": {
        "select_file": "🎞️ Select video/audio file:",
        "output_folder": "📁 Output folder:",
        "filename": "📝 Filename (without extension):",
        "save_format": "💾 Save format:",
        "srt": ".srt (subtitles)",
        "txt": ".txt (plain text)",
        "model": "🤖 Whisper model:",
        "language": "🗣️ Language of the video (for subtitles):",
        "auto_lang": "🧠 Detect language automatically",
        "start": "🚀 START TRANSCRIPTION",
        "waiting": "Waiting for action...",
        "processing": "⏳ Processing...",
        "transcribing": "🔄 Transcribing...",
        "done": "✅ Done!",
        "error": "❌ Error",
        "browse": "Browse...",
        "choose_folder": "Choose folder...",
        "files_saved": "Files saved to:\n{}",
        "lang_select": "🌐 Interface language:",
        "format_info": "(Saved as .srt, .txt and .json)"
    },
    "ru": {
        "select_file": "🎞️ Выберите видео/аудио файл:",
        "output_folder": "📁 Папка для сохранения:",
        "filename": "📝 Имя файла (без расширения):",
        "save_format": "💾 Формат сохранения:",
        "srt": ".srt (субтитры)",
        "txt": ".txt (простой текст)",
        "model": "🤖 Модель Whisper:",
        "language": "🗣️ Язык видео (для субтитров):",
        "auto_lang": "🧠 Определить язык автоматически",
        "start": "🚀 НАЧАТЬ РАСПОЗНАВАНИЕ",
        "waiting": "Ожидание действия...",
        "processing": "⏳ Обработка...",
        "transcribing": "🔄 Распознавание...",
        "done": "✅ Готово!",
        "error": "❌ Ошибка",
        "browse": "Обзор...",
        "choose_folder": "Выбрать папку...",
        "files_saved": "Файлы сохранены в:\n{}",
        "lang_select": "🌐 Язык интерфейса:",
        "format_info": "(Сохраняется как .srt, .txt и .json)"
    }
}

import whisper
import os
import json
from tkinter import messagebox

# ---------- Transcription Function ----------
def transcribe_video(video_path, output_dir, filename, save_srt, save_txt,
                     model_name, status_label, progressbar, language_code, auto_lang, enable_ui_callback):
    try:
        tr = translations[current_lang.get()]
        model = whisper.load_model(model_name)
        status_label.config(text=tr["transcribing"])

        # Транскрибируем всё видео
        if auto_lang:
            result = model.transcribe(video_path)
        else:
            result = model.transcribe(video_path, language=language_code)

        os.makedirs(output_dir, exist_ok=True)

        # Сохранение в текстовый файл
        if save_txt:
            with open(os.path.join(output_dir, filename + ".txt"), "w", encoding="utf-8") as f:
                f.write(result["text"].strip())

        # Сохранение в SRT файл
        if save_srt:
            with open(os.path.join(output_dir, filename + ".srt"), "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], start=1):
                    f.write(f"{i}\n")
                    f.write(f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n")
                    f.write(f"{segment['text'].strip()}\n\n")

        # Сохранение результата в JSON файл
        with open(os.path.join(output_dir, filename + ".json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        status_label.config(text=tr["done"])
        messagebox.showinfo("Done", tr["files_saved"].format(output_dir))

    except Exception as e:
        status_label.config(text=tr["error"])
        messagebox.showerror("Error", str(e))

    finally:
        # Останавливаем прогресс-бар
        progressbar.stop()

        # Восстанавливаем доступность интерфейса
        root.after(0, enable_ui_callback)

# ---------- UI Control ----------
def disable_ui():
    for child in frame.winfo_children():
        try:
            child.configure(state="disabled")
        except:
            pass

def enable_ui():
    for child in frame.winfo_children():
        try:
            child.configure(state="normal")
        except:
            pass

def start_transcription():
    video_path = video_path_var.get()
    output_dir = output_dir_var.get()
    filename = filename_var.get()
    save_srt = srt_var.get()
    save_txt = txt_var.get()
    model_name = model_var.get()
    language_name = language_var.get()
    auto_lang = auto_lang_var.get()

    tr = translations[current_lang.get()]

    if not video_path or not os.path.isfile(video_path):
        messagebox.showwarning("Error", tr["select_file"])
        return
    if not output_dir:
        messagebox.showwarning("Error", tr["output_folder"])
        return
    if not filename.strip():
        messagebox.showwarning("Error", tr["filename"])
        return
    if not save_srt and not save_txt:
        messagebox.showwarning("Error", tr["save_format"])
        return

    language_code = language_name.split(" - ")[0]

    progressbar.start()
    status_label.config(text=tr["processing"])
    disable_ui()
    threading.Thread(target=transcribe_video, args=(
        video_path, output_dir, filename, save_srt, save_txt,
        model_name, status_label, progressbar, language_code, auto_lang, enable_ui
    ), daemon=True).start()

# ---------- GUI ----------
root = tk.Tk()
root.title("Whisper Subtitle Generator")
root.geometry("580x730")
root.iconbitmap("logo.ico")  # Только .ico файл
current_lang = tk.StringVar(value="en")


video_path_var = tk.StringVar()
output_dir_var = tk.StringVar()
filename_var = tk.StringVar(value="subs")
srt_var = tk.BooleanVar(value=True)
txt_var = tk.BooleanVar(value=True)
auto_lang_var = tk.BooleanVar(value=False)
model_var = tk.StringVar(value="medium")
language_var = tk.StringVar(value="ja - Japanese")

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

labels = {}

def browse_file():
    path = filedialog.askopenfilename(filetypes=[
        ("Media Files", "*.mp4 *.mkv *.mov *.avi *.mp3 *.wav"),
        ("All Files", "*.*")
    ])
    if path:
        video_path_var.set(path)

def browse_folder():
    path = filedialog.askdirectory()
    if path:
        output_dir_var.set(path)

# Interface language
labels["lang_select"] = ttk.Label(frame)
labels["lang_select"].pack(anchor="e", pady=(0, 0))
lang_menu = ttk.Combobox(frame, textvariable=current_lang, values=["en", "ru"], width=8, state="readonly")
lang_menu.pack(anchor="e")
lang_menu.bind("<<ComboboxSelected>>", lambda e: update_labels())

labels["select_file"] = ttk.Label(frame)
labels["select_file"].pack(anchor="w", pady=(10, 5))
entry1 = ttk.Entry(frame, textvariable=video_path_var, width=60)
entry1.pack(fill="x")
browse_button = ttk.Button(frame, command=browse_file)
browse_button.pack(pady=5)

labels["output_folder"] = ttk.Label(frame)
labels["output_folder"].pack(anchor="w", pady=(15, 5))
entry2 = ttk.Entry(frame, textvariable=output_dir_var, width=60)
entry2.pack(fill="x")
folder_button = ttk.Button(frame, command=browse_folder)
folder_button.pack(pady=5)

labels["filename"] = ttk.Label(frame)
labels["filename"].pack(anchor="w", pady=(15, 5))
ttk.Entry(frame, textvariable=filename_var, width=40).pack()

labels["save_format"] = ttk.Label(frame)
labels["save_format"].pack(anchor="w", pady=(15, 5))
srt_check = ttk.Checkbutton(frame, variable=srt_var)
srt_check.pack(anchor="w")
txt_check = ttk.Checkbutton(frame, variable=txt_var)
txt_check.pack(anchor="w")

labels["format_info"] = ttk.Label(frame, foreground="gray")
labels["format_info"].pack(anchor="w", pady=(2, 0))

labels["model"] = ttk.Label(frame)
labels["model"].pack(anchor="w", pady=(15, 5))
ttk.Combobox(frame, textvariable=model_var, values=["tiny", "base", "small", "medium", "large"], state="readonly").pack()

labels["language"] = ttk.Label(frame)
labels["language"].pack(anchor="w", pady=(15, 5))

language_options = sorted([
    "af - Afrikaans", "am - Amharic", "ar - Arabic", "az - Azerbaijani", "be - Belarusian", "bg - Bulgarian",
    "bn - Bengali", "cs - Czech", "da - Danish", "de - German", "el - Greek", "en - English", "es - Spanish",
    "et - Estonian", "fa - Persian", "fi - Finnish", "fr - French", "gu - Gujarati", "he - Hebrew", "hi - Hindi",
    "hr - Croatian", "hu - Hungarian", "id - Indonesian", "it - Italian", "ja - Japanese", "jv - Javanese",
    "ko - Korean", "lt - Lithuanian", "lv - Latvian", "ml - Malayalam", "mn - Mongolian", "mr - Marathi",
    "ms - Malay", "nl - Dutch", "no - Norwegian", "pl - Polish", "pt - Portuguese", "ro - Romanian",
    "ru - Russian", "sk - Slovak", "sl - Slovenian", "sr - Serbian", "sv - Swedish", "ta - Tamil", "te - Telugu",
    "th - Thai", "tr - Turkish", "uk - Ukrainian", "ur - Urdu", "vi - Vietnamese", "zh - Chinese"
])
ttk.Combobox(frame, textvariable=language_var, values=language_options, state="readonly").pack()

auto_lang_check = ttk.Checkbutton(frame, variable=auto_lang_var)
auto_lang_check.pack(anchor="w", pady=(5, 0))

start_btn = tk.Button(
    frame,
    command=start_transcription,
    bg="#007acc",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    padx=10,
    pady=10,
    relief="flat",
    activebackground="#005f99",
    cursor="hand2"
)
start_btn.pack(pady=25, fill="x")

progressbar = ttk.Progressbar(frame, mode="indeterminate")
progressbar.pack(fill="x", pady=10)

status_label = ttk.Label(frame)
status_label.pack(pady=(5, 0))

def update_labels():
    tr = translations[current_lang.get()]
    labels["select_file"].config(text=tr["select_file"])
    labels["output_folder"].config(text=tr["output_folder"])
    labels["filename"].config(text=tr["filename"])
    labels["save_format"].config(text=tr["save_format"])
    srt_check.config(text=tr["srt"])
    txt_check.config(text=tr["txt"])
    labels["model"].config(text=tr["model"])
    labels["language"].config(text=tr["language"])
    auto_lang_check.config(text=tr["auto_lang"])
    start_btn.config(text=tr["start"])
    status_label.config(text=tr["waiting"])
    browse_button.config(text=tr["browse"])
    folder_button.config(text=tr["choose_folder"])
    labels["lang_select"].config(text=tr["lang_select"])
    labels["format_info"].config(text=tr["format_info"])

update_labels()
root.mainloop()
