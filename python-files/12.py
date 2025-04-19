import os
from collections import defaultdict

def get_folder_path():
    folder = input("Укажи путь к папке, где искать файлы: ").strip().strip('"')
    while not os.path.isdir(folder):
        print("❌ Папка не найдена. Попробуй снова.")
        folder = input("Укажи путь к папке: ").strip().strip('"')
    return folder

def get_file_extension():
    ext = input("Укажи тип файлов для анализа (например, .reg, .txt): ").strip()
    if not ext.startswith('.'):
        ext = '.' + ext
    return ext.lower()

def read_file_lines(path):
    lines = set()
    try:
        with open(path, encoding="utf-16") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith(";"):
                    lines.add(line)
    except:
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(";"):
                        lines.add(line)
        except:
            print(f"[!] Не удалось прочитать файл: {path}")
    return lines

def find_duplicates(folder, extension):
    line_to_files = defaultdict(set)
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(extension):
                full_path = os.path.join(root, file)
                for line in read_file_lines(full_path):
                    line_to_files[line].add(full_path)
    return {line: files for line, files in line_to_files.items() if len(files) > 1}

def write_report(duplicates, output_path):
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("=== Найденные одинаковые строки ===\\n\\n")
        for line, files in duplicates.items():
            out.write(f"Строка:\\n{line}\\n")
            for f in files:
                out.write(f"  └─ В файле: {f}\\n")
            out.write("\\n" + "-"*60 + "\\n\\n")

def main():
    print("📁 Анализ одинаковых строк в файлах\\n")
    folder = get_folder_path()
    extension = get_file_extension()
    print("\\n🔍 Идёт поиск...")
    duplicates = find_duplicates(folder, extension)
    report_path = os.path.join(folder, "duplicates_report.txt")
    write_report(duplicates, report_path)
    print(f"✅ Готово! Отчёт сохранён в: {report_path}")

if __name__ == "__main__":
    main()
