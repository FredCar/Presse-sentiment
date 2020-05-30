from pymongo import MongoClient
import pandas as pd
import spacy


nlp = spacy.load('fr_core_news_md')


client = MongoClient('base_mongo', username="root", password="example")
dbase  = client["presse-sentiment"]
collec = dbase["corpus"]
collec_nom = dbase["nom_propre"]


def concatenation(sortie):
    """Concaténation du texte à traiter pour la matrice de termes"""
    chaine = ""
    chaine += sortie["titre"] + " "
    if sortie["extrait"][:20] == sortie["texte"][:20]:
        chaine += sortie["texte"]
    else:
        chaine += sortie["extrait"] + " "
        chaine += sortie["texte"]

    return chaine


def logeur(log):
    """Écrit les logs dans un fichier"""
    with open("/src/denommeur.log", "a") as logs:
        logs.write(log)


def spaceur(phrase, df):
    """ Prend un article en entrée, le traite avec SpaCy,
    et enregistre les noms propres dans une base de données Mongodb """
    doc = nlp(phrase) # Traitement avec SpaCy
    
    nouveau = 0
    existant = 0
    
    for token in doc: # Un tour pour chaque mot
        if token.pos_ == "PROPN": # Vérifi que ce soit bien un Nom Propre
            requete = collec_nom.find({"nom": token.lemma_}) # Vérifi si il est déjà dans la base
            
            if len(list(requete)) != 0: # Il y est déjà
                existant += 1
                
                res = collec_nom.find({"nom": token.lemma_}, {"articles": 1, "_id": 0}) # On récupère la liste des articles ou il est déjà présent
                
                liste_ids = []
                for r in res:
                    for d in r["articles"]:                        
                        for k in d.items():                            
                            if k[0] == "id":
                                liste_ids.append(k[1])
                                
                liste_ids = list(set(liste_ids))
                
                if df["_id"] in liste_ids: # Si l'article est déjà répertorié
                    # Incrémenter "nb_occurence" au lieu d'ajouter une entrée
                    res = collec_nom.find_one({"nom": token.lemma_, "articles.id": df["_id"]})
                    for u in res["articles"]:
                        if u["id"] == df["_id"]:
                            u["nb_occurence"] += 1
                                           
                    collec_nom.update_one({"nom": token.lemma_, "articles.id": df["_id"]},
                                      {"$set": {"articles": res["articles"]}})
                else:
                     # Ajouter l'entrée
                    data = {"id": df["_id"], "poistivite": df["positivite"], "nb_occurence": 1} # On ajoute les nouvelles données
                    collec_nom.update_one({"nom": token.lemma_},
                                      {"$addToSet": {"articles": data}})

            else: # Ce nom n'est pas encore dans la base
                nouveau += 1
                data = {"nom": token.lemma_,
                        "articles": [{"id": df["_id"], "poistivite": df["positivite"], "nb_occurence": 1}]}
                collec_nom.insert_one(data) # On l'enregistre
    return nouveau, existant


if __name__ == "__main__":
    requete = collec.find()

    df = pd.DataFrame(list(requete))

    df.sort_values(by=["date"], axis=0, inplace=True)
    df = df.reset_index()

    taille = df.shape[0]
    nb = 0

    while nb < taille:

        df_part = df[nb:nb+10]
        df_part = df_part.T.to_dict()
        
        logeur("{} > à > {} >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format(nb, nb+10))

        for x in df_part: # Un tour par article
            y = concatenation(df_part[x])
            nouveau, existant = spaceur(y, df_part[x])
            logeur(">> {} === New : {} === Old : {} \n".format(df_part[x]["_id"], nouveau, existant))

        nb += 10