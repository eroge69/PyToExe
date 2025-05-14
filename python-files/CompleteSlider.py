import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial
import os

# --- Configuration ---
THUMBNAIL_WIDTH = 100
THUMBNAIL_HEIGHT = 75
BUTTON_WIDTH = 15
BUTTON_HEIGHT = 2
FONT_NORMAL = ("Arial", 10)
FONT_BOLD = ("Arial", 20, "bold")
FONT_TITLE = ("Arial", 24, "bold")

# --- Target image and description sizes ---
TARGET_IMAGE_WIDTH = 700
TARGET_IMAGE_HEIGHT = 400
TARGET_DESCRIPTION_HEIGHT_FACTOR = 0.5

# --- Dummy Image Data ---
t1 = "الكود : 8473 \n\n" +   "قطعه نسيج قباطي متعددة الالوان جزء من قميص او ستاره بخيوط الصوف والكتان" + "وذات الزخارف ملونه داخل مربعين واطار يحيط بهما بسخارف الاشكال ادميه في حركات واوضاع مختلفه بعضها نصفي"+"والبعض الاخر في حركه مع مخلوقات بحريه داخل اشكال هندسيينقرن 6  7 ميلادي"
t4= " 2011 \n\n" +  "قطعة من النسيج القباطى من الصوف  عليها شكل زخرفى لصليب متعدد الالوان بيه زخارف محورة ادمية ونباتية وطيور القرن ٥/ ٦"   
t7 = " الكود ٧٨٢٢ \n\n" + "قطعة نسيج متعددة الالوان من نسيج القباطى والنسيج الوبرى بخيوط الصوف والكتان عليها زخرف فى الوسط الحيوانى الاسطورى ( القنطور) داخل دائرة وفى الاركان راقصات واسد  وارنب بينهم سلال فاكهة القرن ٤-٥ ممشترهاه من تانو"
t8 = " الكود 4763\n\n" + "قطعة من النسيج القباطى من الكتان والصوف عليها زخرف دائرة بها نسر ناشرا جناحيه بالالوان القرن ٤ - ٥"
image_data = [
    {"path": "image1.jpg", "details": t1},
    {"path": "image4.jpg", "details": t4},
    {"path": "image7.jpg", "details": t7},
    {"path": "image8.jpg", "details": t8}
]

# --- Create dummy images ---
for i, data in enumerate(image_data):
    if not os.path.exists(data["path"]) and "missing" not in data.get("path", ""):
        try:
            img = Image.new('RGB', (600, 400), color='lightcoral')
            img.save(data["path"])
        except Exception as e:
            print(f"Error creating dummy image {data['path']}: {e}")


def display_image_and_details(image_path, details, image_label, details_container):
    try:
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            img_resized = img.resize((TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img_resized)

            image_label.config(image=photo)
            image_label.image = photo

            details_container_frame = details_container
            details_container_frame.config(width=TARGET_IMAGE_WIDTH,
                                           height=int(TARGET_IMAGE_HEIGHT * TARGET_DESCRIPTION_HEIGHT_FACTOR))

            details_label_widget = details_container_frame.winfo_children()[0]
            details_label_widget.config(text=details, wraplength=TARGET_IMAGE_WIDTH - 20, bg="gray", fg="white")  # Apply colors

        elif image_path and not os.path.exists(image_path):
            image_label.config(text="Image not found", image="", width=TARGET_IMAGE_WIDTH // 10,
                            height=TARGET_IMAGE_HEIGHT // 20)
            image_label.image = None
            details_label_widget = details_container.winfo_children()[0]
            details_label_widget.config(text=f"Error: Image file not found at {image_path}",
                            wraplength=TARGET_IMAGE_WIDTH - 20, bg="gray", fg="white")  # Apply colors
        else:
            image_label.config(text="No image selected" if not image_path else "Image error",
                            image="", width=TARGET_IMAGE_WIDTH // 10, height=TARGET_IMAGE_HEIGHT // 20)
            image_label.image = None
            details_label_widget = details_container.winfo_children()[0]
            details_label_widget.config(text=details if details else "No details provided.",
                            wraplength=TARGET_IMAGE_WIDTH - 20, bg="gray", fg="white")  # Apply colors

    except FileNotFoundError:
        image_label.config(text="Image not found (FNF)", image="", width=TARGET_IMAGE_WIDTH // 10,
                        height=TARGET_IMAGE_HEIGHT // 20)
        image_label.image = None
        details_label_widget = details_container.winfo_children()[0]
        details_label_widget.config(text=f"Error: Image file not found at {image_path}",
                        wraplength=TARGET_IMAGE_WIDTH - 20, bg="gray", fg="white")  # Apply colors

    except Exception as e:
        print(f"Error in display_image_and_details: {e}")
        image_label.config(text="Error loading image", image="", width=TARGET_IMAGE_WIDTH // 10,
                        height=TARGET_IMAGE_HEIGHT // 20)
        image_label.image = None
        details_label_widget = details_container.winfo_children()[0]
        details_label_widget.config(text=f"Error loading image: {e}",
                        wraplength=TARGET_IMAGE_WIDTH - 20, bg="gray", fg="white")  # Apply colors


def create_slider_page(root, navigate_to_room1, navigate_to_home):
    page_frame = ttk.Frame(root)
    page_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    main_area = ttk.Frame(page_frame)
    main_area.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    center_frame = ttk.Frame(main_area)
    center_frame.pack(expand=True)

    image_and_details_frame = ttk.Frame(center_frame)
    image_and_details_frame.pack()

    image_label = tk.Label(image_and_details_frame, image=None,
                           bg="lightgrey", relief="groove", borderwidth=1)
    image_label.configure(width=TARGET_IMAGE_WIDTH, height=TARGET_IMAGE_HEIGHT)
    image_label.pack()

    details_container_frame = ttk.Frame(image_and_details_frame)
    details_container_frame.pack(pady=0, anchor='center', fill='x')
    details_container_frame.pack_propagate(False)

    details_label = tk.Label(  # This is the original label
        details_container_frame,
        text="",
        justify="center",
        bg="#ADD8E6",  # Original background
        fg="black",
        font=("Arial", 12, "bold"),
        padx=10,
        pady=5,
        relief="groove",
        borderwidth=1
    )
    details_label.pack(fill="both", expand=True)

    thumb_container = ttk.Frame(page_frame, width=THUMBNAIL_WIDTH + 40)
    thumb_container.pack(side="right", fill="y", padx=(0, 10), pady=10)
    thumb_container.pack_propagate(False)

    thumb_canvas = tk.Canvas(thumb_container, borderwidth=0, highlightthickness=0, background="#ffffff")
    thumb_frame = tk.Frame(thumb_canvas, background="#000000")
    thumb_scrollbar = ttk.Scrollbar(thumb_container, orient="vertical", command=thumb_canvas.yview)
    thumb_canvas.configure(yscrollcommand=thumb_scrollbar.set)

    thumb_scrollbar.pack(side="right", fill="y")
    thumb_canvas.pack(side="left", fill="both", expand=True)
    thumb_canvas_window = thumb_canvas.create_window((0, 0), window=thumb_frame, anchor="nw")

    def on_frame_configure(event):
        thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all"))
        thumb_canvas.itemconfig(thumb_canvas_window, width=event.width)

    thumb_frame.bind("<Configure>", on_frame_configure)

    def on_mouse_wheel(event):
        delta = 0
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        elif event.delta > 0:
            delta = -1
        elif event.delta < 0:
            delta = 1
        if delta != 0:
            thumb_canvas.yview_scroll(delta, "units")

    thumb_canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    thumb_canvas.bind_all("<Button-4>", on_mouse_wheel)
    thumb_canvas.bind_all("<Button-5>", on_mouse_wheel)

    thumbnail_photos = []

    def update_main_display_closure(index):
        if 0 <= index < len(image_data):
            data = image_data[index]
            display_image_and_details(data["path"], data["details"], image_label, details_container_frame)
        else:
            display_image_and_details(None, "Invalid image index.", image_label, details_container_frame)

    for i, data in enumerate(image_data):
        try:
            if not os.path.exists(data["path"]) and "missing" not in data.get("path", ""):
                placeholder_path = f"placeholder_thumb_{i}.png"
                if not os.path.exists(placeholder_path):
                    Image.new('RGB', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), color='grey').save(placeholder_path)
                img_path_for_thumb = placeholder_path
                actual_display_path = data["path"]
                print(f"Using placeholder for thumbnail: {data['path']}")
            else:
                img_path_for_thumb = data["path"]
                actual_display_path = data["path"]

            img_thumb = Image.open(img_path_for_thumb)
            img_thumb.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.LANCZOS)
            photo_thumb = ImageTk.PhotoImage(img_thumb)
            thumbnail_photos.append(photo_thumb)

            thumb_button = tk.Button(thumb_frame, image=photo_thumb, relief="flat", borderwidth=1,
                                     bg='#ffffff', activebackground='#e0e0e0',
                                     command=partial(update_main_display_closure, i))
            thumb_button.image = photo_thumb
            thumb_button.pack(pady=5, padx=5, anchor='n')
            thumb_button.configure(cursor="hand2")

            def enter(e, b=thumb_button):
                b.config(bg='#f0f0f0')

            def leave(e, b=thumb_button):
                b.config(bg='#ffffff')

            thumb_button.bind("<Enter>", enter)
            thumb_button.bind("<Leave>", leave)

        except FileNotFoundError:
            print(f"Thumbnail Error: Image not found - {data['path']}")
            error_label_thumb = tk.Label(thumb_frame, text=f"Missing:\n{os.path.basename(data['path'])}",
                                   font=("Arial", 8), relief="solid", borderwidth=1, bg="lightcoral",
                                   width=THUMBNAIL_WIDTH // 7, wraplength=THUMBNAIL_WIDTH - 10, justify="center")
            error_label_thumb.pack(pady=5, padx=5, anchor='n')
        except Exception as e:
            print(f"Error creating thumbnail for {data['path']}: {e}")
            error_label_thumb = tk.Label(thumb_frame, text="Error", font=("Arial", 8),
                                   width=THUMBNAIL_WIDTH // 7, relief="solid", borderwidth=1, bg="lightcoral",
                                   justify="center")
            error_label_thumb.pack(pady=5, padx=5, anchor='n')

    if image_data:
        update_main_display_closure(0)
    else:
        display_image_and_details(None, "No image data configured.", image_label, details_container_frame)

    page_frame.update_idletasks()
    thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all"))
    if thumb_frame.winfo_exists():
        thumb_canvas.itemconfig(thumb_canvas_window, width=thumb_frame.winfo_width())
    return page_frame


def add_return_to_video_button(root_window):
    button_text_arabic = "العودة إلى الفيديو"

    def on_return_to_video_click():
        print("Return to video button clicked!")

    return_button = tk.Button(
        root_window,
        text=button_text_arabic,
        background="orange",
        foreground="white",
        font=FONT_BOLD,
        command=on_return_to_video_click,
        relief="raised",
        borderwidth=1
    )

    return_button.place(relx=0.0, rely=0.05, x=10, anchor="nw")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Slider with Return Button")

    max_width = root.winfo_screenwidth()
    max_height = root.winfo_screenheight()
    root.geometry(f"{max_width}x{max_height}+0+0")
    root.attributes("-topmost", True)

    title_bar = tk.Frame(root, bg="gray", height=50)
    title_bar.pack(fill=tk.X)

    title_label = tk.Label(title_bar, text="معرض صور الغرفة 1", font=FONT_TITLE, bg="gray", fg="white")
    title_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def navigate_to_room1():
        print("Navigating to Room 1")

    def navigate_to_home():
        print("Navigating to Home")

    slider_page = create_slider_page(root, navigate_to_room1, navigate_to_home)

    add_return_to_video_button(root)

    root.mainloop()