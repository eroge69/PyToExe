if eq_type == 'Linear':
                if len(coeffs) != 2:
                    raise ValueError("Need 2 coefficients (a, b) for ax + b = 0")
                solution = sp.solve(coeffs[0] * x + coeffs[1], x)

            elif eq_type == 'Quadratic':
                if len(coeffs) != 3:
                    raise ValueError("Need 3 coefficients (a, b, c) for ax² + bx + c = 0")
                solution = sp.solve(coeffs[0] * x**2 + coeffs[1] * x + coeffs[2], x)

            elif eq_type == 'Cubic':
                if len(coeffs) != 4:
                    raise ValueError("Need 4 coefficients (a, b, c, d) for ax³ + bx² + cx + d = 0")
                solution = sp.solve(coeffs[0] * x3 + coeffs[1] * x2 + coeffs[2] * x + coeffs[3], x)

            else:
                raise ValueError("Please select a valid equation type")

            if solution:
                self.ids.equation_result.text = f"Solutions:\n" + "\n".join([f"x = {sol.evalf(5)}" for sol in solution])
            else:
                self.ids.equation_result.text = "No solution found."

        except Exception as e:
            self.ids.equation_result.text = f"Error: {str(e)}"

class TrigonometryTab(BoxLayout):
    def calculate_trig(self):
        try:
            func = self.ids.trig_function.text
            value = float(self.ids.trig_input.text)
            radians = self.ids.use_radians.active

            if not radians:
                value = math.radians(value)

            if func == 'sin':
                result = math.sin(value)
            elif func == 'cos':
                result = math.cos(value)
            elif func == 'tan':
                result = math.tan(value)
            elif func == 'asin':
                result = math.asin(value)
                if not radians:
                    result = math.degrees(result)
            elif func == 'acos':
                result = math.acos(value)
                if not radians:
                    result = math.degrees(result)
            elif func == 'atan':
                result = math.atan(value)
                if not radians:
                    result = math.degrees(result)
            else:
                raise ValueError("Select a trigonometric function")

            self.ids.trig_result.text = f"{func}({self.ids.trig_input.text}{' rad' if radians else '°'}) = {result:.5f}"

        except Exception as e:
            self.ids.trig_result.text = f"Error: {str(e)}"

class CalculusTab(BoxLayout):
    def calculate_calc(self):
        try:
            operation = self.ids.calc_operation.text
            expr = self.ids.calc_input.text
            x = sp.symbols('x')

            if operation == 'Derivative':
                result = sp.diff(expr, x)
                self.ids.calc_result.text = f"d/dx({expr}) = {result}"

            elif operation == 'Integral':
                result = sp.integrate(expr, x)
                self.ids.calc_result.text = f"∫({expr})dx = {result} + C"

            else:
                raise ValueError("Select a calculus operation")

        except Exception as e:
            self.ids.calc_result.text = f"Error: {str(e)}"

class ScientificCalculator(TabbedPanel):
    pass

class CalculatorApp(App):
    def build(self):
        return ScientificCalculator()

if name == 'main':
    CalculatorApp().run()
