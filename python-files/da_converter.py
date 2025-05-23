import tkinter as tk
from tkinter import messagebox

# Constants
STEP_FT = 250
STEP_ET = 0.016
STEP_SPEED = 0.256

# Function to convert ET and Trap Speed between any two DA values
def convert_values(measured_da, measured_et, measured_speed, desired_da):
    # Validate ranges
    if not (-1000 <= measured_da <= 7000 and -1000 <= desired_da <= 7000):
        raise ValueError("DA must be between -1000 and 7000 ft")
    # Steps difference
    steps = (desired_da - measured_da) / STEP_FT
    # Apply corrections
    new_et = measured_et + steps * STEP_ET
    new_speed = measured_speed - steps * STEP_SPEED
    return new_et, new_speed

# GUI Application
class DAConverterApp:
    def __init__(self, root):
        self.root = root
        root.title("DA to DA ET/Speed Converter")
        root.resizable(False, False)

        # Input fields
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack()

        tk.Label(frame, text="Measured DA (ft):").grid(row=0, column=0, sticky="e")
        tk.Label(frame, text="Measured ET (sec):").grid(row=1, column=0, sticky="e")
        tk.Label(frame, text="Measured Speed (mph):").grid(row=2, column=0, sticky="e")
        tk.Label(frame, text="Desired DA (ft):").grid(row=3, column=0, sticky="e")

        self.entry_da = tk.Entry(frame)
        self.entry_et = tk.Entry(frame)
        self.entry_speed = tk.Entry(frame)
        self.entry_target = tk.Entry(frame)
        
        # Default example values
        self.entry_da.insert(0, "2250")
        self.entry_et.insert(0, "9.960")
        self.entry_speed.insert(0, "171.270")
        self.entry_target.insert(0, "0")

        self.entry_da.grid(row=0, column=1)
        self.entry_et.grid(row=1, column=1)
        self.entry_speed.grid(row=2, column=1)
        self.entry_target.grid(row=3, column=1)

        # Calculate button
        tk.Button(frame, text="Calculate", command=self.on_calculate).grid(row=4, columnspan=2, pady=10)

        # Result label
        self.result_var = tk.StringVar()
        tk.Label(root, textvariable=self.result_var, font=("Courier", 12), justify="left").pack(pady=5)

    def on_calculate(self):
        try:
            measured_da = int(self.entry_da.get())
            measured_et = float(self.entry_et.get())
            measured_speed = float(self.entry_speed.get())
            desired_da = int(self.entry_target.get())

            new_et, new_speed = convert_values(measured_da, measured_et, measured_speed, desired_da)
            self.result_var.set(
                f"ET @ {desired_da} ft: {new_et:.3f} sec\n" +
                f"Speed @ {desired_da} ft: {new_speed:.3f} mph"
            )
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception:
            messagebox.showerror("Error", "Invalid input or calculation error.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DAConverterApp(root)
    root.mainloop()
