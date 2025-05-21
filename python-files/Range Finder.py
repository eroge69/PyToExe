import tkinter as tk

def calculate_distance():
    try:
        mils = float(mil_input.get())
        size = float(size_input.get())
        distance = (size / mils) * 1000
        result_label.config(text=f"Distance: {distance:.2f}")
    except ValueError:
        result_label.config(text="Please enter valid numbers")

def reset_fields():
    size_input.delete(0, tk.END)
    mil_input.delete(0, tk.END)
    result_label.config(text="Distance: ")

# Create the application window
root = tk.Tk()
root.title("WW2 Panzer Tank Sight Range Finder")
root.configure(bg="black")

# Set font properties
font_large = ("IBM Plex Mono", 20)
font_medium = ("IBM Plex Mono", 15)

# UI elements with spacing
tk.Label(root, text="Enter the size:", fg="#4AF626", bg="black", font=font_medium, pady=10).pack()
size_input = tk.Entry(root, font=font_large, width=20)
size_input.pack(pady=10)

tk.Label(root, text="Enter the mils:", fg="#4AF626", bg="black", font=font_medium, pady=10).pack()
mil_input = tk.Entry(root, font=font_large, width=20)
mil_input.pack(pady=10)

tk.Button(root, text="Calculate", font=font_medium, padx=20, pady=10, command=calculate_distance).pack(pady=10)
tk.Button(root, text="Reset", font=font_medium, padx=20, pady=10, command=reset_fields).pack(pady=10)

result_label = tk.Label(root, text="Distance: ", fg="#4AF626", bg="black", font=font_medium, pady=20)
result_label.pack()

# Run the application
root.mainloop()