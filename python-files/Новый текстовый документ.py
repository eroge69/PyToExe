import tkinter as tk
import time

# Define the main window
root = tk.Tk()
root.title("FaceitClown")
root.geometry("400x300")
root.configure(bg="#333333")
root.resizable(False, False)

# Define the login page
login_frame = tk.Frame(root, bg="#333333")
login_frame.pack(pady=50)

label = tk.Label(login_frame, text="Введи пороль", fg="white", bg="#333333", font=("Arial", 12, "bold"))
label.pack(pady=10)

password_entry = tk.Entry(login_frame, show="", font=("Arial", 12))
password_entry.pack(pady=10)

def login():
    if password_entry.get() == "FaceitClown":
        login_frame.destroy()
        crack_page()
    else:
        label.configure(text="Incorrect password. Try again.", fg="red")

login_button = tk.Button(login_frame, text="Login", command=login, bg="#4d4d4d", fg="white", font=("Arial", 12, "bold"), padx=20, pady=5)
login_button.pack(pady=10)

# Define the crack page
def crack_page():
    crack_frame = tk.Frame(root, bg="#333333")
    crack_frame.pack(pady=50)

    label = tk.Label(crack_frame, text="crack faceit^ anti-cheat", fg="white", bg="#333333", font=("Arial", 12, "bold"))
    label.pack(pady=10)

    start_time = time.time()

    def update_timer():
        elapsed_time = time.time() - start_time
        timer_label.configure(text=f"{elapsed_time:.2f} seconds")
        timer_label.after(10, update_timer)

    timer_label = tk.Label(crack_frame, text="0.00 seconds", fg="white", bg="#333333", font=("Arial", 12, "bold"))
    timer_label.pack(pady=5)

    update_timer()

    label = tk.Label(crack_frame, text="Successful! You can run your cheat!", fg="green", bg="#333333", font=("Arial", 12, "bold"))
    label.pack(pady=10)

    def logout():
        root.destroy()

    logout_button = tk.Button(crack_frame, text="LOGOUT", command=logout, bg="#FF0000", fg="white", font=("Arial", 12, "bold"), padx=20, pady=5)
    logout_button.pack(pady=10)

root.mainloop()