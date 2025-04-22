from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.lang import Builder
import math
import sympy as sp
import re
import ast

Window.clearcolor = (0.2, 0.2, 0.2, 1)

Builder.load_string('''
<ScientificCalculator>:
    do_default_tab: False

    TabbedPanelItem:
        text: 'Basic'
        Calculator:

    TabbedPanelItem:
        text: 'Equations'
        EquationsTab:

    TabbedPanelItem:
        text: 'Trigonometry'
        TrigonometryTab:

    TabbedPanelItem:
        text: 'Inequalities'
        InequalitiesTab:

    TabbedPanelItem:
        text: 'Interest Calc'
        InterestCalculatorTab:

<Calculator>:
    orientation: 'vertical'
    spacing: 5
    padding: 5

    Label:
        id: display
        text: '0'
        font_size: 40
        halign: 'right'
        valign: 'middle'
        size_hint_y: None
        height: 100
        text_size: self.width - 20, None
        color: 1, 1, 1, 1

    GridLayout:
        cols: 4
        spacing: 5

        Button:
            text: 'C'
            background_color: 0.5, 0.5, 0.5, 1
            on_press: root.clear()
        Button:
            text: '('
            background_color: 0.5, 0.5, 0.5, 1
            on_press: root.add_character('(')
        Button:
            text: ')'
            background_color: 0.5, 0.5, 0.5, 1
            on_press: root.add_character(')')
        Button:
            text: '⌫'
            background_color: 0.5, 0.5, 0.5, 1
            on_press: root.backspace()

        Button:
            text: '7'
            on_press: root.add_character('7')
        Button:
            text: '8'
            on_press: root.add_character('8')
        Button:
            text: '9'
            on_press: root.add_character('9')
        Button:
            text: '÷'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('/')

        Button:
            text: '4'
            on_press: root.add_character('4')
        Button:
            text: '5'
            on_press: root.add_character('5')
        Button:
            text: '6'
            on_press: root.add_character('6')
        Button:
            text: '×'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('*')

        Button:
            text: '1'
            on_press: root.add_character('1')
        Button:
            text: '2'
            on_press: root.add_character('2')
        Button:
            text: '3'
            on_press: root.add_character('3')
        Button:
            text: '-'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('-')

        Button:
            text: '0'
            on_press: root.add_character('0')
        Button:
            text: '.'
            on_press: root.add_character('.')
        Button:
            text: '='
            background_color: 1, 0.6, 0, 1
            on_press: root.calculate()
        Button:
            text: '+'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('+')
        Button:
            text: '^'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('^')
        Button:
            text: '√'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('√')
        Button:
            text: '%'
            background_color: 1, 0.6, 0, 1
            on_press: root.add_character('%')

<EquationsTab>:
    orientation: 'vertical'
    spacing: 10
    padding: 10

    Label:
        text: 'Equation Solver'
        font_size: 24
        size_hint_y: None
        height: 50

    TextInput:
        id: equation_input
        hint_text: 'Enter equation (e.g., 2x + 3 = 7)'
        size_hint_y: None
        height: 50

    Button:
        text: 'Solve'
        size_hint_y: None
        height: 50
        on_press: root.solve_equation()

    Label:
        id: equation_result
        text: ''
        font_size: 18
        size_hint_y: None
        height: 100
        text_size: self.width - 20, None

    Label:
        id: equation_steps
        text: ''
        font_size: 14
        size_hint_y: None
        height: 800
        text_size: self.width - 20, None

<TrigonometryTab>:
    orientation: 'vertical'
    spacing: 10
    padding: 10

    Label:
        text: 'Trigonometry Calculator'
        font_size: 24
        size_hint_y: None
        height: 50

    Spinner:
        id: trig_function
        text: 'Select Function'
        values: ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']
        size_hint_y: None
        height: 40

    TextInput:
        id: trig_input
        hint_text: 'Enter angle in degrees/radians'
        size_hint_y: None
        height: 50

    CheckBox:
        id: use_radians
        size_hint_y: None
        height: 40
        text: 'Use Radians'

    Button:
        text: 'Calculate'
        size_hint_y: None
        height: 50
        on_press: root.calculate_trig()

    Label:
        id: trig_result
        text: ''
        font_size: 18
        size_hint_y: None
        height: 100
        text_size: self.width - 20, None

    Label:
        id: trig_steps
        text: ''
        font_size: 14
        size_hint_y: None
        height: 800
        text_size: self.width - 20, None

<InequalitiesTab>:
    orientation: 'vertical'
    spacing: 10
    padding: 10

    Label:
        text: 'Inequality Solver'
        font_size: 24
        size_hint_y: None
        height: 50

    TextInput:
        id: inequality_input
        hint_text: 'Enter inequality (e.g., 2x + 3 > 7)'
        size_hint_y: None
        height: 50

    Button:
        text: 'Solve'
        size_hint_y: None
        height: 50
        on_press: root.solve_inequality()

    Label:
        id: inequality_result
        text: ''
        font_size: 18
        size_hint_y: None
        height: 100
        text_size: self.width - 20, None

    Label:
        id: inequality_steps
        text: ''
        font_size: 14
        size_hint_y: None
        height: 800
        text_size: self.width - 20, None

<InterestCalculatorTab>:
    orientation: 'vertical'
    spacing: 10
    padding: 10

    Label:
        text: 'Interest Calculator'
        font_size: 24
        size_hint_y: None
        height: 50

    Spinner:
        id: interest_type
        text: 'Select Interest Type'
        values: ['Simple Interest', 'Compound Interest']
        size_hint_y: None
        height: 40

    Spinner:
        id: find_value
        text: 'Find Value'
        values: ['Amount (A)', 'Principal (P)', 'Rate (r)', 'Time (t)']
        size_hint_y: None
        height: 40

    GridLayout:
        cols: 2
        spacing: 5
        size_hint_y: None
        height: 120

        Label:
            text: 'Principal (P):'
            size_hint_y: None
            height: 40
        TextInput:
            id: principal_input
            hint_text: 'Enter principal'
            size_hint_y: None
            height: 40

        Label:
            text: 'Rate (r %):'
            size_hint_y: None
            height: 40
        TextInput:
            id: rate_input
            hint_text: 'Enter rate'
            size_hint_y: None
            height: 40

        Label:
            text: 'Time (t):'
            size_hint_y: None
            height: 40
        TextInput:
            id: time_input
            hint_text: 'Enter time'
            size_hint_y: None
            height: 40

        Label:
            text: 'Amount (A):'
            size_hint_y: None
            height: 40
        TextInput:
            id: amount_input
            hint_text: 'Enter amount'
            size_hint_y: None
            height: 40

    Label:
        text: 'For Compound Interest:'
        size_hint_y: None
        height: 30

    GridLayout:
        cols: 2
        spacing: 5
        size_hint_y: None
        height: 80

        Label:
            text: 'Compounds per year (n):'
            size_hint_y: None
            height: 40
        TextInput:
            id: compounds_input
            hint_text: 'e.g., 12 for monthly'
            size_hint_y: None
            height: 40
            disabled: False

    Button:
        text: 'Calculate'
        size_hint_y: None
        height: 50
        on_press: root.calculate_interest()

    Label:
        id: interest_result
        text: ''
        font_size: 18
        size_hint_y: None
        height: 100
        text_size: self.width - 20, None

    Label:
        id: interest_steps
        text: ''
        font_size: 14
        size_hint_y: None
        height: 800
        text_size: self.width - 20, None
''')

class Calculator(BoxLayout):
    def add_character(self, char):
        current = self.ids.display.text
        if current == '0' and char not in '/*-+(':
            self.ids.display.text = char
        else:
            self.ids.display.text += char

    def clear(self):
        self.ids.display.text = '0'

    def backspace(self):
        current = self.ids.display.text
        self.ids.display.text = current[:-1] if len(current) > 1 else '0'

    def calculate(self):
        try:
            expression = self.ids.display.text.replace('×', '*').replace('÷', '/')
            expression = self.add_multiplication(expression)
            expression = self.handle_exponents(expression)
            expression = self.handle_sqrt(expression)
            expression = self.handle_percentage(expression)
            result = self.evaluate_expression(expression)
            self.ids.display.text = str(result) if isinstance(result, (int, float)) else 'Error'
        except Exception:
            self.ids.display.text = 'Error'

    def evaluate_expression(self, expression):
        try:
            tree = ast.parse(expression, mode='eval')
            code = compile(tree, filename='', mode='eval')
            return eval(code)
        except (SyntaxError, TypeError, NameError):
            return 'Error'

    def add_multiplication(self, expression):
        return re.sub(r'(\d)\(', r'\1*(', expression)

    def handle_exponents(self, expression):
        return expression.replace('^', '**')

    def handle_sqrt(self, expression):
        return re.sub(r'√(\d+)', r'math.sqrt(\1)', expression)

    def handle_percentage(self, expression):
        expression = re.sub(r'(\d+)%\s+of\s+(\d+)', r'(\1/100)*\2', expression)
        expression = re.sub(r'(\d+)%', r'(\1/100)', expression)
        return expression

class EquationsTab(BoxLayout):
    def solve_equation(self):
        try:
            equation_str = self.ids.equation_input.text.strip()
            x = sp.symbols('x')
            self.ids.equation_steps.text = ""

            equation_str = re.sub(r'(\d+)x', r'\1*x', equation_str)
            equation_str = re.sub(r'x\*\*(\d+)', r'x^\1', equation_str)
            equation_str = re.sub(r'(\d+)\*\*(\d+)', r'\1^\2', equation_str)
            equation_str = re.sub(r'(\d+)²' , r'\1^2', equation_str)
            equation_str = re.sub(r'(\d+)³' , r'\1^3', equation_str)
            equation_str = re.sub(r'(\d+)⁴' , r'\1^4', equation_str)
            equation_str = re.sub(r'(\d+)⁵' , r'\1^5', equation_str)
            equation_str = re.sub(r'(\d+)⁶' , r'\1^6', equation_str)
            equation_str = re.sub(r'(\d+)⁷' , r'\1^7', equation_str)
            equation_str = re.sub(r'(\d+)⁸' , r'\1^8', equation_str)
            equation_str = re.sub(r'(\d+)⁹' , r'\1^9', equation_str)
            equation_str = re.sub(r'√√(\d+)', r'(\1**(1/4))', equation_str)
            equation_str = re.sub(r'√(\d+)', r'(\1**(1/2))', equation_str)
            equation_str = re.sub(r'=', '- (', equation_str)
            equation_str += ')'

            try:
                equation = sp.sympify(equation_str)
                degree = sp.degree(equation, x)

                if degree == 1:
                    eq_type = "Linear"
                elif degree == 2:
                    eq_type = "Quadratic"
                elif degree == 3:
                    eq_type = "Cubic"
                elif 'log' in equation_str:
                    eq_type = "Logarithmic"
                elif degree > 3:
                    eq_type = "Polynomial"
                else:
                    eq_type = "Unknown"

                solution = sp.solve(equation, x)

                if solution:
                    solution_texts = [f"x = {sol.evalf(5)}" for sol in solution]
                    self.ids.equation_result.text = "Solutions:\n" + "\n".join(solution_texts)
                    self.ids.equation_steps.text = f"Equation: {equation_str}\nType: {eq_type}"
                else:
                    self.ids.equation_result.text = "No solution found."
                    self.ids.equation_steps.text = f"Equation: {equation_str}\nType: {eq_type}"

            except sp.SympifyError:
                self.ids.equation_result.text = "Invalid Equation"
                self.ids.equation_steps.text = "Invalid Equation"

        except Exception as e:
            self.ids.equation_result.text = f"Error: {str(e)}"
            self.ids.equation_steps.text = f"Error: {str(e)}"

class TrigonometryTab(BoxLayout):
    def calculate_trig(self):
        try:
            func = self.ids.trig_function.text
            value = float(self.ids.trig_input.text)
            radians = self.ids.use_radians.active

            if not radians:
                value = math.radians(value)

            result = 0
            if func == 'sin':
                result = sp.sin(value).evalf(5)
            elif func == 'cos':
                result = sp.cos(value).evalf(5)
            elif func == 'tan':
                result = sp.tan(value).evalf(5)
            elif func == 'sec':
                result = (1 / sp.cos(value)).evalf(5)
            elif func == 'csc':
                result = (1 / sp.sin(value)).evalf(5)
            elif func == 'cot':
                result = (1 / sp.tan(value)).evalf(5)
            else:
                raise ValueError("Select a trigonometric function")

            self.ids.trig_result.text = f"{func}({self.ids.trig_input.text}{' rad' if radians else '°'}) = {result}"
            self.ids.trig_steps.text = ""
        except Exception as e:
            self.ids.trig_result.text = f"Error: {str(e)}"
            self.ids.trig_steps.text = f"Error: {str(e)}"

class InequalitiesTab(BoxLayout):
    def solve_inequality(self):
        try:
            inequality_str = self.ids.inequality_input.text.strip()
            x = sp.symbols('x')

            inequality_str = re.sub(r'(\d+)x', r'\1*x', inequality_str)
            inequality_str = re.sub(r'x(\d+)', r'x*\1', inequality_str)

            inequality_str = inequality_str.replace('>=', '>').replace('<=', '<')

            inequality = sp.sympify(inequality_str)
            solution = sp.solve(inequality, x)

            if solution is not sp.EmptySet:
                self.ids.inequality_result.text = f"x ∈ {sp.pretty(solution)}"
                self.ids.inequality_steps.text = ""
            else:
                self.ids.inequality_result.text = "There are no numbers that make this true."
                self.ids.inequality_steps.text = ""

        except sp.SympifyError:
            self.ids.inequality_result.text = "That's not an inequality I can solve right now."
            self.ids.inequality_steps.text = ""
        except Exception as e:
            self.ids.inequality_result.text = f"Whoops! Something went wrong: {str(e)}"
            self.ids.inequality_steps.text = f"Error: {str(e)}"

class InterestCalculatorTab(BoxLayout):
    def calculate_interest(self):
        try:
            interest_type = self.ids.interest_type.text
            find_value = self.ids.find_value.text
            compounds_per_year = 1
            
            # Get all input values (empty strings will be treated as None)
            P = self.ids.principal_input.text
            r = self.ids.rate_input.text
            t = self.ids.time_input.text
            A = self.ids.amount_input.text
            
            # Convert to float if not empty
            P = float(P) if P else None
            r = float(r) if r else None
            t = float(t) if t else None
            A = float(A) if A else None
            
            if interest_type == 'Compound Interest':
                n = self.ids.compounds_input.text
                compounds_per_year = float(n) if n else 1
            
            result = ""
            steps = ""
            
            if interest_type == 'Simple Interest':
                if find_value == 'Amount (A)':
                    if P is not None and r is not None and t is not None:
                        I = P * (r/100) * t
                        A = P + I
                        result = f"Amount (A) = {A:.2f}\nInterest (I) = {I:.2f}"
                        steps = f"Simple Interest Formula:\nA = P + (P × r × t)\nA = {P} + ({P} × {r/100} × {t})\nA = {P} + {I}\nA = {A:.2f}"
                    else:
                        result = "Please enter Principal, Rate, and Time"
                elif find_value == 'Principal (P)':
                    if A is not None and r is not None and t is not None:
                        P = A / (1 + (r/100) * t)
                        I = A - P
                        result = f"Principal (P) = {P:.2f}\nInterest (I) = {I:.2f}"
                        steps = f"Simple Interest Formula:\nP = A / (1 + r × t)\nP = {A} / (1 + {r/100} × {t})\nP = {A} / {1 + (r/100)*t}\nP = {P:.2f}"
                    else:
                        result = "Please enter Amount, Rate, and Time"
                elif find_value == 'Rate (r)':
                    if A is not None and P is not None and t is not None:
                        r = ((A/P) - 1) * (100/t)
                        I = A - P
                        result = f"Rate (r) = {r:.2f}%\nInterest (I) = {I:.2f}"
                        steps = f"Simple Interest Formula:\nr = ((A/P) - 1) × (100/t)\nr = (({A}/{P}) - 1) × (100/{t})\nr = {((A/P)-1)*100/t:.2f}%"
                    else:
                        result = "Please enter Amount, Principal, and Time"
                elif find_value == 'Time (t)':
                    if A is not None and P is not None and r is not None:
                        t = ((A/P) - 1) * (100/r)
                        I = A - P
                        result = f"Time (t) = {t:.2f} years\nInterest (I) = {I:.2f}"
                        steps = f"Simple Interest Formula:\nt = ((A/P) - 1) × (100/r)\nt = (({A}/{P}) - 1) × (100/{r})\nt = {((A/P)-1)*100/r:.2f} years"
                    else:
                        result = "Please enter Amount, Principal, and Rate"
            
            elif interest_type == 'Compound Interest':
                if find_value == 'Amount (A)':
                    if P is not None and r is not None and t is not None:
                        A = P * (1 + (r/100)/compounds_per_year) ** (compounds_per_year * t)
                        I = A - P
                        result = f"Amount (A) = {A:.2f}\nInterest (I) = {I:.2f}"
                        steps = f"Compound Interest Formula:\nA = P(1 + r/n)^(n×t)\nA = {P}(1 + {r/100}/{compounds_per_year})^({compounds_per_year}×{t})\nA = {P} × {1 + (r/100)/compounds_per_year}^{compounds_per_year*t}\nA = {A:.2f}"
                    else:
                        result = "Please enter Principal, Rate, and Time"
                elif find_value == 'Principal (P)':
                    if A is not None and r is not None and t is not None:
                        P = A / ((1 + (r/100)/compounds_per_year) ** (compounds_per_year * t))
                        I = A - P
                        result = f"Principal (P) = {P:.2f}\nInterest (I) = {I:.2f}"
                        steps = f"Compound Interest Formula:\nP = A / (1 + r/n)^(n×t)\nP = {A} / (1 + {r/100}/{compounds_per_year})^({compounds_per_year}×{t})\nP = {A} / {1 + (r/100)/compounds_per_year}^{compounds_per_year*t}\nP = {P:.2f}"
                    else:
                        result = "Please enter Amount, Rate, and Time"
                elif find_value == 'Rate (r)':
                    if A is not None and P is not None and t is not None:
                        # This requires solving for r in the compound interest formula
                        # We'll use sympy to solve it numerically
                        n = compounds_per_year
                        r_sym = sp.symbols('r')
                        equation = P * (1 + r_sym/(100*n))**(n*t) - A
                        solution = sp.nsolve(equation, r_sym, 5)  # 5 is initial guess
                        r = float(solution)
                        I = A - P
                        result = f"Rate (r) = {r:.4f}%\nInterest (I) = {I:.2f}"
                        steps = f"Compound Interest Formula:\nA = P(1 + r/n)^(n×t)\nSolving for r:\n{A} = {P}(1 + r/{n})^({n}×{t})\nNumerical solution gives r = {r:.4f}%"
                    else:
                        result = "Please enter Amount, Principal, and Time"
                elif find_value == 'Time (t)':
                    if A is not None and P is not None and r is not None:
                        # This requires solving for t in the compound interest formula
                        n = compounds_per_year
                        t_sym = sp.symbols('t')
                        equation = P * (1 + (r/100)/n)**(n*t_sym) - A
                        solution = sp.nsolve(equation, t_sym, 5)  # 5 is initial guess
                        t = float(solution)
                        I = A - P
                        result = f"Time (t) = {t:.4f} years\nInterest (I) = {I:.2f}"
                        steps = f"Compound Interest Formula:\nA = P(1 + r/n)^(n×t)\nSolving for t:\n{A} = {P}(1 + {r/100}/{n})^({n}×t)\nNumerical solution gives t = {t:.4f} years"
                    else:
                        result = "Please enter Amount, Principal, and Rate"
            
            self.ids.interest_result.text = result
            self.ids.interest_steps.text = steps
            
        except Exception as e:
            self.ids.interest_result.text = f"Error: {str(e)}"
            self.ids.interest_steps.text = f"Make sure you've entered all required values correctly."

class ScientificCalculator(TabbedPanel):
    pass

class CalculatorApp(App):
    def build(self):
        return ScientificCalculator()

if __name__ == '__main__':
    CalculatorApp().run()