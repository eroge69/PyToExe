from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from gtts import gTTS
import pygame
import time
import os
import pyjokes
from deep_translator import GoogleTranslator

# Define the UI using Kivy language
KV = '''
BoxLayout:
    orientation: 'vertical'
    spacing: 20
    padding: 40

    Label:
        text: "Click Play for a Joke!"
        font_size: 32
        halign: 'center'

    Button:
        text: "Play Joke"
        font_size: 24
        on_press: app.play_joke()
'''

class MainApp(App):
    def build(self):
        return Builder.load_string(KV)

    def play_joke(self):
        joke = pyjokes.get_joke(language='en')
        translated_joke = GoogleTranslator(source='auto', target='hi').translate(joke)
        
        tts = gTTS(text=translated_joke, lang='hi')
        audio_file = "temp_joke.mp3"
        tts.save(audio_file)

        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        os.remove(audio_file)

if __name__ == '__main__':
    MainApp().run()
