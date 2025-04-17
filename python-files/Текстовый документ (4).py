import os
from bs4 import BeautifulSoup # type: ignore

# Укажите путь к распакованному архиву
folder_path = "C:\Users\user\Downloads\AyuGram Desktop\ChatExport_2025-04-17"

for filename in os.listdir(folder_path):
    if filename.endswith(".html"):
        with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            text = soup.get_text(separator="\n")
            print(f"Файл {filename}:\n{text}\n---")