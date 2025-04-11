import tkinter as tk
from tkinter import scrolledtext
import requests
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Настройки Google Custom Search API
API_KEY = "AIzaSyBTZf17H9rJlhC6B2l-5GAwHrM6MNXyft4"
CX = "502215f01a95243ca"

nltk.download('punkt')
nltk.download('stopwords')

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={'AIzaSyBTZf17H9rJlhC6B2l-5GAwHrM6MNXyft4'}&cx={'502215f01a95243ca'}&q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def process_query():
    query = entry.get("1.0", tk.END).strip()
    result_text.delete("1.0", tk.END)  # Очистить предыдущие результаты
    response = search_google(query)
    if response and 'items' in response:
        snippets = [item['snippet'] for item in response['items']]
        text = ' '.join(snippets).replace('\n', ' ')
        
        # Упрощенная обработка текста
        stop_words = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        sentences = sent_tokenize(text)
        summary = ''
        for sentence in sentences:
            words = [stemmer.stem(word.lower()) for word in sentence.split() if word.isalpha() and word.lower() not in stop_words]
            if len(words) > 5:  # Используем предложения с достаточным количеством значимых слов
                summary += sentence + ' '
        
        # Выводим либо краткое резюме, либо исходный текст, если резюме слишком короткое
        if len(summary.strip()) > 50:
            result_text.insert(tk.END, summary.strip())
        else:
            result_text.insert(tk.END, text[:500])  # Ограничиваем длину выводимого текста
    else:
        result_text.insert(tk.END, "По вашему запросу ничего не найдено.")

root = tk.Tk()
root.title("ИИ Помощник")

entry = scrolledtext.ScrolledText(root, width=60, height=5)
entry.pack(padx=10, pady=10)

button = tk.Button(root, text="Задать вопрос", command=process_query)
button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=60, height=15)
result_text.pack(padx=10, pady=10)

root.mainloop()
