import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import random

class RandomPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("随机摇号软件")
        self.root.geometry("800x600")
        
        self.running = False
        self.available_numbers = []

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

        # 参数区
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, pady=10, sticky="ew")
        
        ttk.Label(frame, text="开始值:").grid(row=0, column=0)
        self.start_entry = ttk.Entry(frame, width=8)
        self.start_entry.insert(0, "0")
        self.start_entry.grid(row=0, column=1)

        ttk.Label(frame, text="结束值:").grid(row=0, column=2)
        self.end_entry = ttk.Entry(frame, width=8)
        self.end_entry.insert(0, "100")
        self.end_entry.grid(row=0, column=3)

        self.unique_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="不重复抽取", variable=self.unique_var).grid(row=0, column=4, padx=5)

        ttk.Label(frame, text="抽取数量:").grid(row=1, column=0)
        self.pick_count_entry = ttk.Entry(frame, width=8)
        self.pick_count_entry.insert(0, "1")
        self.pick_count_entry.grid(row=1, column=1)

        ttk.Label(frame, text="字体大小:").grid(row=1, column=2)
        self.font_size_entry = ttk.Entry(frame, width=8)
        self.font_size_entry.insert(0, "50")
        self.font_size_entry.grid(row=1, column=3)

        ttk.Button(frame, text="背景颜色", command=self.choose_bg_color).grid(row=1, column=4, padx=5)
        ttk.Button(frame, text="字体颜色", command=self.choose_font_color).grid(row=1, column=5, padx=5)

        # 主数字显示
        self.number_label = tk.Label(root, text="准备开始", font=("Arial", 50), bg="white", fg="black", anchor="center", justify="center")
        self.number_label.grid(row=5, column=0, sticky="nsew", pady=10)

        # 按钮区
        button_frame = ttk.Frame(root)
        button_frame.grid(row=6, column=0, pady=10)

        self.start_button = ttk.Button(button_frame, text="开始", command=self.start_random)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_random, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10)

        self.clear_button = ttk.Button(button_frame, text="清除记录", command=self.clear_history)
        self.clear_button.grid(row=0, column=2, padx=10)

        self.restart_button = ttk.Button(button_frame, text="重新开始", command=self.restart, state=tk.DISABLED)
        self.restart_button.grid(row=0, column=3, padx=10)

        # 历史记录区
        history_frame = ttk.Frame(root)
        history_frame.grid(row=7, column=0, pady=5, sticky="ew")

        ttk.Label(history_frame, text="历史记录:").pack(anchor="w")
        self.history_text = tk.Text(history_frame, height=5, wrap="word")
        self.history_text.pack(fill="both", expand=True)

    def choose_bg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.number_label.config(bg=color)

    def choose_font_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.number_label.config(fg=color)

    def start_random(self):
        try:
            self.start_num = int(self.start_entry.get())
            self.end_num = int(self.end_entry.get())
            self.pick_count = int(self.pick_count_entry.get())
            font_size = int(self.font_size_entry.get())
            self.number_label.config(font=("Arial", font_size))
            if self.start_num >= self.end_num:
                messagebox.showerror("错误", "开始值必须小于结束值！")
                return
            if self.pick_count <= 0:
                messagebox.showerror("错误", "抽取数量必须大于0！")
                return
            if self.unique_var.get() and self.pick_count > (self.end_num - self.start_num + 1):
                messagebox.showerror("错误", "抽取数量超过可用范围！")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字范围、抽取数量和字体大小！")
            return
        
        if self.unique_var.get():
            self.available_numbers = list(range(self.start_num, self.end_num + 1))

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)  # Enable restart button
        self.animate_random()

    def animate_random(self):
        if self.running:
            # 先快速滚动
            numbers = [random.randint(self.start_num, self.end_num) for _ in range(self.pick_count)]
            self.display_numbers(numbers)
            self.root.after(50, self.animate_random)

    def stop_random(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)  # Enable restart button

        if self.unique_var.get():
            if len(self.available_numbers) < self.pick_count:
                numbers = random.sample(self.available_numbers, len(self.available_numbers))
            else:
                numbers = random.sample(self.available_numbers, self.pick_count)
        else:
            numbers = [random.randint(self.start_num, self.end_num) for _ in range(self.pick_count)]

        self.display_numbers(numbers)

        # 更新可用数字
        if self.unique_var.get():
            for num in numbers:
                if num in self.available_numbers:
                    self.available_numbers.remove(num)

        # 保存到历史
        self.history_text.insert(tk.END, " ".join(map(str, numbers)) + "\n")
        self.history_text.see(tk.END)  # 滚动到最后

    def display_numbers(self, numbers):
        font_size = int(self.font_size_entry.get())
        win_width = self.number_label.winfo_width()
        if win_width == 1:
            win_width = self.root.winfo_width()
        char_width = font_size

        max_chars_per_line = max(1, win_width // (char_width + 10))
        lines = []
        line = []
        for i, num in enumerate(numbers):
            line.append(str(num))
            if (i + 1) % max_chars_per_line == 0:
                lines.append("  ".join(line))
                line = []
        if line:
            lines.append("  ".join(line))

        display_text = "\n".join(lines)
        self.number_label.config(text=display_text)

    def clear_history(self):
        self.history_text.delete(1.0, tk.END)

    def restart(self):
        # Reset the interface and the numbers
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, "0")
        self.end_entry.delete(0, tk.END)
        self.end_entry.insert(0, "100")
        self.pick_count_entry.delete(0, tk.END)
        self.pick_count_entry.insert(0, "1")
        self.font_size_entry.delete(0, tk.END)
        self.font_size_entry.insert(0, "50")
        self.number_label.config(text="准备开始", font=("Arial", 50), bg="white", fg="black")

        self.running = False
        self.available_numbers = []
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomPickerApp(root)
    root.mainloop()
