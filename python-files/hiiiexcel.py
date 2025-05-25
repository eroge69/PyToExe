import subprocess
import threading
from openpyxl import Workbook

# Function to read IPs from a text file
def load_ips_from_file(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file.readlines()]

# Create a new Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "Ping Results"
ws.append(["IP Address", "Status"])  # Adding column headers

# Store results first (avoids threading issues)
results = []

# Function to ping IP and store results safely
def ping_ip(ip):
    ps_command = f'powershell -Command "Test-Connection -ComputerName {ip} -Count 2 -Quiet"'
    result = subprocess.run(ps_command, capture_output=True, text=True)
    
    status = "Online" if "True" in result.stdout else "Offline"
    results.append([ip, status])  # Store result instead of writing immediately

# Load IPs from file
ip_addresses = load_ips_from_file("C:\\Users\\piyush.khairnar\\Desktop\\New_folder\\ip_list.txt")


# Create and start threads
threads = []
for ip in ip_addresses:
    thread = threading.Thread(target=ping_ip, args=(ip,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Write results to Excel **after** all threads finish
for result in results:
    ws.append(result)

# Save the Excel file
wb.save("C:\\Users\\piyush.khairnar\\Desktop\\New_folder\\ping_results.xlsx")


print("\nPing results saved successfully in 'ping_results.xlsx' ✅")

input("Process completed. Press Enter to exit...")
