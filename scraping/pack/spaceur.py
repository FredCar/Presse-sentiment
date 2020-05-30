# Pour pouvoir importer mes propres packages, même depuis un dossier parent
import sys
sys.path.insert(0, "/src") # Avec Docker
from pack.traitement import Traitement

from pymongo import MongoClient
import pandas as pd


client = MongoClient('base_mongo', username="root", password="example")
dbase  = client["presse-sentiment"]
collec_nom = dbase["nom_propre"]


def connection():
    """ Connexion à la base de données  """
    client = MongoClient('base_mongo', username="root", password="example") # Avec Docker
    dbase = client["presse-sentiment"]
    collec = dbase["corpus"]

    return collec


def read(filtre={}):
    """ Récupère les données de la base et les mets en DataFrame """
    collec = connection()
    requete = collec.find(filtre)

    df = pd.DataFrame(list(requete))
    # df.sort_values(by=["date"], axis=0, inplace=True)

    return df


def spaceur(doc, df):
    """ Prend un article en entrée, le traite avec SpaCy,
    et enregistre les noms propres dans une base de données Mongodb """    
    nouveau = 0
    existant = 0
    
    for token in doc: # Un tour pour chaque mot
        if token.pos_ == "PROPN": # Vérifi que ce soit bien un Nom Propre
            requete = collec_nom.find({"nom": token.lemma_}) # Vérifi si il est déjà dans la base
            
            if len(list(requete)) != 0: # Il y est déjà
                existant += 1
                
                # On récupère la liste des articles ou il est déjà présent
                res = collec_nom.find({"nom": token.lemma_}, {"articles": 1, "_id": 0}) 
                liste_ids = []
                for r in res:
                    for d in r["articles"]:                        
                        for k in d.items():                            
                            if k[0] == "id":
                                liste_ids.append(k[1])                              
                liste_ids = list(set(liste_ids)) # On supprime les doublons
                
                if df["_id"].values[0] in liste_ids: # Si l'article est déjà répertorié
                    # Incrémenter "nb_occurence" au lieu d'ajouter une entrée
                    res = collec_nom.find_one({"nom": token.lemma_, "articles.id": df["_id"].values[0]})
                    for u in res["articles"]:
                        if u["id"] == df["_id"].values[0]:
                            u["nb_occurence"] += 1
                                           
                    collec_nom.update_one({"nom": token.lemma_, "articles.id": df["_id"].values[0]},
                                          {"$set": {"articles": res["articles"]}})
                else: # Si cet article n'est pas encore répertorié
                    # Ajouter l'entrée
                    data = {"id": df["_id"].values[0], "poistivite": df["positivite"].values[0], "nb_occurence": 1} # On ajoute les nouvelles données
                    collec_nom.update_one({"nom": token.lemma_},
                                        {"$addToSet": {"articles": data}})

            else: # Ce nom n'est pas encore dans la base
                nouveau += 1
                data = {"nom": token.lemma_,
                        "articles": [{"id": df["_id"].values[0], "poistivite": df["positivite"].values[0], "nb_occurence": 1}]}
                collec_nom.insert_one(data) # On l'enregistre
    return nouveau, existant

# def spaceur(doc):
#     """ Prend un article en entrée, le traite avec SpaCy,
#     et enregistre les noms propres dans une base de données Mongodb """    
#     nouveau = 0
#     existant = 0
    
#     for token in doc: # Un tour pour chaque mot
#         if token.pos_ == "PROPN": # Vérifi que ce soit bien un Nom Propre
#             requete = collec_nom.find({"nom": token.lemma_}) # Vérifi si il est déjà dans la base
            
#             if len(list(requete)) != 0: # Il y est déjà
#                 existant += 1
                
#                 # On récupère la liste des articles ou il est déjà présent
#                 res = collec_nom.find({"nom": token.lemma_}, {"articles": 1, "_id": 0}) 
#                 liste_ids = []
#                 for r in res:
#                     for d in r["articles"]:                        
#                         for k in d.items():                            
#                             if k[0] == "id":
#                                 liste_ids.append(k[1])                              
#                 liste_ids = list(set(liste_ids)) # On supprime les doublons
                
#                 # TODO Il y a erreur il n'y a pas d'id à comparer
#                 if df["_id"] in liste_ids: # Si l'article est déjà répertorié
#                     # Incrémenter "nb_occurence" au lieu d'ajouter une entrée
#                     res = collec_nom.find_one({"nom": token.lemma_, "articles.id": df["_id"]})
#                     for u in res["articles"]:
#                         if u["id"] == df["_id"]:
#                             u["nb_occurence"] += 1
                                           
#                     collec_nom.update_one({"nom": token.lemma_, "articles.id": df["_id"]},
#                                       {"$set": {"articles": res["articles"]}})
#                 else: # Si cet article n'est pas encore répertorié
#                 # Ajouter l'entrée
#                 data = {"id": df["_id"], "poistivite": df["positivite"], "nb_occurence": 1} # On ajoute les nouvelles données
#                 collec_nom.update_one({"nom": token.lemma_},
#                                     {"$addToSet": {"articles": data}})

#             else: # Ce nom n'est pas encore dans la base
#                 nouveau += 1
#                 data = {"nom": token.lemma_,
#                         "articles": [{"id": df["_id"], "poistivite": df["positivite"], "nb_occurence": 1}]}
#                 collec_nom.insert_one(data) # On l'enregistre
#     return nouveau, existant