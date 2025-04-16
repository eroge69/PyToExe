import random
import csv

fichier = "resultats_des_lancers.csv"
total_essais = 1000
lancers_par_essai = 10000000000
total_3 = 0

with open(fichier, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Essai", "Nombre de 3 obtenus"])

    for essai in range(1, total_essais + 1):
        lancers = [random.randint(1, 6) for _ in range(lancers_par_essai)]
        nb_de_3 = lancers.count(3)
        total_3 += nb_de_3
        writer.writerow([essai, nb_de_3])

        # Affichage du pourcentage d'avancement
        pourcentage = (essai / total_essais) * 100
        print(f"Essai {essai}/{total_essais} terminé ({pourcentage:.1f}%)")

# Calcul et affichage de la moyenne
moyenne = total_3 / total_essais
print(f"\nMoyenne de '3' obtenus par essai : {moyenne:.2f}")
print("Fichier CSV créé avec succès !")
