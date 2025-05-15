import tkinter as tk
from tkinter import filedialog

def upload_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")],
        title="Chọn ảnh để upload"
    )
    if file_path:
        print(f"Đã chọn file: {file_path}")
        # Bạn có thể thêm code xử lý ảnh tại đây

def set_username():
    username = input_username.get()  # Lấy giá trị từ input_field1
    if username:
        print(f"Đã đặt username: {username}")
    else:
        print("Username không được để trống")

def set_sodu():
    sodu = input_sodu.get()  # Lấy giá trị từ input_field1
    if sodu:
        print(f"Đã đặt username: {sodu}")
    else:
        print("Username không được để trống")

        

root = tk.Tk()
root.title("Bet giả lập 1.0")

# Lấy kích thước màn hình
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Cửa sổ chiếm 1/4 chiều rộng, full chiều cao và nằm bên phải màn hình
window_width = screen_width // 4
window_height = screen_height
x_position = screen_width - window_width
y_position = 0

# Đặt vị trí và kích thước cửa sổ
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Thiết lập font mặc định
default_font = ('Arial', 12)
root.option_add("*Font", default_font)

# --------- Nút Upload Image ở hàng đầu tiên ---------
wrapperUploadImage = tk.Frame(root)
wrapperUploadImage.grid(row=0, column=0, padx=0, pady=20, sticky="ew")

# Label
label = tk.Label(wrapperUploadImage, text="Chọn ảnh che:")
label.grid(row=0, column=0, sticky="w", padx=30, pady=5)

# Button
button = tk.Button(wrapperUploadImage, text="Chọn ảnh", command=upload_image, bg="blue", fg="white", padx=50, pady=5)
button.grid(row=0, column=1, sticky="e")

# --------- Hàng 2 ---------
row = 1

# Cột 1: Label và button cho username
set_username_button = tk.Button(root, text="Đặt username", command=set_username, bg="blue", fg="white")
set_username_button.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

# set_username_button = tk.Button(root, text="Xác nhận username", command=set_username, bg="blue", fg="white")
# set_username_button.grid(row=row, column=2, sticky="ew", padx=10, pady=5)

input_username = tk.Entry(root)
input_username.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

# Cột 2: Label và button cho số dư
row += 1
set_sodu_button = tk.Button(root, text="Đặt số dư", command=set_sodu, bg="blue", fg="white")
set_sodu_button.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

input_sodu = tk.Entry(root)
input_sodu.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

# --------- Hàng 3 ---------
row += 1
input_field3 = tk.Entry(root)
input_field3.grid(row=row, column=0, sticky="ew", padx=10, pady=50)

button_bet = tk.Button(root, text="Đặt cược", bg="blue", fg="white", height=2)
button_bet.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

# --------- Hàng 4: Các lựa chọn thắng thua ---------
row += 1
button_win = tk.Button(root, text="Con thắng", bg="green", fg="white", height=2)
button_win.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

button_lose = tk.Button(root, text="Cái thắng", bg="green", fg="white", height=2)
button_lose.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

# --------- Hàng 5: Các lựa chọn hòa và thua ---------
row += 1
button_draw = tk.Button(root, text="Hòa", bg="#ff7f00", fg="white", height=2)
button_draw.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

button_lose = tk.Button(root, text="Thua", bg="red", fg="white", height=2)
button_lose.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

# --------- Hàng 6: Khu vực log ---------
row += 1
log_frame = tk.Frame(root)
log_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

log_box = tk.Text(log_frame, height=30)
log_box.pack(fill="both", expand=True)
log_box.insert(tk.END, "")

# Cấu hình để cột 0 và cột 1 có thể mở rộng
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
