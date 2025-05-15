#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_text_to_pdfs_gui.py
=======================

Graficzne narzędzie do seryjnego dodawania napisów do wielu plików PDF.

**NOWOŚCI – czerwiec 2025**
---------------------------
* **Paleta kolorów** – wybierasz barwę w standardowym oknie `colorchooser` zamiast wpisywać #RRGGBB.
* **Lista zainstalowanych czcionek** – wyskakuje okno z listą wszystkich rodzin fontów dostępnych w systemie (Tk 8.6 → Windows/macOS/Linux). Klikasz nazwę, zatwierdzasz **OK**.
* Nadal: sortowanie PDF‑ów alfabetycznie i mapowanie na kolejne wiersze CSV.

Budowanie EXE (bez konsoli):
```
pyinstaller --onefile --noconsole add_text_to_pdfs_gui.py
```

Wymagania PyPI: `pypdf reportlab pillow tk` (+ `pyinstaller` dla EXE).
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from typing import List
from tkinter import (
    Button,
    END,
    Listbox,
    Scrollbar,
    SINGLE,
    Tk,
    Toplevel,
    colorchooser,
    filedialog,
    font as tkfont,
    messagebox,
    simpledialog,
)

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, toColor
from reportlab.pdfgen import canvas as rl_canvas
from pypdf import PdfReader, PdfWriter, PageObject

DEFAULT_SIZE = 12
DEFAULT_COLOR = "#000000"
DEFAULT_FONT = "Helvetica"
SUPPORTED_PDF = (("Pliki PDF", "*.pdf"),)
SUPPORTED_CSV = (("Pliki CSV", "*.csv"),)

# ---------------------------------------------------------------------------
# GUI helpers
# ---------------------------------------------------------------------------

def choose_pdfs(root: Tk) -> List[Path]:
    paths = filedialog.askopenfilenames(
        title="Wybierz pliki PDF (kolejność nie ma znaczenia)",
        filetypes=SUPPORTED_PDF,
        parent=root,
    )
    return sorted((Path(p) for p in paths), key=lambda p: p.name.lower())


def choose_csv(root: Tk) -> Path | None:
    path = filedialog.askopenfilename(
        title="Wybierz plik CSV z napisami (pierwsza kolumna)",
        filetypes=SUPPORTED_CSV,
        parent=root,
    )
    return Path(path) if path else None


def choose_output_dir(root: Tk) -> Path | None:
    directory = filedialog.askdirectory(
        title="Katalog wyjściowy (Anuluj = obok oryginału)", parent=root
    )
    return Path(directory) if directory else None


def ask_coordinates(root: Tk) -> tuple[float, float]:
    x = simpledialog.askfloat(
        "Pozycja X",
        "Podaj współrzędną X (punkty; 72 pt = 1 cal):",
        parent=root,
        minvalue=0.0,
        initialvalue=20.0,
    )
    y = simpledialog.askfloat(
        "Pozycja Y",
        "Podaj współrzędną Y (punkty, od lewego‑dolnego rogu):",
        parent=root,
        minvalue=0.0,
        initialvalue=20.0,
    )
    if x is None or y is None:
        raise SystemExit
    return x, y


def ask_font_size(root: Tk) -> int:
    size = simpledialog.askinteger(
        "Rozmiar czcionki",
        f"Podaj rozmiar czcionki w punktach (domyślnie {DEFAULT_SIZE}):",
        parent=root,
        initialvalue=DEFAULT_SIZE,
        minvalue=4,
        maxvalue=200,
    )
    return size or DEFAULT_SIZE


def choose_color(root: Tk) -> str:
    rgb_tuple, hex_color = colorchooser.askcolor(color=DEFAULT_COLOR, parent=root)
    if hex_color is None:  # Anulowano
        return DEFAULT_COLOR
    return hex_color


def choose_font(root: Tk) -> str:
    families = sorted(set(tkfont.families(root)), key=str.casefold)

    dialog = Toplevel(root)
    dialog.title("Wybierz czcionkę")
    dialog.grab_set()

    lb = Listbox(dialog, selectmode=SINGLE, width=30, height=20)
    for fam in families:
        lb.insert(END, fam)
    lb.pack(side="left", fill="both", expand=True)

    sb = Scrollbar(dialog, command=lb.yview)
    sb.pack(side="right", fill="y")
    lb.configure(yscrollcommand=sb.set)

    selected: dict[str, str | None] = {"font": None}

    def confirm() -> None:
        idx = lb.curselection()
        if idx:
            selected["font"] = families[idx[0]]
        dialog.destroy()

    Button(dialog, text="OK", command=confirm).pack(fill="x")
    root.wait_window(dialog)
    return selected["font"] or DEFAULT_FONT

# ---------------------------------------------------------------------------
# Processing helpers
# ---------------------------------------------------------------------------

def read_csv_texts(path: Path) -> List[str]:
    with path.open(newline="", encoding="utf-8-sig") as csvfile:
        return [row[0] for row in csv.reader(csvfile) if row]


def ensure_font_registered(font_name: str) -> str:
    """Rejestruje font TTF, jeśli podano ścieżkę do pliku zamiast nazwy."""
    fp = Path(font_name)
    if fp.is_file():
        name = fp.stem
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fp)))
        return name
    return font_name  # zakładamy, że to nazwa systemowa


def create_overlay_pdf(
    width: float,
    height: float,
    text: str,
    x: float,
    y: float,
    size: int,
    color: str,
    font_name: str,
) -> bytes:
    packet = io.BytesIO()
    c = rl_canvas.Canvas(packet, pagesize=(width, height))
    try:
        c.setFillColor(toColor(color))
    except ValueError:
        c.setFillColor(HexColor(color))
    try:
        c.setFont(font_name, size)
    except Exception:  # nieznana czcionka
        c.setFont(DEFAULT_FONT, size)
    c.drawString(x, y, text)
    c.save()
    return packet.getvalue()


def process_pdf(
    pdf_path: Path,
    text: str,
    coords: tuple[float, float],
    font_size: int,
    color: str,
    font_name: str,
    output_dir: Path | None,
) -> bool:
    try:
        reader = PdfReader(str(pdf_path))
        first_page: PageObject = reader.pages[0]
        width, height = map(float, (first_page.mediabox.width, first_page.mediabox.height))

        overlay = create_overlay_pdf(width, height, text, coords[0], coords[1], font_size, color, font_name)
        first_page.merge_page(PdfReader(io.BytesIO(overlay)).pages[0])

        writer = PdfWriter()
        writer.add_page(first_page)
        for page in reader.pages[1:]:
            writer.add_page(page)

        out_dir = output_dir or pdf_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{pdf_path.stem}_label{pdf_path.suffix}"
        with out_path.open("wb") as f:
            writer.write(f)
        return True
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    root = Tk()
    root.withdraw()

    pdf_files = choose_pdfs(root)
    if not pdf_files:
        root.destroy(); sys.exit()

    csv_path = choose_csv(root)
    if not csv_path:
        messagebox.showerror("Błąd", "Nie wybrano pliku CSV.", parent=root)
        root.destroy(); sys.exit()

    texts = read_csv_texts(csv_path)
    if len(texts) < len(pdf_files):
        messagebox.showerror("Błąd", f"CSV ma {len(texts)} wierszy, a wybrano {len(pdf_files)} PDF‑ów.", parent=root)
        root.destroy(); sys.exit()

    output_dir = choose_output_dir(root)
    coords = ask_coordinates(root)
    font_size = ask_font_size(root)
    color = choose_color(root)
    font_sel = choose_font(root)
    font_name = ensure_font_registered(font_sel)

    success = 0
    for pdf_path, text in zip(pdf_files, texts):
        if process_pdf(pdf_path, text, coords, font_size, color, font_name, output_dir):
            success += 1

    messagebox.showinfo(
        "Zakończono",
        f"Przetworzono {success} z {len(pdf_files)} plików.\nCSV: {csv_path.name}\nCzcionka: {font_name}\nKolor: {color}",
        parent=root,
    )
    root.destroy()


if __name__ == "__main__":
    main()
