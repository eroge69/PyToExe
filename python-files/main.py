import subprocess
import os
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def save_last_application_path(path):
    with open("last_application.txt", "w") as file:
        file.write(path)

def load_last_application_path():
    try:
        with open("last_application.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def launch_timer(timer_path_label, root):
    path_to_timer = timer_path_label.cget("text")

    if path_to_timer:
        process = subprocess.Popen([path_to_timer])
        save_last_application_path(path_to_timer)  # Save the last launched application path
        return process

def record_duration(filename, start_time, end_time):
    duration_seconds = round(end_time - start_time, 2)

    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_duration = f'{int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}'

    start_datetime = time.strftime('%d-%m %H:%M:%S', time.localtime(start_time))
    end_datetime = time.strftime('%d-%m %H:%M:%S', time.localtime(end_time))

    record = f'Duration: {formatted_duration} / {start_datetime} / {end_datetime}'

    if os.path.exists(filename):
        with open(filename, 'a') as file:
            file.write(f'\n{record}')
    else:
        with open(filename, 'w') as file:
            file.write(record)

def is_process_running(process):
    return process.poll() is None

def browse_timer_path(timer_path_label):
    path_to_timer = filedialog.askopenfilename()
    timer_path_label.config(text=path_to_timer)

def set_image_as_background(root, image_path):
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)
    background_label = tk.Label(root, image=photo, bg="gray")  # Set background color to gray
    background_label.image = photo
    background_label.place(relwidth=1, relheight=1)
    root.geometry(f"{image.width}x{image.height}")
    return background_label  # Return the created label

def on_launch_button_click(timer_path_label, root, background_label):
    timer_process = launch_timer(timer_path_label, root)

    if timer_process:
        start_time = time.time()

        while is_process_running(timer_process):
            time.sleep(1)

        end_time = time.time()

        timer_filename = os.path.basename(timer_path_label.cget("text"))
        duration_filename = f'{timer_filename}_duration.txt'

        record_duration(duration_filename, start_time, end_time)
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Timer")

    # Load the image and get the background_label
    background_label = set_image_as_background(root, "U:\Grisaia.png")  # Replace with the actual path to your image

    timer_path_label = tk.Label(root, text=load_last_application_path())
    timer_path_label.pack()

    browse_button = tk.Button(root, text="Browse", command=lambda: browse_timer_path(timer_path_label))
    browse_button.pack()

    launch_button = tk.Button(root, text="Launch Timer", command=lambda: on_launch_button_click(timer_path_label, root, background_label))
    launch_button.pack()

    root.mainloop()
