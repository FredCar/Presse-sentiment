from pack.scrapeur import Scrapeur
from pack.traitement import Traitement
from pack.enregistrement import Enregistrement

import time

debut = time.time()

# Instanciation des Classes
scrap = Scrapeur()
trait = Traitement()
enreg = Enregistrement()

tour = 0
cpt = 1
while cpt > 0:
    tour += 1
    # Scraping
    # liste_editeur = scrap.editeurs
    sortie = scrap.scrap()

    # Traitement par articles
    cpt = 0
    total = 0
    for x in sortie.keys():
        total += 1

        # Contrôle de l'éditeur pour ne garder que les données complètes
        # if sortie[x]["auteur"].lower() in liste_editeur:
        #     pass
        # else:
        #     print(">>>", sortie[x]["auteur"], "<<<")
        #     print("Pas dans la liste des éditeurs")
        #     continue

        # Contrôle des doublons avant traitement
        requete = enreg.read({"titre": sortie[x]["titre"],
                              "auteur": sortie[x]["auteur"]})

        if len(list(requete)) > 0:
            # print(">>> Existe déjà !")
            # print(total, "/", sortie[x]["auteur"])
            # print(sortie[x]["titre"])
            # print("---------------------------------------")
            continue

        # Concaténation du texte à traiter pour la matrice de termes
        chaine = trait.concatenation(sortie[x])

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
            part = trait.nettoyage(part)

            # TODO Stematisaton utile ou pas ?
            # print(trait.stematisation(part))
            # print("----------------------------------------------------")
            # print(part)
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            liste_parts.append(part)


        # Matrice de termes
        mat = trait.matrice(liste_parts)
        mat = mat.to_dict()

        sortie[x]["matrice"] = mat


        # Enregistrement
        cpt += 1
        enreg.insert(sortie[x], method="one")
        # print("============Enregistré=================")
        # print(total, "/", sortie[x]["auteur"])
        # print(sortie[x]["titre"])
        # print("=======================================")

        # TODO Enregistrement des logs dans un fichier

    temps = time.time() - debut
    temps = time.strftime('%Hh, %Mm %Ss', time.gmtime(temps))
    print("Tour n°", tour, "- Nb d'enregistrement :", cpt, "/", total, "articles, en :", temps)

