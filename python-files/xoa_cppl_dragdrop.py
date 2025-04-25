import sys
import os
import re

def clean_cppl_tags(file_path):
    # Đọc nội dung file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Xóa nội dung giữa <CPPl> và </CPPl>, giữ lại tag
    cleaned = re.sub(r"(<CPPl>).*?(</CPPl>)", r"\1\2", content, flags=re.DOTALL)

    # Tạo tên file mới
    base, ext = os.path.splitext(file_path)
    new_file = base + "_clean" + ext

    # Ghi file mới
    with open(new_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"Đã xử lý: {os.path.basename(file_path)}")
    print(f"File mới: {os.path.basename(new_file)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kéo thả file .aepx vào script này để xử lý.")
    else:
        for path in sys.argv[1:]:
            if path.lower().endswith(".aepx"):
                clean_cppl_tags(path)
            else:
                print(f"Bỏ qua file không hợp lệ: {path}")
