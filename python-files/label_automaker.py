import os
import base64
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from pylibdmtx.pylibdmtx import encode

def img_to_base64(path):
    with open(path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

def format_mat_num(mat_num_raw):
    if len(mat_num_raw) == 8 and mat_num_raw.isdigit():
        return f"{mat_num_raw[0]}.{mat_num_raw[1:4]}-{mat_num_raw[4:7]}.{mat_num_raw[7]}"
    else:
        return mat_num_raw

def genera_etichette():
    try:
        product_code_raw = entry_product_code.get().strip()
        supplier = entry_supplier.get().strip()
        version = entry_version.get().strip()
        date = entry_date.get().strip()
        start_serial = int(entry_start_serial.get().strip())
        end_serial = int(entry_end_serial.get().strip())

        if not product_code_raw or not supplier or not version:
            messagebox.showerror("Errore", "Compila tutti i campi obbligatori.")
            return
        if start_serial > end_serial:
            messagebox.showerror("Errore", "Seriale iniziale deve essere <= seriale finale.")
            return

        product_code_formatted = format_mat_num(product_code_raw)

        home_dir = os.path.expanduser("~")
        qr_folder = os.path.join(home_dir, ".qr_hidden_files")
        os.makedirs(qr_folder, exist_ok=True)
        desktop = os.path.join(home_dir, "Desktop")
        html_file = os.path.join(desktop, "etichette_locali.html")

        html_head = '''<!DOCTYPE html>
<html lang="it">
<head><meta charset="utf-8" />
<title>Etichette con DataMatrix</title>
<style>
@page { size: A4; margin: 5mm; }
body {
  margin:0; padding:0;
  display:flex; flex-wrap:wrap; gap:0.5mm;
  background:#f0f0f0; font-family:Helvetica,sans-serif;
}
.label {
  width:25mm; height:12mm;
  background:white; border:0.4pt solid #aaa; border-radius:3mm;
  box-sizing:border-box; padding:1mm; display:flex; align-items:center;
}
.qr {
  width:10mm; height:10mm;
  margin-right:1mm; margin-left:1mm;
  flex-shrink:0; display:flex; align-items:center; justify-content:center;
}
.info {
  flex:1; display:flex; flex-direction:column; justify-content:center;
  line-height:1.2; padding:1mm 0;    /* 1mm sopra e sotto, uguale a margin-bottom delle righe */
  overflow:hidden;
}
.line {
  white-space:nowrap; overflow:hidden;
  margin-bottom:1mm;               /* spazio tra le righe */
}
.line:last-child { margin-bottom:0; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<script>
window.onload = function() {
  document.querySelectorAll('.label').forEach(function(label){
    var info = label.querySelector('.info'),
        lines = info.querySelectorAll('.line'),
        fs = 4.5;
    info.style.fontSize = fs + 'pt';
    var overflow = Array.from(lines).some(l => l.scrollWidth > l.clientWidth);
    if(overflow) {
      while(overflow && fs > 2.0) {
        fs -= 0.1;
        info.style.fontSize = fs + 'pt';
        overflow = Array.from(lines).some(l => l.scrollWidth > l.clientWidth);
      }
      label.querySelector('.qr').style.marginRight = '0.5mm';
    }
  });

  html2pdf().set({
    margin:       5,
    filename:     'etichette_locali.pdf',
    image:        { type:'png', quality:0.98 },
    html2canvas:  { scale:2 },
    jsPDF:        { unit:'mm', format:'a4', orientation:'portrait' }
  }).from(document.body).save();
};
</script>
</head><body>
'''

        html_tail = '</body></html>'

        html_labels = []
        for serial in range(start_serial, end_serial + 1):
            sn = str(serial)
            data_matrix_str = f"{product_code_raw} V{supplier}2P{version} {sn}"

            # genera DataMatrix
            encoded = encode(data_matrix_str.encode("utf-8"))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
            # ridimensiona a 10mm ≈ 100x100px
            img = img.resize((100, 100), Image.Resampling.NEAREST)

            img_path = os.path.join(qr_folder, f"dmx_{serial}.png")
            img.save(img_path)

            b64 = img_to_base64(img_path)

            html_labels.append(f'''
  <div class="label">
    <div class="qr">
      <img src="{b64}" style="width:100%;height:100%;">
    </div>
    <div class="info">
      <div class="line">Mat. Num: {product_code_formatted}</div>
      <div class="line">Supplier: {supplier}</div>
      <div class="line">HV Version: {version}</div>
      <div class="line">SN: {sn}</div>
    </div>
  </div>
''')

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_head + ''.join(html_labels) + html_tail)

        messagebox.showinfo("Fatto!",
          f"✅ HTML creato sul Desktop:\n{html_file}\n\n"
          f"Immagini DataMatrix salvate in:\n{qr_folder}")
    except Exception as e:
        messagebox.showerror("Errore", f"{e}")

root = tk.Tk()
root.title("Generatore Etichette DataMatrix")
root.geometry("400x430")
root.resizable(False, False)

labels = ["Codice prodotto (Mat. Num.):",
          "Fornitore (Supplier):",
          "HV Version:",
          "Data (solo uso interno):",
          "Seriale iniziale:",
          "Seriale finale:"]

entries = []
for i, text in enumerate(labels):
    tk.Label(root, text=text).pack(anchor="w", padx=10, pady=(10 if i==0 else 5,0))
    e = tk.Entry(root, width=50 if i<4 else 20)
    e.pack(padx=10)
    entries.append(e)

(entry_product_code,
 entry_supplier,
 entry_version,
 entry_date,
 entry_start_serial,
 entry_end_serial) = entries

tk.Button(root, text="Genera etichette", command=genera_etichette,
          bg="#4CAF50", fg="white", font=("Helvetica",12,"bold")
).pack(pady=20, ipadx=10, ipady=5)

root.mainloop()
