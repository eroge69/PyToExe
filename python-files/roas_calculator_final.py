import pandas as pd
import os
import unicodedata

def normalize_text(text):
    if isinstance(text, str):
        nfkd_form = unicodedata.normalize('NFKD', text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()
    return text

koncert_kody = {
    'lu': 'Muzyka Ludovico Einaudi',
    'wl': 'Koncert muzyki z Wladcy Pierscieni i Gry o Tron',
    'bi': 'Najwieksze hity Billie Eilish, Taylor Swift i innych',
    'ba': 'Koncert Muzyki Bajkowej',
    'gh': 'Muzyka Studia Ghibli'
}

miasto_kody = {
    'lu': 'Lublin', 'ta': 'Tarnow', 'rz': 'Rzeszow', 'gd': 'Gdansk', 'ra': 'Radom',
    'zi': 'Zielona Gora', 'wr': 'Wroclaw', 'ko': 'Koszalin', 'lo': 'Lodz', 'bi': 'Bialystok',
    'sz': 'Szczecin', 'wa': 'Warszawa'
}

def process_files():
    sprzedaz_folder = 'sprzedaz'
    kampanie_folder = 'kampanie'
    exceptions_file = 'exceptions.txt'

    sprzedaz_frames = []
    for file in os.listdir(sprzedaz_folder):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(sprzedaz_folder, file), sep=';', on_bad_lines='skip')
            df['Kwota_biletu'] = df['Kwota_biletu'].str.replace(',', '.').astype(float)
            sprzedaz_frames.append(df)
    sprzedaz_df = pd.concat(sprzedaz_frames)

    sprzedaz_df['Nazwa_wydarzenia_norm'] = sprzedaz_df['Nazwa_wydarzenia'].apply(normalize_text)
    sprzedaz_df['Miasto_norm'] = sprzedaz_df['Miasto'].apply(normalize_text)
    sprzedaz_grupowana = sprzedaz_df.groupby(['Nazwa_wydarzenia_norm', 'Miasto_norm'])['Kwota_biletu'].sum().reset_index()
    sprzedaz_grupowana.rename(columns={'Kwota_biletu': 'Suma_sprzedazy'}, inplace=True)

    kampanie_frames = []
    for file in os.listdir(kampanie_folder):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(kampanie_folder, file), sep=';', on_bad_lines='skip')
            kampanie_frames.append(df)
    kampanie_df = pd.concat(kampanie_frames)

    kampanie_df['Kod_kampanii'] = kampanie_df['Nazwa kampanii'].str.extract(r'(\d+[a-z]{4})$')
    kampanie_df['kod_koncertu'] = kampanie_df['Kod_kampanii'].str[-4:-2]
    kampanie_df['kod_miasta'] = kampanie_df['Kod_kampanii'].str[-2:]

    kampanie_df['Nazwa_wydarzenia'] = kampanie_df['kod_koncertu'].map(koncert_kody)
    kampanie_df['Miasto'] = kampanie_df['kod_miasta'].map(miasto_kody)

    exceptions = kampanie_df[kampanie_df['Nazwa_wydarzenia'].isna() | kampanie_df['Miasto'].isna()]
    exceptions.to_csv(exceptions_file, index=False)

    kampanie_clean = kampanie_df.dropna(subset=['Nazwa_wydarzenia', 'Miasto'])

    kampanie_clean['Nazwa_wydarzenia_norm'] = kampanie_clean['Nazwa_wydarzenia'].apply(normalize_text)
    kampanie_clean['Miasto_norm'] = kampanie_clean['Miasto'].apply(normalize_text)

    kampanie_clean_grouped = kampanie_clean.groupby(['Nazwa_wydarzenia_norm', 'Miasto_norm']).agg({
        'Wydana kwota (PLN)': 'sum'
    }).reset_index()

    result = pd.merge(kampanie_clean_grouped, sprzedaz_grupowana, on=['Nazwa_wydarzenia_norm', 'Miasto_norm'], how='left')
    result['ROAS'] = result['Suma_sprzedazy'] / result['Wydana kwota (PLN)']

    result.to_csv('roas_report.csv', index=False)
    print("Plik roas_report.csv został wygenerowany. Błędne wpisy zapisano w exceptions.txt")

if __name__ == '__main__':
    process_files()
