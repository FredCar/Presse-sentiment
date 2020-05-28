import time
import datetime
import random
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from stop_words import get_stop_words
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import glob
import os


#==============================================
# \\\\\\\\\\\\\\ ---Fonctions--- //////////////
#==============================================
def connection():
    """ Connexion à la base de données  """
    # client = MongoClient("localhost", 27017) # Sans Docker
    client = MongoClient('base_mongo', username="root", password="example") # Avec Docker
    # client = MongoClient("base_mongo") # Test
    dbase = client["presse-sentiment"]
    collec = dbase["corpus"]

    return collec


def read(filtre={}):
    """
    Récupère les données de la base et les mets en DataFrame
    """
    collec = connection()

    requete = collec.find(filtre)

    df = pd.DataFrame(list(requete))

    df.sort_values(by=["date"], axis=0, inplace=True)
    # df = df.reset_index()

    return df


def date_heure(x):
    """
    retourne la date et l'heure concaténés
    """
    datetime = str(x["date"]) + "-" + str(x["heure"][:2])
    return datetime


def hh(x):
    """
    Prends la date-heure-min-sec
    retourne juste l'heure
    """
    liste = []
    for y in x:
        liste.append(str(y)[11:13])
    return liste


def limiteur(periode=30):
    """Pour filtrer par période"""
    df = read()

    df = df[df["date"] != "--"]
    df = df[df["heure"] != "--"]

    sec_par_jour = 60 * 60 * 24
    limit = time.time() - (sec_par_jour * periode)
    limit = datetime.datetime.fromtimestamp(limit)

    # TODO Le probleme vient de la limite de temps imposée et du fait que le scrap ne fonctionne pas:
    #  les articles sont trop anciens;
    #  Solution provisoire: refaire un export plus récent;
    #  solution définitive: automatiser le scraping
    limit = limit.strftime('%Y-%m-%d-%H')
    # End TODO

    df["date-heure"] = df.apply(date_heure, axis=1)
    df["date-heure"] = pd.to_datetime(df["date-heure"])

    # TODO Le problème ce concrétise ici: le DF retourné est vide
    df = df[df["date-heure"] > limit]
    # End TODO

    return df


def suppression():
    """Pour vider le dossier d'images"""
    for f in glob.glob("/src/static/images/*"):
        os.remove(f)


def graph_pos_jour(code=0):
    """
    Enregistre un graph de la positivite par jours
    """
    df = read()

    # df = df[df["positivite"] != 0]
    df = df[df["date"] != "--"]

    table = df.pivot_table(index=["date"], values="positivite")

    titre = "Positivité moyenne des articles de presse par jours"
    filename = "graph-jour" + str(code)
    ploteur(table.index, table.positivite, titre, filename)



def graph_pos_24_heure(code=0):
    """
    Enregistre ung raph de la positivite pour les dernières 24 heures
    """
    df = limiteur(periode=1)

    table = df.pivot_table(index=["date-heure"], values="positivite")
    table = table[1:]

    a = table.index.values
    table["hh"] = hh(a)

    titre = "Positivité moyenne des articles de presse des dernières 24 heures"
    filename = "graph-24-heure" + str(code)
    ploteur(table.hh, table.positivite, titre, filename)


def ploteur(x,y, titre="", filename="graph"):
    """
    Crée et enregistre les graphs
    """
    plt.figure(figsize=(18, 8))
    plt.plot(x, y, label="Courbe de positivite")
    plt.axhline(y=0, linestyle="--", c="red", label="Neutre")
    plt.title(titre, fontsize=28)
    plt.xticks(rotation=70, fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)

    chemin = "/src/static/images/" + filename
    plt.savefig(chemin, format="png")


def couleur_positivite(data):
    for x in data:
        data[x]["positivite"] = round((data[x]["positivite"]*100))
        pos = data[x]["positivite"]
        if pos >= 80:
            data[x]["couleur"] = "vert-5"
        elif pos >= 60:
            data[x]["couleur"] = "vert-4"
        elif pos >= 40:
            data[x]["couleur"] = "vert-3"
        elif pos >= 20:
            data[x]["couleur"] = "vert-2"
        elif pos > 0:
            data[x]["couleur"] = "vert-1"
        elif pos == 0:
            data[x]["couleur"] = "gris"
        elif pos >= -20:
            data[x]["couleur"] = "rouge-1"
        elif pos >= -40:
            data[x]["couleur"] = "rouge-2"
        elif pos >= -60:
            data[x]["couleur"] = "rouge-3"
        elif pos >= -80:
            data[x]["couleur"] = "rouge-4"
        else:
            data[x]["couleur"] = "rouge-5"

    return data

def trieur(periode=30, ascendant=False):
    """
    Renvois les données du DataFrame en dico
    """
    df = limiteur(periode)

    df.sort_values(by=["positivite"], axis=0, inplace=True, ascending=ascendant)
    data = df.T.to_dict()
    data = couleur_positivite(data)

    return data


def texteur(x):
    liste = []
    for y, z in x.items():
        for t in range(z):
            liste.append(y)
    random.shuffle(liste)
    chaine = " ".join(liste)

    return chaine


def stop_wordeur():
    french_stop_words = get_stop_words('french')
    ajout_stop_words = ["etre", "plus", "meme", "ca", "tre", "tres", "dont", "apre", "apres", "selon", "celui"]
    french_stop_words += ajout_stop_words

    return french_stop_words


def cloudeur(periode=1, positif=True, filename="cloud", code=0):
    french_stop_words = stop_wordeur()

    df = limiteur(periode)

    # Travailler à partir de la matrice de termes
    df["chaine_matrice"] = df["matrice"].apply(texteur)
    texte = df["chaine_matrice"].values
    titres_modif = list(texte)
    text = " ".join(titres_modif)

    wordcloud = WordCloud(stopwords=french_stop_words,
                          background_color="white")
    wordcloud.generate(text)

    plt.figure(figsize=(18, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    chemin = "src/static/images/" + filename + str(code)
    plt.savefig(chemin, format="png")


def top(df, limit=20):
    a = df.pivot_table(values="titre", index="auteur", aggfunc="count")
    b = df.pivot_table(values=["positivite"], index="auteur", aggfunc="mean")
    table_auteur = pd.concat([a, b], axis=1)
    table_auteur = table_auteur.sort_values(by="titre", ascending=False)
    table_auteur = table_auteur.head(limit)
    table_auteur = table_auteur.reset_index()

    table_auteur["positivite"] = round(table_auteur["positivite"] * 100, 2)

    top = table_auteur.T.to_dict()

    return top


def statistiques():
    df = read()

    data = {}
    data["total"] = df.shape[0]
    data["journaux"] = len(df["auteur"].unique())
    data["top20"] = top(df, 20)

    return data


# Similarité
def similaires(text, corpus):
    french_stop_words = stop_wordeur()

    # Entrainement du modèle TF-IDF
    tf_idf_chat = TfidfVectorizer(stop_words=french_stop_words)
    tf_phrases = tf_idf_chat.fit_transform(corpus)  # Matrice du corpus

    text = [text]
    tf_text = tf_idf_chat.transform(text)  # Matrice de la question utilisateur
    vals = cosine_similarity(tf_text, tf_phrases)  # Calcul de similarité

    ids = np.where(vals[0] > 0.25)  # ids des meilleurs scores
    ids = ids[0]  # On ne veut qu'une liste [.] pas [[.]]

    dico_id = {}  # Création d'un dico pour faciliter le tri
    for id in ids:
        dico_id[id] = vals[0][id]

    dico_id = sorted(dico_id.items(), key=lambda x: x[1], reverse=True)  # Liste de tuples triée par similarité : + -> -
    
    ids = []  # Liste des meilleurs ids triés
    for x in dico_id:
        ids.append(x[0])

    reponses = []
    if ids:
        reponses = ids
    else:
        reponses.append("Désolé, je ne trouve pas d'articles similaires.")

    return reponses