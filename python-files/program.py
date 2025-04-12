import pandas as pd
import json
from datetime import datetime

# Nazwa pliku Excel
xlsx_path = "OG F-102 (Daily Report) 12.04.2025 .xlsx"

# Wczytaj plik
df = pd.read_excel(xlsx_path, sheet_name="Daily Report", header=None)

# Data raportu
telegram_datetime = pd.to_datetime(df.iloc[0, 8])  # I1

# Pozycja
latitude_raw = df.iloc[2, 1]   # B3
longitude_raw = df.iloc[2, 4]  # E3

lat_parts = latitude_raw.split()
lat_deg = int(lat_parts[0])
lat_min = float(lat_parts[1][:-1])
lat_dir = lat_parts[1][-1]

lon_parts = longitude_raw.split()
lon_deg = int(lon_parts[0])
lon_min = float(lon_parts[1][:-1])
lon_dir = lon_parts[1][-1]

# Remarks (A39:C45 → indeksy 38:44)
remarks_rows = df.loc[38:44, [0, 1, 2]]
remarks_text = ""
for _, row in remarks_rows.iterrows():
    start, end, activity = row
    if pd.notna(activity):
        remarks_text += f"{start}\t{activity}\t\t\t\t\t\t\t\n"

# Telegram JSON
telegram = {
    "telegramType": "N",
    "vesselCode": "003",
    "telegramDateTime": telegram_datetime.strftime("%Y/%m/%d %H:%M"),
    "indicatedSpeed": "T",
    "timeZone": 2,
    "voyageNumber": "79",
    "gmt": (telegram_datetime - pd.Timedelta(hours=2)).strftime("%Y/%m/%d %H:%M"),
    "latitudeDegrees": lat_deg,
    "latitudeMinutes": lat_min,
    "latitudeDirection": lat_dir,
    "longitudeDegrees": lon_deg,
    "longitudeMinutes": lon_min,
    "longitudeDirection": lon_dir,
    "distanceRunFromLastReport": 0.0,
    "distanceRunVoyageTotal": 0.0,
    "steamingTimeFromLastReportHours": 0,
    "steamingTimeFromLastReportMinutes": 0,
    "steamingTimeVoyageTotalHours": 0,
    "steamingTimeVoyageTotalMinutes": 0,
    "speedFromLastReport": 0.0,
    "speedVoyageTotal": 0.0,
    "windDirection": 0,
    "windForceSpeed": 0,
    "seaDirection": 0,
    "seaForceSpeed": 0,
    "swellDirection": "",
    "swellForceSpeed": "",
    "currentDirection": "",
    "currentForceSpeed": "",
    "seaWaterTemp": "",
    "current": "Y",
    "previousRobMgo": 0.0,
    "volumeMgo": 0.0,
    "densityMgo": 0.0,
    "totalMgo": 0.0,
    "robMgo": 0.0,
    "etaDate": "",
    "etbDate": "",
    "etdDate": "",
    "destination": "Vigo",
    "lastPort": "Brest",
    "milesToGo": "",
    "remarks": remarks_text.strip(),
    "hasBeenOnlySaved": True
}

# Zapis do pliku tekstowego
with open("telegram_output.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(telegram, ensure_ascii=False, indent=4))

print("✅ Plik telegram_output.txt został zapisany.")
