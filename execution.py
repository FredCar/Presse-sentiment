from pack.scrapeur import Scrapeur
from pack.traitement import Traitement
from pack.enregistrement import Enregistrement
import pprint
import time

debut = time.time()

# Instanciation des Classes
scrap = Scrapeur()
trait = Traitement()
enreg = Enregistrement()

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
        print(">>> Existe déjà !")
        print(sortie[x]["titre"])
        print("---------------------------------------")
        continue

    # Concaténation du texte à traiter pour la matrice de termes
    chaine = ""
    chaine += sortie[x]["titre"] + " "
    if sortie[x]["extrait"][:20] == sortie[x]["texte"][:20]:
        chaine += sortie[x]["texte"]
    else:
        chaine += sortie[x]["extrait"] + " "
        chaine += sortie[x]["texte"]

    # Conversion en liste de phrases (format attendu pour la création de la matrice de termes)
    parts = chaine.split(". ")

    # Nettoyage du texte
    liste_parts = []
    for part in parts:

        # Lemmatisation
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
    print("============Enregistré=================")
    print(sortie[x]["titre"])
    print("=======================================")


temps = round(time.time() - debut, 2)
print("Nb d'enregistrement :", cpt, "/", total, "articles, en :", temps, "secondes")
#pprint.pprint(sortie)

