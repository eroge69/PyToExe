
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from scipy.integrate import trapz
import matplotlib.pyplot as plt
from datetime import datetime
import os

def load_data(file_path):
    # Identifikuojam failo tipą pagal extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.txt', '.csv']:
        try:
            # Bandoma pirmiausia kaip CSV su delimiteriu
            try:
                df = pd.read_csv(file_path)
            except:
                df = pd.read_csv(file_path, delim_whitespace=True, header=None)
            if df.shape[1] < 3:
                # Jeigu stulpelių mažiau, pabandykime skaityti be header
                df = pd.read_csv(file_path, delim_whitespace=True, header=None)
            # Užtikriname, kad mes turime bent 3 stulpelius
            df = df.iloc[:, :3]
            df.columns = ['id', 'dist', 'h']
        except Exception as e:
            raise Exception('Klaida skaitant TXT/CSV failą: ' + str(e))
    elif ext in ['.xlsx']:
        try:
            df = pd.read_excel(file_path, header=None)
            df = df.iloc[:, :3]
            df.columns = ['id', 'dist', 'h']
        except Exception as e:
            raise Exception('Klaida skaitant XLSX failą: ' + str(e))
    else:
        raise Exception('Nepalaikomas failo formatas.')
    
    # Konvertuojame reikšmes į skaičius
    df['dist'] = pd.to_numeric(df['dist'].astype(str).str.replace(',', '.'), errors='coerce')
    df['h'] = pd.to_numeric(df['h'].astype(str).str.replace(',', '.'), errors='coerce')
    df = df.dropna()
    return df

def run_analysis(file_path):
    try:
        df = load_data(file_path)
        
        # Sąrašai rezultatų saugojimui
        results = []
        graphs_no_offset = []
        graphs_with_offset = []
        
        unique_ids = df['id'].unique()
        
        # Iteruojame per visus unikalias profilių ID
        for profile_id in unique_ids:
            profile_data = df[df['id'] == profile_id].sort_values('dist')
            x = profile_data['dist'].values
            h = profile_data['h'].values
            
            # Apskaičiuojame pagrindinius parametrus
            min_h = np.min(h)
            x_min = np.min(x)
            x_max = np.max(x)
            h_at_xmin = profile_data[profile_data['dist'] == x_min]['h'].values[0]
            h_at_xmax = profile_data[profile_data['dist'] == x_max]['h'].values[0]
            avg_h = (h_at_xmin + h_at_xmax) / 2
            mean_h = np.mean(h)
            offset = h_at_xmin
            mean_h_minus_offset = mean_h - offset
            
            # Tiesinis trendas naudojant kraštinius taškus
            slope = (h_at_xmax - h_at_xmin) / (x_max - x_min)
            intercept = h_at_xmin - slope * x_min
            trend = slope * x + intercept
            trend_bottom = trend + (min_h - avg_h)
            avg_h_bottom = min_h
            
            # Antra variacija: realūs aukščiai atėmus offset
            h_minus_offset = h - offset
            min_h_new = np.min(h_minus_offset)
            avg_h_new = (h_minus_offset[0] + h_minus_offset[-1]) / 2
            slope_new = (h_minus_offset[-1] - h_minus_offset[0]) / (x_max - x_min)
            intercept_new = h_minus_offset[0] - slope_new * x_min
            trend_new = slope_new * x + intercept_new
            trend_bottom_new = trend_new + (min_h_new - avg_h_new)
            avg_h_bottom_new = min_h_new
            
            # Plotų skaičiavimai
            area_min = trapz(h - min_h, x)
            area_avg = trapz(abs(h - avg_h), x)
            area_linest = trapz(abs(h - trend), x)
            
            results.append({
                'id': profile_id,
                'length': x_max - x_min,
                'h_at_xmin': h_at_xmin,
                'h_at_xmax': h_at_xmax,
                'avg_height': avg_h,
                'mean_height': mean_h,
                'mean_h_minus_offset': mean_h_minus_offset,
                'min_height': min_h,
                'area_min': area_min,
                'area_avg': area_avg,
                'area_linest': area_linest
            })
            
            # Grafikas 1: originalūs aukščiai
            plt.figure(figsize=(10,5))
            plt.plot(x, h, 'b-', label='Profilis')
            plt.axhline(y=min_h, color='r', linestyle='--', label='Minimumas')
            plt.axhline(y=avg_h_bottom, color='g', linestyle='--', label='Vidurkis (x_min, x_max)')
            plt.plot(x, trend_bottom, 'y--', label='Tiesinis trendas')
            plt.plot([x_min, x_max], [min_h, min_h], 'ko', label='Kraštiniai taškai')
            plt.xlabel('Atstumas')
            plt.ylabel('Aukštis')
            plt.title('Profilis ID: ' + str(profile_id) + ' (be offset atėmimo)')
            plt.grid(True)
            plt.legend()
            graph_filename_no = 'grafikas_id_' + str(profile_id) + '_be_offset.png'
            plt.savefig(graph_filename_no)
            graphs_no_offset.append(graph_filename_no)
            plt.close()
            
            # Grafikas 2: aukščiai atėmus offset
            plt.figure(figsize=(10,5))
            plt.plot(x, h_minus_offset, 'b-', label='Profilis (minus offset)')
            plt.axhline(y=min_h_new, color='r', linestyle='--', label='Minimumas')
            plt.axhline(y=avg_h_bottom_new, color='g', linestyle='--', label='Vidurkis (x_min, x_max)')
            plt.plot(x, trend_bottom_new, 'y--', label='Tiesinis trendas')
            plt.plot([x_min, x_max], [min_h_new, min_h_new], 'ko', label='Kraštiniai taškai')
            plt.xlabel('Atstumas')
            plt.ylabel('Aukštis (minus offset)')
            plt.title('Profilis ID: ' + str(profile_id) + ' (su offset atėmimu)')
            plt.grid(True)
            plt.legend()
            graph_filename_offset = 'grafikas_id_' + str(profile_id) + '_su_offset.png'
            plt.savefig(graph_filename_offset)
            graphs_with_offset.append(graph_filename_offset)
            plt.close()
        
        # Sukuriame rezultatus kaip DataFrame
        results_df = pd.DataFrame(results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        csv_filename = 'rezultatai_' + timestamp + '.csv'
        results_df.to_csv(csv_filename, index=False)
        
        xlsx_filename = 'rezultatai_' + timestamp + '.xlsx'
        results_df.to_excel(xlsx_filename, index=False)
        
        txt_filename = 'rezultatai_' + timestamp + '.txt'
        with open(txt_filename, 'w') as f:
            f.write(results_df.to_string())
        
        msg = 'Analizė baigta sėkmingai. Rezultatai:\
'
        msg += 'CSV: ' + csv_filename + '\
'
        msg += 'Excel: ' + xlsx_filename + '\
'
        msg += 'TXT: ' + txt_filename + '\
\
'
        msg += 'Grafikai (be offset): ' + ', '.join(graphs_no_offset) + '\
'
        msg += 'Grafikai (su offset): ' + ', '.join(graphs_with_offset)
        messagebox.showinfo('Rezultatai', msg)
    except Exception as e:
        messagebox.showerror('Klaida', 'Įvyko klaida: ' + str(e))

def choose_file():
    file_path = filedialog.askopenfilename(
        title='Pasirinkite failą',
        filetypes=[
            ('TXT Files', '*.txt'),
            ('CSV Files', '*.csv'),
            ('Excel Files', '*.xlsx'),
            ('Visi failai', '*.*')
        ]
    )
    if file_path:
        run_analysis(file_path)

# Sukuriame pagrindinį langą
root = tk.Tk()
root.title('Profilio analizės programa')
root.geometry('400x200')

# Pridėti mygtuką įkelti failą
btn_load = tk.Button(root, text='Įkelti failą ir paleisti analizę', command=choose_file, width=40, height=2)
btn_load.pack(expand=True)

# Informacijos žymėjimas
lbl_info = tk.Label(root, text='Paspauskite mygtuką ir pasirinkite analizės failą (TXT, CSV arba XLSX).')
lbl_info.pack(pady=20)

root.mainloop()
