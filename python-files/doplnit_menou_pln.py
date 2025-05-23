
import xml.etree.ElementTree as ET
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def main():
    root = tk.Tk()
    root.withdraw()  # Skryje hlavní okno

    input_path = filedialog.askopenfilename(title="Vyber XML soubor", filetypes=[("XML files", "*.xml")])
    if not input_path:
        return

    try:
        tree = ET.parse(input_path)
        xml_root = tree.getroot()

        for faktura in xml_root.findall(".//FaktVyd"):
            if faktura.find("Mena") is None:
                mena = ET.SubElement(faktura, "Mena")
                kod = ET.SubElement(mena, "Kod")
                kod.text = "PLN"

        output_path = Path(input_path).with_name(Path(input_path).stem + "-s-menou-PLN.xml")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        messagebox.showinfo("Hotovo", f"Upravený soubor byl uložen jako:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Chyba", f"Nastala chyba při zpracování souboru:\n{e}")

if __name__ == "__main__":
    main()
