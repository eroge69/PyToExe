import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
from tkcalendar import DateEntry

# Database connection
db = sqlite3.connect("bob.db")
cursor = db.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        order_info TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        order_date TEXT NOT NULL,
        entry_date TEXT,
        vreme_dostave TEXT NOT NULL
    )
""")

db.commit()

# Function to add user
def add_user():
    name = name_entry.get().strip()
    order_info = order_entry.get().strip()
    address = address_entry.get().strip()
    phone = phone_entry.get().strip()
    order_date = date_entry.get().strip()
    entry_date = datetime.datetime.now().strftime("%d/%m/%Y")
    vreme_dostave = vreme_entry.get().strip()

    if not name or not order_info or not address or not phone or not order_date:
        messagebox.showerror("Error", "Fill in all fields!")
        return

    cursor.execute("INSERT INTO users (name, order_info, address, phone, order_date, entry_date, vreme_dostave) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (name, order_info, address, phone, order_date, entry_date,vreme_dostave))
    db.commit()
    update_tables()
    name_entry.delete(0, tk.END)
    order_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    vreme_entry.delete(0, tk.END)

# Function to update tables
def update_tables():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    week_later = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    cursor.execute("SELECT name, order_date FROM users")
    all_users = cursor.fetchall()

    today_listbox.delete(0, tk.END)
    upcoming_listbox.delete(0, tk.END)

    for user in all_users:
        name, order_date = user
        try:
            # Convert existing DD/MM/YYYY dates to YYYY-MM-DD
            formatted_date = datetime.datetime.strptime(order_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = order_date  # Keep the date as is if it's already correct

        if formatted_date == today:
            today_listbox.insert(tk.END, f"{name} - {order_date}")

        elif today < formatted_date <= week_later:
            upcoming_listbox.insert(tk.END, f"{name} - {order_date}")

# Function to search user
def search_user():
    search_term = search_entry.get().strip()
    if not search_term:
        messagebox.showerror("Error", "Enter name or phone number to search!")
        return

    cursor.execute("SELECT name, entry_date FROM users WHERE name LIKE ? OR phone LIKE ?", (f"%{search_term}%", f"%{search_term}%"))
    results = cursor.fetchall()

    search_results_listbox.delete(0, tk.END)

    if results:
        for user in results:
            search_results_listbox.insert(tk.END, f"Name: {user[0]}, Entry date: {user[1]}")
    else:
        search_results_listbox.insert(tk.END, "No users found.")

def show_user_details(event=None):
    listbox = event.widget  # Identifikujemo iz kog Listbox-a dolazi klik
    selected = listbox.curselection()
    if not selected:
        return  # Ako nema selektovanog korisnika, prekini funkciju

    index = selected[0]  # Uzimamo indeks selektovanog reda
    user_text = listbox.get(index)  # Dobijamo tekst iz reda

    # Ako podaci dolaze iz pretrage, struktura je "Ime: Korisnik..."
    if "Name:" in user_text:
        user_name = user_text.split(",")[0].replace("Name: ", "").strip()
    else:
        # Ako podaci dolaze iz today_listbox ili upcoming_listbox, ime je pre prvog "-"
        user_name = user_text.split("-")[0].strip()

    cursor.execute("SELECT * FROM users WHERE name = ?", (user_name,))
    user = cursor.fetchone()

    if user:
        user_details_label.config(
            text=f"Ime: {user[1]}\nPorudžbina: {user[2]}\nAdresa: {user[3]}\nTelefon: {user[4]}\nDatum: {user[5]} \nVreme Dostave: {user[7]}"
        )

# GUI setup
root = tk.Tk()
root.title("B.O.B. - Orders")
root.geometry("1000x1200")

# Apply a dark theme manually by modifying widget colors
root.configure(bg="#2E2E2E")

# Apply a modern ttk theme to the root window
style = ttk.Style()
style.theme_use('clam')  # You can experiment with 'alt', 'classic', etc.
style.configure("TButton", background="#4A4A4A", foreground="white")
style.configure("TLabel", background="#2E2E2E", foreground="white")
style.configure("TEntry", fieldbackground="#3E3E3E", foreground="white")
style.configure("TFrame", background="#2E2E2E")
style.configure("TButton", background="#4A4A4A", foreground="white")
style.map("TButton", background=[('active', '#D3D3D3')], foreground=[('active', 'black')])

# Data entry
frame_data_entry = ttk.Frame(root, padding=15)
frame_data_entry.pack(fill=tk.X, padx=20, pady=10)

ttk.Label(frame_data_entry, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
name_entry = ttk.Entry(frame_data_entry, width=40)
name_entry.grid(row=0, column=1, padx=10)

ttk.Label(frame_data_entry, text="Order:").grid(row=1, column=0, sticky="w", pady=5)
order_entry = ttk.Entry(frame_data_entry, width=40)
order_entry.grid(row=1, column=1, padx=10)

ttk.Label(frame_data_entry, text="Address:").grid(row=2, column=0, sticky="w", pady=5)
address_entry = ttk.Entry(frame_data_entry, width=40)
address_entry.grid(row=2, column=1, padx=10)

ttk.Label(frame_data_entry, text="Phone number:").grid(row=3, column=0, sticky="w", pady=5)
phone_entry = ttk.Entry(frame_data_entry, width=40)
phone_entry.grid(row=3, column=1, padx=10)

ttk.Label(frame_data_entry, text="Order date:").grid(row=5, column=0, sticky="w", pady=5)
date_entry = DateEntry(frame_data_entry, 
                       width=40, 
                       background='#808080',  
                       foreground='white',     
                       fieldbackground='#808080',  
                       borderwidth=2, 
                       normalbackground='#808080')  
date_entry.grid(row=5, column=1, padx=10)
tk.Label(frame_data_entry, text="Vreme dostave:").grid(row=4, column=0, sticky="w", pady=5)
vreme_entry = ttk.Entry(frame_data_entry, width=40)
vreme_entry.grid(row=4, column=1, padx=10)


def set_selected_date_style():
    date_entry.config(date_pattern="dd/mm/yyyy", normalbackground='#808080', normalforeground='white')


set_selected_date_style()

add_button = ttk.Button(frame_data_entry, text="Add user", command=add_user)
add_button.grid(row=6, column=1, columnspan=2, pady=10)

# User search
frame_search = ttk.Frame(root, padding=10)
frame_search.pack(fill=tk.X, padx=10, pady=10)

ttk.Label(frame_search, text="Search user (name or phone):").grid(row=0, column=0, sticky="w", pady=5)
search_entry = ttk.Entry(frame_search, width=40)
search_entry.grid(row=0, column=1, padx=10)

search_button = ttk.Button(frame_search, text="Search", command=search_user)
search_button.grid(row=1, column=0, columnspan=2, pady=10)

search_results_listbox = tk.Listbox(frame_search, height=5, width=70)
search_results_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

user_details_label = ttk.Label(frame_search, text="User details will appear here...", justify="left", font=("Arial", 12), relief="solid", padding=10)
user_details_label.grid(row=2, column=2, padx=10, pady=10, sticky="n")

frame_tables = ttk.Frame(root, padding=10)
frame_tables.pack(fill=tk.X, padx=10, pady=10)

ttk.Label(frame_tables, text="Delivery today").grid(row=0, column=0, sticky="w")
ttk.Label(frame_tables, text="Delivery within the next 7 days").grid(row=0, column=1, sticky="w")

today_listbox = tk.Listbox(frame_tables, height=10, width=35)
today_listbox.grid(row=1, column=0, padx=10)

upcoming_listbox = tk.Listbox(frame_tables, height=10, width=35)
upcoming_listbox.grid(row=1, column=1, padx=10)

refresh_button = ttk.Button(root, text="Refresh", command=update_tables)
refresh_button.pack(pady=20)

search_results_listbox.bind("<<ListboxSelect>>", show_user_details)
today_listbox.bind("<<ListboxSelect>>", show_user_details)
upcoming_listbox.bind("<<ListboxSelect>>", show_user_details)

update_tables()

root.mainloop()

db.close()
