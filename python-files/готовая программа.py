import os
import random
import shutil
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageOps
import concurrent.futures

# Функция для открытия диалогового окна и выбора папки
def open_folder_dialog(treeview=None):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        if treeview:
            # Обновляем treeview с новым путем
            treeview.delete(*treeview.get_children())
            for dirpath, dirnames, filenames in os.walk(folder_selected):
                for filename in filenames:
                    treeview.insert("", "end", text=filename, values=(dirpath,))
    return folder_selected

# Функция для сортировки файлов по дате съемки
def sort_files_by_date(folder, message_label):
    try:
        message_label.pack()  # Показываем сообщение "Ожидайте, пожалуйста"
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    timestamp = os.path.getmtime(file_path)  # Получаем дату изменения файла
                    date_folder = os.path.join(folder, f'{file[:10]}')  # Формируем имя папки по дате
                    if not os.path.exists(date_folder):
                        os.makedirs(date_folder)
                    shutil.move(file_path, os.path.join(date_folder, file))  # Перемещаем файл
                except Exception as e:
                    print(f"Ошибка при обработке файла {file}: {e}")
        messagebox.showinfo("Успех", "Файлы успешно отсортированы по дате.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при сортировке файлов: {str(e)}")
    finally:
        message_label.pack_forget()  # Скрываем сообщение "Ожидайте, пожалуйста"

# Функция для переименования файлов в случайном порядке
def rename_files_in_folder(folder, message_label):
    try:
        message_label.pack()  # Показываем сообщение "Ожидайте, пожалуйста"
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    random_name = str(random.randint(1000000000, 9999999999)) + os.path.splitext(file)[1]
                    new_file_path = os.path.join(root, random_name)
                    os.rename(file_path, new_file_path)
        messagebox.showinfo("Успех", "Файлы успешно переименованы.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при переименовании файлов: {str(e)}")
    finally:
        message_label.pack_forget()  # Скрываем сообщение "Ожидайте, пожалуйста"

# Функция для поиска дубликатов файлов
def find_duplicates(folder, message_label):
    try:
        message_label.pack()  # Показываем сообщение "Ожидайте, пожалуйста"
        files_dict = {}
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size in files_dict:
                    files_dict[file_size].append(file_path)
                else:
                    files_dict[file_size] = [file_path]
        duplicates = []
        for size, paths in files_dict.items():
            if len(paths) > 1:
                duplicates.append(paths)
        if duplicates:
            messagebox.showinfo("Дубликаты", f"Найдено {len(duplicates)} дубликатов.")
        else:
            messagebox.showinfo("Дубликаты", "Дубликаты не найдены.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при поиске дубликатов: {str(e)}")
    finally:
        message_label.pack_forget()  # Скрываем сообщение "Ожидайте, пожалуйста"

# Функция для преобразования изображений в черно-белое
def convert_to_grayscale(folder, message_label, progress_bar):
    try:
        message_label.pack()  # Показываем сообщение "Ожидайте, пожалуйста"
        with concurrent.futures.ThreadPoolExecutor() as executor:
            files = []
            for root, dirs, files_in_dir in os.walk(folder):
                for file in files_in_dir:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        file_path = os.path.join(root, file)
                        files.append(file_path)
            total_files = len(files)

            # Запускаем асинхронное преобразование для каждого файла
            for index, file_path in enumerate(files):
                executor.submit(process_grayscale, file_path, progress_bar, index, total_files)

        messagebox.showinfo("Успех", "Все изображения в папке преобразованы в черно-белое.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при преобразовании в черно-белое: {str(e)}")
    finally:
        message_label.pack_forget()  # Скрываем сообщение "Ожидайте, пожалуйста"

# Функция для асинхронного преобразования в черно-белое
def process_grayscale(file_path, progress_bar, current_index, total_files):
    try:
        img = Image.open(file_path)
        img_gray = img.convert("L")  # Конвертируем изображение в черно-белое
        new_file_path = os.path.splitext(file_path)[0] + "_gray" + ".png"  # Сохраняем в PNG без потерь
        img_gray.save(new_file_path, format="PNG")  # Сохраняем в формате PNG для минимизации потерь

        # Обновляем прогресс-бар
        progress_bar['value'] = (current_index + 1) / total_files * 100
        progress_bar.update()
    except Exception as e:
        print(f"Ошибка при обработке изображения {file_path}: {e}")

# Функция для преобразования изображений в сепию
def convert_to_sepia(folder, message_label, progress_bar):
    try:
        message_label.pack()  # Показываем сообщение "Ожидайте, пожалуйста"
        with concurrent.futures.ThreadPoolExecutor() as executor:
            files = []
            for root, dirs, files_in_dir in os.walk(folder):
                for file in files_in_dir:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        file_path = os.path.join(root, file)
                        files.append(file_path)
            total_files = len(files)

            # Запускаем асинхронное преобразование для каждого файла
            for index, file_path in enumerate(files):
                executor.submit(process_sepia, file_path, progress_bar, index, total_files)

        messagebox.showinfo("Успех", "Все изображения в папке преобразованы в сепию.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при преобразовании в сепию: {str(e)}")
    finally:
        message_label.pack_forget()  # Скрываем сообщение "Ожидайте, пожалуйста"

# Функция для асинхронного преобразования в сепию
def process_sepia(file_path, progress_bar, current_index, total_files):
    try:
        img = Image.open(file_path)
        width, height = img.size
        pixels = img.load()  # Создаем доступ к пикселям изображения

        for py in range(height):
            for px in range(width):
                r, g, b = img.getpixel((px, py))

                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                # Ограничиваем цвета в пределах допустимых значений
                tr = min(255, tr)
                tg = min(255, tg)
                tb = min(255, tb)

                pixels[px, py] = (tr,tg,tb)

        new_file_path = os.path.splitext(file_path)[0] + "_sepia" + ".png"  # Сохраняем в PNG без потерь
        img.save(new_file_path, format="PNG")  # Сохраняем в формате PNG для минимизации потерь

        # Обновляем прогресс-бар
        progress_bar['value'] = (current_index + 1) / total_files * 100
        progress_bar.update()
    except Exception as e:
        print(f"Ошибка при обработке изображения {file_path}: {e}")

# Функция для абскейлинга изображений
def upscale_images_in_folder(folder, scale_factor, message_label, progress_bar):
    try:
        message_label.pack()  # Показываем сообщение "Ожидайте, пожалуйста"
        with concurrent.futures.ThreadPoolExecutor() as executor:
            files = []
            for root, dirs, files_in_dir in os.walk(folder):
                for file in files_in_dir:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        file_path = os.path.join(root, file)
                        files.append(file_path)
            total_files = len(files)

            # Запускаем асинхронное преобразование для каждого файла
            for index, file_path in enumerate(files):
                executor.submit(process_upscale, file_path, scale_factor, progress_bar, index, total_files)

        messagebox.showinfo("Успех", f"Все изображения в папке увеличены в {scale_factor} раза.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при увеличении изображений: {str(e)}")
    finally:
        message_label.pack_forget()  # Скрываем сообщение "Ожидайте, пожалуйста"

# Функция для асинхронного абскейлинга
def process_upscale(file_path, scale_factor, progress_bar, current_index, total_files):
    try:
        img = Image.open(file_path)
        width, height = img.size
        img_resized = img.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)
        new_file_path = os.path.splitext(file_path)[0] + f"_{scale_factor}x" + ".png"
        img_resized.save(new_file_path, format="PNG")

        # Обновляем прогресс-бар
        progress_bar['value'] = (current_index + 1) / total_files * 100
        progress_bar.update()
    except Exception as e:
        print(f"Ошибка при обработке изображения {file_path}: {e}")

# Основная программа
def main():
    # Создаем окно с бежевым фоном
    root = Tk()
    root.title("Программа для обработки файлов")
    root.geometry("600x500")
    root.config(bg="#f5f5dc")

    # Создаем метку для уведомления и прогресс-бар
    message_label = Label(root, text="Ожидайте, пожалуйста...", font=("Arial", 12, "italic"), fg="brown", bg="#f5f5dc")
    progress_bar = ttk.Progressbar(root, length=400, mode="determinate")

    # Создаем кнопки
    button_style = {"width": 20, "height": 2, "font": ("Arial", 12, "italic bold"), "bg": "#a8e6cf", "fg": "brown"}

    Button(root, text="Сортировка по дате", command=lambda: sort_files_by_date(open_folder_dialog(), message_label), **button_style).pack(pady=5)
    Button(root, text="Переименовать", command=lambda: rename_files_in_folder(open_folder_dialog(), message_label), **button_style).pack(pady=5)
    Button(root, text="Поиск дубликатов", command=lambda: find_duplicates(open_folder_dialog(), message_label), **button_style).pack(pady=5)
    Button(root, text="Абскейлинг (2x)", command=lambda: upscale_images_in_folder(open_folder_dialog(), 2, message_label, progress_bar), **button_style).pack(pady=5)
    Button(root, text="Абскейлинг (4x)", command=lambda: upscale_images_in_folder(open_folder_dialog(), 4, message_label, progress_bar), **button_style).pack(pady=5)
    Button(root, text="Абскейлинг (8x)", command=lambda: upscale_images_in_folder(open_folder_dialog(), 8, message_label, progress_bar), **button_style).pack(pady=5)
    Button(root, text="Ч/Б преобразование", command=lambda: convert_to_grayscale(open_folder_dialog(), message_label, progress_bar), **button_style).pack(pady=5)
    Button(root, text="Сепия", command=lambda: convert_to_sepia(open_folder_dialog(), message_label, progress_bar), **button_style).pack(pady=5)

    # Прогресс-бар и метка уведомления
    progress_bar.pack(pady=10)

    root.mainloop()

# Запуск программы
if __name__ == "__main__":
    main()
