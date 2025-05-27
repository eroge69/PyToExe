import pandas as pd

# Muat data
df_xlsm = pd.read_excel('DiscreteTSS.xlsm', sheet_name=0)
df_POINT = pd.read_csv('SIEMENS.csv', header=None, sep='\t')
df_analog = pd.read_excel('Analog.xlsm', sheet_name=0)

# Bersihkan dan dapatkan nilai unik dari DiscreteTSS.xlsm
scadamom_discrete_col_name = 'SCADAMOM composite id[SCADAMOMCompositeId] *'
if scadamom_discrete_col_name in df_xlsm.columns:
    scadamom_discrete_cleaned = df_xlsm[scadamom_discrete_col_name].astype(str).str.replace(r'^(.*)\..*$', r'\1', regex=True)
    unique_scadamom_discrete = scadamom_discrete_cleaned.drop_duplicates().reset_index(drop=True)
else:
    print(f"Peringatan: Kolom '{scadamom_discrete_col_name}' tidak ditemukan di DiscreteTSS.xlsm.")
    unique_scadamom_discrete = pd.Series(dtype='object')

# Dapatkan nilai unik dari kolom BAY di SIEMENS.csv
if 1 < df_POINT.shape[1]:
    unique_bay = df_POINT.iloc[:, 1].drop_duplicates().reset_index(drop=True)
else:
    print("Peringatan: File SIEMENS.csv tidak memiliki kolom kedua untuk 'BAY'.")
    unique_bay = pd.Series(dtype='object')

# Identifikasi dan bersihkan kolom SCADAMOM dari Analog.xlsm
scadamom_col_analog_name_exact = 'SCADAMOM composite id[SCADAMOMCompositeId] *'
scadamom_col_analog_name = None

if scadamom_col_analog_name_exact in df_analog.columns:
    scadamom_col_analog_name = scadamom_col_analog_name_exact
else:
    for col in df_analog.columns:
        if 'SCADAMOM' in str(col).upper():
            scadamom_col_analog_name = col
            break

if scadamom_col_analog_name:
    scadamom_analog_cleaned = df_analog[scadamom_col_analog_name].astype(str).str.replace(r'^(.*)\..*$', r'\1', regex=True)
    unique_scadamom_analog = scadamom_analog_cleaned.drop_duplicates().reset_index(drop=True)
else:
    print("Peringatan: Kolom SCADAMOM tidak dapat ditemukan secara otomatis di Analog.xlsm.")
    unique_scadamom_analog = pd.Series(dtype='object')

# Buat DataFrame hasil
result_df = pd.DataFrame({
    'Unique BAY': unique_bay,
    'Unique SCADAMOM (Discrete)': unique_scadamom_discrete,
    'Unique SCADAMOM (Analog)': unique_scadamom_analog
})

# Cetak hasil
print(result_df)