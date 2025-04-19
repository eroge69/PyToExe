import os
import shutil
import re
import json
from collections import Counter
import concurrent.futures
import math
from collections import OrderedDict

# Cabeçalho do programa
def exibir_cabecalho():
    # Obtém o tamanho do terminal
    columns = shutil.get_terminal_size().columns
    print("=" * columns)
    print("🔥 Desenvolvido por H4RD STORE 🔥".center(columns))
    print("=" * columns)

def escolher_idioma():
    print("Escolha o idioma / Choose the language:")
    print("1. Português")
    print("2. English")
    idioma = input("Digite o número correspondente / Enter the corresponding number: ").strip()
    if idioma == "1":
        return "pt"
    elif idioma == "2":
        return "en"
    else:
        print("Opção inválida / Invalid option. Padrão para Português / Defaulting to Portuguese.")
        return "pt"

# Dicionário de mensagens para suporte a múltiplos idiomas
mensagens = {
    "pt": {
        "menu": "\n=== Steam Toolkit ===\n"
                "1. Extrair shared_secret e identity_secret\n"
                "2. Extrair apenas shared_secret\n"
                "3. Adicionar identity_secret (a partir do shared)\n"
                "4. Remover shared_secret (manter username:password)\n"
                "5. Verificar usernames duplicados\n"
                "6. Renomear .maFile para steamid\n"
                "7. Renomear .maFile para username\n"
                "8. Gerar configs ASF\n"
                "9. Processar completo (shared, identity, renomear, ASF)\n"  # Adicionado
                "0. Sair\n"
                "Escolha uma opção: ",
        "exit": "👋 A sair...",
        "invalid_option": "❌ Opção inválida.",
        "file_not_found": "❌ ERRO: Arquivo '{caminho}' não encontrado.",
        "folder_not_found": "❌ ERRO: Pasta '{caminho}' não encontrada.",
        "output_file": "📤 Nome do ficheiro de saída: ",
        "choose_file": "📄 Caminho do arquivo {descricao}: ",
        "choose_folder": "📁 Caminho da pasta {descricao}: ",
    },
    "en": {
        "menu": "\n=== Steam Toolkit ===\n"
                "1. Extract shared_secret and identity_secret\n"
                "2. Extract only shared_secret\n"
                "3. Add identity_secret (from shared)\n"
                "4. Remove shared_secret (keep username:password)\n"
                "5. Check for duplicate usernames\n"
                "6. Rename .maFile to steamid\n"
                "7. Rename .maFile to username\n"
                "8. Generate ASF configs\n"
                "9. Complete process (shared, identity, rename, ASF)\n"  # Adicionado
                "0. Exit\n"
                "Choose an option: ",
        "exit": "👋 Exiting...",
        "invalid_option": "❌ Invalid option.",
        "file_not_found": "❌ ERROR: File '{caminho}' not found.",
        "folder_not_found": "❌ ERROR: Folder '{caminho}' not found.",
        "output_file": "📤 Output file name: ",
        "choose_file": "📄 File path for {descricao}: ",
        "choose_folder": "📁 Folder path for {descricao}: ",
    }
}

# Atualização das funções para exibir o cabeçalho antes de cada interação
def menu(idioma):
    exibir_cabecalho()  # Exibe o cabeçalho antes do menu
    return input(mensagens[idioma]["menu"]).strip()

def pedir_caminho_arquivo(descricao, formato_esperado, idioma):
    exibir_cabecalho()  # Exibe o cabeçalho antes de pedir o caminho
    print(f"⚠️ {formato_esperado}")
    caminho = input(mensagens[idioma]["choose_file"].format(descricao=descricao)).strip()
    if caminho.startswith('"') and caminho.endswith('"'):
        caminho = caminho[1:-1]  # Remove as aspas no início e no fim
    if not os.path.exists(caminho):
        print(mensagens[idioma]["file_not_found"].format(caminho=caminho))
        return None
    return caminho

def pedir_caminho_pasta(descricao, formato_esperado, idioma):
    exibir_cabecalho()  # Exibe o cabeçalho antes de pedir o caminho
    print(f"⚠️ {formato_esperado}")
    caminho = input(mensagens[idioma]["choose_folder"].format(descricao=descricao)).strip()
    if caminho.startswith('"') and caminho.endswith('"'):  # Corrigido 'e' para 'and'
        caminho = caminho[1:-1]  # Remove as aspas no início e no fim
    if not os.path.exists(caminho):
        print(mensagens[idioma]["folder_not_found"].format(caminho=caminho))
        return None
    return caminho

# Funções de manipulação de .maFile
def extrair_shared_e_identity(accounts_file, mafiles_folder, output_file):
    if not output_file.endswith(".txt"):
        output_file += ".txt"  # Garante que a saída seja .txt
    with open(accounts_file, "r", encoding="utf-8") as f:
        accounts = [line.strip().split(":") for line in f if ":" in line]

    new_accounts = []

    for account in accounts:
        if len(account) != 2:
            continue
        username, password = account
        mafile_path = os.path.join(mafiles_folder, f"{username}.maFile")

        if os.path.exists(mafile_path):
            with open(mafile_path, "r", encoding="utf-8") as f:
                raw_json = f.read()
            shared = re.search(r'"shared_secret"\s*:\s*"([^"]+)"', raw_json)
            identity = re.search(r'"identity_secret"\s*:\s*"([^"]+)"', raw_json)

            if shared and identity:
                new_accounts.append(f"{username}:{password}:{shared.group(1)}:{identity.group(1)}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_accounts))
    print(f"✅ Exportado para {output_file}")

def extrair_shared(accounts_file, mafiles_folder, output_file):
    if not output_file.endswith(".txt"):
        output_file += ".txt"  # Garante que a saída seja .txt
    with open(accounts_file, "r", encoding="utf-8") as f:
        accounts = [line.strip().split(":") for line in f if ":" in line]

    new_accounts = []

    for account in accounts:
        if len(account) != 2:
            continue
        username, password = account
        mafile_path = os.path.join(mafiles_folder, f"{username}.maFile")
        if os.path.exists(mafile_path):
            with open(mafile_path, "r", encoding="utf-8") as f:
                raw_json = f.read()
            shared = re.search(r'"shared_secret"\s*:\s*"([^"]+)"', raw_json)
            if shared:
                new_accounts.append(f"{username}:{password}:{shared.group(1)}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_accounts))
    print(f"✅ Exportado para {output_file}")

def adicionar_identity(input_file, mafiles_folder, output_file):
    if not output_file.endswith(".txt"):
        output_file += ".txt"  # Garante que a saída seja .txt
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip().split(":") for line in f if line.count(":") == 2]

    new_accounts = []

    for line in lines:
        if len(line) != 3:
            continue
        username, password, shared_secret = line
        mafile_path = os.path.join(mafiles_folder, f"{username}.maFile")
        if os.path.exists(mafile_path):
            with open(mafile_path, "r", encoding="utf-8") as f:
                raw_json = f.read()
            identity = re.search(r'"identity_secret"\s*:\s*"([^"]+)"', raw_json)
            if identity:
                new_accounts.append(f"{username}:{password}:{shared_secret}:{identity.group(1)}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_accounts))
    print(f"✅ Exportado para {output_file}")

def remover_shared(input_file, output_file):
    if not output_file.endswith(".txt"):
        output_file += ".txt"  # Garante que a saída seja .txt
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    new_lines = []
    for line in lines:
        parts = line.split(":")
        if len(parts) >= 2:
            new_lines.append(f"{parts[0]}:{parts[1]}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    print(f"✅ Exportado para {output_file}")

def verificar_duplicados(input_file, log_file):
    if not log_file.endswith(".txt"):
        log_file += ".txt"  # Garante que a saída seja .txt
    with open(input_file, "r", encoding="utf-8") as f:
        usernames = [line.split(":")[0] for line in f if ":" in line]

    counts = Counter(usernames)
    duplicados = [u for u, c in counts.items() if c > 1]

    with open(log_file, "w", encoding="utf-8") as f:
        for user in duplicados:
            f.write(f"{user} aparece {counts[user]}x\n")

    print(f"✅ Log de duplicados salvo em: {log_file}")

def renomear_mafiles_para_steamid(mafiles_folder):
    def renomear(filename):
        if not filename.endswith(".maFile"): return
        filepath = os.path.join(mafiles_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        steamid = data.get("steamid") or data.get("Session", {}).get("SteamID")
        if steamid:
            new_path = os.path.join(mafiles_folder, f"{steamid}.maFile")
            if not os.path.exists(new_path):
                os.rename(filepath, new_path)
                print(f"{filename} ➜ {steamid}.maFile")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(renomear, os.listdir(mafiles_folder))

def renomear_mafiles_para_username(mafiles_folder):
    def renomear(filename):
        if not filename.endswith(".maFile"): 
            return
        filepath = os.path.join(mafiles_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:  # Removido o parêntese extra
            data = json.load(f)
        username = data.get("account_name")
        if username:
            new_path = os.path.join(mafiles_folder, f"{username}.maFile")
            if not os.path.exists(new_path):
                os.rename(filepath, new_path)
                print(f"{filename} ➜ {username}.maFile")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(renomear, os.listdir(mafiles_folder))

def generate_asf_configs(accounts_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(accounts_file):
        print(f"❌ ERRO: O arquivo '{accounts_file}' não foi encontrado!")
        return

    with open(accounts_file, 'r', encoding='utf-8') as f:
        accounts = [line.strip().split(":") for line in f if line.count(":") == 1]  # Corrigido 'para' para 'for'

    if not accounts:
        print("❌ ERRO: Nenhuma conta válida encontrada em accounts.txt!")
        return

    total_created = 0

    for account in accounts:  # Corrigido 'para' para 'for'
        if len(account) != 2:
            print(f"⚠️ AVISO: Linha ignorada devido a formato inválido: {account}")
            continue

        username, password = account
        output_path = os.path.join(output_folder, f"{username}.json")

        asf_config = OrderedDict([
            ("BotBehaviour", 63),
            ("CompleteTypesToSend", [3, 5]),
            ("Enabled", True),
            ("FarmingOrders", [4]),
            ("FarmingPreferences", 383),
            ("GamesPlayedWhileIdle", [730, 440]),
            ("LootableTypes", [1, 2, 3, 4, 5, 6, 7, 8, 10]),
            ("MatchableTypes", [1, 2, 3, 4, 5, 6, 7, 8, 10]),
            ("OnlinePreferences", 1),
            ("OnlineStatus", 7),
            ("RemoteCommunication", 0),
            ("SteamLogin", username),
            ("SteamMasterClanID", 103582791475008990),
            ("SteamPassword", password),
            ("SteamTradeToken", "sZo6NdUe"),
            ("SteamUserPermissions", {"76561198809112536": 3}),
            ("TransferableTypes", [1, 2, 3, 4, 5, 6, 7, 8, 10])
        ])

        json_string = json.dumps(asf_config, indent=4, ensure_ascii=False)

        try:
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_string)
            print(f"✅ Arquivo criado: {output_path}")
            total_created += 1
        except Exception as e:
            print(f"❌ ERRO ao salvar {output_path}: {e}")

    print(f"\n🔹 Processo concluído! {total_created} arquivos foram criados.")

def processar_completo(accounts_file, mafiles_folder, output_folder):
    """
    Realiza as seguintes operações:
    1. Cria um arquivo com username:password:shared.
    2. Cria um arquivo com username:password:shared:identity.
    3. Renomeia arquivos .maFile para username.maFile.
    4. Gera configurações ASF.
    """
    # Etapa 1: Processar shared_secret e identity_secret
    with open(accounts_file, "r", encoding="utf-8") as f:
        accounts = [line.strip().split(":") for line in f if ":" in line]

    shared_accounts = []
    full_accounts = []

    for account in accounts:
        if len(account) != 2:
            continue
        username, password = account
        mafile_path = os.path.join(mafiles_folder, f"{username}.maFile")

        if os.path.exists(mafile_path):
            with open(mafile_path, "r", encoding="utf-8") as f:
                raw_json = f.read()
            shared = re.search(r'"shared_secret"\s*:\s*"([^"]+)"', raw_json)
            identity = re.search(r'"identity_secret"\s*:\s*"([^"]+)"', raw_json)

            if shared:
                shared_accounts.append(f"{username}:{password}:{shared.group(1)}")
            if shared and identity:
                full_accounts.append(f"{username}:{password}:{shared.group(1)}:{identity.group(1)}")

    # Salvar arquivos com shared e full (shared + identity)
    shared_file = accounts_file.replace(".txt", "_shared.txt")
    full_file = accounts_file.replace(".txt", "_full.txt")

    with open(shared_file, "w", encoding="utf-8") as f:
        f.write("\n".join(shared_accounts))
    print(f"✅ Arquivo com shared_secret salvo em: {shared_file}")

    with open(full_file, "w", encoding="utf-8") as f:
        f.write("\n".join(full_accounts))
    print(f"✅ Arquivo com shared_secret e identity_secret salvo em: {full_file}")

    # Etapa 2: Renomear arquivos .maFile para username.maFile
    def renomear(filename):
        if not filename.endswith(".maFile"):
            return
        filepath = os.path.join(mafiles_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        username = data.get("account_name")
        if username:
            new_path = os.path.join(mafiles_folder, f"{username}.maFile")
            if not os.path.exists(new_path):
                os.rename(filepath, new_path)
                print(f"{filename} ➜ {username}.maFile")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(renomear, os.listdir(mafiles_folder))

    print("✅ Arquivos .maFile renomeados com sucesso.")

    # Etapa 3: Gera configurações ASF
    os.makedirs(output_folder, exist_ok=True)

    for account in full_accounts:
        parts = account.split(":")
        if len(parts) < 2:
            continue
        username, password = parts[:2]
        output_path = os.path.join(output_folder, f"{username}.json")

        asf_config = OrderedDict([
            ("BotBehaviour", 63),
            ("CompleteTypesToSend", [3, 5]),
            ("Enabled", True),
            ("FarmingOrders", [4]),
            ("FarmingPreferences", 383),
            ("GamesPlayedWhileIdle", [730, 440]),
            ("LootableTypes", [1, 2, 3, 4, 5, 6, 7, 8, 10]),
            ("MatchableTypes", [1, 2, 3, 4, 5, 6, 7, 8, 10]),
            ("OnlinePreferences", 1),
            ("OnlineStatus", 7),
            ("RemoteCommunication", 0),
            ("SteamLogin", username),
            ("SteamMasterClanID", 103582791475008990),
            ("SteamPassword", password),
            ("SteamTradeToken", "sZo6NdUe"),
            ("SteamUserPermissions", {"76561198809112536": 3}),
            ("TransferableTypes", [1, 2, 3, 4, 5, 6, 7, 8, 10])
        ])

        json_string = json.dumps(asf_config, indent=4, ensure_ascii=False)

        try:
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_string)
            print(f"✅ Configuração ASF criada: {output_path}")
        except Exception as e:
            print(f"❌ ERRO ao salvar {output_path}: {e}")

    print("✅ Todas as configurações ASF foram geradas com sucesso.")

# Caminhos relativos ao mesmo diretório do script
accounts_file = "accounts.txt"
output_folder = "ASF_Configs"
mafiles_folder = "maFiles"  # Só para organizar

# Execução principal
exibir_cabecalho()  # Exibe o cabeçalho
idioma = escolher_idioma()  # Escolha do idioma
while True:
    exibir_cabecalho()  # Exibe o cabeçalho antes de cada interação no loop principal
    escolha = menu(idioma)

    if escolha == "1":
        acc = pedir_caminho_arquivo("accounts.txt", "username:password ou username:password:shared_secret", idioma)
        if not acc:
            continue
        pasta = pedir_caminho_pasta("maFiles", "username.maFile ou steamid.maFile", idioma)
        if not pasta:
            continue
        out = input(mensagens[idioma]["output_file"]).strip()
        extrair_shared_e_identity(acc, pasta, out)

    elif escolha == "2":
        acc = pedir_caminho_arquivo("accounts.txt", "username:password ou username:password:shared_secret", idioma)
        if not acc:
            continue
        pasta = pedir_caminho_pasta("maFiles", "username.maFile ou steamid.maFile", idioma)
        if not pasta:
            continue
        out = input(mensagens[idioma]["output_file"]).strip()
        extrair_shared(acc, pasta, out)

    elif escolha == "3":
        inp = pedir_caminho_arquivo("username:password:shared_secret", "username:password:shared_secret", idioma)
        if not inp:
            continue
        pasta = pedir_caminho_pasta("maFiles", "username.maFile ou steamid.maFile", idioma)
        if not pasta:
            continue
        out = input(mensagens[idioma]["output_file"]).strip()
        adicionar_identity(inp, pasta, out)

    elif escolha == "4":
        inp = pedir_caminho_arquivo("com shared_secret", "username:password:shared_secret", idioma)
        if not inp:
            continue
        out = input(mensagens[idioma]["output_file"]).strip()
        remover_shared(inp, out)

    elif escolha == "5":
        inp = pedir_caminho_arquivo("accounts para verificar duplicados", "username:password ou username:password:shared_secret", idioma)
        if not inp:
            continue
        out = input(mensagens[idioma]["output_file"]).strip()
        verificar_duplicados(inp, out)

    elif escolha == "6":
        pasta = pedir_caminho_pasta("com .maFiles", "username.maFile ou steamid.maFile", idioma)
        if not pasta:
            continue
        renomear_mafiles_para_steamid(pasta)

    elif escolha == "7":
        pasta = pedir_caminho_pasta("com .maFiles", "username.maFile ou steamid.maFile", idioma)
        if not pasta:
            continue
        renomear_mafiles_para_username(pasta)

    elif escolha == "8":
        acc = pedir_caminho_arquivo("accounts.txt", "username:password", idioma)
        if not acc:
            continue
        generate_asf_configs(acc, "ASF_Configs")

    elif escolha == "9":
        acc = pedir_caminho_arquivo("accounts.txt", "username:password", idioma)
        if not acc:
            continue
        pasta = pedir_caminho_pasta("maFiles", "username.maFile ou steamid.maFile", idioma)
        if not pasta:
            continue
        out = input(mensagens[idioma]["output_file"]).strip()
        processar_completo(acc, pasta, out)

    elif escolha == "0":
        print(mensagens[idioma]["exit"])
        break

    else:
        print(mensagens[idioma]["invalid_option"])
