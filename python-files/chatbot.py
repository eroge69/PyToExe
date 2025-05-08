def chatbot():
    print("Salut ! Je suis un mini chatbot pour Bonus Life.")
    while True:
        question = input("Pose ta question (ou 'bye' pour quitter) : ").lower()
        if question == 'bye':
            print("À bientôt !")
            break
        elif 'concentration' in question:
            print("Nos compléments pour la concentration peuvent améliorer ta clarté mentale et ta réactivité.")
        elif 'energie' in question:
            print("Pour un boost d'énergie durable pendant tes longues sessions de jeu, essaie nos produits énergisants.")
        elif 'endurance' in question:
            print("Nos formules pour l'endurance t'aideront à rester au top de ta forme plus longtemps.")
        elif 'panier' in question:
            print("Le panier te permet de visualiser et de gérer les articles que tu souhaites acheter.")
        elif 'compte' in question or 'connexion' in question:
            print("La section compte te permet de te connecter, de gérer tes informations et de voir tes commandes.")
        elif 'paramètres' in question:
            print("Dans les paramètres, tu peux personnaliser ton expérience, comme choisir le thème ou gérer les notifications.")
        elif 'commentaire' in question or 'avis' in question:
            print("La section commentaires permet aux autres joueurs de partager leurs expériences avec nos produits.")
        else:
            print("Je ne suis pas sûr de comprendre ta question. Peux-tu reformuler ?")

if __name__ == "__main__":
    chatbot()