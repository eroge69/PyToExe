import tkinter as tk
from tkinter import messagebox

def calculate_contract_price(turnover):
    try:
        turnover = float(turnover)
        if turnover <= 3000000:
            price = turnover * 0.002
        elif turnover <= 10000000:
            price = (turnover - 3000000) * 0.001 + 6000
        elif turnover <= 20000000:
            price = (turnover - 10000000) * 0.0005 + 13000
        else:
            price = (turnover - 20000000) * 0.0002 + 18000
        return round(price, 2)
    except ValueError:
        return None

def on_calculate():
    turnover = entry_turnover.get()
    result = calculate_contract_price(turnover)
    if result is not None:
        label_result.config(text=f"Contract Price: {result:.2f} AZN")
    else:
        messagebox.showerror("Invalid Input", "Please enter a valid number for turnover.")

# Set up GUI
root = tk.Tk()
root.title("Contract Price Calculator")
root.geometry("400x200")

label_intro = tk.Label(root, text="Enter Turnover (AZN, without VAT):")
label_intro.pack(pady=10)

entry_turnover = tk.Entry(root, width=30)
entry_turnover.pack()

button_calculate = tk.Button(root, text="Calculate Contract Price", command=on_calculate)
button_calculate.pack(pady=10)

label_result = tk.Label(root, text="", font=("Arial", 12, "bold"))
label_result.pack(pady=10)

root.mainloop()
