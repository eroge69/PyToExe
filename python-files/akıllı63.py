Python 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
import datetime
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw
import io
import openai

# OPENAI API anahtarı (gerekirse buraya ekleyin)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Konuşma motorunu başlat
engine = pyttsx3.init()
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.thomas' if 'com.apple' in engine.getProperty('driverName') else engine.getProperty('voices')[0].id)

# Sesli konuşma fonksiyonu
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Yazıyı sese dönüştürme ve yazılı çıktı

def respond(text):
    print("Akıllı:", text)
    speak(text)

# Hava durumu bilgisi (örnek olarak OpenWeatherMap API kullanılıyor)
def get_weather(city="Istanbul"):
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=tr&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get("main"):
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        respond(f"{city} için hava durumu: {description}, sıcaklık {temp}°C.")
    else:
        respond("Hava durumu alınamadı.")

# Basit çizim aracı
def draw_image():
    image = Image.new("RGB", (400, 400), "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((100, 100, 300, 300), fill="blue")
    image.show()

# İnternette arama fonksiyonu
def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    respond(f"İnternette {query} için sonuçları gösteriyorum.")

# ChatGPT ile sohbet
def chat_with_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        message = response['choices'][0]['message']['content']
        respond(message)
    except Exception as e:
        respond("Bir hata oluştu: " + str(e))

# Sesli komut algılayıcı
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Dinleniyor...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio, language="tr-TR")
            print("Sen:", command)
            return command.lower()
        except:
            return ""

# "Hey Akıllı!" tetikleyicisini dinle

def listen_for_wake_word():
    while True:
        command = listen()
        if "hey akıllı" in command:
            respond("Buradayım!")
            handle_command()

# Komutları yönet

def handle_command():
    command = listen()

    if "hava durumu" in command:
        get_weather()
    elif "ara" in command:
        respond("Ne aramamı istersin?")
        query = listen()
        search_web(query)
    elif "çizim" in command:
        draw_image()
    elif "konuş" in command or "sohbet" in command:
        respond("Ne hakkında konuşmak istersin?")
        prompt = listen()
...         chat_with_ai(prompt)
...     else:
...         respond("Bunu anlayamadım.")
... 
... # Klavyeden komut girme arayüzü
... def start_gui():
...     def on_submit():
...         user_input = entry.get()
...         if user_input:
...             respond("Komut alındı.")
...             if "hava" in user_input:
...                 get_weather()
...             elif "ara" in user_input:
...                 search_web(user_input.replace("ara", ""))
...             elif "çiz" in user_input:
...                 draw_image()
...             elif "konuş" in user_input or "sohbet" in user_input:
...                 chat_with_ai(user_input)
...             else:
...                 respond("Anlamadım. Lütfen tekrar edin.")
... 
...     root = tk.Tk()
...     root.title("Akıllı Asistan")
...     root.geometry("400x150")
... 
...     label = tk.Label(root, text="Komut girin veya 'Hey Akıllı!' deyin:")
...     label.pack(pady=10)
... 
...     entry = tk.Entry(root, width=50)
...     entry.pack(pady=5)
... 
...     button = tk.Button(root, text="Gönder", command=on_submit)
...     button.pack(pady=10)
... 
...     threading.Thread(target=listen_for_wake_word, daemon=True).start()
...     root.mainloop()
... 
... # Uygulamayı başlat
... if __name__ == "__main__":
...     respond("Merhaba, ben Akıllı. Size nasıl yardımcı olabilirim?")
...     start_gui()
