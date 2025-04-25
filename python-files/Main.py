import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import os
import json
import re
import requests
import textwrap
import time
from PyPDF2 import PdfReader

# === STIER ===
base_dir = os.path.dirname(__file__)
os.chdir(base_dir)
tekst_mappe = os.path.join(base_dir, "konverteret_tekster")
pdf_mappe = os.path.join(base_dir, "pdf")
indeks_fil = os.path.join(base_dir, "indeks.json")
svar_fil = os.path.join(base_dir, "svar.txt")
spørgsmål_fil = os.path.join(base_dir, "spørgsmål.txt")
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

OCR_AKTIV = False

# === HENT INDEKS ===
def hent_indeks():
    with open(indeks_fil, "r", encoding="utf-8") as f:
        return json.load(f)

# === AI-KALD ===
def spørg_ai(spørgsmål, kontekst):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "mathstral-7b-v0.1",
        "messages": [
            {"role": "system", "content": "Du er en elektrikerfagkyndig assistent. Svar på dansk. Husk at nævne hvilken side i konteksten svaret findes."},
            {"role": "user", "content": f"Kontekst:\n{kontekst}\n\nSpørgsmål: {spørgsmål}"}
        ],
        "temperature": 0.4
    }
    try:
        res = requests.post(LM_STUDIO_URL, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            return f"[FEJL {res.status_code}] – {res.text}"
    except Exception as e:
        return f"[FEJL] Kunne ikke kontakte modellen: {e}"

# === OCR BILLEDE ===
def upload_billede():
    global OCR_AKTIV
    try:
        import pytesseract
        from PIL import Image
        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        OCR_AKTIV = True
    except ImportError:
        messagebox.showerror("Fejl", "OCR kræver pytesseract og pillow. Installer først med pip.")
        return

    filsti = filedialog.askopenfilename(filetypes=[("Billeder", "*.png;*.jpg;*.jpeg")])
    if not filsti:
        return
    try:
        billede = Image.open(filsti)
        tekst = pytesseract.image_to_string(billede, lang="dan")
        input_felt.delete("1.0", tk.END)
        input_felt.insert(tk.END, tekst.strip())
        messagebox.showinfo("OCR", "Spørgsmålene blev hentet fra billedet.")
    except Exception as e:
        messagebox.showerror("Fejl", f"Kunne ikke læse billedet: {e}")

# === FORTOLKER (PDF-SØGNING)
def kør_fortolker():
    if not os.path.exists(spørgsmål_fil):
        messagebox.showerror("Fejl", "spørgsmål.txt blev ikke fundet.")
        return
    brug_ai = brug_ai_var.get()
    with open(spørgsmål_fil, "r", encoding="utf-8") as f:
        spørgsmål = [linje.strip() for linje in f if linje.strip()]

    alle_svar = []

    for filnavn in os.listdir(pdf_mappe):
        if filnavn.lower().endswith(".pdf"):
            sti = os.path.join(pdf_mappe, filnavn)
            reader = PdfReader(sti)
            for i, side in enumerate(reader.pages):
                tekst = side.extract_text()
                if not tekst:
                    continue
                for spm in spørgsmål:
                    if spm.lower() in tekst.lower():
                        if brug_ai:
                            svar = spørg_ai(spm, tekst)
                        else:
                            svar = "(AI slået fra – vis kun tekstudsnit)"

                        svarblok = (
                            f"🔎 Spørgsmål: {spm}\n"
                            f"📄 Fil: {filnavn}, Side: {i+1}\n"
                            f"📌 Udsnit:\n{textwrap.shorten(tekst.strip(), width=800)}\n"
                            f"🧾 Svar:\n{svar.strip()}\n"
                            f"{'='*80}\n"
                        )
                        alle_svar.append(svarblok)

    if not alle_svar:
        messagebox.showinfo("Resultat", "Ingen svar fundet i PDF'er.")
        return

    with open(svar_fil, "a", encoding="utf-8") as f:
        for s in alle_svar:
            f.write(s + "\n")

    messagebox.showinfo("✅ Færdig!", f"{len(alle_svar)} svar gemt i svar.txt.")

# === FIND RELEVANTE BIDDER ===
def find_relevante(fritekst, indeks):
    ord_liste = re.findall(r"\b\w+\b", fritekst.lower())
    resultater = {}
    for ord in ord_liste:
        hits = indeks.get(ord, [])
        for fil, side in hits:
            key = (fil, side)
            resultater.setdefault(key, 0)
            resultater[key] += 1
    return sorted(resultater.items(), key=lambda x: -x[1])

# === HENT TEKST ===
def hent_tekst(filnavn, side):
    sti = os.path.join(tekst_mappe, filnavn)
    if not os.path.exists(sti):
        return ""
    with open(sti, "r", encoding="utf-8") as f:
        tekst = f.read()
    sider = re.split(r"(?:^|\n)Side:\s*(\d+)", tekst)
    for i in range(1, len(sider), 2):
        hvis_side = sider[i].strip()
        if hvis_side == side:
            return sider[i + 1].strip()
    return ""

# === FIND SVAR ===
def kør_søgning():
    spørgsmål = input_felt.get("1.0", tk.END).strip()
    if not spørgsmål:
        messagebox.showwarning("Ingen spørgsmål", "Skriv eller hent et spørgsmål først!")
        return

    indeks = hent_indeks()
    spørgsmålsliste = [s.strip() for s in spørgsmål.split("\n") if s.strip()]

    global sidste_resultat
    sidste_resultat = ""
    resultat_felt.delete("1.0", tk.END)

    brug_ai = brug_ai_var.get()

    for spm in spørgsmålsliste:
        match = find_relevante(spm, indeks)
        if not match:
            visning = f"\n🧠 Spørgsmål: {spm}\nIngen relevante sider fundet.\n{'='*80}\n"
            resultat_felt.insert(tk.END, visning)
            sidste_resultat += visning
            continue

        (filnavn, side), score = match[0]
        tekst = hent_tekst(filnavn, side)

        if brug_ai:
            svar = spørg_ai(spm, tekst)
        else:
            svar = "(AI-svar slået fra. Kun tekstudsnit vises.)"

        visning = (
            f"\n🧠 Spørgsmål: {spm}\n"
            f"{'-'*80}\n"
            f"📄 Fil: {filnavn} – Side: {side} – Score: {score}\n\n"
            f"📑 Tekstudsnit:\n{textwrap.fill(tekst[:500], width=100)}...\n\n"
            f"🧾 Svar:\n{textwrap.fill(svar, width=100)}\n"
            f"{'='*80}\n"
        )

        resultat_felt.insert(tk.END, visning)
        sidste_resultat += visning

# === GEM SVAR ===
def gem_svar():
    if not sidste_resultat:
        messagebox.showinfo("Intet svar", "Der er intet at gemme endnu.")
        return
    with open(svar_fil, "a", encoding="utf-8") as f:
        f.write(sidste_resultat)
    messagebox.showinfo("Gemt", "Svaret er gemt i svar.txt")

# === CHATVINDUE ===
def start_chat_vindue():
    chat_win = tk.Toplevel(root)
    chat_win.title("Chat med AI")
    chat_win.geometry("800x600")

    chat_output = scrolledtext.ScrolledText(chat_win, wrap=tk.WORD, state='disabled')
    chat_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    input_frame = tk.Frame(chat_win)
    input_frame.pack(pady=10, fill=tk.X)

    chat_input = tk.Entry(input_frame, width=80)
    chat_input.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

    def send_chat():
        spørgsmål = chat_input.get().strip()
        if not spørgsmål:
            return
        chat_input.delete(0, tk.END)
        chat_output.config(state='normal')
        chat_output.insert(tk.END, f"🧍‍♂️ Dig: {spørgsmål}\n")
        chat_output.config(state='disabled')
        chat_output.yview(tk.END)

        svar = spørg_ai(spørgsmål, "Du kan bruge al relevant viden fra PDF'er. Ingen ekstra kontekst.")
        chat_output.config(state='normal')
        chat_output.insert(tk.END, f"🤖 AI: {svar.strip()}\n\n")
        chat_output.config(state='disabled')
        chat_output.yview(tk.END)

    send_btn = tk.Button(input_frame, text="Send", command=send_chat)
    send_btn.pack(side=tk.RIGHT, padx=10)

    chat_input.bind("<Return>", lambda event: send_chat())

# === GUI OPSÆTNING ===
root = tk.Tk()
root.title("Bo Bach - Trylle værktøj")
root.geometry("1000x780")

tk.Label(root, text="Skriv dit spørgsmål eller upload billede med spørgsmål:").pack(anchor="w", padx=20, pady=(20, 0))
input_felt = scrolledtext.ScrolledText(root, height=8, width=110)
input_felt.pack(padx=10, pady=5)

knap_frame = tk.Frame(root)
knap_frame.pack()

tk.Button(knap_frame, text="📸 Upload billede", command=upload_billede).grid(row=0, column=0, padx=5)
tk.Button(knap_frame, text="🔍 Find svar", command=kør_søgning).grid(row=0, column=1, padx=5)
tk.Button(knap_frame, text="💾 Gem svar", command=gem_svar).grid(row=0, column=2, padx=5)
brug_ai_var = tk.BooleanVar(value=False)
tk.Checkbutton(knap_frame, text="Uddybende Svar", variable=brug_ai_var).grid(row=0, column=3, padx=5)
tk.Button(knap_frame, text="🎯 Kør Fortolker", command=kør_fortolker).grid(row=0, column=5, padx=5)

resultat_felt = scrolledtext.ScrolledText(root, height=30, width=110)
resultat_felt.pack(padx=10, pady=10)

copyright_label = tk.Label(root, text="© 2025 Bo Bach", font=("Arial", 8), fg="gray")
copyright_label.pack(side="bottom", pady=(0, 5))

sidste_resultat = ""
root.mainloop()
