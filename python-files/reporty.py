import os
import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar  # Modul na výber dátumu cez kalendár

# Vytvorenie hlavného okna Tkinter
root = tk.Tk()
root.title("Čítanie Reportov")  # Nastavenie názvu okna
root.withdraw()  # Skryje hlavné okno, pokiaľ sa GUI nespustí

# Nastavenie predvoleného dátumu na aktuálny deň
selected_date = tk.StringVar(root, value=datetime.datetime.now().strftime("%Y%m%d"))
selected_status = tk.StringVar(root, value="NG")  # Predvolený stav (NG alebo OK)

# Premenné na zobrazenie počtu kusov
ng_count = tk.StringVar(root, value="NG kusy: 0")
ok_count = tk.StringVar(root, value="OK kusy: 0")

def get_inspection_path():
    """Vygeneruje cestu na základe vybraného dátumu a typu (NG/OK)."""
    return rf"\\fspov05\reports\F162\{selected_date.get()}\{selected_status.get()}"

def select_date():
    """Otvorí kalendár na výber dátumu a nastaví ho do premennej."""
    def apply_date():
        selected_date.set(cal.get_date().replace("/", ""))  # Nastavenie dátumu vo formáte YYYYMMDD
        update_file_counts()  # Aktualizácia počtu kusov po zmene dátumu
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Vyber dátum")
    cal = Calendar(top, selectmode="day", date_pattern="yyyy/mm/dd")
    cal.pack(pady=10)
    tk.Button(top, text="OK", command=apply_date).pack()

def count_files():
    """Spočíta počet súborov v zložkách NG a OK."""
    ng_path = rf"\\fspov05\reports\F162\{selected_date.get()}\NG"
    ok_path = rf"\\fspov05\reports\F162\{selected_date.get()}\OK"

    ng_files = len(os.listdir(ng_path)) if os.path.exists(ng_path) else 0
    ok_files = len(os.listdir(ok_path)) if os.path.exists(ok_path) else 0

    return ng_files, ok_files

def update_file_counts():
    """Aktualizuje zobrazenie počtu kusov."""
    ng_files, ok_files = count_files()
    ng_count.set(f"NG kusy: {ng_files}")
    ok_count.set(f"OK kusy: {ok_files}")

def parse_inspection_file(file_path):
    """Spracuje jeden súbor a extrahuje požadované dáta."""
    sn, tester, position, jig, model, start_date, start_time = None, None, None, None, None, None, None
    errors = set()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("BarCode="):
                sn = line.split("=")[1]
            elif line.startswith("MachinIpAddress="):
                tester = line.split("=")[1]
            elif line.startswith("MachinNo="):
                position = line.split("=")[1]
            elif line.startswith("FixtureId="):
                jig = line.split("=")[1]
            elif line.startswith("InspectionFile="):
                model = line.split("=")[1].replace(".zip", "")
            elif line.startswith("StartTime="):
                full_time = line.split("=")[1]
                start_date = f"{full_time[:4]}/{full_time[4:6]}/{full_time[6:8]}"
                start_time = f"{full_time[8:10]}:{full_time[10:12]}:{full_time[12:14]}"
            elif f"=NG" in line:
                parts = line.split("|")
                if len(parts) >= 6:
                    errors.add(parts[5])

    errors = list(errors)[:3]  # Maximálne 3 unikátne chyby
    return [start_date, start_time, sn, tester, position, jig, model] + errors

def watch_directory():
    """Monitoruje priečinok na nové súbory a spracováva ich."""
    seen_files = set()
    results = []
    path = get_inspection_path()

    if not os.path.exists(path):
        return results

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if filename.endswith(".txt") and file_path not in seen_files:
            seen_files.add(file_path)
            results.append(parse_inspection_file(file_path))

    results.sort(key=lambda x: (x[0], x[1]) if x[0] and x[1] else ("", ""), reverse=True)
    return results

def adjust_column_widths():
    """Automaticky nastaví šírku stĺpcov podľa najdlhšieho obsahu."""
    root.update_idletasks()
    for col in tree["columns"]:
        max_width = max(
            [len(str(tree.set(item, col))) for item in tree.get_children()] + [len(col)]
        ) * 10
        tree.column(col, width=max_width, stretch=True)

def update_table():
    """Obnoví tabuľku podľa nového dátumu alebo stavu."""
    for row in tree.get_children():
        tree.delete(row)

    results = watch_directory()
    for row in results:
        tree.insert("", tk.END, values=row)

    adjust_column_widths()
    update_file_counts()  # Aktualizuje počet kusov po obnovení tabuľky

def create_gui():
    """Vytvorí grafické rozhranie na zobrazovanie tabuľky."""
    global tree, results

    root.deiconify()

    frame_top = tk.Frame(root)
    frame_top.pack(pady=10)

    # Zobrazenie počtu kusov NG a OK
    label_ng = tk.Label(frame_top, textvariable=ng_count, fg="red", font=("Arial", 12))
    label_ng.pack(side=tk.LEFT, padx=10)

    label_ok = tk.Label(frame_top, textvariable=ok_count, fg="green", font=("Arial", 12))
    label_ok.pack(side=tk.LEFT, padx=10)

    tk.Label(frame_top, text="Dátum:").pack(side=tk.LEFT)
    tk.Button(frame_top, text="Vyber dátum", command=select_date).pack(side=tk.LEFT, padx=5)

    tk.Label(frame_top, text="Stav:").pack(side=tk.LEFT)
    dropdown_status = ttk.Combobox(frame_top, textvariable=selected_status, values=["NG", "OK"], width=5)
    dropdown_status.pack(side=tk.LEFT, padx=5)

    tk.Button(frame_top, text="Obnoviť", command=update_table).pack(side=tk.LEFT)

    frame_table = tk.Frame(root)
    frame_table.pack(fill=tk.BOTH, expand=True)

    scrollbar_y = tk.Scrollbar(frame_table, orient=tk.VERTICAL)
    scrollbar_x = tk.Scrollbar(frame_table, orient=tk.HORIZONTAL)

    columns = ["Dátum testu", "Čas testu", "SN", "Tester", "Pozícia", "JIG", "Model", "Chyba 1", "Chyba 2", "Chyba 3"]
    tree = ttk.Treeview(frame_table, columns=columns, show="headings", yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, stretch=False)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    tree.pack(fill=tk.BOTH, expand=True)

    results = watch_directory()
    for row in results:
        tree.insert("", tk.END, values=row)

    update_file_counts()  # Zobrazí počet kusov pri spustení aplikácie

    root.mainloop()

# Spusti grafické rozhranie
create_gui()
