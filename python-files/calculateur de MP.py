import tkinter as tk
from tkinter import messagebox

choice = None
nbr_melange = None

# Function to display the selected option and close the main window
def show_choice():
    global choice
    choice = var.get()
    if choice:
        messagebox.showinfo("Selection", f"Vous avez selectionner: {choice}")
        root.destroy()  # Close the main window
    else:
        messagebox.showwarning("aucune selection", "Please select an option")

# Create the main window
root = tk.Tk()
root.title("choisir le melange")
root.geometry("300x400")

# Create a StringVar to hold the selected option
var = tk.StringVar(value="")

# Define the options
options = ["Dry SF+", "Dry F", "Compac puma", "Compac puma EC", "Desmor",
           "Retardamort", "Paviland a6", "Paviland a10", "Reprifix", "Acelmor",
           "Aceldur", "Hydromor", "Impermor", "Implafix"]

# Create radio buttons for each option
for option in options:
    rb = tk.Radiobutton(root, text=option, variable=var, value=option)
    rb.pack(anchor="w")

# Create a button to submit the selection
submit_button = tk.Button(root, text="continuer", command=show_choice)
submit_button.pack()

# Run the main event loop
root.mainloop()

# Check if choice is made
if choice:
    print(f"Final selected choice: {choice}")
else:
    print("No selection made")

# Create a new window to enter the number of mixtures
def get_value():
    global nbr_melange
    try:
        nbr_melange = float(entry.get())  # Get the number from the entry widget
        nbr_melange_window.destroy()  # Close the window
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Create a Toplevel window for entering the number of mixtures
nbr_melange_window = tk.Toplevel()
nbr_melange_window.title("Entrer le nombre de melange")
nbr_melange_window.geometry("300x100")

# Entry widget to get the number of mixtures
entry = tk.Entry(nbr_melange_window)
entry.pack(pady=10)

# Button to submit the number of mixtures
submit_button = tk.Button(nbr_melange_window, text="Valider", command=get_value)
submit_button.pack()

# Wait for the user to enter the value
nbr_melange_window.wait_window()

# Ensure nbr_melange has been set before using it
if nbr_melange is None:
    raise ValueError("Number of mixtures was not provided.")

# Create a dictionary of options and their corresponding formula
my_dict = {
    "Dry SF+": f"Eau = {nbr_melange*647} Kg\nIPPOL 6000 = {nbr_melange*350} Kg\nAnti mousse(Tekam) = {nbr_melange*0.4} Kg\nAnti bacterien = {nbr_melange*2} Kg",
    "Dry F": f"Eau = {nbr_melange*243} Kg\nIPPOL 6000 = {nbr_melange*752} Kg\nAnti mousse(Tekam) = {nbr_melange*0.13} Kg\nAnti bacterien = {nbr_melange*4.5} Kg",
    "Compac puma": f"exostruct 6066 = {nbr_melange * 1000} Kg",
    "Compac puma EC": f"Eau = {nbr_melange*400} Kg\nexostruct 6066 = {nbr_melange * 600} Kg",
    "Desmor": f"Eau = {nbr_melange * 345} Kg\nAcide Chlorhydrique = {nbr_melange * 655} Kg",
    "Retardamort": f"Eau = {nbr_melange * 348} Kg\nSodium gluconate = {nbr_melange * 106.25} Kg\nSodium Lignosulphonate = {nbr_melange * 41.8} Kg\nAnti mousse(Tekam) = {nbr_melange*1} Kg\nAnti bacterien = {nbr_melange * 3.05} Kg",
    "Paviland a6": f"Eau = {nbr_melange * 1000 * 54 / 100} Kg\nexostruct 6066 = {nbr_melange * 1000 * 46 / 100} Kg",
    "Paviland a10": f"Eau = {nbr_melange * 298} Kg\nExostruct 6066 = {nbr_melange * 700} Kg\nAnti bacterien = {nbr_melange * 1.8} Kg",
    "Reprifix": f"Eau = {nbr_melange * 148} Kg\nIppol 5000 = {nbr_melange * 350} Kg\nDekafine = {nbr_melange * 1.5} Kg\nAnti bacterien = {nbr_melange * 0.9} Kg",
    "Acelmor": f"Eau = {nbr_melange * (650 - 650 * 48 / 100)} Kg\nAlluminium Sulphate = {nbr_melange * 650 * 48 / 100} Kg",
    "Aceldur": f"Eau = {nbr_melange * 364} Kg\nAlluminium Sulphate = {nbr_melange * 286} Kg",
    "Hydromor": f"Eau = {nbr_melange * 356} Kg\nSodium Gluconate = {nbr_melange * 40.75} Kg\nSodium Lignosulphonate = {nbr_melange * 43} Kg\nNaCl = {nbr_melange * 57} Kg\nAnti mousse (Tekam) = {nbr_melange * 1} Kg\nAnti bacterien = {nbr_melange * 2.9} Kg",
    "Impermor": f"Eau = {nbr_melange * 816} Kg\nSiloxane = 0 Kg\nBRB Siloen = {nbr_melange * 182} Kg\nAnti bacterien = {nbr_melange*2} Kg",
    "Implafix": f"Dekafine = {nbr_melange * 0.8} Kg\nDLP 212 = {nbr_melange * 0.25} Kg\nSable blanc = {nbr_melange * 220} Kg\nPigment Jaune = {nbr_melange * 4.65} Kg\nPinobinder 9411 = {nbr_melange * 107} Kg\nAnti mousse (Tekam) = {nbr_melange * 0.5} Kg\nSilice = {nbr_melange * 100} Kg\nAnti bacterien = {nbr_melange * 0.65} Kg",
}

# Create a new window to show the result
result_window = tk.Tk()  # Use Tk() for a new main window
result_window.title("Result")
result_window.geometry("300x300")

# Create a label to show the result
result_label = tk.Label(result_window, text=my_dict[choice], font=("Arial", 12))
result_label.pack(pady=10)

# Center the result window
result_window.update_idletasks()
x = (result_window.winfo_screenwidth() - result_window.winfo_reqwidth()) // 2
y = (result_window.winfo_screenheight() - result_window.winfo_reqheight()) // 2
result_window.geometry(f"+{x}+{y}")

result_window.mainloop()
