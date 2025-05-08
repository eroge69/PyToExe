from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import csv
import os

# Get all JSON files in the current directory
json_files = [file for file in os.listdir() if file.endswith(".json")]

# List to store results
results = []

def split_dpd(string, size=3):
    """Splits the DPD string into chunks of size 3 (Monthly DPD values)."""
    return [string[i:i+size] for i in range(0, len(string), size)]

for json_file in json_files:
    with open(json_file, 'r') as file:
        df = json.loads(file.read())

    data_1 = df.get("tuefHeader", {})
    data_2 = df.get("names", [{}])
    data_3 = df.get("accounts", [])

    date_processed = data_1.get("dateProcessedFormatted")
    dob = data_2[0].get("birthDateFormatted")

    # Convert date strings to datetime objects
    date_processed = datetime.strptime(date_processed, "%d-%m-%Y").date()
    dob = datetime.strptime(dob, "%d-%m-%Y").date()

    # Calculate age
    age = round((date_processed - dob).days / 365.25)

    # Extract payment history
    monthly_reportings_data = []
    
    for j, entry in enumerate(data_3):
        payment_history = entry.get("paymentHistory", "")
        payment_start_date_str = entry.get("paymentStartDateFormatted", "")

        # Convert payment start date string to date object
        payment_start_date = datetime.strptime(payment_start_date_str, "%d-%m-%Y").date()

        for i, dpd in enumerate(split_dpd(payment_history)):
            reference_date = payment_start_date - relativedelta(months=i)

            monthly_reportings_data.append({
                "Contract_ID": j + 1,
                "Month_ID": i + 1,
                "monthly_dpds": int(dpd) if dpd.isdigit() else 0,  # Convert to numeric, default to 0
                "Reference_Date": reference_date
            })

    # Filter last 12 months reportings
    L12M_reportings = [entry for entry in monthly_reportings_data if entry["Reference_Date"] >= (date_processed - relativedelta(years=1))]

    # Count occurrences of DPD ≥ 30 in last 12 months
    count_30plus_L12M = {}

    for entry in L12M_reportings:
        contract_id = entry["Contract_ID"]
        if contract_id not in count_30plus_L12M:
            count_30plus_L12M[contract_id] = 0
        if entry["monthly_dpds"] >= 30:
            count_30plus_L12M[contract_id] += 1

    total_instances_30plus_L12M = max(count_30plus_L12M.values(), default=0)

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
