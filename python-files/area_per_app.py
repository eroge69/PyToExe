from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

class AreaPerimeterApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.layout.add_widget(Label(text="Choose a shape:"))
        self.shape_spinner = Spinner(
            text="Rectangle",
            values=["Rectangle", "Square"],
        )
        self.layout.add_widget(self.shape_spinner)

        self.layout.add_widget(Label(text="Enter Length "))
        self.length_input = TextInput()
        self.layout.add_widget(self.length_input)

        self.layout.add_widget(Label(text="Enter Width "))
        self.width_input = TextInput()
        self.layout.add_widget(self.width_input)

        self.calculate_button = Button(text="Calculate", on_press=self.calculate)
        self.layout.add_widget(self.calculate_button)

        self.result_label = Label(text="")
        self.layout.add_widget(self.result_label)

        return self.layout

    def calculate(self, instance):
        shape = self.shape_spinner.text
        try:
            if shape == "Rectangle":
                length = float(self.length_input.text)
                width = float(self.width_input.text)
                area = length * width
                perimeter = 2 * (length + width)
            elif shape == "Square":
                side = float(self.length_input.text)
                area = side ** 2
                perimeter = 4 * side
            else:
                self.result_label.text = "Invalid Shape"
                return

            self.result_label.text = f"Area: {area}, Perimeter: {perimeter}"
        except ValueError:
            self.result_label.text = "Please enter valid numbers or get out and dont use my app !!!!"

AreaPerimeterApp().run()
