
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class RenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量重命名工具")
        self.file_entries = []
        self.folder_path = ""

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        btn_select = tk.Button(top_frame, text="选择文件夹", command=self.select_folder)
        btn_select.pack()

        self.canvas = tk.Canvas(self.root, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=10)

        self.btn_rename = tk.Button(self.bottom_frame, text="确认重命名", command=self.rename_files, state=tk.DISABLED)
        self.btn_rename.pack()

    def select_folder(self):
        path = filedialog.askdirectory(title="选择需要重命名的文件夹")
        if not path:
            return

        self.folder_path = path
        self.load_files()

    def load_files(self):
        # 清空旧内容
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.file_entries.clear()

        files = sorted(os.listdir(self.folder_path), key=self.extract_number)
        row = 0
        for filename in files:
            full_path = os.path.join(self.folder_path, filename)
            if os.path.isfile(full_path):
                tk.Label(self.frame, text=filename, width=40, anchor="w").grid(row=row, column=0, padx=5, pady=2)
                entry = tk.Entry(self.frame, width=40)
                entry.insert(0, os.path.splitext(filename)[0])
                entry.grid(row=row, column=1, padx=5, pady=2)
                self.file_entries.append((filename, entry))
                row += 1

        if self.file_entries:
            self.btn_rename.config(state=tk.NORMAL)

    def extract_number(self, filename):
        import re
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    def rename_files(self):
        for old_name, entry in self.file_entries:
            new_base = entry.get().strip()
            if not new_base:
                messagebox.showerror("错误", f"新文件名不能为空：{old_name}")
                return

        confirm = messagebox.askyesno("确认", "确定要进行批量重命名吗？")
        if not confirm:
            return

        success = 0
        for old_name, entry in self.file_entries:
            new_base = entry.get().strip()
            old_path = os.path.join(self.folder_path, old_name)
            ext = os.path.splitext(old_name)[1]
            new_name = new_base + ext
            new_path = os.path.join(self.folder_path, new_name)

            if os.path.exists(new_path):
                messagebox.showwarning("跳过", f"文件已存在，跳过：{new_name}")
                continue

            os.rename(old_path, new_path)
            success += 1

        messagebox.showinfo("完成", f"成功重命名 {success} 个文件")
        self.load_files()

if __name__ == "__main__":
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()
