import tkinter as tk

root = tk.Tk()
root.title("Quota Input")
root.geometry("500x300")

labels = ["Quota #", "Quota Value", "Daily Average", "Quota Average"]
fileNames = ["QuotaNumber.txt", "QuotaValue.txt", "DailyAverage.txt", "QuotaAverage.txt"]
entries = []

def validate_input(P):
    if P == "" or P.replace('.', '', 1).isdigit():  
        return True
    return False

validate_cmd = root.register(validate_input)

def updateField(index):
    value = entries[index].get()
    with open(fileNames[index], "w") as file:
        file.write(value)
    print(f"{labels[index]} updated to: {value}")

for i, text in enumerate(labels):
    label = tk.Label(root, text=text)
    label.pack(anchor="w", padx=10, pady=(10, 0))

    frame = tk.Frame(root)
    frame.pack(fill="x", padx=10, pady=(0, 5))

    entry = tk.Entry(frame, width=30, validate="key", validatecommand=(validate_cmd, "%P"))
    entry.pack(side="left")
    entries.append(entry)

    button = tk.Button(frame, text="Update", width=8, height=1,
                       command=lambda i=i: updateField(i))
    button.pack(side="right", padx=20)

root.mainloop()
