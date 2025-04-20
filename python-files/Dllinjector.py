import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ctypes
from ctypes import wintypes
import subprocess
import os
import sys

# Настройка WinAPI-функций
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Константы
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04

# Типы данных
SIZE_T = ctypes.c_size_t
LPSTR = ctypes.c_char_p

# Объявление функций
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE

kernel32.VirtualAllocEx.argtypes = [wintypes.HANDLE, wintypes.LPVOID, SIZE_T, wintypes.DWORD, wintypes.DWORD]
kernel32.VirtualAllocEx.restype = wintypes.LPVOID

kernel32.WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, SIZE_T, ctypes.POINTER(SIZE_T)]
kernel32.WriteProcessMemory.restype = wintypes.BOOL

kernel32.CreateRemoteThread.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p), SIZE_T, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
kernel32.CreateRemoteThread.restype = wintypes.HANDLE

kernel32.GetModuleHandleA.argtypes = [LPSTR]
kernel32.GetModuleHandleA.restype = wintypes.HANDLE

kernel32.GetProcAddress.argtypes = [wintypes.HANDLE, LPSTR]
kernel32.GetProcAddress.restype = wintypes.LPVOID

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def inject(pid, dll_path):
    try:
        if not os.path.isfile(dll_path):
            raise FileNotFoundError("DLL file not found")

        process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not process:
            raise ctypes.WinError(ctypes.get_last_error())
        
        dll_path = os.path.abspath(dll_path)
        dll_path_encoded = dll_path.encode('utf-8')
        size = len(dll_path_encoded) + 1
        remote_memory = kernel32.VirtualAllocEx(process, None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not remote_memory:
            raise ctypes.WinError(ctypes.get_last_error())
            
        written = SIZE_T()
        if not kernel32.WriteProcessMemory(process, remote_memory, dll_path_encoded, size, ctypes.byref(written)):
            raise ctypes.WinError(ctypes.get_last_error())
        
        load_library = kernel32.GetProcAddress(kernel32.GetModuleHandleA(b"kernel32.dll"), b"LoadLibraryA")
        if not load_library:
            raise ctypes.WinError(ctypes.get_last_error())
        
        thread = kernel32.CreateRemoteThread(process, None, 0, load_library, remote_memory, 0, None)
        if not thread:
            raise ctypes.WinError(ctypes.get_last_error())
            
        kernel32.CloseHandle(thread)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка внедрения: {str(e)}")
        return False
    finally:
        if 'process' in locals() and process:
            kernel32.CloseHandle(process)

class InjectorApp:
    def __init__(self, root):
        self.root = root
        root.title("DLL Injector")
        root.geometry("500x300")

        # Стиль
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=5)

        # PID
        self.pid_frame = ttk.Frame(root)
        self.pid_frame.pack(pady=5, fill=tk.X)
        self.pid_label = ttk.Label(self.pid_frame, text="PID процесса:")
        self.pid_label.pack(side=tk.LEFT)
        self.pid_entry = ttk.Entry(self.pid_frame)
        self.pid_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.chpid_btn = ttk.Button(self.pid_frame, text="Список процессов", command=self.show_processes)
        self.chpid_btn.pack(side=tk.LEFT)

        # DLL
        self.dll_frame = ttk.Frame(root)
        self.dll_frame.pack(pady=5, fill=tk.X)
        self.dll_label = ttk.Label(self.dll_frame, text="Путь к DLL:")
        self.dll_label.pack(side=tk.LEFT)
        self.dll_entry = ttk.Entry(self.dll_frame)
        self.dll_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.browse_btn = ttk.Button(self.dll_frame, text="Обзор", command=self.browse_dll)
        self.browse_btn.pack(side=tk.LEFT)

        # Кнопка инжекта
        self.inject_btn = ttk.Button(root, text="Внедрить DLL", command=self.inject)
        self.inject_btn.pack(pady=10)

    def browse_dll(self):
        dll_path = filedialog.askopenfilename(filetypes=[("DLL files", "*.dll")])
        if dll_path:
            self.dll_entry.delete(0, tk.END)
            self.dll_entry.insert(0, dll_path)

    def show_processes(self):
        proc = subprocess.run(
            ["tasklist", "/fo", "csv", "/nh"],
            capture_output=True,
            text=True,
            shell=True
        )

        processes = []
        for line in proc.stdout.splitlines():
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                processes.append((parts[1], parts[0]))

        win = tk.Toplevel(self.root)
        win.title("Процессы")
        win.geometry("600x400")

        tree = ttk.Treeview(win, columns=("PID", "Name"), show="headings")
        tree.heading("PID", text="PID")
        tree.heading("Name", text="Имя процесса")
        tree.column("PID", width=100)
        tree.column("Name", width=400)

        for pid, name in processes:
            tree.insert("", tk.END, values=(pid, name))

        tree.pack(fill=tk.BOTH, expand=True)

        # Обработчик выбора процесса
        def on_select(event):
            selected_item = tree.focus()
            if selected_item:
                pid = tree.item(selected_item, "values")[0]
                self.pid_entry.delete(0, tk.END)
                self.pid_entry.insert(0, pid)

        # Изменено на обычный клик вместо двойного
        tree.bind("<<TreeviewSelect>>", on_select)

    def inject(self):
        pid = self.pid_entry.get()
        dll_path = self.dll_entry.get()
        
        if not pid.isdigit():
            messagebox.showerror("Ошибка", "Введите корректный PID")
            return
            
        if not dll_path.lower().endswith(".dll"):
            messagebox.showerror("Ошибка", "Выберите файл .dll")
            return
            
        if not os.path.exists(dll_path):
            messagebox.showerror("Ошибка", "Файл DLL не найден")
            return
            
        if inject(int(pid), dll_path):
            messagebox.showinfo("Успех", "DLL успешно внедрена!")
        else:
            messagebox.showerror("Ошибка", "Не удалось внедрить DLL")

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    root = tk.Tk()
    app = InjectorApp(root)
    root.mainloop()