# -*- coding: utf-8 -*-

# Pour pouvoir importer mes propres packages, même depuis un dossier parent
import sys
sys.path.insert(0, "/src")

from pack.scraping import Scrapeur
from pack.traitement import Traitement, concatenation, nettoyage
from pack.enregistrement import Enregistrement
from pack.spaceur import spaceur, read

import time
import datetime

debut = time.time()

# Création du log de début de cycle
now = datetime.datetime.fromtimestamp(time.time())  # date actuelle
now = now.strftime('%Y-%m-%d %H:%M:%S')
log = str(now) + " ================================================= \n"

# Instanciation des Classes
enreg = Enregistrement()
    # Ecriture du 1er log dans un fichier
enreg.logeur(log)
scrap = Scrapeur()
trait = Traitement()



tour = 0
cpt = 1
# Tant qu'il trouve de nouveaux articles
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

        liste_parts = []
        for part in parts:
            # Lemmatisation et Stemmatisation
            part = trait.lemmatisation_stemmatisation(part)

            # Nettoyage du texte
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
        enreg.insert(sortie[x]) 
 
        # Traitement des noms propres
        doc = trait.extracteur_de_nom(chaine)

        filtre = {"titre": sortie[x]["titre"],
                  "auteur": sortie[x]["auteur"]}
        df = read(filtre, collec="corpus")
        
        nouveau, existant = spaceur(doc, df) 

        # # Décommenter pour afficher les logs de traitement des noms propres
        # now = datetime.datetime.fromtimestamp(time.time())  # date actuelle
        # now = now.strftime('%Y-%m-%d %H:%M:%S')
        # log = "{} >> {} === New : {} === Old : {} \n".format(now, df["_id"].values[0], nouveau, existant)
        # enreg.logeur(log)



    temps = time.time() - debut
    debut = time.time()
    temps = time.strftime('%Hh, %Mm %Ss', time.gmtime(temps))
    log = "Tour n° {} - Nb d'enregistrement : {}/{} articles, en : {} \n".format(tour, cpt, total, temps)
    enreg.logeur(log)

# Création du log de fin de cycle
now = datetime.datetime.fromtimestamp(time.time())  # date actuelle
now = now.strftime('%Y-%m-%d %H:%M:%S')
log = "Fin" + " ==============================================" + str(now) + "\n"
enreg.logeur(log)
