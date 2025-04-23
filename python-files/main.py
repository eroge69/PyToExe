import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

# API ID и API Hash, полученные с сайта Telegram
YOUR_API_ID = '2040'
YOUR_API_HASH = 'b18441a1ff607e10a989891a5462e627'

def convert_tdata_to_session(tdata_paths, output_folder):
    """Функция для конвертации tdata в .session файл"""
    successful_conversions = []

    for tdata_path in tdata_paths:
        # Получаем имя папки/файла tdata
        session_name = os.path.basename(tdata_path)

        if not os.path.isdir(tdata_path):
            messagebox.showerror("Ошибка", f"{tdata_path} не является директорией.")
            return

        tdata_files = os.listdir(tdata_path)
        if len(tdata_files) == 0:
            messagebox.showerror("Ошибка", f"Директория {tdata_path} пуста.")
            return

        try:
            # Создаем клиент Telegram
            client = TelegramClient(session_name, api_id=YOUR_API_ID, api_hash=YOUR_API_HASH)
            client.start()
            client.connect()

            if not client.is_user_authorized():
                messagebox.showerror("Ошибка", "Не удается авторизоваться, требуется ввести пароль.")
                return

            # Сохраняем сессию в выбранную папку
            output_path = os.path.join(output_folder, f"{session_name}.session")
            client.session.save()
            successful_conversions.append(output_path)

        except SessionPasswordNeededError:
            messagebox.showerror("Ошибка", "Для выполнения требуется ввести двухфакторный пароль.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        finally:
            client.disconnect()

    return successful_conversions

def on_convert():
    """Обработчик кнопки конвертации"""
    tdata_paths = entry_tdata.get().split(';')
    output_folder = entry_output_folder.get()

    if not tdata_paths or not output_folder:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите файлы tdata и папку для сохранения.")
        return

    # Начинаем конвертацию
    successful_conversions = convert_tdata_to_session(tdata_paths, output_folder)

    if successful_conversions:
        # Показываем галочку после успешной конвертации
        button_convert.config(text="Конвертация завершена", state=tk.DISABLED)
        button_download.config(state=tk.NORMAL)

def on_drag_drop(event):
    """Обработчик перетаскивания файлов"""
    files = event.data.split()
    valid_paths = []

    for file in files:
        if os.path.isdir(file):
            valid_paths.append(file)

    if valid_paths:
        entry_tdata.delete(0, tk.END)
        entry_tdata.insert(0, ";".join(valid_paths))

def on_browse_folder():
    """Открыть проводник для выбора папки для сохранения .session файлов"""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_output_folder.delete(0, tk.END)
        entry_output_folder.insert(0, folder_selected)

def on_browse_tdata():
    """Открыть проводник для выбора файлов tdata"""
    files_selected = filedialog.askdirectory(multiple=True)
    if files_selected:
        entry_tdata.delete(0, tk.END)
        entry_tdata.insert(0, ";".join(files_selected))

# Создаем главное окно с поддержкой drag-and-drop
root = TkinterDnD.Tk()
root.title("Конвертер tdata в .session")
root.geometry("600x300")

# Метки
label_tdata = tk.Label(root, text="Путь к папке tdata (перетащите сюда или выберите):")
label_tdata.pack(pady=5)

# Поле для ввода пути к папке tdata (drag-and-drop)
entry_tdata = tk.Entry(root, width=60)
entry_tdata.pack(pady=5)

# Делаем это поле поддерживающим drag-and-drop
entry_tdata.drop_target_register(DND_FILES)
entry_tdata.dnd_bind('<<Drop>>', on_drag_drop)

# Кнопка для выбора папки
button_browse_tdata = tk.Button(root, text="Выбрать файлы tdata", command=on_browse_tdata)
button_browse_tdata.pack(pady=5)

# Метка для вывода директории для сохранения .session
label_output_folder = tk.Label(root, text="Папка для сохранения .session:")
label_output_folder.pack(pady=5)

# Поле для ввода директории для сохранения
entry_output_folder = tk.Entry(root, width=60)
entry_output_folder.pack(pady=5)

# Кнопка для выбора папки для сохранения
button_browse_folder = tk.Button(root, text="Выбрать папку", command=on_browse_folder)
button_browse_folder.pack(pady=5)

# Кнопка для конвертации
button_convert = tk.Button(root, text="Конвертировать", command=on_convert)
button_convert.pack(pady=20)

# Кнопка для скачивания
button_download = tk.Button(root, text="Скачать", state=tk.DISABLED)
button_download.pack(pady=5)

# Запускаем GUI
root.mainloop()
