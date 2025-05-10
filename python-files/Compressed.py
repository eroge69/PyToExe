import re
import smtplib
import dns.resolver
import socket
import pyodbc
import threading
import queue
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import tkinter.font as tkfont
import datetime
from dotenv import load_dotenv
load_dotenv()
import os
from db_config import conn_str


#Current Run Time
current_run_time = datetime.datetime.now()

# --- Configuration ---
SMTP_TIMEOUT = 10
SENDER_EMAIL = "check@yourdomain.com"
socket.setdefaulttimeout(SMTP_TIMEOUT)

logging.basicConfig(filename="email_validator.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Validation Functions ---
def is_valid_email_format(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def get_mx_record(domain: str) -> str:
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = sorted(answers, key=lambda r: r.preference)
        return str(mx_records[0].exchange)
    except Exception:
        return None

def verify_email_smtp(email: str) -> str:
    try:
        domain = email.split('@')[1]
        mx_host = get_mx_record(domain)
        if not mx_host:
            return "unknown"
        with smtplib.SMTP(mx_host, timeout=SMTP_TIMEOUT) as server:
            server.helo(socket.gethostname())
            server.mail(SENDER_EMAIL)
            code, _ = server.rcpt(email)
            return "valid" if code in (250, 251) else "invalid"
    except Exception:
        print("invalid")
   
def get_final_status(format_status: str, smtp_status: str) -> str:
    if format_status == "valid" and smtp_status=="valid":
        return "valid"
    else:
        return "invalid"
 
def parse_date(date_str: str) -> datetime:
    return datetime.datetime.strptime(date_str.strip().split()[0], "%Y-%m-%d").date()
    
    
# Store popup references to toggle them
calendar_popups = {}
# Track which date to fill next: 'from' or 'to'
next_date_target = "from"

def open_calendar(entry_from, entry_to, var_from, var_to, button):
    global next_date_target

    # Destroy any existing calendar
    for popup in calendar_popups.values():
        if popup.winfo_exists():
            popup.destroy()
    calendar_popups.clear()

    calendar_window = tk.Toplevel(window)
    calendar_window.overrideredirect(True)
    calendar_window.attributes("-topmost", True)

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = button.winfo_rootx()
    y = button.winfo_rooty() + button.winfo_height()

    calendar_width = 194
    calendar_height = 180

    if x + calendar_width > screen_width:
        x = screen_width - calendar_width
    if y + calendar_height > screen_height:
        y = screen_height - calendar_height
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    calendar_window.geometry(f"{calendar_width}x{calendar_height}+{x}+{y}")

    calendar = Calendar(
        calendar_window,
        selectmode='day',
        date_pattern="yyyy-MM-dd",
        background="lightblue",
        foreground="black",
        font=("Arial", 8)
    )
    calendar.pack()

    def on_select():
        global next_date_target
        selected_date = calendar.get_date()
        if next_date_target == "from":
            var_from.set(selected_date)
            next_date_target = "to"
        else:
            var_to.set(selected_date)
            next_date_target = "from"
        calendar_window.destroy()
        window.unbind("<Button-1>", click_binding_id)

    tk.Button(calendar_window, text="Select", command=on_select, bg="black", fg="white", padx=100, pady=100).pack()
    calendar_popups["calendar"] = calendar_window

    # Close calendar if user clicks outside
    def close_calendar_on_click(event):
        if calendar_window.winfo_exists():
            if not (calendar_window.winfo_rootx() <= event.x_root <= calendar_window.winfo_rootx() + calendar_window.winfo_width() and
                    calendar_window.winfo_rooty() <= event.y_root <= calendar_window.winfo_rooty() + calendar_window.winfo_height()):
                calendar_window.destroy()
                window.unbind("<Button-1>", click_binding_id)

    # Define binding AFTER function is defined
    click_binding_id = window.bind("<Button-1>", close_calendar_on_click)

    def on_window_deactivate(event):
        if calendar_window.winfo_exists():
            calendar_window.destroy()

    def on_window_minimize(event):
        if calendar_window.winfo_exists():
            calendar_window.destroy()

    window.bind("<Deactivate>", on_window_deactivate)
    window.bind("<Unmap>", on_window_minimize)

# --- Main Validation Logic ---
result_queue = queue.Queue()
def start_validation():
    start_button.config(state=tk.DISABLED)  # Prevent Duplicate Clicks While Validatiob
    for item in result_table.get_children():
        result_table.delete(item)             

    try:
        start_member = int(start_member_entry.get()) if start_member_entry.get() else None
        end_member = int(end_member_entry.get()) if end_member_entry.get() else None
        start_date = parse_date(start_date_var.get()) if start_date_var.get() else None
        end_date = parse_date(end_date_var.get()) if end_date_var.get() else None

        if not (member_no_checkbox_var.get() or date_checkbox_var.get()):
            messagebox.showerror("Input Error", "Please enable and provide Member No or Register Date range.")
            start_button.config(state=tk.NORMAL)
            return

        if member_no_checkbox_var.get() and (not start_member or not end_member):
            messagebox.showerror("Input Error", "Please provide both Member No From and To.")
            start_button.config(state=tk.NORMAL)
            return

        if date_checkbox_var.get() and (not start_date or not end_date):
            messagebox.showerror("Input Error", "Please provide both Register Date From and To.")
            start_button.config(state=tk.NORMAL)
            return

    except ValueError:
        messagebox.showerror("Input Error", "Please check your input formats.")
        start_button.config(state=tk.NORMAL)
        return

    def run_validation():
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Build user query based on filters
            query = "SELECT member_no, email, reg_date FROM dbo.user_mast"
            conditions = []
            params = []

            if member_no_checkbox_var.get():
                conditions.append("member_no BETWEEN ? AND ?")
                params.extend([start_member, end_member])
            if date_checkbox_var.get():
                conditions.append("reg_date BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            total_records = len(rows)

            if not rows:
                messagebox.showinfo("No Data", "No matching records found.")
                start_button.config(state=tk.NORMAL)
                return

            current_run_time = datetime.datetime.now()

            # Sending Already Validated Record To Main_Page
            cursor.execute("""
                SELECT member_no, mail_status FROM dbo.email_validation_results
                WHERE CAST(run_time AS DATE) = CAST(GETDATE() AS DATE)
            """)
            validated_today = {row.member_no: row.mail_status for row in cursor.fetchall()}

            to_validate = []                      #Will Use By email_validation_results Table
            valid_count = invalid_count = 0
            saved_records = 0

            for member_no, email, reg_date in rows:
                if member_no in validated_today:
                    status_str = "valid" if validated_today[member_no] == 1 else "invalid"
                    result_queue.put(('update', member_no, email, status_str))
                    if status_str == "valid":
                        valid_count += 1
                    else:
                        invalid_count += 1
                    result_queue.put(('counts', valid_count, invalid_count))
                else:
                    to_validate.append((member_no, email, reg_date))

            if not to_validate:
                messagebox.showinfo("Notice", "All records were validated today.")
                result_queue.put(('complete', valid_count, invalid_count))
                return

            # email_querry_status Part Of Insertion
            cursor.execute("""
                INSERT INTO dbo.email_query_status (
                    run_time, total_records, saved_records,
                    member_no_from, member_no_to,
                    register_date_from, register_date_to
                )
                OUTPUT INSERTED.query_id             
                VALUES (?, ?, ?, ?, ?, ?, ?)        
            """, (
                current_run_time,
                total_records,
                0,
                start_member,
                end_member,
                start_date,
                end_date
            ))
            query_id = cursor.fetchone()[0]                #So That Starts From Latest querry_id

            # Prepare bulk MERGE values 
            # Check For Valid And Invalid In to_validate
            merge_values = []
            for member_no, email, reg_date in to_validate:
                if not email:
                    format_status = smtp_status = "invalid"
                else:
                    format_status = "valid" if is_valid_email_format(email) else "invalid"
                    smtp_status = verify_email_smtp(email) if format_status == "valid" else "invalid"

                final_status = get_final_status(format_status, smtp_status)
                mail_status = 1 if final_status == "valid" else 0

                merge_values.append((member_no, current_run_time, mail_status))

                if mail_status:
                    valid_count += 1
                else:
                    invalid_count += 1

                result_queue.put(('update', member_no, email, final_status))
                result_queue.put(('counts', valid_count, invalid_count))
                saved_records += 1

            # email_validation_results Part With Update And Insert
            for member_no, run_time, mail_status in merge_values:
                cursor.execute("""
                    MERGE INTO dbo.email_validation_results AS target
                    USING (SELECT ? AS member_no, ? AS run_time, ? AS mail_status) AS source
                    ON target.member_no = source.member_no
                    WHEN MATCHED AND CONVERT(date, target.run_time) <> CONVERT(date, GETDATE()) THEN
                        UPDATE SET run_time = source.run_time, mail_status = source.mail_status
                    WHEN NOT MATCHED THEN
                        INSERT (member_no, run_time, mail_status)
                        VALUES (source.member_no, GETDATE(), source.mail_status);
                """, (member_no, run_time, mail_status))

            # Final update to query status
            cursor.execute("UPDATE dbo.email_query_status SET saved_records = ? WHERE query_id = ?", (saved_records, query_id))

            conn.commit()
            result_queue.put(('complete', valid_count, invalid_count))

        except Exception as ex:
            logging.exception("Error during validation process")
            messagebox.showerror("Error", f"An error occurred:\n{ex}")
        finally:
            start_button.config(state=tk.NORMAL)

    # 🔁 GUI update loop & background thread starts HERE (inside the function)
    window.after(100, update_gui)
    threading.Thread(target=run_validation, daemon=True).start()

def update_gui():
    try:
        while not result_queue.empty():
            task = result_queue.get_nowait()
            if task[0] == 'update':
                for item in result_table.get_children():
                    result_table.item(item, tags="")

                new_item = result_table.insert("", "end", values=(task[1], task[2], task[3]), tags=("highlight",))
                result_table.tag_configure("highlight", background="lightblue")
                result_table.see(new_item)

            elif task[0] == 'complete':
                messagebox.showinfo("Validation Complete", f"✔ Valid: {task[1]}\n❌ Invalid: {task[2]}\n")
                start_button.config(state=tk.NORMAL)

            elif task[0] == 'counts':
                valid_count_var.set(f"Valid: {task[1]}")
                invalid_count_var.set(f"Invalid: {task[2]}")
    except queue.Empty:
        pass

    window.after(100, update_gui)
   # threading.Thread(target=run_validation, daemon=True).start()
# --- Filter Toggle Functions ---
def toggle_member_filter():
    state = "normal" if member_no_checkbox_var.get() else "disabled"
    start_member_entry.config(state=state)
    end_member_entry.config(state=state)

def toggle_date_filter():
    state = "normal" if date_checkbox_var.get() else "disabled"
    start_date_entry.config(state=state)
    end_date_entry.config(state=state)
    calendar_button.config(state=state)


#--UI------------
window = tk.Tk()
pages = {}  # To store frame references

page_container = tk.Frame(window, bg="#E8E9EB")
page_container.pack(fill="both", expand=True)

page_container.grid_rowconfigure(0, weight=1)
page_container.grid_columnconfigure(0, weight=1)

window.title("Email Validation Tool")

# --- Center the window ---
window_width = 800
window_height = 600
entry_width = 20

# --- Enable Ctrl+C/V in Entry widgets ---
def enable_copy_paste(widget):
    widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-C>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))
    widget.bind("<Control-V>", lambda e: widget.event_generate("<<Paste>>"))


# --- Enable Ctrl+C in Treeview to copy selected row ---
def copy_treeview_row(event):
    selected = result_table.focus()
    if selected:
        values = result_table.item(selected, 'values')
        row_text = '\t'.join(str(v) for v in values)
        window.clipboard_clear()
        window.clipboard_append(row_text)


# Get screen dimensions
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate position x, y
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

# Set the position of the window
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

window.configure(bg="#E8E9EB")  # light bluish-gray background

report_window = None  # Global tracker
main_page = tk.Frame(page_container, bg="#E8E9EB")
main_page.grid(row=0, column=0, sticky="nsew")
pages["main"] = main_page

report_page = tk.Frame(page_container, bg="#E8E9EB")
report_page.grid(row=0, column=0, sticky="nsew")
pages["report"] = report_page

# Show main page first
def show_page(name):
    pages[name].tkraise()
    window.update_idletasks()
 

def open_report_page():
    for widget in report_page.winfo_children():
        widget.destroy()

    # Variables
    report_member_filter_var = tk.BooleanVar(value=False)
    report_date_filter_var = tk.BooleanVar(value=False)
    report_member_from_var = tk.StringVar()
    report_member_to_var = tk.StringVar()
    report_date_from_var = tk.StringVar()
    report_date_to_var = tk.StringVar()
    valid_count_var = tk.StringVar(value="Valid: 0")
    invalid_count_var = tk.StringVar(value="Invalid: 0")
    selected_status = tk.StringVar(value="Email Status")
    search_var = tk.StringVar()

    # Title
    tk.Label(report_page, text="Email Status Report", font=("Segoe UI", 14), bg="#E8E9EB").pack(pady=10)

    # Filter Frame
    filter_frame = tk.Frame(report_page, bg="#E8E9EB")
    filter_frame.pack()

    # Status Dropdown
    ttk.Combobox(
    filter_frame,
    textvariable=selected_status,
    values=["all", "valid", "invalid"],
    state="readonly",
    width=10
    ).grid(row=0, column=1, padx=5, sticky="w")

    #elected_status.set("all")

    ttk.Label(filter_frame, text="Status:", background="#E8E9EB", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, sticky="e")
    #ttk.Combobox(filter_frame, textvariable=selected_status, values=["valid", "invalid"], state="readonly", width=10).grid(row=0, column=1, padx=5, sticky="w")

    # Member Filter
    tk.Checkbutton(filter_frame, text="Member No. Range", variable=report_member_filter_var, bg="#E8E9EB", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e")
    tk.Entry(filter_frame, textvariable=report_member_from_var, width=10, justify="center").grid(row=1, column=1)
    tk.Label(filter_frame, text="to", bg="#E8E9EB").grid(row=1, column=2)
    tk.Entry(filter_frame, textvariable=report_member_to_var, width=10, justify="center").grid(row=1, column=3)

    # Date Filter
    tk.Checkbutton(filter_frame, text="Run Date Range", variable=report_date_filter_var, bg="#E8E9EB", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="e")
    tk.Entry(filter_frame, textvariable=report_date_from_var, width=12, justify="center").grid(row=2, column=1)
    tk.Label(filter_frame, text="to", bg="#E8E9EB").grid(row=2, column=2)
    tk.Entry(filter_frame, textvariable=report_date_to_var, width=12, justify="center").grid(row=2, column=3)

    # Search Frame
    search_frame = tk.Frame(report_page, bg="#E8E9EB")
    search_frame.pack(pady=8)
    tk.Label(search_frame, text="🔍 Search Email:", bg="#E8E9EB", font=("Segoe UI", 10)).pack(side="left")
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)
    tk.Button(search_frame, text="Search", command=lambda: fetch_report_data(search_var.get())).pack(side="left")

    # Treeview
    tree_frame = tk.Frame(report_page, bg="#E8E9EB")
    tree_frame.pack(expand=True, fill="both", padx=20, pady=(0, 5))

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    report_tree = ttk.Treeview(tree_frame, columns=("member_no", "email", "mail_status", "run_time"),
                               show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    report_tree.pack(expand=True, fill="both")
    tree_scroll_y.config(command=report_tree.yview)
    tree_scroll_x.config(command=report_tree.xview)

    for col in ("member_no", "email", "mail_status", "run_time"):
        report_tree.heading(col, text=col.title())
        report_tree.column(col, anchor="center", width=140)

    # Count Display
    count_frame = tk.Frame(report_page, bg="#E8E9EB")
    count_frame.pack()
    tk.Label(count_frame, textvariable=valid_count_var, fg="green", bg="#E8E9EB", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
    tk.Label(count_frame, textvariable=invalid_count_var, fg="red", bg="#E8E9EB", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

    # Run Filter Button
    run_filter_btn = tk.Button(
        filter_frame,
        text="🔎 Run Filter",
        font=("Segoe UI", 10, "bold"),
        bg="#565b5e", fg="white", padx=10,
        state="disabled",
        command=lambda: fetch_report_data(search_var.get())
    )
    run_filter_btn.grid(row=3, column=0, columnspan=4, pady=10)

    def update_filter_button_state(*args):
        run_filter_btn.config(state="normal" if report_member_filter_var.get() or report_date_filter_var.get() else "disabled")

    report_member_filter_var.trace_add("write", update_filter_button_state)
    report_date_filter_var.trace_add("write", update_filter_button_state)

    def fetch_report_data(search_email=""):
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            query = """
            SELECT evr.member_no, um.email, evr.mail_status, evr.run_time
            FROM dbo.email_validation_results evr
            LEFT JOIN dbo.user_mast um ON evr.member_no = um.member_no
            WHERE 1 = 1
            """
            params = []

            # Apply status filter if not "all"
            if selected_status.get() == "valid":
                query += " AND evr.mail_status = ?"
                params.append(1)
            elif selected_status.get() == "invalid":
                query += " AND evr.mail_status = ?"
                params.append(0)

            if report_member_filter_var.get():
                query += " AND evr.member_no BETWEEN ? AND ?"
                params += [report_member_from_var.get(), report_member_to_var.get()]

            if report_date_filter_var.get():
                query += " AND CAST(evr.run_time AS DATE) BETWEEN ? AND ?"
                params += [report_date_from_var.get(), report_date_to_var.get()]

            if search_email.strip():
                query += " AND um.email LIKE ?"
                params.append(f"%{search_email.strip()}%")

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Clear existing data
            for row in report_tree.get_children():
                report_tree.delete(row)

            valid_count = invalid_count = 0

            if not rows:
                report_tree.insert("", "end", values=("", "No result found", "", ""), tags=("no_result",))
                report_tree.tag_configure("no_result", foreground="gray", font=("Segoe UI", 12, "italic"))
            else:
                for member_no, email, mail_status, run_time in rows:
                    report_tree.insert("", "end", values=(member_no, email, mail_status, run_time.strftime("%Y-%m-%d %H:%M:%S") if run_time else ""))
                    if mail_status == 1:
                        valid_count += 1
                    else:
                        invalid_count += 1

            valid_count_var.set(f"Valid: {valid_count}")
            invalid_count_var.set(f"Invalid: {invalid_count}")

        except Exception as ex:
            logging.exception("Error fetching report data")
            messagebox.showerror("Database Error", str(ex))

    # Bindings
    # Status Dropdown
    dropdown = ttk.Combobox(filter_frame, textvariable=selected_status, values=["All","valid", "invalid"], state="readonly", width=10)
    dropdown.grid(row=0, column=1, padx=5, sticky="w")
    dropdown.bind("<<ComboboxSelected>>", lambda e: fetch_report_data(search_var.get()))

    # Load initial data
    fetch_report_data()

    # Back Button
    tk.Button(report_page, text="Back", font=("Segoe UI", 10, "bold"), fg="white", bg="#565b5e",
              relief="groove", width=15, command=lambda: show_page("main")).pack()

    show_page("report")

# Font
bold_font = tkfont.Font(family="Segoe UI", size=10,weight="bold")
frame = tk.Frame(main_page)
frame = tk.Frame(main_page,  borderwidth=2, relief="flat", bg="#E8E9EB")
count_frame = tk.Frame(main_page, bg="#E8E9EB")
table_frame = tk.Frame(main_page)

frame.pack(padx=(0,0) ,pady=(0,0), fill="both", expand=True)

# --- Row 0: Member No. From / To ---
tk.Label(frame, text="Member No. From:", font=bold_font, fg="black", bg="#E8E9EB",
         anchor="e", width=18).grid(row=0, column=0, padx=(0,0), pady=(12,0), sticky="e")
start_member_entry = tk.Entry(frame, width=entry_width,relief="groove",border=1,font=("Segoe UI", 10),justify="center")
start_member_entry.grid(row=0, column=1, padx=(0,0), pady=(12,0),ipady=1)

tk.Label(frame, text="To", font=bold_font, fg="black", bg="#E8E9EB",
         anchor="e", width=2).grid(row=0, column=1, padx=(0, 0), pady=(12,0), sticky="e")  # Adjust width and padding here
end_member_entry = tk.Entry(frame, width=entry_width,font=("Segoe UI", 10),justify="center")
end_member_entry.grid(row=0, column=2, padx=(0,0), pady=(12,0),ipady=1)

# --- Load Calendar Icon ---
calendar_icon = None
icon_path = "C:/Users/PC/Downloads/calendar-color-icon.png"
if os.path.exists(icon_path):
    original_icon = Image.open(icon_path)
    try:
        from PIL import Resampling
        RESAMPLE_FILTER = Resampling.LANCZOS
    except ImportError:
        RESAMPLE_FILTER = Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.BICUBIC
    resized_icon = original_icon.resize((21, 21), RESAMPLE_FILTER)
    calendar_icon = ImageTk.PhotoImage(resized_icon)

# From Register Date
tk.Label(frame, text="Register Date From:", font=bold_font, fg="black", bg="#E8E9EB", anchor="e", width=18)\
    .grid(row=1, column=0, padx=(24,0), pady=(12, 15), sticky="e")
start_date_var = tk.StringVar()
start_date_entry = tk.Entry(frame, textvariable=start_date_var, width=entry_width,font=("Segoe UI", 10),justify="center")
start_date_entry.grid(row=1, column=1, padx=(0, 0), pady=(0, 0),ipady=1)

# To Register Date
tk.Label(frame, text="To", font=bold_font, fg="black", bg="#E8E9EB", anchor="e", width=2)\
    .grid(row=1, column=1, padx=(0, 0), pady=(0, 0), sticky="e")  # Adjust width and padding here
end_date_var = tk.StringVar()
end_date_entry = tk.Entry(frame, textvariable=end_date_var, width=entry_width, font=("Segoe UI", 10),justify="center")
end_date_entry.grid(row=1, column=2, padx=(0, 0), pady=(0, 0),ipady=1)

# Button inside the frame using grid layout
start_button = tk.Button(frame, text="Start Validation", 
                         font=("Segoe UI", 10, "bold"),
                         fg="white", bg="#565b5e",  # Dark gray for industrial look
                         activebackground="#4A4A4A",  # Slightly darker when active
                         activeforeground="white",
                         relief="ridge", 
                         command=start_validation)

# Grid for button inside the frame
start_button.grid(row=3, column=1,columnspan=2, pady=(5, 15),padx=(80,0), sticky="w")

window.bind('<Return>', lambda event: start_validation())
# Shared Calendar Button
if calendar_icon:
    calendar_button = tk.Button(frame, image=calendar_icon, bg="#E8E9EB", relief="raised", cursor="hand2",
        command=lambda: open_calendar(start_date_entry, end_date_entry, start_date_var, end_date_var, calendar_button))
    calendar_button.grid(row=1, column=4, padx=(5, 10), pady=(0, 10), sticky="w")



# --- Checkboxes to Enable/Disable Filters ---
member_no_checkbox_var = tk.BooleanVar(value=False)
date_checkbox_var = tk.BooleanVar(value=False)

member_checkbox = tk.Checkbutton(frame, variable=member_no_checkbox_var,  # Active text color
                                  bg="#E8E9EB", command=toggle_member_filter)
member_checkbox.grid(row=0, column=0, pady=(16, 5), sticky="w", padx=(20,0))

date_checkbox = tk.Checkbutton(frame, variable=date_checkbox_var,bg="#E8E9EB",command=toggle_date_filter)
date_checkbox.grid(row=1, column=0, pady=(0, 5), sticky="w", padx=(20,0))

# Initialize states
toggle_member_filter()
toggle_date_filter()

# --- Validation Counts ---
count_frame.pack(pady=5)

valid_count_var = tk.StringVar(value="Valid: 0")
invalid_count_var = tk.StringVar(value="Invalid: 0")

tk.Label(count_frame, textvariable=valid_count_var, fg="green", font=("Segoe UI", 11, "bold"), bg="#E8E9EB").pack(side="left", padx=40)
tk.Label(count_frame, textvariable=invalid_count_var, fg="red", font=("Segoe UI", 11, "bold"), bg="#E8E9EB").pack(side="left", padx=40)


# Frame to hold the table and scrollbars
table_frame.pack(padx=20, pady=(10,20), fill="both", expand=True)

# --- Custom Style for Treeview ---
style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#ACADA8",
                foreground="black",
                rowheight=25,
                fieldbackground="#ACADA8",
                bordercolor="#ACADA8",
                borderwidth=0,
                font=("Segoe UI", 10))

style.map('Treeview', background=[('selected', '#3484F0')])

style.configure("Treeview.Heading",
                background="#565b5e",
                foreground="white",
                relief="flat",
                font=("Segoe UI", 10, "bold"))

style.map("Treeview.Heading", background=[('active', '#3484F0')])
#filter button
report_button = tk.Button(table_frame, text="Report ", command=open_report_page)
report_button.pack(padx=(700,0),pady=(0,0))

# --- Treeview widget --
columns = ("member_no", "email", "mail_status")
result_table = ttk.Treeview(table_frame, columns=columns, show="headings")

# Define columns
for col in columns:
    result_table.heading(col, text=col.replace("_", " ").title())
    result_table.column(col, width=200 if col == "email" else 120, anchor="center")


# --- Custom Scrollbar Style ---
style.configure("Vertical.TScrollbar",
                gripcount=0,
                background="#565b5e",
                darkcolor="#2a2d2e",
                lightcolor="#2a2d2e",
                troughcolor="#3a3b3c",
                bordercolor="#3a3b3c",
                arrowcolor="white")

style.configure("Horizontal.TScrollbar",
                gripcount=0,
                background="#565b5e",
                darkcolor="#2a2d2e",
                lightcolor="#2a2d2e",
                troughcolor="#3a3b3c",
                bordercolor="#3a3b3c",
                arrowcolor="white")

style.map("TScrollbar",
          background=[("active", "#3484F0")])

# --- Scrollbars with Styled Themes ---
vsb = ttk.Scrollbar(table_frame, orient="vertical", command=result_table.yview, style="Vertical.TScrollbar")
result_table.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=result_table.xview, style="Horizontal.TScrollbar")
result_table.configure(xscrollcommand=hsb.set)
hsb.pack(side="bottom", fill="x")

# Apply copy/paste bindings to Entry widgets
for entry in [start_member_entry, end_member_entry, start_date_entry, end_date_entry]:
    enable_copy_paste(entry)

# Apply copy binding to Treeview
result_table.bind("<Control-c>", copy_treeview_row)
result_table.bind("<Control-C>", copy_treeview_row)


# Pack Treeview
result_table.pack(fill="both", expand=True)

#topLevel
show_page("main")
window.mainloop()
