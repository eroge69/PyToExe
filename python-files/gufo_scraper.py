import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, filedialog

def fetch_words(url):
    words = []
    page = 1
    while True:
        response = requests.get(f"{url}&page={page}")
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        word_elements = soup.select('.word-list-item__word')
        if not word_elements:
            break
        for element in word_elements:
            words.append(element.text.strip())
        page += 1
    return words

def start_scraping():
    url = entry.get()
    if not url:
        messagebox.showerror("Ошибка", "Пожалуйста, введите URL.")
        return
    try:
        words = fetch_words(url)
        if words:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(words))
                messagebox.showinfo("Успех", f"Собрано {len(words)} слов.")
        else:
            messagebox.showinfo("Результат", "Слова не найдены.")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

root = tk.Tk()
root.title("Gufo Scraper")

tk.Label(root, text="Введите URL:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)
tk.Button(root, text="Собрать слова", command=start_scraping).pack(pady=10)

root.mainloop()
