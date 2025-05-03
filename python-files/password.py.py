import json
import tkinter as tk
from tkinter import messagebox

DATA_FILE = 'clients.json'

# Load or create client database
def load_clients():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_clients(clients):
    with open(DATA_FILE, 'w') as file:
        json.dump(clients, file, indent=4)

# Add a new client
def add_client():
    user_id = entry_user_id.get().strip()
    password = entry_password.get().strip()
    name = entry_name.get().strip()

    if not user_id or not password or not name:
        messagebox.showwarning("Missing Info", "All fields are required.")
        return

    clients = load_clients()
    if user_id in clients:
        messagebox.showerror("Error", "User ID already exists.")
        return

    clients[user_id] = {"password": password, "name": name}
    save_clients(clients)
    messagebox.showinfo("Success", "Client added successfully.")
    entry_user_id.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_name.delete(0, tk.END)

# Search client by name
def search_client():
    search_name = entry_search.get().strip().lower()
    clients = load_clients()
    results = []

    for uid, info in clients.items():
        if search_name in info["name"].lower():  # Now supports partial search
            results.append(f"User ID: {uid}\nPassword: {info['password']}")

    if results:
        messagebox.showinfo("Client Found", "\n\n".join(results))
    else:
        messagebox.showerror("Not Found", "No client found with that name.")

# Change password for an existing client
def change_password():
    user_id = entry_user_id.get().strip()
    new_password = entry_password.get().strip()

    if not user_id or not new_password:
        messagebox.showwarning("Missing Info", "User ID and new password are required.")
        return

    clients = load_clients()
    if user_id not in clients:
        messagebox.showerror("Error", "User ID does not exist.")
        return

    # Update the password for the client
    clients[user_id]["password"] = new_password
    save_clients(clients)
    messagebox.showinfo("Success", "Password changed successfully.")
    entry_user_id.delete(0, tk.END)
    entry_password.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Client Manager")

# Add Client Section
tk.Label(root, text="Add New Client").grid(row=0, column=0, columnspan=2, pady=5)

tk.Label(root, text="User ID:").grid(row=1, column=0, sticky="e")
entry_user_id = tk.Entry(root, width=30)
entry_user_id.grid(row=1, column=1)

tk.Label(root, text="Password:").grid(row=2, column=0, sticky="e")
entry_password = tk.Entry(root, width=30)
entry_password.grid(row=2, column=1)

tk.Label(root, text="Name:").grid(row=3, column=0, sticky="e")
entry_name = tk.Entry(root, width=30)
entry_name.grid(row=3, column=1)

tk.Button(root, text="Add Client", command=add_client).grid(row=4, column=0, columnspan=2, pady=10)

# Search Section
tk.Label(root, text="Search Client by Name").grid(row=5, column=0, columnspan=2, pady=5)
entry_search = tk.Entry(root, width=30)
entry_search.grid(row=6, column=0, columnspan=2)

tk.Button(root, text="Search", command=search_client).grid(row=7, column=0, columnspan=2, pady=10)

# Change Password Section
tk.Label(root, text="Change Client Password").grid(row=8, column=0, columnspan=2, pady=5)

tk.Label(root, text="User ID:").grid(row=9, column=0, sticky="e")
entry_user_id = tk.Entry(root, width=30)
entry_user_id.grid(row=9, column=1)

tk.Label(root, text="New Password:").grid(row=10, column=0, sticky="e")
entry_password = tk.Entry(root, width=30)
entry_password.grid(row=10, column=1)

tk.Button(root, text="Change Password", command=change_password).grid(row=11, column=0, columnspan=2, pady=10)

root.mainloop()
