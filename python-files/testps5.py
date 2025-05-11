import asyncio
from pydualsense import pydualsense
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

# Initialiser la manette DualSense
dualsense = pydualsense()
dualsense.init()  # Se connecte en Bluetooth si déjà appairée

# Configurer la connexion Lovense via Buttplug
async def lovense_to_dualsense():
    client = ButtplugClient("PS5 DualSense Vibrator")
    connector = ButtplugClientWebsocketConnector("ws://127.0.0.1:12345")  # Intiface
    
    try:
        await client.connect(connector)
        print("🔌 Connecté à Lovense via Buttplug.io")
        
        # Scanner les appareils Lovense (ex. Lush, Domi, etc.)
        await client.start_scanning()
        print("📡 Recherche d'appareils Lovense...")
        
        # Attendre qu'un appareil soit détecté
        while not client.devices:
            await asyncio.sleep(1)
        
        device = client.devices[0]
        print(f"🎮 Appareil connecté : {device.name}")
        
        # Fonction de vibration
        async def handle_vibration(msg):
            speed = msg.ScalarCmd[0].Scalar  # Reçoit 0.0 à 1.0
            vibration = int(speed * 255)    # Convertit en 0-255
            dualsense.setRightMotor(vibration)  # Active le vibreur
            print(f"📳 Vibration : {vibration}/255")
        
        # Écouter les commandes Lovense
        device.on("vibrate", handle_vibration)
        
        # Maintenir la connexion
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        await client.disconnect()
        dualsense.close()

# Lancer le programme
asyncio.run(lovense_to_dualsense())