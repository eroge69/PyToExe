import tkinter as tk
import subprocess
from tkinter import messagebox

class UtilitiesApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Утилиты")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)  # Блокировка закрытия через крестик
        self.anydesk_process = None
        self.vnc_process = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопка подключения к удаленному рабочему столу
        tk.Button(self.master, text="Подключиться к удаленному рабочему столу", 
                 command=self.connect_to_remote_desktop).pack(pady=10)
        
        # Кнопка запуска VNC Viewer
        tk.Button(self.master, text="Запустить VNC Viewer", 
                 command=self.open_vnc).pack(pady=10)
        
        # Кнопка выключения компьютера
        tk.Button(self.master, text="Выключить компьютер", 
                 command=self.shutdown_computer).pack(pady=10)
        
        # Кнопка запуска cmd
        tk.Button(self.master, text="Запустить командную строку", 
                 command=self.open_cmd).pack(pady=10)
        
        # Кнопка запуска AnyDesk
        tk.Button(self.master, text="Запустить AnyDesk", 
                 command=self.open_anydesk).pack(pady=10)
        
        # Кнопка закрытия AnyDesk
        tk.Button(self.master, text="Закрыть AnyDesk", 
                 command=self.close_anydesk).pack(pady=10)
        
        # Кнопка открытия панели управления
        tk.Button(self.master, text="Открыть Панель управления", 
                 command=self.open_control_panel).pack(pady=10)
        
        # Кнопка выхода из приложения
        tk.Button(self.master, text="Выход", 
                 command=self.on_close, fg="red").pack(pady=20)
    
    def connect_to_remote_desktop(self):
        try:
            subprocess.run(["mstsc"], shell=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить удаленный рабочий стол: {e}")
    
    def open_vnc(self):
        try:
            self.vnc_process = subprocess.Popen(["C:\\Program Files\\RealVNC\\VNC Viewer\\vncviewer.exe"])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить VNC Viewer: {e}")
    
    def shutdown_computer(self):
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите выключить компьютер?"):
            try:
                subprocess.run(["shutdown", "/s", "/t", "0"], shell=True)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось выключить компьютер: {e}")
    
    def open_cmd(self):
        try:
            subprocess.Popen(["cmd", "/k"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть командную строку: {e}")
    
    def open_anydesk(self):
        try:
            self.anydesk_process = subprocess.Popen(["C:\\AnyDesk.exe"])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить AnyDesk: {e}")
    
    def close_anydesk(self):
        if self.anydesk_process:
            try:
                self.anydesk_process.terminate()
                self.anydesk_process = None
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось закрыть AnyDesk: {e}")
        else:
            messagebox.showinfo("Информация", "AnyDesk не запущен")
    
    def open_control_panel(self):
        try:
            subprocess.run(["control"], shell=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть панель управления: {e}")
    
    def on_close(self):
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти из приложения?"):
            # Закрываем все запущенные процессы перед выходом
            if self.anydesk_process:
                self.anydesk_process.terminate()
            if self.vnc_process:
                self.vnc_process.terminate()
            self.master.destroy()

def main():
    root = tk.Tk()
    app = UtilitiesApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()