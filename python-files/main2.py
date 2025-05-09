from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
import joblib
import numpy as np

# Загружаем модель
model = joblib.load('diabetes_model.pkl')

result_map = {
    0: "🟢 Низкий риск диабета (здоров)",
    1: "🟡 Преддиабет (повышенный риск)",
    2: "🔴 Высокий риск (диабет)"
}

KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10

        TextInput:
            id: age
            hint_text: "Возраст"
            input_filter: 'int'

        TextInput:
            id: gender
            hint_text: "Пол (0 - Женский, 1 - Мужской)"
            input_filter: 'int'

        TextInput:
            id: urea
            hint_text: "Мочевина"
            input_filter: 'float'

        TextInput:
            id: cr
            hint_text: "Креатинин"
            input_filter: 'float'

        TextInput:
            id: hba1c
            hint_text: "HbA1c (%)"
            input_filter: 'float'

        TextInput:
            id: chol
            hint_text: "Холестерин"
            input_filter: 'float'

        TextInput:
            id: tg
            hint_text: "Триглицериды"
            input_filter: 'float'

        TextInput:
            id: hdl
            hint_text: "HDL"
            input_filter: 'float'

        TextInput:
            id: ldl
            hint_text: "LDL"
            input_filter: 'float'

        TextInput:
            id: vldl
            hint_text: "VLDL"
            input_filter: 'float'

        TextInput:
            id: bmi
            hint_text: "ИМТ"
            input_filter: 'float'

        Button:
            text: "Получить результат"
            on_press: root.predict()

        Label:
            id: result
            text: ""
'''

class MainScreen(Screen):
    def predict(self):
        try:
            inputs = [
                int(self.ids.gender.text),
                int(self.ids.age.text),
                float(self.ids.urea.text),
                float(self.ids.cr.text),
                float(self.ids.hba1c.text),
                float(self.ids.chol.text),
                float(self.ids.tg.text),
                float(self.ids.hdl.text),
                float(self.ids.ldl.text),
                float(self.ids.vldl.text),
                float(self.ids.bmi.text)
            ]
            pred = model.predict([inputs])[0]
            self.ids.result.text = f"Результат: {result_map[pred]}"
        except Exception as e:
            self.ids.result.text = f"Ошибка: {e}"

class DiabetesApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    DiabetesApp().run()
