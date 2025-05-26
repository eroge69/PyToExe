import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import sqlite3
from tkinter import ttk
from PIL import Image, ImageTk
import time
from datetime import datetime, timedelta
import string
import os
import sys

inquiries = []
approved_files = []

# Open database connection (Avoids "database is locked" error)
conn = sqlite3.connect("imrsearch.db", check_same_thread=False)
cursor = conn.cursor()

# Create Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    pin TEXT NOT NULL
)
""")

# Insert default admin account if not exists
cursor.execute("SELECT * FROM users WHERE username=?", ("ADMINISTRATOR",))
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password, pin) VALUES (?, ?, ?)", ("ADMINISTRATOR", "1234", "1234"))

conn.commit()  # Commit changes before closing
conn.close()  # Close connection to prevent locking
with sqlite3.connect("imrsearch.db") as conn:
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN deleted_at TEXT")
        print("Column 'deleted_at' added to 'users' table.")
    except sqlite3.OperationalError as e:
        print("Error:", e)

def debug_table_schema(table_name):
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        print(f"Schema for {table_name}:")
        for column in schema:
            print(f" - {column[1]} ({column[2]})")
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # Set by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def execute_query(query, params=()):
    conn = sqlite3.connect("imrsearch.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()  # Ensure the connection is closed


def fetch_one(query, params=()):
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
def toggle_password():
    if show_password_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")



def column_exists(table, column):
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        return column in columns

def patch_existing_tables():
    # Check and add columns to `users` table
    if not column_exists("users", "deleted"):
        try:
            execute_query("ALTER TABLE users ADD COLUMN deleted INTEGER DEFAULT 0")
            print("Added 'deleted' to users table.")
        except Exception as e:
            print("Error adding 'deleted' to users:", e)

    if not column_exists("users", "deleted_at"):
        try:
            execute_query("ALTER TABLE users ADD COLUMN deleted_at TEXT")
            print("Added 'deleted_at' to users table.")
        except Exception as e:
            print("Error adding 'deleted_at' to users:", e)

    # Check and add columns to `approved_files` table
    if not column_exists("approved_files", "deleted"):
        try:
            execute_query("ALTER TABLE approved_files ADD COLUMN deleted INTEGER DEFAULT 0")
            print("Added 'deleted' to approved_files table.")
        except Exception as e:
            print("Error adding 'deleted' to approved_files:", e)

    if not column_exists("approved_files", "deleted_at"):
        try:
            execute_query("ALTER TABLE approved_files ADD COLUMN deleted_at TEXT")
            print("Added 'deleted_at' to approved_files table.")
        except Exception as e:
            print("Error adding 'deleted_at' to approved_files:", e)



def initialize_db():
    """Initialize the database and add the necessary tables and columns."""
    # Create users table with deleted_at column
    execute_query(""" 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        pin TEXT NOT NULL,
        deleted_at TIMESTAMP DEFAULT NULL
    )""")

    # Create approved_files table with deleted_at column
    execute_query(""" 
    CREATE TABLE IF NOT EXISTS approved_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        deleted_at TIMESTAMP DEFAULT NULL
    )""")

    # Create inquiry_files table (no changes needed here)
    execute_query(""" 
    CREATE TABLE IF NOT EXISTS inquiry_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL
    )""")

    # Ensure the default admin exists
    if not fetch_one("SELECT * FROM users WHERE username=?", ("ADMINISTRATOR",)):
        execute_query("INSERT INTO users (username, password, pin) VALUES (?, ?, ?)", ("ADMINISTRATOR", "1234", "1234"))
    execute_query("UPDATE approved_files SET deleted_at = datetime('now') WHERE deleted = 1 AND deleted_at IS NULL")
    execute_query("UPDATE users SET deleted_at = datetime('now') WHERE deleted = 1 AND deleted_at IS NULL")
    # Add 'deleted_at' column to approved_files table if it doesn't exist
    try:
        execute_query("ALTER TABLE approved_files ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL")
    except sqlite3.OperationalError:
        # If column already exists, this will be ignored
        pass

initialize_db()
def reopen_admin_panel_from_delete(delete_window):
    try:
        delete_window.destroy()
    except:
        pass  # If already closed

    open_admin_panel()  # Open fresh instance

def soft_delete_user(user_id):
    deleted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query("UPDATE users SET deleted = 1, deleted_at = ? WHERE id = ?", (deleted_at, user_id))
    manage_users()

def soft_delete_file(file_id):
    deleted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query("UPDATE approved_files SET deleted = 1, deleted_at = ? WHERE id = ?", (deleted_at, file_id))

def check_for_automatic_deletion():
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()

        # Deleted files cleanup
        cursor.execute("SELECT id, deleted_at FROM approved_files WHERE deleted = 1")
        for file_id, deleted_at in cursor.fetchall():
            if deleted_at and isinstance(deleted_at, str):  # Ensure it's a valid string
                try:
                    deleted_time = datetime.strptime(deleted_at, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() - deleted_time > timedelta(days=30):
                        cursor.execute("DELETE FROM approved_files WHERE id=?", (file_id,))
                except ValueError as e:
                    print(f"Skipping file ID {file_id} due to invalid timestamp: {e}")
            else:
                print(f"Skipping file ID {file_id}: deleted_at is None or not a string.")

        # Deleted users cleanup
        cursor.execute("SELECT id, deleted_at FROM users WHERE deleted = 1")
        for user_id, deleted_at in cursor.fetchall():
            if deleted_at and isinstance(deleted_at, str):
                try:
                    deleted_time = datetime.strptime(deleted_at, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() - deleted_time > timedelta(days=30):
                        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                except ValueError as e:
                    print(f"Skipping user ID {user_id} due to invalid timestamp: {e}")
            else:
                print(f"Skipping user ID {user_id}: deleted_at is None or not a string.")

        conn.commit()


# Function to restore a deleted file
def restore_file(file_name, file_path, frame):
    execute_query("UPDATE approved_files SET deleted = 0 WHERE file_name=? AND file_path=?", (file_name, file_path))

    messagebox.showinfo("Restored", f"File '{file_name}' has been restored.")
    show_trash_bin()

# Function to permanently delete a file
def permanently_delete_file(file_name, file_path, frame):
    execute_query("DELETE FROM approved_files WHERE file_name=? AND file_path=?", (file_name, file_path))

    messagebox.showinfo("Deleted", f"File '{file_name}' has been permanently deleted.")
    show_trash_bin()

# Function to restore a deleted user
def restore_user(user_id, frame):
    execute_query("UPDATE users SET deleted = 0 WHERE id=?", (user_id,))
    messagebox.showinfo("Restored", "User has been restored.")
    show_trash_bin()

# Function to permanently delete a user
def permanently_delete_user(user_id, frame):
    execute_query("DELETE FROM users WHERE id=?", (user_id,))
    messagebox.showinfo("Deleted", "User has been permanently deleted.")
    show_trash_bin()

# Now, you can define the function to show the trash bin:

def show_trash_bin():
    """Opens a full-screen window showing deleted files and users in the trash bin."""
    trash_bin_window = tk.Toplevel()
    trash_bin_window.title("🗑 Trash Bin")

    # Full-screen setup
    screen_width = trash_bin_window.winfo_screenwidth()
    screen_height = trash_bin_window.winfo_screenheight()
    trash_bin_window.geometry(f"{screen_width}x{screen_height}")
    trash_bin_window.configure(bg="#1E1E2E")

    # Header
    tk.Label(trash_bin_window, text="🗑 Trash Bin", font=("Arial", 28, "bold"), bg="#1E1E2E", fg="#00ADB5").pack(pady=30)

    # Main content frame
    frame = tk.Frame(trash_bin_window, bg="#1E1E2E")
    frame.pack(fill=tk.BOTH, expand=True, padx=60, pady=20)

    canvas = tk.Canvas(frame, bg="#1E1E2E", highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1E1E2E")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Fetch and display deleted files
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name, file_path, deleted_at FROM approved_files WHERE deleted = 1")
        deleted_files_db = cursor.fetchall()

    # Display deleted files
    tk.Label(scrollable_frame, text="Deleted Files", font=("Arial", 20, "bold"), bg="#1E1E2E", fg="#00ADB5").pack(pady=20)

    for file_name, file_path, deleted_at in deleted_files_db:
        file_frame = tk.Frame(scrollable_frame, bg="#2E2E3C", relief="solid", bd=2, padx=10, pady=10)
        file_frame.pack(pady=10, fill="x", anchor="w")

        file_label = tk.Label(file_frame, text=file_name, bg="#2E2E3C", fg="white", font=("Arial", 14), anchor="w")
        file_label.pack(side="left", expand=True, fill="x", padx=10)

        # Handle None for deleted_at
        if deleted_at:
            deleted_time = datetime.strptime(deleted_at, "%Y-%m-%d %H:%M:%S")
            remaining_time = deleted_time + timedelta(days=30) - datetime.now()

            if remaining_time.total_seconds() > 0:
                # Show the countdown
                countdown_label = tk.Label(file_frame, text=f"Time remaining: {str(remaining_time).split('.')[0]}", bg="#2E2E3C", fg="white", font=("Arial", 10))
                countdown_label.pack(side="left", padx=10)
            else:
                # Show that it's expired and should be deleted
                countdown_label = tk.Label(file_frame, text="Expired", bg="#2E2E3C", fg="red", font=("Arial", 10))
                countdown_label.pack(side="left", padx=10)
        else:
            # If deleted_at is None, show an empty label or something else
            countdown_label = tk.Label(file_frame, text="No timestamp", bg="#2E2E3C", fg="white", font=("Arial", 10))
            countdown_label.pack(side="left", padx=10)

        restore_btn = tk.Button(file_frame, text="🔄 Restore", bg="#00FF00", fg="white", font=("Arial", 12, "bold"),
                                command=lambda f=file_name, p=file_path, fr=file_frame: restore_file(f, p, fr))
        restore_btn.pack(side="left", padx=15)

        delete_btn = tk.Button(file_frame, text="🗑 Permanently Delete", bg="#FF5555", fg="white", font=("Arial", 12, "bold"),
                               command=lambda f=file_name, p=file_path, fr=file_frame: permanently_delete_file(f, p, fr))
        delete_btn.pack(side="right", padx=15)

    # Fetch and display deleted users
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, deleted_at FROM users WHERE deleted = 1")
        deleted_users_db = cursor.fetchall()

    # Display deleted users
    tk.Label(scrollable_frame, text="Deleted Users", font=("Arial", 20, "bold"), bg="#1E1E2E", fg="#00ADB5").pack(pady=20)

    for user_id, username, deleted_at in deleted_users_db:
        user_frame = tk.Frame(scrollable_frame, bg="#2E2E3C", relief="solid", bd=2, padx=10, pady=10)
        user_frame.pack(pady=10, fill="x", anchor="w")

        user_label = tk.Label(user_frame, text=username, bg="#2E2E3C", fg="white", font=("Arial", 14), anchor="w")
        user_label.pack(side="left", expand=True, fill="x", padx=10)

        # Handle None for deleted_at
        if deleted_at:
            deleted_time = datetime.strptime(deleted_at, "%Y-%m-%d %H:%M:%S")
            remaining_time = deleted_time + timedelta(days=30) - datetime.now()

            if remaining_time.total_seconds() > 0:
                # Show the countdown
                countdown_label = tk.Label(user_frame, text=f"Time remaining: {str(remaining_time).split('.')[0]}", bg="#2E2E3C", fg="white", font=("Arial", 10))
                countdown_label.pack(side="left", padx=10)
            else:
                # Show that it's expired and should be deleted
                countdown_label = tk.Label(user_frame, text="Expired", bg="#2E2E3C", fg="red", font=("Arial", 10))
                countdown_label.pack(side="left", padx=10)
        else:
            # If deleted_at is None, show an empty label or something else
            countdown_label = tk.Label(user_frame, text="No timestamp", bg="#2E2E3C", fg="white", font=("Arial", 10))
            countdown_label.pack(side="left", padx=10)

        restore_user_btn = tk.Button(user_frame, text="🔄 Restore", bg="#00FF00", fg="white", font=("Arial", 12, "bold"),
                                     command=lambda u=user_id, fr=user_frame: restore_user(u, fr))
        restore_user_btn.pack(side="left", padx=15)

        delete_user_btn = tk.Button(user_frame, text="🗑 Permanently Delete", bg="#FF5555", fg="white", font=("Arial", 12, "bold"),
                                     command=lambda u=user_id, fr=user_frame: permanently_delete_user(u, fr))
        delete_user_btn.pack(side="right", padx=15)

    # Close button
    ttk.Button(
        trash_bin_window,
        text="❌ Close",
        command=lambda: [trash_bin_window.destroy()]
    ).pack(pady=30)

    # Check for automatic deletion
    check_for_automatic_deletion()

debug_table_schema("users")
debug_table_schema("approved_files")
# Automatic deletion function
def check_for_automatic_deletion():
    """Checks for files and users that have been in the trash for over 30 days and deletes them."""
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()

        # Check for files older than 30 days and delete
        cursor.execute("SELECT file_name, file_path, deleted_at FROM approved_files WHERE deleted = 1")
        deleted_files_db = cursor.fetchall()

        for file_name, file_path, deleted_at in deleted_files_db:
            deleted_time = datetime.strptime(deleted_at, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - deleted_time).days > 30:
                permanently_delete_file(file_name, file_path, None)

        # Check for users older than 30 days and delete
        cursor.execute("SELECT id, username, deleted_at FROM users WHERE deleted = 1")
        deleted_users_db = cursor.fetchall()

        for user_id, username, deleted_at in deleted_users_db:
            deleted_time = datetime.strptime(deleted_at, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - deleted_time).days > 30:
                permanently_delete_user(user_id, None)

def open_file(file_path):
    """Open the file with the default system program."""
    try:
        os.startfile(file_path)  # On Windows
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {e}")
    open_subadmin_panel()


def logout_to_panel2():
    global admin_window
    for _ in range(2):
        try:
            admin_window.destroy()
        except:
            pass  # admin_window already destroyed or never created

        panel_2.pack(fill="both", expand=True)

def upload_file():
    file_path = filedialog.askopenfilename()  # Open file dialog
    if file_path:
        file_name = file_path.split("/")[-1]  # Extract file name
        execute_query("INSERT INTO inquiry_files (file_name, file_path) VALUES (?, ?)", (file_name, file_path))
        messagebox.showinfo("Success", f"File '{file_name}' uploaded for approval.")
    open_subadmin_panel()


def manage_users():
    users_window = tk.Toplevel(root)
    users_window.title("Manage Users")

    # Fullscreen dimensions
    screen_width = users_window.winfo_screenwidth()
    screen_height = users_window.winfo_screenheight()
    users_window.geometry(f"{screen_width}x{screen_height}")

    # Load and resize background image to full screen
    bg_image = Image.open("logo7.png")
    bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Set the background image
    bg_label = tk.Label(users_window, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(relwidth=1, relheight=1)

    # Title label
    tk.Label(users_window, text="Manage Users", font=("Arial", 32, "bold"),
             bg="midnightblue", fg="white").pack(pady=40)

    # Scrollable frame container
    container = tk.Frame(users_window, bg="white")
    container.pack(fill="both", expand=True, padx=int(screen_width * 0.15), pady=10)  # 15% horizontal padding

    canvas = tk.Canvas(container, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Fetch and display users that are not deleted
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username != 'ADMINISTRATOR' AND deleted = 0")
        users = cursor.fetchall()

    for index, (user_id, username) in enumerate(users):
        row_frame = tk.Frame(scrollable_frame, bg="white")
        row_frame.pack(pady=8)

        username_entry = tk.Entry(row_frame, font=("Arial", 14), bg="white", width=35)
        username_entry.insert(0, username)
        username_entry.grid(row=0, column=0, padx=10)

        update_button = tk.Button(row_frame, text="Update", bg="blue", fg="white", font=("Arial", 12),
                                  width=12,
                                  command=lambda uid=user_id, entry=username_entry: update_user(uid, entry))
        update_button.grid(row=0, column=1, padx=10)

        delete_button = tk.Button(row_frame, text="Delete", bg="red", fg="white", font=("Arial", 12),
                                  width=12,
                                  command=lambda uid=user_id: delete_user(uid))
        delete_button.grid(row=0, column=2, padx=10)

        password_button = tk.Button(row_frame, text="Change Password", bg="green", fg="white", font=("Arial", 12),
                                    width=18,
                                    command=lambda uid=user_id: change_password(uid))
        password_button.grid(row=0, column=3, padx=10)

    close_button = tk.Button(
        users_window,
        text="Close",
        command=lambda: [users_window.destroy()],
        font=("Arial", 16, "underline"),
        bg="white",
        fg="deepskyblue",
        width=20,
        height=2
    )  # ✅ This closing parenthesis was missing

    close_button.pack(pady=30)

def update_user(user_id, entry):
    new_username = entry.get()
    if new_username:
        with sqlite3.connect("imrsearch.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username=? WHERE id=?", (new_username, user_id))
            conn.commit()
        messagebox.showinfo("Success", "Username updated successfully!")
        manage_users()

def delete_user(user_id):
    """Mark a user as deleted (soft delete)."""
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?")
    if confirm:
        execute_query("UPDATE users SET deleted = 1 WHERE id=?", (user_id,))
        messagebox.showinfo("Success", "User has been marked as deleted!")
        manage_users()  # Refresh the user list

def change_password(user_id):
    new_password = simpledialog.askstring("Change Password", "Enter new password:", show="*")
    if new_password:
        with sqlite3.connect("imrsearch.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
            conn.commit()
        messagebox.showinfo("Success", "Password changed successfully!")
        manage_users()


def delete_approved_file(file_name, file_path, frame):
    """Marks an approved file as deleted instead of removing it from the database."""
    confirm = messagebox.askyesno("Delete File", f"Are you sure you want to delete '{file_name}' from the archive?")
    if confirm:
        with sqlite3.connect("imrsearch.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE approved_files SET deleted = TRUE WHERE file_name=? AND file_path=?", (file_name, file_path))
            conn.commit()
        messagebox.showinfo("Deleted", f"File '{file_name}' has been moved to the trash bin.")



def inquiry():
    """Displays the inquiry window for approving, rejecting, or deleting files."""
    inquiry_window = tk.Toplevel(root)
    inquiry_window.title("Library Tech Inquiry")

    # Set full screen using screen dimensions
    screen_width = inquiry_window.winfo_screenwidth()
    screen_height = inquiry_window.winfo_screenheight()
    inquiry_window.geometry(f"{screen_width}x{screen_height}")

    # Optional: prevent resizing if you want fixed fullscreen
    # inquiry_window.resizable(False, False)

    # Beige background to mimic library vibe
    inquiry_window.configure(bg="#f3e8d1")

    # Escape key to allow exit from full screen
    inquiry_window.bind("<Escape>", lambda e: inquiry_window.attributes("-fullscreen", False))

    # Font and color theme
    label_font = ("Georgia", 12)
    button_font = ("Georgia", 10, "bold")

    def approve_file(file_name, file_path, frame):
        execute_query("INSERT INTO approved_files (file_name, file_path) VALUES (?, ?)", (file_name, file_path))
        execute_query("DELETE FROM inquiry_files WHERE file_name=? AND file_path=?", (file_name, file_path))  # Remove from inquiries
        messagebox.showinfo("Approved", f"File '{file_name}' has been approved!")
        inquiry()


    def reject_file(file_name, file_path, frame):
        execute_query("DELETE FROM inquiry_files WHERE file_name=? AND file_path=?", (file_name, file_path))
        messagebox.showinfo("Rejected", f"File '{file_name}' has been rejected!")
        inquiry()

    # Fetch inquiries from the database
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name, file_path FROM inquiry_files")
        inquiries_db = cursor.fetchall()

    for file_name, file_path in inquiries_db:
        # Book-like frame design for each file entry
        file_frame = tk.Frame(inquiry_window, bg="#e1d7c6", padx=15, pady=10, relief="solid", borderwidth=2)
        file_frame.pack(fill="x", padx=15, pady=8)

        file_label = tk.Label(file_frame, text=f"Book: {file_name}\nLocation: {file_path}", bg="#e1d7c6", font=label_font, anchor="w")
        file_label.pack(side="left", expand=True, fill="x", padx=5)

        approve_btn = tk.Button(file_frame, text="✔ Approve", bg="#8a9a5b", fg="white", font=button_font,
                                command=lambda f=file_name, p=file_path, fr=file_frame: approve_file(f, p, fr))
        approve_btn.pack(side="right", padx=8)

        reject_btn = tk.Button(file_frame, text="✖ Reject", bg="#d34b2d", fg="white", font=button_font,
                               command=lambda f=file_name, p=file_path, fr=file_frame: reject_file(f, p, fr))
        reject_btn.pack(side="right", padx=8)

    # Button to delete approved files with library card design
    ttk.Button(inquiry_window, text="🗑 Delete Approved Files", command=delete_approved_files,
               style="TButton").pack(pady=15)

    # Close button with a soft, classic font
    close_button = tk.Button(
        inquiry_window,
        text="Close",
        command=lambda: [inquiry_window.destroy()],
        font=("Georgia", 25, "underline"),
        bg="#e6f7ff",
        fg="#5d8e8f"
    )

    close_button.pack(pady=10)


    # Styling for the button with library-like appearance
    style = ttk.Style()
    style.configure("TButton",
                    font=("Georgia", 30, "bold"),
                    padding=10,
                    background="#e1d7c6",
                    foreground="#4f4f4f")


# Start the inquiry process


def delete_approved_file(file_name, file_path, frame):
    """Mark an approved file as deleted (not remove from UI)."""
    confirm = messagebox.askyesno("Delete File", f"Are you sure you want to delete '{file_name}' from the archive?")
    if confirm:
        # Mark the file as deleted (set 'deleted' column to 1)
        execute_query("UPDATE approved_files SET deleted = 1 WHERE file_name=? AND file_path=?", (file_name, file_path))

        # Destroy the UI frame to remove it from the current screen


        messagebox.showinfo("Deleted",
                            f"File '{file_name}' has been marked as deleted. It will now appear in the Trash Bin.")
        delete_approved_files()


def delete_approved_files():
    """Opens a full-screen window to delete approved files with a library-tech theme."""
    delete_window = tk.Toplevel()
    delete_window.title("📂 Digital Archive Management")

    # Full screen setup
    screen_width = delete_window.winfo_screenwidth()
    screen_height = delete_window.winfo_screenheight()
    delete_window.geometry(f"{screen_width}x{screen_height}")
    delete_window.configure(bg="#1E1E2E")

    # Header
    tk.Label(delete_window, text="📂 Digital Archive Management", font=("Arial", 28, "bold"),
             bg="#1E1E2E", fg="#00ADB5").pack(pady=30)

    # Main content frame
    frame = tk.Frame(delete_window, bg="#1E1E2E")
    frame.pack(fill=tk.BOTH, expand=True, padx=60, pady=20)

    canvas = tk.Canvas(frame, bg="#1E1E2E", highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1E1E2E")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Fetch and display approved files that are not deleted
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name, file_path FROM approved_files WHERE deleted = 0")
        approved_files_db = cursor.fetchall()

    # Calculate card width (e.g., 75% of screen width)
    card_width = int(screen_width * 0.75)

    for file_name, file_path in approved_files_db:
        file_frame = tk.Frame(scrollable_frame, bg="#44475A", relief="raised", bd=3)
        file_frame.pack(pady=15, anchor="center")  # Center the frame

        file_frame.configure(width=card_width, height=80)
        file_frame.pack_propagate(False)  # Prevent shrinking

        file_label = tk.Label(file_frame, text=file_name, bg="#44475A", fg="white",
                              font=("Arial", 16, "bold"), anchor="w")
        file_label.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        delete_btn = tk.Button(file_frame, text="🗑 Remove", bg="#FF5555", fg="white",
                               font=("Arial", 12, "bold"),
                               command=lambda f=file_name, p=file_path, fr=file_frame: delete_approved_file(f, p, fr))
        delete_btn.pack(side="right", padx=20)

    # Close button
    ttk.Button(
        delete_window,
        text="❌ Close",
        command=lambda: [delete_window.destroy()]
    ).pack(pady=30)

    # Optional: Escape key to exit fullscreen
    delete_window.bind("<Escape>", lambda e: delete_window.attributes("-fullscreen", False))


def open_file(file_path):
    """Opens a file from the approved library."""
    try:
        os.startfile(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open file: {e}")


def search_files(event, search_entry, file_labels, canvas, scrollable_frame):
    """Searches for files, highlights matches, and scrolls to the first match."""
    query = search_entry.get().lower()
    found_label = None  # Store the first matching file label

    for label in file_labels:
        if query in label.cget("text").lower():
            label.config(bg="#0077B6", fg="white")  # Highlight matching file
            if found_label is None:
                found_label = label  # Store the first matching label
        else:
            label.config(bg="#44475A", fg="white")  # Reset others

    if found_label:
        # Ensure all layout updates are processed
        canvas.update_idletasks()

        # Calculate relative position inside the scrollable frame
        label_y = found_label.winfo_rooty() - scrollable_frame.winfo_rooty()

        # Get full scroll region and calculate scrolling percentage
        scroll_region = canvas.bbox("all")
        if scroll_region:
            scroll_height = scroll_region[3] - scroll_region[1]  # Total height
            if scroll_height > 0:
                scroll_fraction = label_y / scroll_height
                canvas.yview_moveto(scroll_fraction)


def view_content():
    """Creates a full-screen, tech-themed digital archive viewer."""
    view_window = tk.Toplevel()
    view_window.title("📚 Digital Library - Archive")
    view_window.configure(bg="#1E1E2E")

    # Full screen
    screen_width = view_window.winfo_screenwidth()
    screen_height = view_window.winfo_screenheight()
    view_window.geometry(f"{screen_width}x{screen_height}")

    # Grid layout
    view_window.columnconfigure(0, weight=1)
    view_window.columnconfigure(1, weight=4)
    view_window.columnconfigure(2, weight=1)

    for i in range(5):
        view_window.rowconfigure(i, weight=0)
    view_window.rowconfigure(3, weight=1)  # File list grows vertically

    # 📚 Title
    title = tk.Label(
        view_window,
        text="📚 Digital Archive Viewer",
        font=("Segoe UI", 32, "bold"),
        bg="#1E1E2E",
        fg="#00ADB5"
    )
    title.grid(row=0, column=1, pady=(30, 10), sticky="n")

    # 🔍 Search Frame
    search_frame = tk.Frame(view_window, bg="#1E1E2E")
    search_frame.grid(row=1, column=1, pady=10, sticky="n")

    search_entry = ttk.Entry(search_frame, font=("Arial", 16), width=60)
    search_entry.pack(side=tk.LEFT, padx=10, ipady=6)

    search_button = ttk.Button(
        search_frame,
        text="🔍 Search",
        command=lambda: search_files(None, search_entry, file_labels, canvas, scrollable_frame)
    )
    search_button.pack(side=tk.LEFT, padx=5)

    search_entry.bind(
        "<KeyRelease>",
        lambda event: search_files(event, search_entry, file_labels, canvas, scrollable_frame)
    )

    # 📂 File List Frame
    file_list_outer_frame = tk.Frame(view_window, bg="#1E1E2E")
    file_list_outer_frame.grid(row=3, column=1, sticky="nsew", padx=60, pady=(10, 20))

    file_list_outer_frame.grid_rowconfigure(0, weight=1)
    file_list_outer_frame.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(file_list_outer_frame, bg="#1E1E2E", highlightthickness=0)
    scrollbar = ttk.Scrollbar(file_list_outer_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    scrollable_frame = tk.Frame(canvas, bg="#282A36")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # 📄 Populate File Entries
    file_labels = []
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()

        # Fetch only files that are not deleted
        cursor.execute("SELECT file_name, file_path FROM approved_files WHERE deleted = 0")
        approved_files_db = cursor.fetchall()

    for file_name, file_path in approved_files_db:
        file_frame = tk.Frame(
            scrollable_frame,
            bg="#44475A",
            padx=30,
            pady=20,
            relief="ridge",
            bd=4
        )
        file_frame.pack(fill="x", expand=True, padx=30, pady=12)

        file_label = tk.Label(
            file_frame,
            text=file_name,
            bg="#44475A",
            fg="white",
            font=("Arial", 18, "bold"),
            anchor="w",
            cursor="hand2",
            padx=10,
            pady=5
        )
        file_label.pack(fill="x")

        file_label.bind("<Button-1>", lambda event, path=file_path: open_file(path))
        file_label.bind("<Enter>", lambda e, lbl=file_label: lbl.config(bg="#0077B6"))
        file_label.bind("<Leave>", lambda e, lbl=file_label: lbl.config(bg="#44475A"))

        file_labels.append(file_label)

    # ❌ Close Button
    close_btn = ttk.Button(view_window, text="❌ Close", command=view_window.destroy)
    close_btn.grid(row=4, column=1, pady=20, sticky="n")




def logout():
    global admin_window
    try:
        admin_window.destroy()
        admin_window = None  # <-- Important!
    except:
        pass
    panel_2.pack(fill="both", expand=True)

# Function to add a new user
def add_user(username, password, pin):
    # Check if the username already exists
    if fetch_one("SELECT * FROM users WHERE username=?", (username,)):
        return False  # Username already exists

    # Insert new user into the database
    execute_query("INSERT INTO users (username, password, pin) VALUES (?, ?, ?)", (username, password, pin))
    return True  # Account creation successful


# Function to update admin credentials
def update_admin_credentials(new_username, new_password, new_pin):
    execute_query("UPDATE users SET username=?, password=?, pin=? WHERE id=2",
                  (new_username, new_password, new_pin))

    # Verify the update
    updated_admin = fetch_one("SELECT id FROM users WHERE id=2")
    if updated_admin:
        messagebox.showinfo("Success", "Admin credentials updated successfully!")
    else:
        messagebox.showerror("Error", "Failed to update admin credentials.")



def open_admin_panel():
    global admin_window
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel")

    # Get screen dimensions for fullscreen
    screen_width = admin_window.winfo_screenwidth()
    screen_height = admin_window.winfo_screenheight()
    admin_window.geometry(f"{screen_width}x{screen_height}")

    bg_image = Image.open("admin3.png")
    bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)

    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_image_label = tk.Label(admin_window, image=bg_photo)
    bg_image_label.image = bg_photo  # Keep a reference!
    bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Set background color
    admin_window.configure(bg="#F3ECD3")

    # Add a frame to hold the buttons and center it
    button_frame = tk.Frame(admin_window, bg="#9EB1C1")
    button_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Hover effect function
    def add_hover_effect(widget, hover_bg, hover_fg, default_bg, default_fg):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg, fg=hover_fg))
        widget.bind("<Leave>", lambda e: widget.config(bg=default_bg, fg=default_fg))

    # Function to change credentials
    def change_credentials():
        current_password = simpledialog.askstring("Current Password", "Enter current password:", show="*")

        # Ensure that we're modifying the admin account with id=2
        admin = fetch_one("SELECT * FROM users WHERE id=2 AND password=?", (current_password,))

        if not admin:
            messagebox.showerror("Error", "Incorrect password!")
            return

        new_username = simpledialog.askstring("New Username", "Enter new username:")
        new_password = simpledialog.askstring("New Password", "Enter new password:", show="*")
        new_pin = simpledialog.askstring("New PIN", "Enter new PIN:", show="*")

        if new_username and new_password and new_pin:
            update_admin_credentials(new_username, new_password, new_pin)
        else:
            messagebox.showerror("Error", "All fields are required!")

    # Create buttons
    buttons = [
        {
            "text": "Create Faculty Account 🧑‍🏫",
            "command": create_account,
            "row": 0, "column": 0
        },
        {
            "text": "Manage Users 🧑‍💻",
            "command": manage_users,
            "row": 0, "column": 1
        },
        {
            "text": "IM'S INQUIRY 📜",
            "command": inquiry,
            "row": 0, "column": 2
        },
        {
            "text": "Change Credentials 🔑",
            "command": change_credentials,
            "row": 1, "column": 0
        },
        {
             "text": "Logout 🚪",
    "command": lambda: logout_to_panel2(),
    "row": 1, "column": 2
        },
        {
            "text": "Data Recovery 🚪",
            "command": show_trash_bin,
            "row": 1, "column": 1
        }
    ]

    for btn in buttons:
        b = tk.Button(
            button_frame,
            text=btn["text"],
            command=btn["command"],
            font=("Arial", 16, "bold"),
            bg="maroon",
            fg="#FFD700",
            width=30 if btn["text"] != "Logout 🚪" else 20,
            height=2,
            relief="flat",
            cursor="hand2"
        )
        b.grid(row=btn["row"], column=btn["column"], pady=10, padx=10, sticky="ew")
        add_hover_effect(b, "#A52A2A", "white", "maroon", "#FFD700")

    # Escape key to exit fullscreen mode (if needed)
    admin_window.bind("<Escape>", lambda e: admin_window.attributes("-fullscreen", False))






# Function to validate user login
def validate_user(username, password):
    with sqlite3.connect("imrsearch.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()
    conn.close()
    return user

def on_enter(e):
    e.widget.config(bg="#005A9E")

def on_leave(e):
    e.widget.config(bg="#0078D7")


# Function to switch panels
def open_subadmin_panel():
    subadmin_window = tk.Toplevel(root)
    subadmin_window.title("Faculty Panel")

    # Full screen setup
    screen_width = subadmin_window.winfo_screenwidth()
    screen_height = subadmin_window.winfo_screenheight()
    subadmin_window.geometry(f"{screen_width}x{screen_height}")
    subadmin_window.configure(bg="#1E1E1E")  # Dark tech background

    # Title
    title_label = tk.Label(
        subadmin_window,
        text="👨‍🏫 Welcome to the Faculty Panel",
        font=("Segoe UI", 28, "bold"),
        bg="#1E1E1E",
        fg="#00FFFF"
    )
    title_label.pack(pady=50)

    # Unified button styling
    btn_color = "#0078D7"
    btn_hover = "#005A9E"
    btn_text_color = "white"
    btn_width = 30
    btn_height = 3
    btn_font = ("Arial", 16, "bold")

    # Hover function
    def add_hover(widget, hover_bg, normal_bg):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

    # Upload Button
    upload_btn = tk.Button(
        subadmin_window,
        text="📤 Upload Material",
        font=btn_font,
        bg=btn_color,
        fg=btn_text_color,
        width=btn_width,
        height=btn_height,
        bd=0,
        relief="flat",
        command=upload_file
    )
    upload_btn.pack(pady=20)
    add_hover(upload_btn, btn_hover, btn_color)

    # View Button
    view_btn = tk.Button(
        subadmin_window,
        text="📂 View Content",
        font=btn_font,
        bg=btn_color,
        fg=btn_text_color,
        width=btn_width,
        height=btn_height,
        bd=0,
        relief="flat",
        command=view_content
    )
    view_btn.pack(pady=20)
    add_hover(view_btn, btn_hover, btn_color)

    # Close Button
    close_color = "#FF5555"
    close_hover = "#CC4444"

    close_btn = tk.Button(
        subadmin_window,
        text="❌ Close",
        font=btn_font,
        bg=close_color,
        fg="white",
        width=btn_width,
        height=btn_height,
        bd=0,
        relief="flat",
        command=subadmin_window.destroy
    )
    close_btn.pack(pady=20)
    add_hover(close_btn, close_hover, close_color)


failed_attempts = 3
lock_time = 60
# Function to handle user login
def login():
    global failed_attempts, lock_time

    username = email_entry.get().strip()
    password = password_entry.get().strip()

    # Clear input fields immediately after storing values
    email_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

    if failed_attempts >= 3:
        remaining_time = int(30 - (time.time() - lock_time))
        if remaining_time > 0:
            messagebox.showerror("Error", f"Too many failed attempts. Try again in {remaining_time} seconds.")
            return
        else:
            failed_attempts = 0  # Reset failed attempts after 30 seconds

    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password!")
        return

    admin = fetch_one("SELECT username, password, pin FROM users WHERE id=2")

    if admin and username == admin[0] and password == admin[1]:
        pin = simpledialog.askstring("Admin Security PIN", "Enter the 4-digit Admin PIN:", show="*")
        if pin == admin[2]:
            messagebox.showinfo("Success", "Welcome, Administrator!")
            open_admin_panel()
            return
        else:
            messagebox.showerror("Error", "Invalid Admin PIN.")
            failed_attempts += 1
    else:
        user = fetch_one("SELECT username, password, pin FROM users WHERE username=? AND password=?",
                         (username, password))

        if user:
            pin = simpledialog.askstring("Security PIN", "Enter your 4-digit PIN:", show="*")
            if pin == user[2]:
                messagebox.showinfo("Success", f"Welcome, {username}!")
                open_subadmin_panel()
                return
            else:
                messagebox.showerror("Error", "Invalid PIN.")
                failed_attempts += 1
        else:
            messagebox.showerror("Error", "Invalid username or password.")
            failed_attempts += 1

    # Lock login for 30 seconds if too many failed attempts
    if failed_attempts >= 3:
        lock_time = time.time()
        messagebox.showerror("Error", "Too many failed attempts. Try again in 30 seconds.")



def create_account():
    signup_window = tk.Toplevel(root)
    signup_window.title("Create New Account")

    # Make window full screen
    screen_width = signup_window.winfo_screenwidth()
    screen_height = signup_window.winfo_screenheight()
    signup_window.geometry(f"{screen_width}x{screen_height}")
    signup_window.configure(bg="#f0e6dc")  # Light paper-like background for a library feel

    # Optional: Load a themed background image
    try:
        bg_image = Image.open("tech_library_bg.png")
        bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
        bg_tk = ImageTk.PhotoImage(bg_image)
        background_label = tk.Label(signup_window, image=bg_tk)
        background_label.image = bg_tk
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        background_label = tk.Label(signup_window, bg="#f0e6dc")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame for signup form
    form_frame = tk.Frame(signup_window, bg="white", bd=3, relief="ridge")
    form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=500)

    tk.Label(form_frame, text="📚 Create Faculty Account", font=("Georgia", 20, "bold"),
             bg="white", fg="#800000").pack(pady=20)

    labels = ["Username:", "Password:", "Re-enter Password:", "4-Digit Authentication:"]
    entries = []

    for label_text in labels:
        tk.Label(form_frame, text=label_text, bg="white", font=("Arial", 12)).pack(pady=(10, 0))
        entry = tk.Entry(form_frame, width=35, font=("Arial", 12), bd=2, relief="solid",
                         show="*" if "Password" in label_text else "")
        entry.pack(pady=5)
        entries.append(entry)

    def submit_signup():
        username, password, re_password, pin = [entry.get().strip() for entry in entries]

        if not username or not password or not re_password or not pin:
            messagebox.showerror("Error", "All fields are required!")
            create_account()
            return


        if len(username) < 8 or not any(char.isupper() for char in username):
            messagebox.showerror("Error", "Username must be at least 8 characters with one uppercase letter!")
            create_account()
            return

        if len(password) < 8 or not any(char.isupper() for char in password) or not any(
                char in string.punctuation for char in password):
            messagebox.showerror("Error",
                                 "Password must be at least 8 characters, include one uppercase letter and one symbol!")
            create_account()
            return

        if password != re_password:
            messagebox.showerror("Error", "Passwords do not match!")
            create_account()
            return

        if not pin.isdigit() or len(pin) != 4:
            messagebox.showerror("Error", "PIN must be a 4-digit number!")
            create_account()
            return

        if add_user(username, password, pin):
            messagebox.showinfo("Success", "Account successfully created!")
            signup_window.destroy()
            open_admin_panel()
        else:
            messagebox.showerror("Error", "Username already exists!")
            create_account()
            return

    tk.Button(form_frame, text="Create Account", command=submit_signup,
              bg="#800000", fg="#FFD700", font=("Arial", 14, "bold"),
              relief="flat", width=25, height=2).pack(pady=20)

    tk.Button(form_frame, text="❌ Cancel", command=signup_window.destroy,
              bg="#e0e0e0", fg="#333333", font=("Arial", 12, "bold"),
              relief="flat", width=20).pack(pady=5)

# Create main application window
def switch_to_panel_2():
    panel_1.pack_forget()  # Hide panel_1
    panel_2.pack(fill="both", expand=True)  # Show panel_2


# Function to switch panels with a delay
def open_panel_2():
    panel_1_Label.config(text="Redirecting...")  # Update text
    root.after(2000, switch_to_panel_2)  # Wait 2 seconds, then switch



# Initialize main window
root = tk.Tk()
root.title("IMRSearch: Instructional Materials Repository and Search System")
root.attributes('-fullscreen', True)
root.configure(bg="#f9f2d0")
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# ================= Header =================
header = tk.Frame(root, bg="#2c1b18", height=100)  # dark maroon tech feel
header.pack(fill="x", side="top")

# Logo
logo_path = resource_path("logo1.jpg")
logo_img = Image.open(logo_path).resize((180, 90))
logo_photo = ImageTk.PhotoImage(logo_img)

logo_label = tk.Label(header, image=logo_photo, bg="#2c1b18")
logo_label.pack(side="left", padx=20)

# Title label
title_label = tk.Label(
    header,
    text="IMRSearch: Instructional Materials Repository and Search System",
    font=("Segoe UI", 22, "bold"),  # Sleek, clean font
    bg="#2c1b18",
    fg="#FFD700",
    anchor="w",
    wraplength=root.winfo_screenwidth() - 250
)
title_label.pack(side="left", padx=10, fill="x", expand=True)

# ================= Panel 1: Welcome =================
panel_1 = tk.Frame(root, bg="#f9f2d0")
panel_1.pack(fill="both", expand=True)

# Background image (library aesthetic)
bg_image_path = resource_path("logo3.jpg")
bg_image = Image.open(bg_image_path).resize((root.winfo_screenwidth(), root.winfo_screenheight()))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(panel_1, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)



# ================= Panel 2: Login Panel =================
panel_2 = tk.Frame(root, bg="#f9f2d0")

# Background for login panel
login_bg = Image.open(resource_path("logo2.png")).resize(
    (root.winfo_screenwidth(), root.winfo_screenheight())
)
login_photo = ImageTk.PhotoImage(login_bg)
login_bg_label = tk.Label(panel_2, image=login_photo)
login_bg_label.place(relwidth=1, relheight=1)

# ================= Redirect =================
root.after(2000, switch_to_panel_2)
def switch_to_panel_3():

    open_admin_panel.pack_forget()  # Hide panel_1
    panel_2.pack(fill="both", expand=True)  # Show panel_2

def switch_to_panel_1():
    root.destroy()

# "Go to Login Panel" button

# Panel 2 (Login Panel - Initially Hidden)
panel_2 = tk.Frame(root, bg="#f9f2d0")
panel_2.pack_forget()



# Get screen dimensions dynamically
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Open and resize image to fullscreen
background_image = Image.open("logo2.png")
background_resized = background_image.resize((screen_width, screen_height))
background_tk = ImageTk.PhotoImage(background_resized)

# Create a label to hold the full-screen background image
background_label = tk.Label(panel_2, image=background_tk)
background_label.image = background_tk  # Prevent garbage collection
background_label.place(relwidth=1, relheight=1)









# Adjusted width and height
login_frame = tk.Frame(panel_2, bg="maroon", width=560, height=625)  # 30% smaller width, 25% larger height
login_frame.place(relx=0.5, rely=0.5, anchor="center")

# Label for "Login"
tk.Label(login_frame, text="Login", font=("Arial", 32, "bold"), bg="maroon", fg="white").pack(pady=20)

# Email entry field (adjusted width)
email_entry = tk.Entry(login_frame, width=30, font=("Arial", 16), bd=2, relief="solid")
email_entry.pack(pady=20, padx=40)

# Password entry field (adjusted width)
password_entry = tk.Entry(login_frame, width=30, font=("Arial", 16), bd=2, relief="solid", show="*")
password_entry.pack(pady=20, padx=40)

# Checkbox to toggle password visibility
show_password_var = tk.BooleanVar()
show_password_checkbox = tk.Checkbutton(login_frame, text="Show Password", variable=show_password_var,
                                        command=toggle_password, bg="maroon", fg="white")
show_password_checkbox.pack(pady=5)

tk.Button(login_frame, text="Log In", command=login, width=30, bg="#FFD700", fg="#800000", font=("Arial", 12, "bold"),
          relief="flat").pack(pady=10)
tk.Button(login_frame, text="Terminate", command=switch_to_panel_1, bg="#800000", fg="#FFD700",
          font=("Arial", 12, "bold"), relief="flat", width=20).pack(pady=10)

root.mainloop()
