import requests

print("Bienvenue dans le système!")
print("Fait par alexis20114!")

send_message_channel = "https://discord.com/api/webhooks/1370578370315812894/0ie3cOsb5Yy2DAGGKfQ3LcP9b4eXrCSG6aHqh3znzSwCfzfrywgJ0xup5V1uvfMU7n6T"

def tool_choice():
    print("\n🔧 **Menu Modération** 🔧")
    print("[1] Avertir un membre")
    print("[2] Kick un membre")
    print("[3] Bannir un membre")

    choice = input("Tapez le numéro (correspondant à l'outil) : ")

    if choice == "1":
        tool_warning_sender()
    elif choice == "2":
        tool_kick_sender()
    elif choice == "3":
        tool_ban_sender()
    else:
        print("❌ Erreur : Choix invalide")
        tool_choice()

def tool_warning_sender():
    mod_username = input("Votre pseudo (modérateur) : ")
    the_player_real_user = input("Pseudo réel du joueur : ")
    the_player_username = input("Nom d'affichage : ")

    print("\n⚠ **Raisons d'avertissement**")
    print("[1] Trolling")
    print("[2] RDM")
    print("[3] Hrp")
    print("[4] Tué un modo en duty")
    print("[5] Hacker")
    print("[6] Insultes")
    print("[7] Autre")

    the_reason = input("Entrez la raison (tapez le numéro) : ")

    reasons = {
        "1": "Trolling",
        "2": "RDM",
        "3": "Hrp",
        "4": "Tué un modo en duty",
        "5": "Hacker",
        "6": "Insultes"
    }

    custom_reason = reasons.get(the_reason, "Raison inconnue")

    if the_reason == "7":
        custom_reason = input("Entrez la raison personnalisée : ")

    payload = {
        "content": f"🚨 **Avertissement envoyé** 🚨\n"
                   f"👮 **Modérateur :** {mod_username}\n"
                   f"📌 **Pseudo réel :** {the_player_real_user}\n"
                   f"🆔 **Nom d'affichage :** {the_player_username}\n"
                   f"⚠ **Raison :** {custom_reason}"
    }

    send_to_discord(payload)

def tool_kick_sender():
    mod_username = input("Votre pseudo (modérateur) : ")
    the_player_real_user = input("Pseudo réel du joueur : ")
    the_player_username = input("Nom d'affichage : ")
    kick_reason = input("Entrez la raison du kick : ")

    payload = {
        "content": f"🚨 **Kick effectué** 🚨\n"
                   f"👮 **Modérateur :** {mod_username}\n"
                   f"📌 **Pseudo réel :** {the_player_real_user}\n"
                   f"🆔 **Nom d'affichage :** {the_player_username}\n"
                   f"⚠ **Raison du kick :** {kick_reason}"
    }

    send_to_discord(payload)

def tool_ban_sender():
    mod_username = input("Votre pseudo (modérateur) : ")
    the_player_real_user = input("Pseudo réel du joueur : ")
    the_player_username = input("Nom d'affichage : ")
    ban_reason = input("Entrez la raison du bannissement : ")

    print("\n🔍 **Validation du bannissement en 10 étapes**")

    questions = [
        "Le joueur a-t-il déjà reçu des avertissements ?",
        "Le joueur a-t-il déjà été kické ?",
        "A-t-il causé des problèmes sérieux sur le serveur ?",
        "Le bannissement est-il basé sur une règle officielle ?",
        "Le joueur a-t-il eu l'occasion de s'expliquer ?",
        "La communauté est-elle d'accord avec cette décision ?",
        "Le joueur a-t-il enfreint une règle critique (ex: hacking) ?",
        "Un autre modérateur approuve ce bannissement ?",
        "Ce bannissement est-il temporaire ou définitif ?",
        "Le bannissement est bien justifié et réfléchi ?"
    ]

    validations = []
    confirmations = 0

    for question in questions:
        response = input(f"{question} (oui/non) : ").lower()
        validations.append(f"✔ {question}" if response == "oui" else f"❌ {question}")
        if response == "oui":
            confirmations += 1

    if confirmations >= 7:
        print("✅ Bannissement validé.")
        
        payload = {
            "content": f"🚨 **Bannissement effectué** 🚨\n"
                       f"👮 **Modérateur :** {mod_username}\n"
                       f"📌 **Pseudo réel :** {the_player_real_user}\n"
                       f"🆔 **Nom d'affichage :** {the_player_username}\n"
                       f"⚠ **Raison du bannissement :** {ban_reason}\n"
                       f"🔒 **Validation :** {confirmations}/10\n\n"
                       f"📝 **Validations détaillées :**\n" + "\n".join(validations)
        }

        send_to_discord(payload)
    else:
        print("❌ Bannissement annulé, validation insuffisante.")

def send_to_discord(payload):
    """Fonction pour envoyer un message à Discord avec gestion des erreurs"""
    try:
        response = requests.post(send_message_channel, json=payload)
        if response.status_code == 200:
            print("✅ Message envoyé avec succès !")
        else:
            print(f"❌ Erreur d’envoi ({response.status_code}) : {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"🚨 Erreur lors de la requête : {e}")

tool_choice()