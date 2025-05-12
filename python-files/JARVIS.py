import speech_recognition as sr
import pyttsx3
import datetime
import os
import webbrowser
import pyjokes
import random
import openai
openai.api_key = "your-openai-api-key"  # Replace with your actual key
import wikipedia

engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()
def summarize_with_openai(topic):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Summarize this topic in 4 sentences: {topic}"
            }]
        )
        summary = response['choices'][0]['message']['content'].strip()
        speak(summary)
    except Exception as e:
        speak("Sorry, I couldn’t get a summary from OpenAI.")
        print("OpenAI Error:", e)

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for wake word...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except:
            return ""

def open_app_or_website(command):
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
    elif "open discord" in command:
        webbrowser.open("https://discord.com/channels/@me")
        speak("Opening Discord.")
    elif "open spotify" in command:
        webbrowser.open("https://open.spotify.com/")
        speak("Opening Spotify")
    elif "search for" in command or "search" in command:
        search_term = command.replace("search for", "").replace("search", "").strip()
        if search_term:
            speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
        else:
            speak("What would you like me to search for?")
        speak(f'Here is what I found for {search_term} on google')
    elif "summarize" in command or "wikipedia" in command or "tell me about" in command:
        try:
            topic = command.replace("summarize", "").replace("wikipedia", "").replace("tell me about", "").strip()
            if topic:
                speak(f"Searching Wikipedia for {topic}")
                summary = wikipedia.summary(topic, sentences=2)
                speak(summary)
            else:
                speak("What topic should I summarize?")
        except wikipedia.exceptions.DisambiguationError as e:
            speak(f"There are multiple results for {topic}. Please be more specific.")
        except wikipedia.exceptions.PageError:
            speak("Sorry, I couldn't find anything on that topic.")
    elif "openai summarize" in command or "summarize using openai" in command:
        topic = command.replace("openai summarize", "").replace("summarize using openai", "").strip()
        if topic:
            speak(f"Getting a summary of {topic} from OpenAI.")
            summarize_with_openai(topic)
        else:
            speak("Please tell me what you want me to summarize.")
    elif "open notepad" in command:
        os.system("notepad")
        speak("Opening Notepad.")
    elif "open calculator" in command:
        os.system("calc")
        speak("Opening Calculator.")
    else:
        return False
    return True

def play_music():
    music_folder = r"C:\Users\ATKM\Music\Krishna'music(operated by jarvis)"
    try:
        songs = [song for song in os.listdir(music_folder) if song.endswith(".mp3")]
        if songs:
            song_to_play = random.choice(songs)
            song_path = os.path.join(music_folder, song_to_play)
            os.startfile(song_path)
            speak(f"Playing {song_to_play}")
        else:
            speak("No music files found.")
    except FileNotFoundError:
        speak("Music folder not found.")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def process_command(command):
    if "hello" in command:
        speak("Hello! How can I assist you?")
    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
    elif "your name" in command:
        speak("I am Jarvis, your personal assistant.")
    elif "play music" in command:
        play_music()
    elif "tell me a joke" in command or "joke" in command:
        tell_joke()
    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()
    elif open_app_or_website(command):
        pass
    else:
        speak("I don't understand that command yet.")

# Main loop
speak("Jarvis is online. Say 'Jarvis' to start.")
while True:
    wake = listen()
    if "jarvis" in wake:
        speak("At your service sir.")
        command = listen()
        if command:
            process_command(command)
