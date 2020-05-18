from flask import Flask, render_template, request
import time
import datetime
import random
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import base64
import re
from stop_words import get_stop_words
from wordcloud import WordCloud

# # Pour pouvoir importer mes propres packages, même depuis un dossier parent
# import sys
# sys.path.insert(0, "/home/fred/Formation/Simplon/Exercisses/Projet_Mai2020/Projet_final")
# from pack.traitement import concatenation, nettoyage


# Connexion à la base de données
client = MongoClient("localhost", 27017)
dbase  = client["presse-sentiment"]
collec = dbase["corpus"]


#==============================================
# \\\\\\\\\\\\\\ ---Fonctions--- //////////////
#==============================================
def read(collec=collec, filtre={}):
    """
    Récupère les données de la base et les mets en DataFrame
    """
    requete = collec.find(filtre)

    df = pd.DataFrame(list(requete))

    df.sort_values(by=["date"], axis=0, inplace=True)
    df = df.reset_index()

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
    limit = limit.strftime('%Y-%m-%d-%H')

    df["date-heure"] = df.apply(date_heure, axis=1)
    df["date-heure"] = pd.to_datetime(df["date-heure"])
    df = df[df["date-heure"] > limit]

    return df


def graph_pos_jour():
    """
    Enregistre un graph de la positivite par jours
    """
    df = read()

    # df = df[df["positivite"] != 0]
    df = df[df["date"] != "--"]

    table = df.pivot_table(index=["date"], values="positivite")

    titre = "Positivité moyenne des articles de presse par jours"
    filename = "graph-jour"
    ploteur(table.index, table.positivite, titre, filename)



def graph_pos_24_heure():
    """
    Enregistre ung raph de la positivite pour les dernières 24 heures
    """
    df = limiteur(periode=1)

    table = df.pivot_table(index=["date-heure"], values="positivite")
    table = table[1:]

    a = table.index.values
    table["hh"] = hh(a)

    titre = "Positivité moyenne des articles de presse des dernières 24 heures"
    filename = "graph-24-heure"
    ploteur(table.hh, table.positivite, titre, filename)


def ploteur(x,y, titre="", filename="graph"):
    """
    Crée et enregistre les graphs
    """
    plt.figure(figsize=(18, 8))
    plt.plot(x, y, label="Coubre de positivite")
    plt.axhline(y=0, linestyle="--", c="red", label="Neutre")
    plt.title(titre, fontsize=28)
    plt.xticks(rotation=70, fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)

    chemin = "static/images/" + filename
    plt.savefig(chemin, format="png")


def trieur(periode=30, ascendant=False):
    """
    Renvois les données du DataFrame en dico
    """
    df = limiteur(periode)
    df.sort_values(by=["positivite"], axis=0, inplace=True, ascending=ascendant)
    data = df.T.to_dict()

    for x in data:
        pos = data[x]["positivite"]
        if pos >= 0.8:
            data[x]["couleur"] = "vert-5"
        elif pos >= 0.6:
            data[x]["couleur"] = "vert-4"
        elif pos >= 0.4:
            data[x]["couleur"] = "vert-3"
        elif pos >= 0.2:
            data[x]["couleur"] = "vert-2"
        elif pos > 0:
            data[x]["couleur"] = "vert-1"
        elif pos == 0:
            data[x]["couleur"] = "gris"
        elif pos >= -0.2:
            data[x]["couleur"] = "rouge-1"
        elif pos >= -0.4:
            data[x]["couleur"] = "rouge-2"
        elif pos >= -0.6:
            data[x]["couleur"] = "rouge-3"
        elif pos >= -0.8:
            data[x]["couleur"] = "rouge-4"
        else:
            data[x]["couleur"] = "rouge-5"

    return data


def texteur(x):
    liste = []
    for y, z in x.items():
        for t in range(z):
            liste.append(y)
    random.shuffle(liste)
    chaine = " ".join(liste)

    return chaine


def cloudeur(periode=1, positif=True, filename="cloud"):
    french_stop_words = get_stop_words('french')
    ajout_stop_words = ["etre", "plus", "meme", "ca", "tre", "tres", "dont", "apre", "apres", "selon", "celui"]
    french_stop_words += ajout_stop_words

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

    chemin = "static/images/" + filename
    plt.savefig(chemin, format="png")


def statistiques():
    df = read()
    data = {}
    data["total"] = df.shape[0]
    data["journaux"] = len(df["auteur"].unique())

    return data


choix_periode = [("24 heures", 1),
                 ("48 heures", 2),
                 ("une semaine", 7),
                 ("deux semaine", 14),
                 ("un mois", 30),
                 ("deux mois", 60),
                 ("trois mois", 90),
                 ("six mois", 182),
                 ("un an", 365),
                 ("tout", 100000)]

choix_ordre_pos = [("Les plus positifs en premier", 0),
                   ("Les plus négatifs en premier", 1)]


#==============================================
# \\\\\\\\\\\\\\ ---Flask app--- //////////////
#==============================================
app = Flask(__name__)


@app.route("/")
def home():
    data = {}
    data["date"] = datetime.datetime.now().strftime('%d-%m-%Y')
    data["heure"] = datetime.datetime.now().strftime('%H:%M:%S')
    return render_template("pages/index.html", data=data)




@app.route("/graph/")
def graph():

    graph_pos_jour()
    graph_pos_24_heure()

    return render_template("pages/graph.html")




@app.route("/classement")
def classement():
    data = trieur(periode=1)

    return render_template("pages/classement.html", data=data, choix_periode=choix_periode, choix_ordre_pos=choix_ordre_pos)


@app.route("/classement", methods=["POST"])
def classement_actif():
    periode = int(request.form["periode"])
    ascendant = int(request.form["asc"])
    ascendant = bool(ascendant)
    data = trieur(periode, ascendant)
    data["periode"] = periode
    data["ascendant"] = ascendant

    return render_template("pages/classement.html", data=data, choix_periode=choix_periode, choix_ordre_pos=choix_ordre_pos)


@app.route("/nuage")
def nuage():
    data = {}
    data["periode"] = ""
    return render_template("pages/nuage.html", data=data, choix_periode=choix_periode)


@app.route("/nuage", methods=["POST"])
def nuage_actif():
    data = {}
    periode = int(request.form["periode"])
    data["periode"] = periode

    cloudeur(periode)

    return render_template("pages/nuage.html", data=data, choix_periode=choix_periode)




@app.route("/statistiques")
def stat():
    data = statistiques()

    return render_template("pages/stat.html", data=data)


@app.route("/about")
def a_propos():
    return render_template("pages/about.html")


##########################
if __name__ == "__main__":
    app.run(debug=True)