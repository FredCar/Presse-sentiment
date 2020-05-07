from pack.scrapeur import Scrapeur
from pack.traitement import Traitement
from pack.enregistrement import Enregistrement
import pprint


# Instanciation des Classes
scrap = Scrapeur()
trait = Traitement()
enreg = Enregistrement()

# Scraping
sortie = scrap.scrap()

for x in sortie.keys():
    # Concaténation du texte à traiter pour la matrice de termes
    chaine = ""
    chaine += sortie[x]["titre"] + " "
    if sortie[x]["extrait"][:20] == sortie[x]["texte"][:20]:
        chaine += sortie[x]["texte"]
    else:
        chaine += sortie[x]["extrait"] + " "
        chaine += sortie[x]["texte"]

    parts = chaine.split(". ")

    # Nettoyage du texte
    liste_parts = []
    for part in parts:
        part = trait.nettoyage(part)
        liste_parts.append(part)

    # Matrice de termes
    mat = trait.matrice(liste_parts)
    mat = mat.to_dict()

    sortie[x]["matrice"] = mat

    # Contrôle des doublons avant enregistrement
    requete = enreg.read({"titre": sortie[x]["titre"],
                          "auteur": sortie[x]["auteur"]})

    # Enregistrement
    if len(list(requete)) > 0:
        print(">>> Existe déjà !")
        print(sortie[x]["titre"])
        print("---------------------------------------")
    else:
        enreg.insert(sortie[x], method="one")
        print("============Enregistré=================")
        pprint.pprint(sortie[x])
        print("=======================================")


#pprint.pprint(sortie)

