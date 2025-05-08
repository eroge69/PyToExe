from datetime import datetime, timedelta
import pandas as pd
import json
import csv
import os

# Get all JSON files in the current directory
json_files = [file for file in os.listdir() if file.endswith(".json")]

# List to store results
results = []

for json_file in json_files:
    with open(json_file, 'r') as file:
        df = json.loads(file.read())

    data_1 = df.get("tuefHeader")
    data_2 = df.get("names")
    data_3 = df.get("accounts")

    date_processed = data_1.get("dateProcessedFormatted")
    dob = data_2[0].get("birthDateFormatted")

    # Convert date strings to datetime format
    date_processed = datetime.strptime(date_processed, "%d-%m-%Y").date()
    dob = datetime.strptime(dob, "%d-%m-%Y").date()

    # Calculate age
    age = round((date_processed - dob).days / 365.25)

    # Extract payment history
    paymentHistory = [entry["paymentHistory"] for entry in data_3]
    paymentStartDateFormatted = [entry["paymentStartDateFormatted"] for entry in data_3]
    reportings = pd.DataFrame({"paymentHistory": paymentHistory, "paymentStartDate": paymentStartDateFormatted})
    reportings["paymentStartDate"] = pd.to_datetime(reportings["paymentStartDate"], format="%d-%m-%Y")

    # Function to split DPD data
    def split_dpd(string, size=3):
        return [string[i:i+size] for i in range(0, len(string), size)]

    monthly_reportings_data = []

    # Process DPD history
    for j, row in reportings.iterrows():
        for i, dpd in enumerate(split_dpd(row["paymentHistory"])):
            monthly_reportings_data.append({
                "Contract_ID": j+1, 
                "Month_ID": i+1, 
                "monthly_dpds": dpd, 
                "Reference_Date": (pd.to_datetime(row["paymentStartDate"] - timedelta(days=30 * i)))
            })

    monthly_reportings = pd.DataFrame(monthly_reportings_data)
    monthly_reportings["monthly_dpds"] = pd.to_numeric(monthly_reportings["monthly_dpds"], errors="coerce")

    # Filter last 12 months reportings
    L12M_reportings = monthly_reportings[(monthly_reportings["Reference_Date"] >= pd.to_datetime(date_processed - timedelta(days=365)))]
    count_30plus_L12M = L12M_reportings.groupby("Contract_ID")["monthly_dpds"].apply(lambda x: (x >= 30).sum())
    total_instances_30plus_L12M = count_30plus_L12M.sum()

    # Assign age-based score
    if age < 21 or age > 60:
        Pscore1 = 10
    elif 21 <= age <= 24:
        Pscore1 = 40
    elif 25 <= age <= 34:
        Pscore1 = 75
    elif 35 <= age <= 44:
        Pscore1 = 100
    elif 45 <= age <= 54:
        Pscore1 = 80
    elif 55 <= age <= 60:
        Pscore1 = 60
    else:
        Pscore1 = 0

    # Assign payment history-based score
    if total_instances_30plus_L12M == 0:
        Pscore2 = 100
    elif total_instances_30plus_L12M == 1:
        Pscore2 = 90
    elif total_instances_30plus_L12M == 2:
        Pscore2 = 75
    elif total_instances_30plus_L12M <= 4:
        Pscore2 = 40
    elif total_instances_30plus_L12M <= 7:
        Pscore2 = 20
    elif total_instances_30plus_L12M > 7:
        Pscore2 = 0
    else:
        Pscore2 = 0

    # Final Score
    Score = Pscore1 + Pscore2

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append results to list
    results.append([json_file, timestamp, age, total_instances_30plus_L12M, Pscore1, Pscore2, Score])

# Write results to CSV file
with open("result.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["File Name", "Timestamp", "Age", "# 30+ DPD in L12M", "PScore_Age", "PScore_DPD", "Score"])  # Header
    writer.writerows(results)

print("Processing complete. Results saved to result.csv")
