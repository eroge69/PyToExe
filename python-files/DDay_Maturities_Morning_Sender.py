
import requests
import pandas as pd
import json
import re
import numpy as np
import win32com.client as win32
from tqdm import tqdm
from datetime import datetime, timedelta

Advisor_list = pd.read_csv(r'C:\Users\lwilt\OneDrive - 1900 Wealth\Desktop\advisors_list.csv')
Advisor_list.iloc[:, 0] = Advisor_list.iloc[:, 0].astype(str)

import tkinter as tk
from tkinter import simpledialog

def get_authorization_token():
    # Create a temporary Tkinter window for token input
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Prompt user for the authorization token
    authorization_token = simpledialog.askstring("Authorization Token", "Enter Authorization Token:")
    if not authorization_token:
        raise ValueError("No Authorization Token provided. Please restart and enter a valid token.")
    return authorization_token

# Get the authorization token and assign it to a variable
authorization_token = get_authorization_token()
print(f"Authorization Token: {authorization_token}")

################################################################################

base_url = "https://api.schwabapi.com/as-integration/accounts/v2/accounts?showAccount=Show&page[limit]=500"
headers = {
    'Schwab-Resource-Version': '1',
    'Schwab-Client-CorrelId': '4ffc7c37-0ee3-41a6-b887-d8e1120ef3c3',
    'Master': 'masterAccount=8375808',
    'Authorization': f'Bearer {authorization_token}'
}

try:
    all_accounts = []  # List to store all account details
    cursors = ["", "501", "1001"]  # Define cursor values for pagination manually

    for cursor in cursors:
        # Construct URL with cursor
        current_url = f"{base_url}&page[cursor]={cursor}" if cursor else base_url
        
        # Make the API request
        response = requests.get(current_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        response_json = response.json()
        
        # Extract `id` and `formattedMasterAccount`
        accounts_data = [
            {"id": account["id"], "formattedMasterAccount": account["attributes"]["formattedMasterAccount"],"Account Title": account["attributes"]["accountTitle1"]}
            for account in response_json["data"]
        ]
        all_accounts.extend(accounts_data)  # Append to the list

    # Create a DataFrame with all accounts
    df = pd.DataFrame(all_accounts)
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
except Exception as err:
    print(f"Other error occurred: {err}")

df = df[df["formattedMasterAccount"] == "8375808"]
# Drop the 'formattedMasterAccount' column
df = df.drop(columns=["formattedMasterAccount"])
df_with_names =df
df = df.drop(columns=["Account Title"])
df_with_names.rename(columns={'id': 'Account Number'}, inplace=True)
ids = df["id"].tolist()


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Split the ids list into chunks of 200
id_chunks = list(chunk_list(ids, 200))
all_positions = []




url = "https://api.schwabapi.com/as-integration/accounts/v2/balances/list"

headers = {
    'Schwab-Resource-Version': '1',
    'Schwab-Client-CorrelId': 'a187e247-cbb8-46a9-926e-c00458c84ec0',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {authorization_token}'
}
#breaks the accounts into a managable list

id_chunks = list(chunk_list(ids, 200))

all_balances = []

# Iterate over each chunk and make the API request
for chunk in id_chunks:
    payload = json.dumps({
        'accounts': chunk,
        'showAccount': 'Show'
    })
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        response_json = response.json()
        
        balances = response_json["data"]["attributes"]['balances']
        all_balances.extend(balances)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except Exception as err:
        print(f"Other error occurred: {err}")  # Handle other errors

# Extract relevant data and create DataFrame
extracted_data = [{'formattedAccount': balance['formattedAccount'],
                   'accountTitle1': balance.get('accountTitle1', None),  # Include account title
                   'cashAndCashInvestments': balance.get('cashAndCashInvestments', None)} for balance in all_balances]

negative_df = pd.DataFrame(extracted_data)
negative_df = negative_df[negative_df["cashAndCashInvestments"] < 0]
negative_df = negative_df.rename(columns={
    "formattedAccount": "Account Number",
    "accountTitle1": "Account Title",
    "cashAndCashInvestments": "Cash and Investments"
})
negative_df['Cash and Investments'] = negative_df['Cash and Investments'].apply(lambda x: f"{x:,}")
status_code_2 = response.status_code
print(f"Status Code 2: {status_code_2}")





url = "https://api.schwabapi.com/as-integration/accounts/v2/positions/list"

headers = {
  'Schwab-Resource-Version': '1',
  'Schwab-Client-CorrelId': 'b5246638-1465-4c30-87e1-dd023240a810',
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {authorization_token}'
}
# Iterate over each chunk and make the API request
for chunk in id_chunks:
    payload = json.dumps({
      'accounts': chunk,
      'securityType': 'FixedIncome',
      'showAccount': 'Show'
    })
    
    response = requests.post(url, headers=headers, data=payload)
    response_json = response.json()
    
    positions = response_json["data"]["attributes"]['positions']
    all_positions.extend(positions)
status_code_3 = response.status_code
print(f"Status Code 3: {status_code_3}")
positions_df = pd.DataFrame(all_positions)
positions_df = positions_df[['formattedAccount','accountTitle1','securityName','symbol','quantity']]
positions_df = positions_df.rename(columns={
    'formattedAccount': 'Account Number',
    'accountTitle1': 'Account Title',
    'securityName': 'Security Name',
    'symbol': 'Symbol',
    'quantity': 'Quantity'
})
positions_df['Quantity'] = positions_df['Quantity'].apply(lambda x: f"{x:,}")

def extract_due_date(securityName):
    match = re.search(r'(DUE|CALLED) (\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2}-\d{4})', securityName)
    if match:
        return match.group(2)
    elif "CALLED" in securityName:
        return "CALLED"
    else:
        return None

positions_df['Due Date'] = positions_df['Security Name'].apply(extract_due_date)
called_df = positions_df[positions_df['Due Date'] == 'CALLED']
positions_df['Due Date'] = pd.to_datetime(positions_df['Due Date'], format="%m/%d/%y", errors='coerce')

today = pd.Timestamp.today()
previous_day = today - pd.Timedelta(days=1)

# Calculate 5 business days from today
five_business_days_out = np.busday_offset(today.date(), 5, roll='forward')

# Filter rows where 'dates' fall in the range [today, five_business_days_out]
positions_df = positions_df[(positions_df['Due Date'] >= pd.Timestamp(previous_day)) & 
                 (positions_df['Due Date'] <= pd.Timestamp(five_business_days_out))]

positions_df = positions_df.sort_values(by='Due Date', ascending=True)
positions_df['Due Date'] = positions_df['Due Date'].astype(str)
x = pd.concat([positions_df, called_df], ignore_index=True)
positions_df = x
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today = datetime.now().strftime('%Y-%m-%d')

# Dynamic URL template with yesterday and today as start and end dates
url_template = f"https://api.schwabapi.com/as-integration/accounts/v2/transactions?showAccount=Show&filter[startDate]={yesterday}&filter[endDate]={today}"

# Headers template
headers_template = {
    'Schwab-Resource-Version': '1',
    'Schwab-Client-CorrelId': '197cb192-2d86-49a0-904a-e33cbd72897f',  # Replace with your CorrelId if needed
    'Authorization': f'Bearer {authorization_token}'  # Replace with your actual token
}

# List to store extracted data
extracted_data = []

# Process each chunk of account IDs
for chunk in tqdm(id_chunks, desc="Processing account chunks"):
    for account in tqdm(chunk, desc=f"Processing accounts in chunk {id_chunks.index(chunk) + 1}", leave=False):
        headers = headers_template.copy()
        headers['Schwab-Client-Ids'] = f'account={account}'  # Update with the current account ID
        
        response = requests.request("GET", url_template, headers=headers)
        
        # Assuming the response contains the JSON structure provided above
        if response.status_code == 200:
            data = response.json()
            for transaction in data.get('data', []):
                attributes = transaction.get('attributes', {})
                extracted_data.append({
                    'Account Number': attributes.get('formattedAccount', ''),
                    'Action': attributes.get('action', ''),
                    'Description': attributes.get('description', ''),
                    'Amount': attributes.get('amount', 0)
                })

# Create a DataFrame from the extracted data
transaction_df = pd.DataFrame(extracted_data)
new_df = transaction_df[transaction_df['Action'].isin(['MoneyLink Transfer',
                                                       'MoneyLink Deposit',
                                                       'Journal',
                                                       'Security Transfer',
                                                       'Funds Received',
                                                       'Wire Funds Received'])]

new_df =new_df[new_df['Amount'] >= 0]
new_df['Amount'] = new_df['Amount'].apply(lambda x: f"{x:,}")



merged_new_df = pd.merge(new_df,df_with_names, on='Account Number', how='inner')
merged_new_df = pd.merge(new_df,Advisor_list, on='Account Number', how='inner')
merged_positions_df = pd.merge(positions_df,Advisor_list, on='Account Number', how='inner')
merged_positions_df = merged_positions_df.drop(columns=["Account Name"])
negative_df = pd.merge(negative_df,Advisor_list, on='Account Number', how='inner')


negative_df = negative_df.sort_values(by='Cash and Investments', ascending=False)
merged_new_df = merged_new_df.sort_values(by='Amount', ascending=False)
merged_new_df = merged_new_df.sort_values(by='Primary Advisor', ascending=False)

for advisor, group in merged_new_df.groupby('Primary Advisor'):
    globals()[f"{advisor}_new"] = group


for advisor, group in merged_positions_df.groupby('Primary Advisor'):
    globals()[f"{advisor}_positions"] = group




merged_new_df['Email'] = 'Lawsin@1900wealth.com'
merged_positions_df['Email'] = 'Lawsin@1900wealth.com'





def send_email(dataframes, table_names, subject, recipient):
    # Initialize Outlook application
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # Create a new mail item

    # Prepare HTML tables with names for each DataFrame
    html_tables = ""
    for dataframe, table_name in zip(dataframes, table_names):
        html_tables += f"<h3>{table_name}</h3>"  # Add table name as a heading
        html_tables += dataframe.to_html(index=False)
        html_tables += "<br><br>"  # Add space between tables

    # Set up email properties
    mail.Subject = subject
    mail.To = recipient
    mail.HTMLBody = f"""
    <html>
    <body>
        <p>Here are the requested data:</p>
        {html_tables}
    </body>
    </html>
    """

    # Send the email
    mail.Send()

# Call the function with DataFrames and their respective names
#send_email(
#    [negative_df, merged_new_df, merged_positions_df], 
#    ["Negative Account Balances", "New Funds to account", "Maturities that are due in the next 5 days"], 
#    "Daily Dose", 
#    "bobby@1900wealth.com")
#send_email(
#    [negative_df, merged_new_df, merged_positions_df], 
#    ["Negative Account Balances", "New Funds to account", "Maturities that are due in the next 5 days"], 
#    "Daily Dose", 
#    "Miles@1900wealth.com")
#send_email(
#    [negative_df, merged_new_df, merged_positions_df], 
#    ["Negative Account Balances", "New Funds to account", "Maturities that are due in the next 5 days"], 
#    "Daily Dose", 
#    "Phyllis@1900wealth.com")


def send_email_to_advisors(dataframes_dict, cc_addresses=None):  # Add optional cc_addresses parameter
    # Initialize Outlook application
    outlook = win32.Dispatch("Outlook.Application")
    
    for advisor, dataframes in dataframes_dict.items():
        # Ensure the email address column exists and retrieve the recipient
        if 'Email' in dataframes[0].columns:  # Assuming all sub-DataFrames for the advisor have the same structure
            recipient = dataframes[0]['Email'].iloc[0]  # Get the email address for the advisor
        
            # Prepare HTML content with labeled tables
            html_tables = ""
            for i, dataframe in enumerate(dataframes):
                table_label = f"<h3>{dataframe.name}</h3>" if hasattr(dataframe, "name") else f"<h3>Table {i + 1}</h3>"
                html_tables += table_label + dataframe.to_html(index=False) + "<br><br>"  # Label and HTML table
            
            # Create and send email
            mail = outlook.CreateItem(0)  # Create a new mail item
            mail.Subject = f"Data for {advisor}"
            mail.To = recipient
            mail.HTMLBody = f"""
            <html>
            <body>
                <p>Dear {advisor},</p>
                <p>Please find your requested data below:</p>
                {html_tables}
            </body>
            </html>
            """
            
            # Add CC recipients if provided
            if cc_addresses:
                mail.CC = ";".join(cc_addresses)  # Join the list of CC addresses into a single string
            
            mail.Send()
            print(f"Email sent to {advisor} at {recipient} with CC to {cc_addresses}.")
        else:
            print(f"Email column missing for advisor: {advisor}")



# Grouping DataFrames by Primary Advisor and preparing them for email
dataframes_to_email = {}

for advisor, group in merged_new_df.groupby('Primary Advisor'):
    if advisor not in dataframes_to_email:
        dataframes_to_email[advisor] = []
    group.name = "New Funds to account"  # Add label for the table
    dataframes_to_email[advisor].append(group)

for advisor, group in merged_positions_df.groupby('Primary Advisor'):
    if advisor not in dataframes_to_email:
        dataframes_to_email[advisor] = []
    group.name = "Maturities that are due in the next 5 days"  # Add label for the table
    dataframes_to_email[advisor].append(group)

# Send emails to advisors with their respective DataFrames
#send_email_to_advisors(dataframes_to_email, cc_addresses=["miles@1900wealth.com","phyllis@1900wealth.com","bobby@1900wealth.com"])
send_email_to_advisors(dataframes_to_email)