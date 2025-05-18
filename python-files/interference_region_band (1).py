import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import os
from openpyxl.drawing.image import Image
from datetime import datetime, timedelta

# ------------------------------------------------------------------------------------
# Setup timestamp and paths
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
input_dir = r"D:\Interference Per Band Per Region\input"
output_file = f"D:\Interference Per Band Per Region\Processed_Data_{timestamp}.xlsx"
chart_dir = f"D:\Interference Per Band Per Region\Charts_{timestamp}"
os.makedirs(chart_dir, exist_ok=True)

# ------------------------------------------------------------------------------------
# Determine cutoff (3 months ago) and list valid CSV files
cutoff_date = datetime.now() - timedelta(days=90)
csv_files = []
for f in os.listdir(input_dir):
    if f.endswith(".csv"):
        try:
            # Extract timestamp from filename (assumes format ..._<timestamp>.csv)
            file_ts = datetime.strptime(f.split("_")[-1].split(".")[0], "%Y%m%d%H%M%S")
            if file_ts >= cutoff_date:
                csv_files.append(os.path.join(input_dir, f))
        except Exception as e:
            print(f"Skipping {f}: {e}")

if not csv_files:
    print("No CSV files found in the last 3 months.")
    exit()

# ------------------------------------------------------------------------------------
# Process and consolidate all data (for IT OSS sheet)
all_data_list = []
required_columns = ['DATE_ID', 'REGION', 'BAND', 'RANGE_ID', 'CNT']

for file_path in csv_files:
    df = pd.read_csv(file_path)
    # Clean column names and convert DATE_ID
    df.columns = df.columns.str.strip()
    df['DATE_ID'] = pd.to_datetime(df['DATE_ID'], format='%d-%b-%y', errors='coerce')
    
    # Validate required columns
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns {missing} in {file_path}.")
    
    all_data_list.append(df)

# Consolidate and remove duplicate records
it_oss_data = pd.concat(all_data_list, ignore_index=True)
it_oss_data.drop_duplicates(inplace=True)

# ------------------------------------------------------------------------------------
# Filter for bands F3 and F4 and classify RTWP
rawdata = it_oss_data[it_oss_data['BAND'].isin(['F3', 'F4'])].copy()

def classify_rtwp(range_id):
    rtwp_mapping = {
        'Range 1': -80,
        'Range 2': -84,
        'Range 3': -89,
        'Range 4': -94,
        'Range 5': -96
    }
    return rtwp_mapping.get(range_id, None)

rawdata['RTWP'] = rawdata['RANGE_ID'].apply(classify_rtwp)

# ------------------------------------------------------------------------------------
# Group data by DATE_ID & REGION (using the original logic)
summary_data = rawdata.groupby(['DATE_ID', 'REGION']).agg(
    CNT_Range_1 = ('CNT', lambda x: x[rawdata['RANGE_ID'] == 'Range 1'].sum()),
    CNT_Range_2 = ('CNT', lambda x: x[rawdata['RANGE_ID'] == 'Range 2'].sum()),
    CNT_Range_3 = ('CNT', lambda x: x[rawdata['RANGE_ID'] == 'Range 3'].sum()),
    CNT_Range_4 = ('CNT', lambda x: x[rawdata['RANGE_ID'] == 'Range 4'].sum()),
    CNT_Range_5 = ('CNT', lambda x: x[rawdata['RANGE_ID'] == 'Range 5'].sum())
).reset_index()

# Compute additional columns
summary_data["Total Count of U900 Cells"] = summary_data.iloc[:, 2:7].sum(axis=1)
summary_data["Count of U900 Cells with RTWP > -85"] = summary_data[['CNT_Range_1', 'CNT_Range_2']].sum(axis=1)
summary_data["Count of U900 Cells with RTWP > -90"] = summary_data[['CNT_Range_1', 'CNT_Range_2', 'CNT_Range_3']].sum(axis=1)
summary_data["Count of U900 Cells with RTWP > -95"] = summary_data[['CNT_Range_1', 'CNT_Range_2', 'CNT_Range_3', 'CNT_Range_4']].sum(axis=1)

# ------------------------------------------------------------------------------------
# Compute overall daily data for charting
daily_data = summary_data.groupby('DATE_ID').sum().reset_index()
daily_data["Percentage of U900 Cells with RTWP > -85"] = (daily_data["Count of U900 Cells with RTWP > -85"] / daily_data["Total Count of U900 Cells"]) * 100
daily_data["Percentage of U900 Cells with RTWP > -90"] = (daily_data["Count of U900 Cells with RTWP > -90"] / daily_data["Total Count of U900 Cells"]) * 100
daily_data["Percentage of U900 Cells with RTWP > -95"] = (daily_data["Count of U900 Cells with RTWP > -95"] / daily_data["Total Count of U900 Cells"]) * 100

# ------------------------------------------------------------------------------------
# Prepare pivot table data (for regional breakdown)
pivot_data = summary_data.copy()
pivot_data["Percentage of U900 Cells with RTWP > -85"] = (pivot_data["Count of U900 Cells with RTWP > -85"] / pivot_data["Total Count of U900 Cells"]) * 100
pivot_data["Percentage of U900 Cells with RTWP > -90"] = (pivot_data["Count of U900 Cells with RTWP > -90"] / pivot_data["Total Count of U900 Cells"]) * 100
pivot_data["Percentage of U900 Cells with RTWP > -95"] = (pivot_data["Count of U900 Cells with RTWP > -95"] / pivot_data["Total Count of U900 Cells"]) * 100
pivot_data.sort_values(by="DATE_ID", ascending=True, inplace=True)

# ------------------------------------------------------------------------------------
# Save all sheets to one Excel file (including Overall sheet)
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    it_oss_data.to_excel(writer, sheet_name="IT OSS", index=False)
    summary_data.to_excel(writer, sheet_name="Pivot Data", index=False)
    pivot_data.to_excel(writer, sheet_name="Pivot Table", index=False)
    pivot_data.to_excel(writer, sheet_name="Overall", index=False)

# ------------------------------------------------------------------------------------
# Open workbook for chart embedding
wb = openpyxl.load_workbook(output_file)
ws = wb["Pivot Table"]

# Ensure numeric conversion for plotting (as in original code)
summary_data.iloc[:, 2:] = summary_data.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')

# ------------------------------------------------------------------------------------
# Generate main overall RTWP percentage analysis chart using daily data
plt.figure(figsize=(14, 7))
plt.plot(daily_data['DATE_ID'], daily_data["Percentage of U900 Cells with RTWP > -85"],
         marker='o', linestyle='-', color='green', label="RTWP > -85%")
plt.plot(daily_data['DATE_ID'], daily_data["Percentage of U900 Cells with RTWP > -90"],
         marker='s', linestyle='--', color='blue', label="RTWP > -90%")
plt.plot(daily_data['DATE_ID'], daily_data["Percentage of U900 Cells with RTWP > -95"],
         marker='d', linestyle='-', color='red', label="RTWP > -95%")
plt.xticks(daily_data['DATE_ID'],rotation=45)
plt.xlabel("Date")
plt.ylabel("Percentage (%)")
plt.title("RTWP Percentage Analysis - Overall")
plt.legend()
plt.grid()

main_chart_file = os.path.join(chart_dir, f"Pivot_Chart_Overall_{timestamp}.png")
plt.savefig(main_chart_file)
plt.close()

# Insert main chart into "Pivot Table" sheet
img = Image(main_chart_file)
ws.add_image(img, "B2")

# ------------------------------------------------------------------------------------
# Generate individual charts per region and embed into the same sheet
for index, region in enumerate(pivot_data['REGION'].unique()):
    region_data = pivot_data[pivot_data['REGION'] == region].copy()
    region_data.sort_values(by="DATE_ID", ascending=True, inplace=True)
    
    plt.figure(figsize=(14, 7))
    plt.plot(region_data['DATE_ID'], region_data["Percentage of U900 Cells with RTWP > -85"],
             marker='o', linestyle='-', color='green', label="RTWP > -85%")
    plt.plot(region_data['DATE_ID'], region_data["Percentage of U900 Cells with RTWP > -90"],
             marker='s', linestyle='--', color='blue', label="RTWP > -90%")
    plt.plot(region_data['DATE_ID'], region_data["Percentage of U900 Cells with RTWP > -95"],
             marker='d', linestyle='-', color='red', label="RTWP > -95%")
    plt.xticks(daily_data['DATE_ID'],rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Percentage")
    plt.title(f"RTWP Percentage Analysis - {region}")
    plt.legend()
    plt.grid()
    
    chart_file = os.path.join(chart_dir, f"Pivot_Chart_{region}_{timestamp}.png")
    plt.savefig(chart_file)
    plt.close()
    
    region_img = Image(chart_file)
    # Position each regional chart further below the previous one
    ws.add_image(region_img, f"B{index * 20 + 25}")

# Save updated workbook with all embedded charts
wb.save(output_file)

print(f"Processed data saved to {output_file}.")
print(f"All charts saved in '{chart_dir}' and embedded in the 'Pivot Table' sheet.")