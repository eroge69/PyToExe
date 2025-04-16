import uuid
import json
import os
import requests
import shutil
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style, init

init(autoreset=True)
os.system("title by AkiraLofy - discord.gg/brazilcraft")

def get_lunar_accounts_path():
    home_dir = os.path.expanduser("~")
    lunar_dir = os.path.join(home_dir, ".lunarclient", "settings", "game")
    accounts_file = os.path.join(lunar_dir, "accounts.json")
    return accounts_file


def get_real_uuid(useruuid):
    url = f"https://api.mojang.com/users/profiles/minecraft/{useruuid}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            raw_uuid = response.json().get("id")
            formatted_uuid = f"{raw_uuid[0:8]}-{raw_uuid[8:12]}-{raw_uuid[12:16]}-{raw_uuid[16:20]}-{raw_uuid[20:]}"
            return formatted_uuid
        else:
            print(Fore.RED + "Nome de usuário inválido ou não registrado.")
            return None
    except requests.exceptions.RequestException:
        print(Fore.RED + "Falha ao acessar api da Mojang.")
        return None


def generate_account(account_uuid, username):
    expires_at = (datetime.now(timezone.utc) + timedelta(days=365 * 25)).isoformat().replace("+00:00", "Z")

    return {
        "accessToken": account_uuid,
        "accessTokenExpiresAt": expires_at,
        "eligibleForMigration": False,
        "hasMultipleProfiles": False,
        "legacy": True,
        "persistent": True,
        "userProperties": [],
        "localId": account_uuid,
        "minecraftProfile": {
            "id": account_uuid,
            "name": username
        },
        "remoteId": account_uuid,
        "type": "Xbox",
        "username": username
    }


def load_accounts():
    accounts_path = get_lunar_accounts_path()
    if not os.path.exists(accounts_path):
        return {"accounts": {}}

    try:
        with open(accounts_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "accounts" not in data:
                data["accounts"] = {}
            return data
    except (json.JSONDecodeError, IOError):
        return {"accounts": {}}


def save_accounts(accounts_data):
    accounts_path = get_lunar_accounts_path()
    with open(accounts_path, "w", encoding="utf-8") as file:
        json.dump(accounts_data, file, indent=4)


def add_account_to_lunar():
    username = input(Fore.YELLOW + "Insira um nome: ")

    print(Fore.BLUE + "\nEscolha um método:")
    print(Fore.CYAN + "1. Gerar um UUID aleatório.")
    print(Fore.CYAN + "2. Obter um UUID por um username.")
    print(Fore.CYAN + "3. Inserir um UUID customizado.")

    choice = input(Fore.YELLOW + "Escolha uma opção: ")

    if choice == "1":
        account_uuid = str(uuid.uuid4())
        print(Fore.GREEN + f"UUID Gerado: {account_uuid}")
    elif choice == "2":
        useruuid = input(Fore.YELLOW + "Digite o username para buscar o UUID: ")
        account_uuid = get_real_uuid(useruuid)
        if not account_uuid:
            print(Fore.RED + "Falha ao adicionar conta. Certifique-se de que o nome de usuário esteja correto.")
            return
    elif choice == "3":
        account_uuid = input(Fore.YELLOW + "Insira seu UUID: ")
    else:
        print(Fore.RED + "Escolha inválida. Abortando.")
        return

    accounts_data = load_accounts()
    accounts_data["accounts"][account_uuid] = generate_account(account_uuid, username)
    save_accounts(accounts_data)
    print(Fore.GREEN + f"Conta {username} ({account_uuid}) adicionado com sucesso.")


def list_accounts():
    accounts_data = load_accounts()

    if not accounts_data["accounts"]:
        print(Fore.YELLOW + "Nenhuma conta encontrada.")
        return

    print(Fore.CYAN + "Contas armazenadas:")
    for uuid_key, account_info in accounts_data["accounts"].items():
        name = account_info.get("minecraftProfile", {}).get("name", "Unknown")
        print(Fore.MAGENTA + f"UUID: {uuid_key} - Username: {name}")


def delete_account(account_uuid):
    accounts_data = load_accounts()
    if account_uuid in accounts_data["accounts"]:
        del accounts_data["accounts"][account_uuid]
        save_accounts(accounts_data)
        print(Fore.RED + f"Conta {account_uuid} deletada com sucesso.")
    else:
        print(Fore.YELLOW + "UUID não encontrado.")



def main():
    while True:
        print(Fore.BLUE + "\n1. Adicionar Conta")
        print(Fore.BLUE + "2. Lista de Contas")
        print(Fore.BLUE + "3. Deletar Conta")
        print(Fore.RED + "4. Sair")
        choice = input(Fore.CYAN + "Escolha uma opção: ")

        if choice == "1":
            add_account_to_lunar()
        elif choice == "2":
            list_accounts()
        elif choice == "3":
            account_uuid = input(Fore.YELLOW + "Digite o UUID para excluir: ")
            delete_account(account_uuid)
        elif choice == "4":
            print(Fore.RED + "Saindo...")
            break
        else:
            print(Fore.YELLOW + "Escolha inválida, tente novamente.")


if __name__ == "__main__":
    main()
