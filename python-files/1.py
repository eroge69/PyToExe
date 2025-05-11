import os
import platform
import time
from getpass import getpass  # Ẩn mật khẩu khi nhập

# Mật khẩu cố định để truy cập file bí mật (không dấu)
SECRET_PASSWORD = "matkhaubimat"  # Viết không dấu, thay đổi theo nhu cầu

print("File Test")

# Nhập mật khẩu từ người dùng (không hiển thị khi nhập)
user_pass = getpass("Enter the password to access the secret file (write unaccented text): ")

# Xóa màn hình sau khi nhập mật khẩu (tùy hệ điều hành)
if platform.system() == "Windows":
    os.system("cls")
else:
    os.system("clear")

# Kiểm tra mật khẩu
if user_pass == SECRET_PASSWORD:
    print("Congratulations! You have access to the secret file.")
    try:
        with open(r"D:\Test code\Python\Project 1\Happy secret.txt", "r", encoding='utf-8') as file:
            content = file.read()
            print("You are allowed to access this file")
            print("Here is the content of the file:")
            print("----------------------------------")
            print(content)
    except FileNotFoundError:
        print("Error: Secret file not found at specified path.")
    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print("You are not allowed to access this file.")
    print("Please contact the administrator for access.")
    print("Exiting the program in:")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)
    print("Exiting the program...")
    time.sleep(1)
