
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class RenameBulkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量重命名工具（多行输入）")
        self.folder_path = ""
        self.original_files = []

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        btn_select = tk.Button(top_frame, text="选择文件夹", command=self.select_folder)
        btn_select.pack()

        self.files_text = tk.Text(self.root, height=25, width=50, state="disabled")
        self.files_text.pack(side="left", padx=10, pady=10)

        self.newnames_text = scrolledtext.ScrolledText(self.root, height=25, width=50)
        self.newnames_text.pack(side="right", padx=10, pady=10)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)

        self.btn_rename = tk.Button(bottom_frame, text="确认重命名", command=self.rename_files, state=tk.DISABLED)
        self.btn_rename.pack()

    def select_folder(self):
        path = filedialog.askdirectory(title="选择需要重命名的文件夹")
        if not path:
            return

        self.folder_path = path
        self.load_files()

    def extract_number(self, filename):
        import re
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    def load_files(self):
        self.original_files = sorted(
            [f for f in os.listdir(self.folder_path) if os.path.isfile(os.path.join(self.folder_path, f))],
            key=self.extract_number
        )

        self.files_text.config(state="normal")
        self.files_text.delete("1.0", tk.END)
        for name in self.original_files:
            self.files_text.insert(tk.END, name + "\n")
        self.files_text.config(state="disabled")

        self.newnames_text.delete("1.0", tk.END)
        self.btn_rename.config(state=tk.NORMAL)

    def rename_files(self):
        new_names = self.newnames_text.get("1.0", tk.END).strip().splitlines()

        if len(new_names) != len(self.original_files):
            messagebox.showerror("数量不匹配", f"共有 {len(self.original_files)} 个文件，但输入了 {len(new_names)} 个新名称。")
            return

        for i, new_base in enumerate(new_names):
            new_base = new_base.strip()
            if not new_base:
                messagebox.showerror("错误", f"第 {i+1} 行新文件名为空")
                return

        confirm = messagebox.askyesno("确认", "确定要批量重命名吗？")
        if not confirm:
            return

        count = 0
        for old_name, new_base in zip(self.original_files, new_names):
            old_path = os.path.join(self.folder_path, old_name)
            ext = os.path.splitext(old_name)[1]
            new_name = new_base + ext
            new_path = os.path.join(self.folder_path, new_name)

            if os.path.exists(new_path):
                messagebox.showwarning("跳过", f"文件已存在，跳过：{new_name}")
                continue

            os.rename(old_path, new_path)
            count += 1

        messagebox.showinfo("完成", f"成功重命名 {count} 个文件")
        self.load_files()

if __name__ == "__main__":
    root = tk.Tk()
    app = RenameBulkApp(root)
    root.mainloop()
