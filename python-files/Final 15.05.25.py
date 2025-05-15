import tkinter as tk
import customtkinter
import sv_ttk as sv
import darkdetect
import pywinstyles, sys
from flask import Flask, jsonify, Response
import threading
import json
from mysql.connector import connect, Error
from tkinter import ttk, messagebox

# --- Variabel for passord ---
mysql_password = ""
conn = None
cursor = None

# --- Flask API---
api_app = Flask(__name__)

@api_app.route('/')
def index():
    return "<h3>API er oppe. Prøv <a href='/api/varelager'>/api/varelager</a></h3>"

@api_app.route('/api/varelager', methods=['GET'])
def get_varelager():
    try:
        connection = connect(
            user='root',
            password=mysql_password,
            host='localhost',
            database='varehusdb'
        )
        cur = connection.cursor()
        cur.execute("SELECT VNr, Betegnelse, Pris FROM vare")
        rows = cur.fetchall()
        connection.close()

        varer = []
        for row in rows:
            varer.append({
                "VNr": row[0],
                "Betegnelse": row[1],
                "Pris": float(row[2])
            })

        pretty_json = json.dumps(varer, indent=4, ensure_ascii=False)
        return Response(pretty_json, mimetype='application/json')
    except Error as e:
        return jsonify({"error": str(e)})

def start_api():
    api_app.run(port=5001)
# --- Flask API---

# --- GUI Funksjoner ---
def fetch_kunder():
    # Fjern gamle oppføringer i GUI
    for row in kunde_tree.get_children():
        kunde_tree.delete(row)

    # Opprett stored procedure hvis den ikke allerede eksisterer
    cursor.execute("DROP PROCEDURE IF EXISTS VisAlleKunder")
    procedure_sql = """
    CREATE PROCEDURE VisAlleKunder()
    BEGIN
        SELECT Knr, Fornavn, Etternavn, Adresse, PostNr FROM kunde;
    END
    """
    try:
        cursor.execute(procedure_sql)
        conn.commit()
        print("Stored procedure 'VisAlleKunder' opprettet.")
    except Exception as e:
        print(f"Feil ved opprettelse av stored procedure: {e}")
        return

    # Kall stored procedure for å hente kunder
    try:
        cursor.callproc('VisAlleKunder')
        for result in cursor.stored_results():
            for row in result.fetchall():
                kunde_tree.insert("", tk.END, values=row)
        print("Kundedata hentet med stored procedure.")
    except Exception as e:
        print(f"Feil ved henting av kunder: {e}")

def add_kunde():
    try:
        cursor.execute("SELECT MAX(Knr) FROM kunde")
        max_id = cursor.fetchone()[0]
        next_id = (max_id or 0) + 1

        values = (
            next_id,
            entry_vars["Fornavn"].get(),
            entry_vars["Etternavn"].get(),
            entry_vars["Adresse"].get(),
            entry_vars["PostNr"].get()
        )
        query = """
            INSERT INTO kunde (Knr, Fornavn, Etternavn, Adresse, PostNr)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, values)
        conn.commit()
        label_status.config(text="✅ Kunde lagt til!")
        for field in entry_vars.values():
            field.delete(0, tk.END)
        fetch_kunder()
    except Exception as e:
        label_status.config(text=f"⚠️ Feil: {e}")

def delete_selected_kunde():
    selected = kunde_tree.selection()
    if not selected:
        messagebox.showwarning("Ingen valgt", "Vennligst velg en kunde å slette.")
        return

    item = kunde_tree.item(selected[0])
    kunde_id = item['values'][0]

    confirm = messagebox.askyesno("Bekreft sletting", f"Vil du slette kunde {kunde_id}?")
    if confirm:
        try:
            cursor.execute("DELETE FROM kunde WHERE Knr = %s", (kunde_id,))
            conn.commit()
            fetch_kunder()
            label_status.config(text="🗑️ Kunde slettet.")
        except Exception as e:
            label_status.config(text=f"⚠️ Feil: {e}")

def open_vare_window():
    vare_win = tk.Toplevel(root)
    vare_win.title("Vareoversikt")

    cursor.execute("SHOW COLUMNS FROM vare")
    all_columns = [col[0] for col in cursor.fetchall()]
    visible_columns = [col for col in all_columns if col.lower() != "katnr"]

    vare_tree = ttk.Treeview(vare_win, columns=visible_columns, show="headings")
    for col in visible_columns:
        vare_tree.heading(col, text=col)
        vare_tree.column(col, width=100)
    vare_tree.pack(padx=10, pady=10, fill="both", expand=True)

    cursor.execute(f"SELECT {', '.join(visible_columns)} FROM vare")
    for row in cursor.fetchall():
        vare_tree.insert("", tk.END, values=row)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(vare_win)

def open_ordre_window():
    ordre_win = tk.Toplevel(root)
    ordre_win.title("Ordreoversikt")

    cursor.execute("SHOW COLUMNS FROM ordre")
    ordre_columns = [col[0] for col in cursor.fetchall()]

    ordre_tree = ttk.Treeview(ordre_win, columns=ordre_columns, show="headings")
    for col in ordre_columns:
        ordre_tree.heading(col, text=col)
        ordre_tree.column(col, width=100)
    ordre_tree.pack(padx=10, pady=10, fill="both", expand=True)

    cursor.execute("SELECT * FROM ordre")
    for row in cursor.fetchall():
        ordre_tree.insert("", tk.END, values=row)

    def show_ordrelinjer_for_selected(event):
        selected = ordre_tree.selection()
        if not selected:
            return
        item = ordre_tree.item(selected[0])
        ordrenr = item['values'][0]

        try:
            knr_index = ordre_columns.index("KNr")
            knr = item['values'][knr_index]
        except ValueError:
            messagebox.showerror("Feil", "Kolonnen 'KundeNr' ble ikke funnet i ordre-tabellen.")
            return

        cursor.execute("""
            SELECT 
                ordrelinje.OrdreNr, 
                ordrelinje.VNr, 
                vare.Betegnelse,
                ordrelinje.Antall, 
                ordrelinje.PrisPrEnhet,
                (ordrelinje.Antall * ordrelinje.PrisPrEnhet) AS LinjeTotal
            FROM ordrelinje 
            JOIN vare ON ordrelinje.VNr = vare.VNr 
            WHERE ordrelinje.OrdreNr = %s
        """, (ordrenr,))
        rows = cursor.fetchall()

        cursor.execute("SELECT Fornavn, Etternavn, Adresse, PostNr FROM kunde WHERE Knr = %s", (knr,))
        kundeinfo = cursor.fetchone()

        if not rows:
            messagebox.showinfo("Ingen ordrelinjer", f"Ingen ordrelinjer for Ordre {ordrenr}.")
            return

        column_names = ["OrdreNr", "VNr", "Betegnelse", "Antall", "Pris", "LinjeTotal"]
        linje_win = tk.Toplevel(ordre_win)
        linje_win.title(f"Ordrelinjer for Ordre {ordrenr}")
        sv.set_theme(darkdetect.theme())
        apply_theme_to_titlebar(linje_win)

        if kundeinfo:
            kunde_label = tk.Label(
                linje_win,
                text=f"Kunde: {kundeinfo[0]} {kundeinfo[1]}, {kundeinfo[2]}, {kundeinfo[3]}",
                font=("Arial", 11, "italic")
            )
            kunde_label.pack(pady=(10, 5))

        tree = ttk.Treeview(linje_win, columns=column_names, show="headings")
        for col in column_names:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(padx=10, pady=10, fill='both', expand=True)

        total = 0
        total_items = 0
        for row in rows:
            tree.insert("", tk.END, values=row)
            total += float(row[5])
            total_items += row[3]

        summary = f"Antall produkter: {len(rows)}\nAntall varer: {total_items}\nOrdreverdi: {total:.2f} kr"
        total_label = tk.Label(linje_win, text=summary, font=("Arial", 12, "bold"), justify="left")
        total_label.pack(pady=10)

    ordre_tree.bind("<<TreeviewSelect>>", show_ordrelinjer_for_selected)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(ordre_win)

def start_main_gui():
    global root, entry_vars, kunde_tree, label_status

    root = tk.Tk()
    root.title("Kunderegister (uten Telefonnr)")
    root.geometry("1000x1000")

    frame_form = tk.Frame(root)
    frame_form.pack(pady=10)

    entry_vars = {}
    fields = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
    for i, field in enumerate(fields):
        tk.Label(frame_form, text=field + ": ").grid(row=i, column=0, sticky="e")
        entry = tk.Entry(frame_form)
        entry.grid(row=i, column=1)
        entry_vars[field] = entry

    customtkinter.CTkButton(frame_form, text="➕ Legg til kunde", command=add_kunde).grid(row=len(fields), column=0, columnspan=2, pady=5)

    label_status = tk.Label(root, text="")
    label_status.pack()

    KUNDE_COLUMNS = ["Knr", "Fornavn", "Etternavn", "Adresse", "PostNr"]
    kunde_tree = ttk.Treeview(root, columns=KUNDE_COLUMNS, show="headings")
    for col in KUNDE_COLUMNS:
        kunde_tree.heading(col, text=col)
        kunde_tree.column(col, width=100)
    kunde_tree.pack(padx=10, pady=10, fill='both', expand=True)

    customtkinter.CTkButton(root, text="Slett valgt kunde", command=delete_selected_kunde).pack(pady=5)
    customtkinter.CTkButton(root, text="Vis Vareoversikt", command=open_vare_window).pack(pady=5)
    customtkinter.CTkButton(root, text="Vis Ordreoversikt", command=open_ordre_window).pack(pady=5)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(root)

    fetch_kunder()
    root.mainloop()

def apply_theme_to_titlebar(window):
    version = sys.getwindowsversion()
    if version.major == 10 and version.build >= 22000:
        pywinstyles.change_header_color(window, "#1c1c1c" if sv.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(window, "dark" if sv.get_theme() == "dark" else "normal")
        window.wm_attributes("-alpha", 0.99)
        window.wm_attributes("-alpha", 1)

# --- GUI Funksjoner ---

# --- Innloggingsvindu ---
def Login():
    global mysql_password, conn, cursor
    if Passord.get():
        mysql_password = Passord.get()
        try:
            conn = connect(
                user='root',
                password=mysql_password,
                host='localhost',
                database='varehusdb'
            )
            cursor = conn.cursor()
            api_thread = threading.Thread(target=start_api, daemon=True)
            api_thread.start()
            login_window.destroy()
            start_main_gui()
        except Error as e:
            messagebox.showerror("Feil", f"Kunne ikke koble til databasen:\n{e} Feil Passord?")

login_window = tk.Tk()
login_window.title("VarehusDB Innlogging")
login_window.geometry("300x200")

label = tk.Label(login_window, text="MySQL root Passord:", font=("Arial", 12, "bold")) 
label.pack()

Passord = customtkinter.CTkEntry(login_window, show="*")
Passord.pack(pady=10)

myButton = customtkinter.CTkButton(login_window, text="Logg inn", command=Login)
myButton.pack()

sv.set_theme(darkdetect.theme())
apply_theme_to_titlebar(login_window)

login_window.mainloop()
# --- Innloggingsvindu ---