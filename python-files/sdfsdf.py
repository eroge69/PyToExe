import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import concurrent.futures

# =======================
# КОНФИГУРАЦИЯ (настройте эти параметры здесь)
# =======================
# Параметры маски исходного 500x500 видео.
MASK_CENTER_X = 250
MASK_CENTER_Y = 250
MASK_RADIUS   = 250
# Параметры наложения на фон (фоновое видео всегда 1080×1920).
# Измените эти константы, чтобы задать расположение кружка на фоне.
OVERLAY_X = "80"   # горизонтальная координата
OVERLAY_Y = "610"   # вертикальная координата
# Масштаб (диаметр) кружка на фоне (в пикселях).
CIRCLE_DIAMETER = 920
# =======================

def process_single_video(file, input_folder, output_folder, background_video):
    input_path = os.path.join(input_folder, file)
    base, _ = os.path.splitext(file)
    output_file = os.path.join(output_folder, f"{base}_output.mp4")
    
    # Вычисляем квадрат радиуса для фильтра
    r_squared = MASK_RADIUS ** 2

    if background_video:
        # Формируем filter_complex:
        # 1. Создаём маску с фиксированными параметрами: центр [MASK_CENTER_X, MASK_CENTER_Y], радиус MASK_RADIUS.
        filter_mask = (
            f"[1:v]format=rgba,geq="
            f"r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
            f"a='if(gt((X-{MASK_CENTER_X})*(X-{MASK_CENTER_X})+(Y-{MASK_CENTER_Y})*(Y-{MASK_CENTER_Y}),{r_squared}),0,255)'[mask]"
        )
        # 2. Масштабируем результат до нужного размера (CIRCLE_DIAMETER x CIRCLE_DIAMETER).
        filter_scale = f"[mask]scale={CIRCLE_DIAMETER}:{CIRCLE_DIAMETER}[sm]"
        # 3. Накладываем полученный клип на фоновое видео с фиксированными координатами.
        filter_overlay = f"[0:v][sm]overlay={OVERLAY_X}:{OVERLAY_Y}[v]"
        # 4. Микшируем аудио из фонового ([0:a]) и исходного ([1:a]) видео.
        filter_amix = "[0:a][1:a]amix=inputs=2:duration=shortest[a]"
        filter_complex = filter_mask + ";" + filter_scale + ";" + filter_overlay + ";" + filter_amix

        command = [
            'ffmpeg',
            '-y',
            '-hwaccel', 'cuda', '-i', background_video,  # фоновое видео (индекс 0)
            '-hwaccel', 'cuda', '-i', input_path,         # исходное 500x500 видео (индекс 1)
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '[a]',
            '-shortest',  # итоговое видео ограничивается длительностью самого короткого потока
            '-c:v', 'h264_nvenc',  # аппаратное кодирование через NVENC
            '-preset', 'fast',
            '-c:a', 'aac', '-b:a', '192k',
            output_file
        ]
    else:
        # Если фоновое видео не выбрано, просто применяем маску к исходному видео.
        filter_mask = (
            f"format=rgba,geq="
            f"r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
            f"a='if(gt((X-{MASK_CENTER_X})*(X-{MASK_CENTER_X})+(Y-{MASK_CENTER_Y})*(Y-{MASK_CENTER_Y}),{r_squared}),0,255)'"
        )
        command = [
            'ffmpeg',
            '-y',
            '-hwaccel', 'cuda', '-i', input_path,
            '-vf', filter_mask,
            '-c:v', 'qtrle',  # формат MOV с альфа-каналом для прозрачности
            '-c:a', 'copy',
            output_file
        ]
    
    subprocess.run(command, check=True)
    return output_file

def select_input_folder():
    folder_selected = filedialog.askdirectory(title="Выберите папку с исходными видео (500x500)")
    if folder_selected:
        input_folder_var.set(folder_selected)

def select_output_folder():
    folder_selected = filedialog.askdirectory(title="Выберите папку для сохранения результата")
    if folder_selected:
        output_folder_var.set(folder_selected)

def select_background_file():
    file_selected = filedialog.askopenfilename(
        title="Выберите фоновое .mp4 видео (1080x1920)",
        filetypes=[("MP4 файлы", "*.mp4")]
    )
    if file_selected:
        background_file_var.set(file_selected)

def process_videos():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    background_video = background_file_var.get()  # может быть пустым

    if not input_folder or not output_folder:
        messagebox.showerror("Ошибка", "Выберите папку с видео и папку для сохранения результата!")
        return

    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    files = [f for f in os.listdir(input_folder)
             if os.path.splitext(f)[1].lower() in video_extensions]
    if not files:
        messagebox.showwarning("Предупреждение", "В выбранной папке нет видеофайлов!")
        return

    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_file = {
            executor.submit(process_single_video, file, input_folder, output_folder, background_video): file
            for file in files
        }
        for future in concurrent.futures.as_completed(future_to_file):
            file_name = future_to_file[future]
            try:
                out = future.result()
                print(f"Файл {file_name} обработан: {out}")
            except Exception as exc:
                errors.append(f"Ошибка при обработке файла {file_name}: {exc}")

    if errors:
        messagebox.showerror("Ошибки", "\n".join(errors))
    else:
        messagebox.showinfo("Готово", "Обработка видео завершена!")

# =======================
# Создаем GUI (только для выбора путей)
# =======================
root = tk.Tk()
root.title("Обработка видео: наложение кружка на фон (конфигурация в коде)")

# Переменные для путей
input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
background_file_var = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# Выбор папки с исходными видео (500x500)
tk.Label(frame, text="Папка с видео (500x500):").grid(row=0, column=0, sticky="e")
tk.Entry(frame, textvariable=input_folder_var, width=50).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Выбрать", command=select_input_folder).grid(row=0, column=2, padx=5)

# Выбор папки для сохранения результата
tk.Label(frame, text="Папка для сохранения:").grid(row=1, column=0, sticky="e")
tk.Entry(frame, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5)
tk.Button(frame, text="Выбрать", command=select_output_folder).grid(row=1, column=2, padx=5)

# Выбор фонового видео (1080x1920)
tk.Label(frame, text="Фоновое .mp4 видео (1080x1920):").grid(row=2, column=0, sticky="e")
tk.Entry(frame, textvariable=background_file_var, width=50).grid(row=2, column=1, padx=5)
tk.Button(frame, text="Выбрать", command=select_background_file).grid(row=2, column=2, padx=5)

# Кнопка запуска обработки
tk.Button(frame, text="Начать обработку", command=process_videos)\
    .grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
