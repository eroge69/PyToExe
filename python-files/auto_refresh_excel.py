
import os
import win32com.client as win32

folder_path = r"C:\Users\harshvardhan.palawat\Music\Update"

# Get list of all Excel files
excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xlsm'))]

# Launch Excel application
excel_app = win32.Dispatch("Excel.Application")
excel_app.Visible = False  # Set to True if you want to watch the automation

for file in excel_files:
    full_path = os.path.join(folder_path, file)
    print(f"Processing {file}...")
    
    workbook = excel_app.Workbooks.Open(full_path)

    # Refresh all data connections
    workbook.RefreshAll()
    
    # Wait for refresh to complete
    excel_app.CalculateUntilAsyncQueriesDone()

    # Save and close
    workbook.Save()
    workbook.Close()

excel_app.Quit()
print("All files refreshed, saved, and closed.")
