# -*- coding: utf-8 -*-
#!/home/fred/anaconda3/envs/Lana/bin/python3.7

# Pour pouvoir importer mes propres packages, même depuis un dossier parent
import sys
sys.path.insert(0, "/home/fred/Formation/Simplon/Exercisses/Projet_Mai2020/Projet_final")
from pack.scrapeur import Scrapeur
from pack.traitement import Traitement, concatenation, nettoyage
from pack.enregistrement import Enregistrement

import time
import datetime

debut = time.time()

# Instanciation des Classes
scrap = Scrapeur()
trait = Traitement()
enreg = Enregistrement()

tour = 0
cpt = 1
log = ""
while cpt > 0:
    tour += 1

    # Scraping
    sortie = scrap.scrap()

    # Traitement par articles
    cpt = 0
    total = 0
    for x in sortie.keys():
        total += 1

        # Contrôle des doublons avant traitement
        requete = enreg.read({"titre": sortie[x]["titre"],
                              "auteur": sortie[x]["auteur"]})

        if len(list(requete)) > 0:
            continue

        # Concaténation du texte à traiter pour la matrice de termes
        chaine = concatenation(sortie[x])

        # Calcul de la positivité
        sortie[x]["positivite"] = trait.positivite(chaine)

        # Calcul de l'objectivité
        sortie[x]["subjectivite"] = trait.subjectivite(chaine)

        # Conversion en liste de phrases (format attendu pour la création de la matrice de termes)
        parts = chaine.split(". ")

        # Nettoyage du texte
        liste_parts = []
        for part in parts:

            # Lemmatisation et Stemmatisation
            part = trait.lemmatisation(part)

            # Nettoyage
            part = nettoyage(part)

            liste_parts.append(part)


        # Matrice de termes
        mat = trait.matrice(liste_parts)
        mat = mat.to_dict()

        sortie[x]["matrice"] = mat


        # Date d'enregistrement
        now = datetime.datetime.fromtimestamp(time.time())  # date actuelle
        now = now.strftime('%Y-%m-%d-%H-%M-%S')

        sortie[x]["enregistre"] = now


        # Enregistrement
        cpt += 1
        enreg.insert(sortie[x], method="one")


    temps = time.time() - debut
    debut = time.time()
    temps = time.strftime('%Hh, %Mm %Ss', time.gmtime(temps))
    log += "Tour n° {} - Nb d'enregistrement : {}/{} articles, en : {} \n".format(tour, cpt, total, temps)
    #print(f"Tour n° {tour} - Nb d'enregistrement : {cpt}/{total} articles, en : {temps}")

# Enregistrement des logs dans un fichier
now = datetime.datetime.fromtimestamp(time.time())  # date actuelle
now = now.strftime('%Y-%m-%d %H:%M:%S')
now = str(now) + " ================================================= \n"
log = str(now) + log
with open("scrap.log", "a") as logs:
    logs.write(log)
