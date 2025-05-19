import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import subprocess
import re
import time
import glob
import winreg
from fuzzywuzzy import fuzz
import pygetwindow as gw
import win32gui
import pyautogui
import psutil
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
import threading

class VoiceAssistant:
    def __init__(self, root):
        # Initialize the speech recognition engine
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.2
        
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        
        # Initialize app paths dictionary
        self.app_paths = self.find_installed_apps()
        
        # Set Chrome as the default browser
        self.chrome_path = r'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        self.youtube_url = "https://www.youtube.com"
        self.google_url = "https://www.google.com/search?q="
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Wake word state
        self.active_listening = False
        self.active_until = 0
        
        # GUI components
        self.root = root
        self.root.title("JARVIS Voice Assistant")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0f2b")  # Dark futuristic background
        
        # Load JARVIS-like background image or GIF
        try:
            self.gif_frames = []
            self.current_frame = 0
            self.gif = Image.open("jarvis_background.gif")  # Replace with your GIF path
            self.frame_count = self.gif.n_frames
            for frame in range(self.frame_count):
                self.gif.seek(frame)
                frame_image = ImageTk.PhotoImage(self.gif.copy().resize((800, 600)))
                self.gif_frames.append(frame_image)
        except FileNotFoundError:
            # Fallback to static image or solid color
            self.gif_frames = [ImageTk.PhotoImage(Image.new('RGB', (800, 600), '#0a0f2b'))]
            self.frame_count = 1
        
        # Canvas for background
        self.canvas = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bg_image = self.canvas.create_image(0, 0, image=self.gif_frames[0], anchor="nw")
        
        # Status label
        self.status_var = tk.StringVar(value="Say 'Jarvis' to wake me up")
        self.status_label = tk.Label(
            self.root, textvariable=self.status_var, font=("Helvetica", 16, "bold"),
            fg="#00ffcc", bg="#0a0f2b", wraplength=700
        )
        self.canvas.create_window(400, 50, window=self.status_label)
        
        # Command log
        self.log_text = tk.Text(
            self.root, height=10, width=60, font=("Helvetica", 12),
            fg="#00ffcc", bg="#1c2526", bd=0, wrap="word"
        )
        self.canvas.create_window(400, 450, window=self.log_text)
        
        # Start GIF animation
        self.animate_gif()
        
        # Start voice assistant in a separate thread
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
    
    def animate_gif(self):
        """Animate the GIF background"""
        if self.frame_count > 1:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.canvas.itemconfig(self.bg_image, image=self.gif_frames[self.current_frame])
        self.root.after(100, self.animate_gif)
    
    def speak(self, text):
        """Convert text to speech and update GUI"""
        self.status_var.set(text)
        self.log_text.insert(tk.END, f"Assistant: {text}\n")
        self.log_text.see(tk.END)
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self, timeout=5, retries=2):
        """Listen for voice commands with retries and specified timeout"""
        with sr.Microphone() as source:
            self.status_var.set("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            for _ in range(retries):
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=7)
                    self.status_var.set("Recognizing...")
                    command = self.recognizer.recognize_google(audio).lower()
                    self.log_text.insert(tk.END, f"You said: {command}\n")
                    self.log_text.see(tk.END)
                    print(f"You said: {command}")
                    return command
                except sr.WaitTimeoutError:
                    return ""
                except sr.UnknownValueError:
                    if self.active_listening:
                        self.speak(" ")
                    return ""
                except sr.RequestError:
                    self.speak("Sorry, my speech service is down.")
                    return ""
        return ""
    
    def find_installed_apps(self):
        """Dynamically find installed applications on the PC"""
        app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
        }
        
        search_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Users\*\AppData\Local\Programs",
            r"C:\Users\*\AppData\Roaming",
        ]
        
        whatsapp_paths = [
            r"C:\Users\*\AppData\Local\WhatsApp\WhatsApp.exe",
            r"C:\Program Files\WindowsApps\*\WhatsApp.exe",
        ]
        
        for path in whatsapp_paths:
            for exe in glob.glob(path, recursive=True):
                app_paths["whatsapp"] = exe
                break
        
        start_menu = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
        for root, _, files in os.walk(start_menu):
            for file in files:
                if file.endswith(".lnk"):
                    app_name = os.path.splitext(file)[0].lower()
                    app_paths[app_name] = os.path.join(root, file)
        
        for directory in search_dirs:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".exe"):
                        app_name = os.path.splitext(file)[0].lower()
                        app_paths[app_name] = os.path.join(root, file)
        
        return app_paths
    
    def find_best_app_match(self, app_name):
        """Find the best matching app name using fuzzy matching"""
        app_name = app_name.lower().strip()
        best_match = None
        highest_score = 0
        
        for key in self.app_paths:
            score = fuzz.ratio(app_name, key)
            if score > highest_score and score > 70:
                highest_score = score
                best_match = key
        
        return best_match
    
    def open_application(self, app_name):
        """Open applications based on name"""
        try:
            matched_app = self.find_best_app_match(app_name)
            if not matched_app:
                self.speak(f"Sorry, I couldn't find {app_name} on your system.")
                return False
            
            app_path = self.app_paths[matched_app]
            self.speak(f"Opening {matched_app}")
            
            if app_path.endswith(".lnk"):
                os.startfile(app_path)
            else:
                subprocess.Popen(app_path, shell=True)
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't open {app_name}. Error: {str(e)}")
            return False
    
    def close_application(self, app_name):
        """Close an application by terminating its process"""
        try:
            matched_app = self.find_best_app_match(app_name)
            if not matched_app:
                self.speak(f"Sorry, I couldn't find {app_name} on your system.")
                return False
            
            app_path = self.app_paths[matched_app]
            exe_name = os.path.basename(app_path).lower()
            if exe_name.endswith(".lnk"):
                exe_name = exe_name[:-4] + ".exe"
            
            closed = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == exe_name:
                    proc.terminate()
                    closed = True
            
            if closed:
                self.speak(f"Closed {matched_app}")
            else:
                self.speak(f"No running instance of {matched_app} found")
            return closed
        except Exception as e:
            self.speak(f"Sorry, I couldn't close {app_name}. Error: {str(e)}")
            return False
    
    def get_open_apps(self):
        """Return a list of currently open applications from app_paths"""
        try:
            open_apps = []
            running_processes = [proc.info['name'].lower() for proc in psutil.process_iter(['name'])]
            
            for app_name, app_path in self.app_paths.items():
                exe_name = os.path.basename(app_path).lower()
                if exe_name.endswith(".lnk"):
                    exe_name = exe_name[:-4] + ".exe"
                if exe_name in running_processes:
                    open_apps.append(app_name)
            
            return open_apps
        except Exception as e:
            self.speak(f"Error detecting open apps: {str(e)}")
            return []
    
    def close_tab(self):
        """Close the current browser tab"""
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                self.speak("No active window detected")
                return False
            
            window_title = active_window.title.lower()
            browser_keywords = ["chrome", "edge", "firefox"]
            is_browser = any(keyword in window_title for keyword in browser_keywords)
            
            if not is_browser:
                self.speak("The active window is not a browser")
                return False
            
            pyautogui.hotkey('ctrl', 'w')
            self.speak("Closed the current tab")
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't close the tab. Error: {str(e)}")
            return False
    
    def focus_window(self, app_name=None):
        """Focus a specific application window or YouTube tab"""
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return False
            
            window_title = active_window.title.lower()
            if app_name == "whatsapp":
                whatsapp_exe = os.path.basename(self.app_paths.get("whatsapp", "")).lower()
                if whatsapp_exe.endswith(".lnk"):
                    whatsapp_exe = whatsapp_exe[:-4] + ".exe"
                if whatsapp_exe in [proc.info['name'].lower() for proc in psutil.process_iter(['name'])]:
                    windows = gw.getWindowsWithTitle("WhatsApp")
                    if windows:
                        windows[0].activate()
                        return True
            elif app_name == "youtube":
                browser_keywords = ["chrome", "edge", "firefox"]
                youtube_keywords = ["youtube", "youtu.be", "youtube.com"]
                is_browser = any(keyword in window_title for keyword in browser_keywords)
                is_youtube = any(keyword in window_title for keyword in youtube_keywords)
                if is_browser and is_youtube:
                    active_window.activate()
                    return True
            return False
        except Exception:
            return False
    
    def is_youtube_active(self):
        """Check if the active window is a browser with a YouTube tab"""
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return False
            
            window_title = active_window.title.lower()
            browser_keywords = ["chrome", "edge", "firefox"]
            youtube_keywords = ["youtube", "youtu.be", "youtube.com"]
            
            is_browser = any(keyword in window_title for keyword in browser_keywords)
            is_youtube = any(keyword in window_title for keyword in youtube_keywords)
            
            return is_browser and is_youtube
        except Exception:
            return False
    
    def is_whatsapp_active(self):
        """Check if WhatsApp is the active window"""
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return False
            
            window_title = active_window.title.lower()
            return "whatsapp" in window_title and any(
                os.path.basename(self.app_paths.get("whatsapp", "")).lower() in proc.info['name'].lower()
                for proc in psutil.process_iter(['name'])
            )
        except Exception:
            return False
    
    def open_youtube(self, search_query=None, use_existing_tab=False):
        """Open YouTube in Chrome or search in existing tab"""
        try:
            if use_existing_tab and self.is_youtube_active():
                if not self.focus_window("youtube"):
                    self.speak("Please make sure the YouTube tab is active")
                    return False
                
                self.speak(f"Searching YouTube for {search_query}")
                pyautogui.press('/')
                time.sleep(1.0)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                pyautogui.write(search_query)
                pyautogui.press('enter')
            else:
                if search_query:
                    search_query = search_query.replace(" ", "+")
                    url = f"{self.youtube_url}/results?search_query={search_query}"
                    self.speak(f"Searching YouTube for {search_query.replace('+', ' ')}")
                else:
                    url = self.youtube_url
                    self.speak("Opening YouTube")
                
                webbrowser.get(self.chrome_path).open(url)
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't open YouTube. Error: {str(e)}")
            return False
    
    def web_search(self, query):
        """Perform a general web search using Google"""
        try:
            query = query.replace(" ", "+")
            url = f"{self.google_url}{query}"
            self.speak(f"Searching the web for {query.replace('+', ' ')}")
            webbrowser.get(self.chrome_path).open(url)
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't perform the search. {str(e)}")
            return False
    
    def search_whatsapp_contact(self, contact_name):
        """Search for a contact in WhatsApp"""
        try:
            if not self.is_whatsapp_active():
                self.speak("Please make sure WhatsApp is active")
                return False
            
            if not self.focus_window("whatsapp"):
                self.speak("Could not focus WhatsApp window")
                return False
            
            self.speak(f"Searching WhatsApp for {contact_name}")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            pyautogui.write(contact_name)
            time.sleep(0.5)
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't search WhatsApp. Error: {str(e)}")
            return False
    
    def send_whatsapp_message(self, contact_name, message):
        """Send a message to a contact in WhatsApp"""
        try:
            if not self.is_whatsapp_active():
                self.speak("Please make sure WhatsApp is active")
                return False
            
            if not self.focus_window("whatsapp"):
                self.speak("Could not focus WhatsApp window")
                return False
            
            self.speak(f"Sending '{message}' to {contact_name} on WhatsApp")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            pyautogui.write(contact_name)
            time.sleep(0.5)
            pyautogui.press('down')
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.write(message)
            pyautogui.press('enter')
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't send the message on WhatsApp. Error: {str(e)}")
            return False
    
    def process_command(self, command):
        """Process the voice command"""
        if command.startswith("type "):
            text_to_type = command.replace("type ", "", 1).strip()
            if text_to_type:
                try:
                    self.speak(f"Typing {text_to_type}")
                    pyautogui.write(text_to_type)
                    return True
                except Exception as e:
                    self.speak(f"Sorry, I couldn't type the text. Error: {str(e)}")
                    return False
            else:
                self.speak("Please specify text to type")
                return True
        
        if "what is the time" in command or "tell me the time" in command or "current time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            return True
        
        if "exit" in command or "quit" in command or "goodbye" in command:
            self.speak("Goodbye!")
            self.running = False
            self.root.quit()
            return False
        
        if "help" in command or "what can you do" in command:
            self.speak("Say 'Jarvis' to wake me up. I listen for commands and reset the 20-second timer each time you give a valid command. "
                      "If I hear no commands for 20 seconds, say 'Jarvis' again. I can type text into the active window, "
                      "tell the current time, open and close applications, close browser tabs, open YouTube, search YouTube, "
                      "search the web, detect open apps, and interact with WhatsApp. If on a YouTube tab, 'search' searches YouTube. "
                      "If on WhatsApp, 'search [name]' searches for a contact, and 'send [message] to [name]' sends a message. "
                      "Try saying 'type hello world', 'what is the time', 'open WhatsApp', 'close WhatsApp', 'close tab', "
                      "'open YouTube', 'search YouTube for cats', 'search what is operation', 'search John', or 'send hi to John'.")
            return True
        
        if "list open apps" in command or "what apps are open" in command:
            open_apps = self.get_open_apps()
            if open_apps:
                self.speak(f"Open apps: {', '.join(open_apps)}")
            else:
                self.speak("No known apps are currently open")
            return True
        
        if "close tab" in command:
            self.close_tab()
        
        elif "close" in command and "tab" not in command:
            app_name = command.replace("close", "").strip()
            if app_name:
                self.close_application(app_name)
            else:
                self.speak("Please specify an application to close")
        
        elif "open youtube" in command:
            search_match = re.search(r'search for (.*)', command)
            if search_match:
                search_query = search_match.group(1)
                self.open_youtube(search_query, use_existing_tab=False)
            else:
                self.open_youtube()
        
        elif "open" in command:
            app_name = command.replace("open", "").strip()
            self.open_application(app_name)
        
        elif "search youtube for" in command:
            search_query = command.replace("search youtube for", "").strip()
            self.open_youtube(search_query, use_existing_tab=False)
        
        elif "send" in command and "to" in command and self.is_whatsapp_active():
            send_match = re.search(r'send (.*?) to (.*)', command)
            if send_match:
                message = send_match.group(1).strip()
                contact_name = send_match.group(2).strip()
                self.send_whatsapp_message(contact_name, message)
            else:
                self.speak("Please say 'send [message] to [person name]'")
        
        elif "search" in command and self.is_whatsapp_active():
            search_query = command.replace("search", "").strip()
            if search_query:
                self.search_whatsapp_contact(search_query)
            else:
                self.speak("Please specify a contact name to search")
        
        elif "search for" in command or "search" in command:
            search_query = command.replace("search for", "").replace("search", "").strip()
            if not search_query:
                self.speak("Please specify something to search for")
                return True
            if self.is_youtube_active():
                self.open_youtube(search_query, use_existing_tab=True)
            else:
                self.web_search(search_query)
        
        else:
            self.speak(" ")
            return True
        
        return True
    
    def run(self):
        """Main loop for the voice assistant"""
        self.speak("Hello! I'm your voice assistant. Say 'Jarvis' to wake me up.")
        
        last_command_time = time.time()
        
        while self.running:
            if self.active_listening and time.time() - last_command_time > 20:
                self.active_listening = False
                self.speak("Wake word required. Say 'Jarvis' to activate me.")
            
            command = self.listen(timeout=5 if not self.active_listening else 10)
            
            if command:
                if not self.active_listening:
                    if "jarvis" in command:
                        self.speak("Yes boss, I am here")
                        self.active_listening = True
                        last_command_time = time.time()
                else:
                    result = self.process_command(command)
                    if result and command.strip():
                        last_command_time = time.time()
                    self.running = result
            
            time.sleep(0.3)

if __name__ == "__main__":
    import sys
    # Install required libraries
    for lib in ["fuzzywuzzy", "pygetwindow", "pywin32", "pyautogui", "psutil", "Pillow"]:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
    
    # Create and run the voice assistant with GUI
    root = tk.Tk()
    assistant = VoiceAssistant(root)
    root.mainloop()