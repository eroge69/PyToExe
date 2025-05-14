import os
import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox
from dotenv import load_dotenv
from datetime import datetime
import pytz
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
import pygame
import threading
import requests
from io import BytesIO
import traceback

# Настройка аудио для подавления ALSA/JACK предупреждений
os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'

# Загрузка .env
load_dotenv()
print("Loaded GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY")[:8] + "..." if os.getenv("GEMINI_API_KEY") else "None")

# Инициализация Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("Gemini API configured successfully")
except Exception as e:
    print(f"Failed to configure Gemini API: {e}")
    genai.configure(api_key=None)

# Инициализация pygame для аудио
try:
    pygame.mixer.init()
    print("Pygame audio initialized successfully")
except Exception as e:
    print(f"Failed to initialize Pygame audio: {e}")

# Текущая дата и время
current_time = datetime.now(pytz.timezone('Europe/Paris'))  # CEST
formatted_time = current_time.strftime("%I:%M %p CEST on %A, %B %d, %Y")  # 10:17 PM CEST on Wednesday, May 14, 2025

# Языки интерфейса и обучения
LANGUAGES_UI = {
    "Русский": "ru",
    "English": "en"
}

LANGUAGES_LEARN = {
    "Немецкий (Deutsch)": "de"
}

# Тексты интерфейса
UI_TEXT = {
    "ru": {
        "title": "languageApp — от hamsterfuchs",
        "context": "Диалог: ",
        "listen": "🔊 Прослушать",
        "speak": "🎤 Говорить",
        "next": "↺ Начать заново",
        "ai": "ИИ-кассир: ",
        "you_said": "Вы сказали: ",
        "error": "Ошибка распознавания",
        "api_key": "⚙️ API Ключ",
        "check_balance": "💰 Проверить статус",
        "welcome": "Добро пожаловать! Начните разговор с ИИ-кассиром на немецком.",
        "current_time": f"Текущее время: {formatted_time}",
        "no_internet": "Нет интернета. Проверьте подключение (ping google.com) и перезапустите приложение.",
        "mic_error": "Микрофон не найден или не работает. Проверьте настройки звука (arecord -d 5 test.wav) и подключение микрофона.",
        "timeout": "Таймаут: скажите что-нибудь в течение 15 секунд. Убедитесь, что микрофон активен.",
        "api_error": "Ошибка API Gemini: проверьте ключ (https://aistudio.google.com/app/apikey) и интернет.",
        "tts_error": "Ошибка синтеза речи: проверьте интернет и установите gTTS корректно.",
        "general_error": "Неизвестная ошибка: см. консоль для деталей и обратитесь за помощью.",
        "speech_retry": "Не удалось распознать речь. Попробуйте снова или введите текст вручную в поле выше."
    },
    "en": {
        "title": "languageApp — by hamsterfuchs",
        "context": "Dialogue: ",
        "listen": "🔊 Listen",
        "speak": "🎤 Speak",
        "next": "↺ Start Over",
        "ai": "AI Cashier: ",
        "you_said": "You said: ",
        "error": "Speech not recognized",
        "api_key": "⚙️ API Key",
        "check_balance": "💰 Check Status",
        "welcome": "Welcome! Start a conversation with the AI cashier in German.",
        "current_time": f"Current time: {formatted_time}",
        "no_internet": "No internet connection. Check your network (ping google.com) and restart the app.",
        "mic_error": "Microphone not found or not working. Check audio settings (arecord -d 5 test.wav) and microphone connection.",
        "timeout": "Timeout: Please speak within 15 seconds. Ensure the microphone is active.",
        "api_error": "Gemini API error: Check your key (https://aistudio.google.com/app/apikey) and internet.",
        "tts_error": "Text-to-Speech error: Check your internet and ensure gTTS is installed correctly.",
        "general_error": "Unknown error: See console for details and seek assistance.",
        "speech_retry": "Failed to recognize speech. Try again or enter text manually in the field above."
    }
}

class LanguageApp:
    def __init__(self, root):
        self.root = root
        self.ui_lang = "ru"
        self.learn_lang = "de"
        self.conversation = [{"role": "system", "content": "You are a friendly cashier. Respond in German."}]
        self.setup_ui()

    def setup_ui(self):
        self.frame = tb.Frame(self.root, padding=20)
        self.frame.pack(fill="both", expand=True)

        # Заголовок
        tb.Label(self.frame, text="🤖 Разговор с ИИ на немецком", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Текущее время
        tb.Label(self.frame, text=UI_TEXT[self.ui_lang]["current_time"], font=("Helvetica", 10)).pack(pady=5)

        # Переключатели языка
        self.ui_var = tk.StringVar(value="Русский")
        self.ui_menu = tb.OptionMenu(self.frame, self.ui_var, "Русский", *LANGUAGES_UI.keys(), command=self.set_ui_lang)
        self.ui_menu.pack(side="top", pady=5)

        self.learn_var = tk.StringVar(value="Немецкий (Deutsch)")
        self.learn_menu = tb.OptionMenu(self.frame, self.learn_var, "Немецкий (Deutsch)", *LANGUAGES_LEARN.keys(), command=self.set_learn_lang)
        self.learn_menu.pack(side="top", pady=5)

        # Контекст диалога
        self.context_label = tb.Label(self.frame, text="", font=("Helvetica", 14, "bold"))
        self.context_label.pack(pady=10)

        # Поле для ввода фразы (опционально)
        self.prompt_entry = tb.Entry(self.frame, font=("Helvetica", 16), width=50)
        self.prompt_entry.pack(pady=5)

        # Ответ ИИ
        self.ai_label = tb.Label(self.frame, text="", font=("Helvetica", 12, "italic"), foreground="#00FFAA")
        self.ai_label.pack(pady=10)

        # Кнопки
        btn_frame = tb.Frame(self.frame)
        btn_frame.pack()

        self.listen_btn = tb.Button(btn_frame, text="", command=self.play_text)
        self.listen_btn.pack(side="left", padx=5)

        self.speak_btn = tb.Button(btn_frame, text="", command=self.recognize_speech)
        self.speak_btn.pack(side="left", padx=5)

        self.next_btn = tb.Button(btn_frame, text="", command=self.reset_conversation)
        self.next_btn.pack(side="left", padx=5)

        tb.Button(btn_frame, text="", command=self.set_api_key).pack(side="left", padx=5)
        tb.Button(btn_frame, text="", command=self.check_status).pack(side="left", padx=5)

        # Ответ пользователя
        self.response_label = tb.Label(self.frame, text="", font=("Helvetica", 12), foreground="lightgreen")
        self.response_label.pack(pady=10)

        # Приветственное сообщение
        self.response_label.config(text=UI_TEXT[self.ui_lang]["welcome"])
        self.update_ui_labels()
        self.start_conversation()

    def set_ui_lang(self, choice):
        self.ui_lang = LANGUAGES_UI[choice]
        self.update_ui_labels()

    def set_learn_lang(self, choice):
        self.learn_lang = LANGUAGES_LEARN[choice]

    def update_ui_labels(self):
        t = UI_TEXT[self.ui_lang]
        self.root.title(t["title"])
        self.context_label.config(text=f"{t['context']}")
        self.listen_btn.config(text=t["listen"])
        self.speak_btn.config(text=t["speak"])
        self.next_btn.config(text=t["next"])

    def start_conversation(self):
        self.conversation = [{"role": "system", "content": "You are a friendly cashier. Respond in German."}]
        self.generate_ai_response("Hallo! Wie kann ich Ihnen helfen?")  # Начальная фраза ИИ

    def reset_conversation(self):
        self.conversation = [{"role": "system", "content": "You are a friendly cashier. Respond in German."}]
        self.ai_label.config(text="")
        self.response_label.config(text=UI_TEXT[self.ui_lang]["welcome"])
        self.generate_ai_response("Hallo! Wie kann ich Ihnen helfen?")  # Новый старт

    def generate_ai_response(self, user_input=""):
        if user_input:
            self.conversation.append({"role": "user", "content": user_input})
        def task():
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content([part["content"] for part in self.conversation])
                answer = response.text
                self.conversation.append({"role": "model", "content": answer})
                self.ai_label.config(text=f"{UI_TEXT[self.ui_lang]['ai']}{answer}")
            except genai.errors.APIError as e:
                error_msg = f"{UI_TEXT[self.ui_lang]['api_error']} Код: {e.code}, Сообщение: {e.message}"
                self.ai_label.config(text=error_msg)
                messagebox.showwarning("API Ошибка", f"{error_msg}\nРешение: Проверьте ключ и интернет.")
                print(f"API Error: {traceback.format_exc()}")
            except Exception as e:
                error_msg = f"{UI_TEXT[self.ui_lang]['general_error']}"
                self.ai_label.config(text=error_msg)
                messagebox.showwarning("Ошибка", f"{error_msg}\nДетали: {str(e)}")
                print(f"General Error: {traceback.format_exc()}")
        threading.Thread(target=task).start()

    def play_text(self):
        text = self.ai_label.cget("text").replace(UI_TEXT[self.ui_lang]["ai"], "").strip()
        if not text:
            text = self.response_label.cget("text").replace(UI_TEXT[self.ui_lang]["you_said"], "").strip()
        try:
            tts = gTTS(text=text, lang=self.learn_lang)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            pygame.mixer.music.load(fp, "mp3")
            pygame.mixer.music.play()
        except ValueError as e:
            error_msg = f"{UI_TEXT[self.ui_lang]['tts_error']} Неверный текст: {str(e)}"
            self.response_label.config(text=error_msg)
            messagebox.showwarning("TTS Ошибка", f"{error_msg}\nРешение: Убедитесь, что текст не пустой.")
            print(f"TTS Value Error: {traceback.format_exc()}")
        except Exception as e:
            error_msg = f"{UI_TEXT[self.ui_lang]['tts_error']} Общая ошибка: {str(e)}"
            self.response_label.config(text=error_msg)
            messagebox.showwarning("TTS Ошибка", f"{error_msg}\nРешение: Проверьте интернет и gTTS.")
            print(f"TTS Error: {traceback.format_exc()}")

    def recognize_speech(self):
        def task():
            r = sr.Recognizer()
            # Проверка интернета
            try:
                requests.get("https://www.google.com", timeout=5)
            except requests.ConnectionError:
                error_msg = UI_TEXT[self.ui_lang]["no_internet"]
                self.response_label.config(text=error_msg)
                messagebox.showwarning("Сетевая ошибка", f"{error_msg}\nРешение: Подключитесь к интернету.")
                print(f"Network Error: {traceback.format_exc()}")
                return

            # Проверка микрофона
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=3)  # Увеличено до 3 секунд
                    self.response_label.config(text=UI_TEXT[self.ui_lang]["timeout"])
                    audio = r.listen(source, timeout=15, phrase_time_limit=15)  # Увеличено до 15 секунд
                    text = r.recognize_google(audio, language="de-DE")
                    self.response_label.config(text=f"{UI_TEXT[self.ui_lang]['you_said']}{text}")
                    self.generate_ai_response(text)
            except sr.UnknownValueError:
                error_msg = UI_TEXT[self.ui_lang]["error"]
                self.response_label.config(text=error_msg)
                messagebox.showwarning("Распознавание речи", f"{error_msg}\nПричина: Неясная речь или шум.\nРешение: {UI_TEXT[self.ui_lang]['speech_retry']}")
                print(f"Speech Recognition: Unknown value error - {traceback.format_exc()}")
            except sr.RequestError as e:
                error_msg = f"Speech error: {str(e)}"
                self.response_label.config(text=error_msg)
                messagebox.showwarning("Запрос ошибки", f"{error_msg}\nПричина: Проблемы с Google API.\nРешение: Проверьте интернет.")
                print(f"Speech Recognition Request Error: {traceback.format_exc()}")
            except sr.WaitTimeoutError:
                error_msg = UI_TEXT[self.ui_lang]["timeout"]
                self.response_label.config(text=error_msg)
                messagebox.showwarning("Таймаут", f"{error_msg}\nРешение: Скажите что-то в течение 15 секунд.")
                print(f"Speech Recognition: Timeout error - {traceback.format_exc()}")
            except sr.MicrophoneException:
                error_msg = UI_TEXT[self.ui_lang]["mic_error"]
                self.response_label.config(text=error_msg)
                messagebox.showwarning("Ошибка микрофона", f"{error_msg}\nРешение: Проверьте настройки звука.")
                print(f"Speech Recognition: Microphone error - {traceback.format_exc()}")
            except Exception as e:
                error_msg = f"Speech error: {str(e)}"
                self.response_label.config(text=error_msg)
                messagebox.showwarning("Неизвестная ошибка", f"{error_msg}\nРешение: См. консоль для деталей.")
                print(f"Speech Recognition: Unexpected error - {traceback.format_exc()}")
        threading.Thread(target=task).start()

    def set_api_key(self):
        win = tb.Toplevel(self.root)
        win.title("Установка API ключа")

        tk.Label(win, text="Gemini API Ключ:", font=("Helvetica", 12)).pack(pady=5)
        gemini_key_var = tk.StringVar()
        gemini_key_entry = tb.Entry(win, textvariable=gemini_key_var, width=60)
        gemini_key_entry.pack(pady=5)

        def save_key():
            gemini_key = gemini_key_var.get().strip()
            if gemini_key and not gemini_key.startswith("AI"):
                messagebox.showerror("Ошибка", "Неверный Gemini ключ")
                return
            with open(".env", "w") as f:
                if gemini_key:
                    f.write(f"GEMINI_API_KEY={gemini_key}\n")
            try:
                genai.configure(api_key=gemini_key or os.getenv("GEMINI_API_KEY"))
                messagebox.showinfo("Успех", "Ключ сохранен!")
            except Exception as e:
                error_msg = f"Не удалось инициализировать Gemini: {str(e)}"
                messagebox.showwarning("Ошибка", f"{error_msg}\nРешение: Проверьте ключ и интернет.")
                print(f"API Config Error: {traceback.format_exc()}")
            win.destroy()

        tb.Button(win, text="💾 Сохранить", command=save_key).pack(pady=10)

    def check_status(self):
        def task():
            status = []
            try:
                genai.GenerativeModel("gemini-1.5-flash").generate_content("Test")
                status.append("Gemini: Ключ валиден")
            except Exception as e:
                status.append(f"Gemini: Ошибка - {str(e)}")
                messagebox.showwarning("Статус API", f"Ошибка: {str(e)}\nРешение: Проверьте ключ и интернет.")
                print(f"Status Check Error: {traceback.format_exc()}")
            self.response_label.config(text="\n".join(status))
        threading.Thread(target=task).start()

if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = LanguageApp(root)
    root.mainloop()
