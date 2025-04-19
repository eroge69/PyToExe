
import sys
import re
import os

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # 替換 random(a, b, c) → random(a, b)
    def fix_random(match):
        parts = match.group(1).split(',')
        if len(parts) >= 3:
            return f"random({parts[0].strip()}, {parts[1].strip()})"
        return match.group(0)

    new_content = re.sub(r"random\(([^)]+)\)", fix_random, content)

    # 覆蓋原檔案
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(new_content)

    print(f"處理完成：{filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("請將 .txt 檔案拖到這個程式上")
    else:
        for filepath in sys.argv[1:]:
            if os.path.isfile(filepath) and filepath.endswith(".txt"):
                process_file(filepath)
