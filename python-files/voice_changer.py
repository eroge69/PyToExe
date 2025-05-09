
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from pydub.playback import play
import os

def change_pitch(sound, semitones):
    new_sample_rate = int(sound.frame_rate * (2.0 ** (semitones / 12.0)))
    return sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(44100)

def apply_effect(effect, sound):
    if effect == "طفل 👶":
        return change_pitch(sound, 5)
    elif effect == "رجل غليظ 🔊":
        return change_pitch(sound, -5)
    elif effect == "روبوت 🤖":
        return sound.low_pass_filter(400).reverse()
    elif effect == "شبح 👻":
        return sound + sound.reverse() - 6
    elif effect == "سنفور 😂":
        return change_pitch(sound, 10).speedup(playback_speed=1.5)
    else:
        return sound

class VoiceChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ برنامج تغيير الصوت")
        self.file_path = None

        tk.Label(root, text="1. اختر ملف صوتي:").pack()
        tk.Button(root, text="تحميل", command=self.load_file).pack(pady=5)

        tk.Label(root, text="2. اختر التأثير:").pack()
        self.effect_var = tk.StringVar()
        self.effect_var.set("طفل 👶")
        options = ["طفل 👶", "رجل غليظ 🔊", "روبوت 🤖", "شبح 👻", "سنفور 😂"]
        tk.OptionMenu(root, self.effect_var, *options).pack(pady=5)

        tk.Button(root, text="تشغيل النتيجة", command=self.play_transformed).pack(pady=5)
        tk.Button(root, text="💾 حفظ", command=self.save_result).pack(pady=5)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if path:
            self.file_path = path
            messagebox.showinfo("تم التحميل", "تم تحميل الملف الصوتي بنجاح")

    def play_transformed(self):
        if not self.file_path:
            messagebox.showerror("خطأ", "يرجى تحميل ملف صوت أولاً")
            return
        sound = AudioSegment.from_file(self.file_path)
        transformed = apply_effect(self.effect_var.get(), sound)
        play(transformed)

    def save_result(self):
        if not self.file_path:
            messagebox.showerror("خطأ", "يرجى تحميل ملف صوت أولاً")
            return
        sound = AudioSegment.from_file(self.file_path)
        transformed = apply_effect(self.effect_var.get(), sound)
        save_path = filedialog.asksaveasfilename(defaultextension=".wav")
        if save_path:
            transformed.export(save_path, format="wav")
            messagebox.showinfo("تم الحفظ", "تم حفظ الصوت بنجاح")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceChangerApp(root)
    root.mainloop()
