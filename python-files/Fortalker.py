import os
from PyPDF2 import PdfReader

# === Automatisk find spørgsmål.txt uanset store/små bogstaver ===
def find_spørgsmål_fil():
    for fil in os.listdir():
        if fil.lower() == "spørgsmål.txt":
            return os.path.join(base_dir, fil)
    raise FileNotFoundError("spørgsmål.txt ikke fundet!")

# === Opsætning af mapper og stier ===
base_dir = os.path.dirname(__file__)
os.chdir(base_dir)  # Sikrer at vi arbejder i samme mappe som scriptet

SPØRGSMÅL_FIL = find_spørgsmål_fil()
PDF_MAPPE = os.path.join(base_dir, "pdf")
SVAR_FIL = os.path.join(base_dir, "svar.txt")

# === Læs spørgsmål fra tekstfil ===
def læs_spørgsmål():
    with open(SPØRGSMÅL_FIL, "r", encoding="utf-8") as f:
        return [linje.strip() for linje in f if linje.strip()]

# === Søg direkte i PDF-fil ===
def søg_i_pdf(pdf_fil, spørgsmål):
    svar = []
    reader = PdfReader(pdf_fil)
    for i, side in enumerate(reader.pages):
        tekst = side.extract_text()
        if not tekst:
            continue
        for spm in spørgsmål:
            if spm.lower() in tekst.lower():
                svar.append(
                    f"🔎 Spørgsmål: {spm}\n"
                    f"📄 Fil: {os.path.basename(pdf_fil)}, Side: {i+1}\n"
                    f"📌 Udsnit:\n{tekst.strip()[:800]}...\n"
                )
    return svar

# === Hovedprogram ===
def hovedprogram():
    spørgsmål = læs_spørgsmål()
    alle_svar = []

    for filnavn in os.listdir(PDF_MAPPE):
        if filnavn.lower().endswith(".pdf"):
            sti = os.path.join(PDF_MAPPE, filnavn)
            print(f"Søger i: {filnavn}")
            svar = søg_i_pdf(sti, spørgsmål)
            if svar:
                alle_svar.extend(svar)

    with open(SVAR_FIL, "w", encoding="utf-8") as f:
        for s in alle_svar:
            f.write(s + "\n\n")

    print("✅ Færdig! Svar gemt i svar.txt")

# === Kør programmet ===
if __name__ == "__main__":
    hovedprogram()
