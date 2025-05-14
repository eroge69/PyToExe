import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
import pyautogui
import wikipedia

engine = pyttsx3.init()
voices = engine.getProperty('voices')       #getting details of current voice
for voice in voices:
    engine.setProperty('voice', voice.id)
    engine.setProperty("rate", 150)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def command():
    content = " "
    while content == " ":
        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)

        # recognize speech using Google Speech Recognition
        try:
            content = r.recognize_google(audio, language='en-in')
            print("You Said..." + content)
        except Exception as e:
            print("Please try again...")

    return content

def main_process():
    while True:
        request = command().lower()
        if "hello" in request:
            speak("Welcome, How can i help you.")
        elif "play music" in request:
            speak("Playing music")
            song = random.randint(1,3)
            if song == 1:
                webbrowser.open("https://www.youtube.com/watch?v=Fx7hHmPw8IE")
            elif song == 2:
                webbrowser.open("https://www.youtube.com/watch?v=Fx7hHmPw8IE")
            elif song == 3:
                webbrowser.open("https://www.youtube.com/watch?v=Fx7hHmPw8IE")
        elif "say time" in request:
            now_time = datetime.datetime.now().strftime("%H:%M")
            speak ("Current time is " + str(now_time))
        elif "say date" in request:
            now_time = datetime.datetime.now().strftime("%d:%m")
            speak ("Current date is " + str(now_time))
        elif "open youtube" in request:
            webbrowser.open("www.youtube.com")
        elif "open google" in request:
            webbrowser.open("www.google.com")
        elif "open facebook" in request:
            webbrowser.open("www.facebook.com")
        elif "open instagram" in request:
            webbrowser.open("www.instagram.com")
        elif "open" in request:
            query = request.replace("open", "")
            pyautogui.press("super")
            pyautogui.typewrite(query)
            pyautogui.sleep(2)
            pyautogui.press("enter")
        elif "wikipedia" in request:
            request = request.replace("jarvis ", "")
            request = request.replace("search wikipedia ", "")
            print(request)
            result = wikipedia.summary(request, sentences=2)
            print(result)
            speak(result)
        elif "search google" in request:
            request = request.replace("jarvis ", "")
            request = request.replace("search google ", "")
            webbrowser.open("https://www.google.com/search?q="+request)

main_process()