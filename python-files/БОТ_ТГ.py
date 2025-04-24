import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import asyncio
import random
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from datetime import datetime

class DarkFlooderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LIL BOT")
        self.root.geometry("500x670")
        self.root.configure(bg="#1e1e1e")

        self.template = []
        self.running = False
        self.chat_entries = []
        self.start_time = None
        self.photo_paths = []

        self.build_ui()

    def build_ui(self):
        def make_label(text):
            return tk.Label(self.root, text=text, fg="white", bg="#1e1e1e", anchor="w")

        make_label("Токен бота:").pack(anchor="w", padx=15)
        self.token_entry = tk.Entry(self.root, width=50, bg="#2d2d2d", fg="white", insertbackground="white", relief="flat")
        self.token_entry.pack(pady=5, padx=15)

        self.show_token = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Показать токен", variable=self.show_token,
                       command=self.toggle_token, bg="#1e1e1e", fg="white", activebackground="#1e1e1e",
                       activeforeground="white", selectcolor="#1e1e1e").pack(anchor="w", padx=15)

        tk.Button(self.root, text="Загрузить шаблон", command=self.load_template,
                  bg="#444", fg="white", relief="flat").pack(pady=5)

        self.template_label = tk.Label(self.root, text="Шаблонов: 0", bg="#1e1e1e", fg="white")
        self.template_label.pack()

        make_label("Путь к изображению (необязательно):").pack(anchor="w", padx=15)
        photo_entry = tk.Entry(self.root, width=50, bg="#2d2d2d", fg="white", insertbackground="white", relief="flat")
        photo_entry.pack(padx=15, pady=2)

        tk.Button(self.root, text="Выбрать фото", command=self.select_photos,
                  bg="#444", fg="white", relief="flat").pack(pady=2)

        frame_holder = tk.Frame(self.root, bg="#1e1e1e")
        frame_holder.pack(pady=5, fill="both", expand=True)

        canvas = tk.Canvas(frame_holder, height=180, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_holder, orient="vertical", command=canvas.yview)
        self.chat_frame = tk.Frame(canvas, bg="#1e1e1e")

        self.chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(self.chat_frame, text="Chat ID", width=25, bg="#1e1e1e", fg="white").grid(row=0, column=0)
        tk.Label(self.chat_frame, text="Префикс", width=25, bg="#1e1e1e", fg="white").grid(row=0, column=1)

        for _ in range(4):
            self.add_chat_row()

        make_label("Мин. задержка (мс):").pack(anchor="w", padx=15, pady=(10, 0))
        self.min_delay = tk.Entry(self.root, width=20, bg="#2d2d2d", fg="white", insertbackground="white", relief="flat")
        self.min_delay.insert(0, "100")
        self.min_delay.pack(padx=15)

        make_label("Макс. задержка (мс):").pack(anchor="w", padx=15, pady=(10, 0))
        self.max_delay = tk.Entry(self.root, width=20, bg="#2d2d2d", fg="white", insertbackground="white", relief="flat")
        self.max_delay.insert(0, "5000")
        self.max_delay.pack(padx=15)

        self.status_label = tk.Label(self.root, text="Статус: Ожидание", fg="skyblue", bg="#1e1e1e")
        self.status_label.pack(pady=5)

        self.timer_label = tk.Label(self.root, text="Время работы: 00:00:00", fg="gray", bg="#1e1e1e")
        self.timer_label.pack()

        self.start_btn = tk.Button(self.root, text="Старт", command=self.toggle_bot, bg="green", fg="white", relief="flat", width=20)
        self.start_btn.pack(pady=10)

        self.root.after(1000, self.update_timer)

    def toggle_token(self):
        self.token_entry.config(show="" if self.show_token.get() else "*")

    def select_photos(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.gif")])
        if paths:
            self.photo_paths = list(paths)

    def add_chat_row(self):
        row = len(self.chat_entries) + 1
        id_entry = tk.Entry(self.chat_frame, width=30, bg="#2d2d2d", fg="white", insertbackground="white", relief="flat")
        prefix_entry = tk.Entry(self.chat_frame, width=30, bg="#2d2d2d", fg="white", insertbackground="white", relief="flat")

        def on_enter(event):
            self.add_chat_row()

        id_entry.bind("<Return>", on_enter)
        prefix_entry.bind("<Return>", on_enter)

        id_entry.grid(row=row, column=0, padx=5, pady=2)
        prefix_entry.grid(row=row, column=1, padx=5, pady=2)
        self.chat_entries.append((id_entry, prefix_entry))

    def load_template(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.template = [line.strip() for line in f if line.strip()]
            self.template_label.config(text=f"Шаблонов: {len(self.template)}")
            messagebox.showinfo("Готово", f"Загружено {len(self.template)} сообщений")

    def toggle_bot(self):
        if not self.running:
            self.running = True
            self.start_btn.config(text="Стоп", bg="red")
            self.start_time = datetime.now()
            Thread(target=self.run_bot).start()
        else:
            self.running = False
            self.start_btn.config(text="Старт", bg="green")
            self.status_label.config(text="Статус: Остановлен")

    def run_bot(self):
        asyncio.run(self.start_bot())

    async def start_bot(self):
        token = self.token_entry.get().strip()
        if not token or not self.template:
            messagebox.showerror("Ошибка", "Введите токен и загрузите шаблоны.")
            return

        try:
            min_d = int(self.min_delay.get())
            max_d = int(self.max_delay.get())
        except:
            messagebox.showerror("Ошибка", "Некорректная задержка.")
            return

        chats = {}
        for id_entry, prefix_entry in self.chat_entries:
            cid = id_entry.get().strip()
            prefix = prefix_entry.get().strip()
            if cid:
                # Если префикс пустой, мы его пропускаем
                chats[int(cid)] = prefix if prefix else None

        if not chats:
            messagebox.showerror("Ошибка", "Нет чатов.")
            return

        bot = Bot(token=token)
        self.status_label.config(text="Статус: Активен")

        while self.running:
            for chat_id, prefix in chats.items():
                if not self.running:
                    break
                text = random.choice(self.template)
                
                if prefix:  # Если префикс есть, то добавляем его
                    text = f"{prefix} {text}"
                
                try:
                    if self.photo_paths:
                        random.shuffle(self.photo_paths)  # Перемешиваем список фотографий
                        for path in self.photo_paths:
                            input_file = FSInputFile(path)
                            await bot.send_photo(chat_id=chat_id, photo=input_file, caption=text)
                    else:
                        await bot.send_message(chat_id=chat_id, text=text)
                except Exception as e:
                    print(f"Ошибка при отправке в {chat_id}: {e}")

                await asyncio.sleep(random.randint(min_d, max_d) / 1000)

        await bot.session.close()

    def update_timer(self):
        if self.running and self.start_time:
            delta = datetime.now() - self.start_time
            h, m, s = delta.seconds // 3600, (delta.seconds % 3600) // 60, delta.seconds % 60
            self.timer_label.config(text=f"Время работы: {h:02}:{m:02}:{s:02}")
        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    app = DarkFlooderApp()
    app.root.mainloop()


