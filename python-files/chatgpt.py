import requests
import json
import time
import os

BASE_URL = "https://discord.com/api/v10"

def get_headers(token):
    return {
        "Authorization": token,
        "Content-Type": "application/json"
    }

def get_guild_roles(token, guild_id):
    url = f"{BASE_URL}/guilds/{guild_id}/roles"
    response = requests.get(url, headers=get_headers(token))
    return response.json()

def create_role(token, guild_id, role_data):
    url = f"{BASE_URL}/guilds/{guild_id}/roles"
    response = requests.post(url, headers=get_headers(token), data=json.dumps(role_data))
    return response.json()

def get_guild_channels(token, guild_id):
    url = f"{BASE_URL}/guilds/{guild_id}/channels"
    response = requests.get(url, headers=get_headers(token))
    return response.json()

def create_channel(token, guild_id, channel_data):
    url = f"{BASE_URL}/guilds/{guild_id}/channels"
    response = requests.post(url, headers=get_headers(token), data=json.dumps(channel_data))
    return response.json()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_console()
    print("💻 Discord Sunucu Kopyalayıcı | by ChatGPT\n")
    print("❗ Uyarı: Bu program kullanıcı tokeni kullanır ve sadece kendi hesabınızda denenmelidir.\n")

    token = input("🔐 Kullanıcı tokeninizi girin: ").strip()
    kaynak_id = input("📤 Kaynak sunucu ID'si: ").strip()
    hedef_id = input("📥 Hedef sunucu ID'si: ").strip()

    print("\n📦 Roller kopyalanıyor...")
    roller = get_guild_roles(token, kaynak_id)
    for role in roller[::-1]:  # En alttan yukarı
        if role["name"] != "@everyone":
            role_data = {
                "name": role["name"],
                "color": role["color"],
                "hoist": role["hoist"],
                "mentionable": role["mentionable"],
                "permissions": role["permissions"]
            }
            print(f"➕ Rol: {role['name']}")
            create_role(token, hedef_id, role_data)
            time.sleep(1)

    print("\n📁 Kanallar ve Kategoriler kopyalanıyor...")
    kanallar = get_guild_channels(token, kaynak_id)
    id_map = {}

    # Önce kategoriler
    for kanal in kanallar:
        if kanal["type"] == 4:  # Kategori
            data = {
                "name": kanal["name"],
                "type": 4,
                "position": kanal["position"]
            }
            print(f"📂 Kategori: {kanal['name']}")
            result = create_channel(token, hedef_id, data)
            id_map[kanal["id"]] = result.get("id")
            time.sleep(1)

    # Sonra normal kanallar
    for kanal in kanallar:
        if kanal["type"] != 4:
            data = {
                "name": kanal["name"],
                "type": kanal["type"],
                "position": kanal["position"],
                "parent_id": id_map.get(kanal.get("parent_id")),
                "topic": kanal.get("topic", "")
            }
            print(f"📨 Kanal: {kanal['name']}")
            create_channel(token, hedef_id, data)
            time.sleep(1)

    print("\n✅ Tüm işlemler tamamlandı!")

if __name__ == "__main__":
    main()
