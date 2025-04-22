import tkinter as tk
from tkinter import ttk, messagebox
import time


# This function adds a pretty color transition when showing the result

def animate_result():
    color_steps = ["#bdc3c7", "#95a5a6", "#7f8c8d", "#2ecc71"]  # Grey to Green
    for color in color_steps:
        result_label.config(fg=color)      # Change label color gradually
        root.update()                      # Refresh the window
        time.sleep(0.08)                   # Pause between each step



# This is where the calculator's logic happens

def calculate():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        operation = operation_var.get()

        if operation == "Addition":
            result = num1 + num2
        elif operation == "Subtraction":
            result = num1 - num2
        elif operation == "Multiplication":
            result = num1 * num2
        elif operation == "Division":
            if num2 == 0:
                raise ZeroDivisionError("You can't divide by zero, silly 💔")
            result = num1 / num2
        else:
            messagebox.showerror("Oops!", "Choose a valid operation!")
            return


        # Show the result and start animation
        result_label.config(text=f"Answer = {result:.2f}")
        animate_result()


    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")
    except ZeroDivisionError as e:
        messagebox.showerror("Math Error", str(e))



# Set up the main window

root = tk.Tk()
root.title("💫 Magic Calculator")         # Window title
root.geometry("420x320")                  # Window size
root.configure(bg="#1e272e")              # Background color (dark theme)


# Apply stylish theme using ttk
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Verdana", 11), background="#1e272e", foreground="white")
style.configure("TButton", font=("Verdana", 10, "bold"), padding=6)
style.configure("TEntry", font=("Verdana", 11))


# Input fields and labels
ttk.Label(root, text="Enter First Number:").pack(pady=(20, 5))
entry1 = ttk.Entry(root, width=22)
entry1.pack()

ttk.Label(root, text="Enter Second Number:").pack(pady=(10, 5))
entry2 = ttk.Entry(root, width=22)
entry2.pack()


# Operation choice menu
ttk.Label(root, text="Choose Operation:").pack(pady=(10, 5))
operation_var = tk.StringVar()
operation_var.set("Addition")  # Default value
operation_menu = ttk.OptionMenu(root, operation_var, "Addition", "Addition", "Subtraction", "Multiplication", "Division")
operation_menu.pack()


# Calculate button
ttk.Button(root, text="✨ Calculate ✨", command=calculate).pack(pady=20)


# Result label
result_label = tk.Label(root, text="Answer = ", font=("Verdana", 13, "bold"), bg="#1e272e", fg="#f5f6fa")
result_label.pack(pady=10)


# ⌨Pressing 'Enter' key will also trigger the calculate function
root.bind('<Return>', lambda event: calculate())


# Start the GUI
root.mainloop()