import os
import pyzipper
import secrets
import string
import sys

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    # مسیر پوشه‌ای که فایل exe توش هست
    current_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    folder_name = os.path.basename(current_dir)

    zip_name = f"{folder_name}.zip"
    password_file_name = f"{folder_name}-password.txt"
    password_file_path = os.path.join(current_dir, password_file_name)

    script_name = os.path.basename(sys.argv[0])

    # ساخت پسورد قوی
    password = generate_password()

    # ساخت فایل زیپ با رمزگذاری
    with pyzipper.AESZipFile(os.path.join(current_dir, zip_name), 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode())

        for root, _, files in os.walk(current_dir):
            for file in files:
                if file in [script_name, zip_name, password_file_name]:
                    continue  # اسکریپت، فایل زیپ و فایل پسورد نره توی زیپ

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, current_dir)
                zf.write(file_path, arcname)

    # نوشتن پسورد توی فایل متنی
    with open(password_file_path, 'w') as f:
        f.write(password)

    print("✅ ZIP created and password saved.")
    print(f"Zip: {zip_name}")
    print(f"Password file: {password_file_name}")

if __name__ == "__main__":
    main()
