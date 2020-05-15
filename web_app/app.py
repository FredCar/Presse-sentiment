from flask import Flask, render_template, request
import time
import datetime

from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import base64

import re
from stop_words import get_stop_words
from wordcloud import WordCloud

# Pour pouvoir importer mes propres packages, même depuis un dossier parent
import sys
sys.path.insert(0, "/home/fred/Formation/Simplon/Exercisses/Projet_Mai2020/Projet_final")
from pack.traitement import concatenation, nettoyage


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


def limiteur(limite=""):
    df = read()

    df = df[df["date"] != "--"]
    df = df[df["heure"] != "--"]

    df["date-heure"] = df.apply(date_heure, axis=1)

    hier = datetime.datetime.fromtimestamp(time.time() - (60 * 60 * 24))  # date d'hier
    hier = hier.strftime('%Y-%m-%d-%H')

    df["date-heure"] = pd.to_datetime(df["date-heure"])
    df = df[df["date-heure"] > hier]

    return df


def graph_pos_24_heure():
    """
    Enregistre ung raph de la positivite pour les dernières 24 heures
    """
    df = limiteur()

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


def trieur(ascendant=False):
    """
    Renvois les données du DataFrame en dico
    """
    df = limiteur()

    df.sort_values(by=["positivite"], axis=0, inplace=True, ascending=ascendant)

    data = df.T.to_dict()

    return data


def cloudeur(filename="cloud"):
    french_stop_words = get_stop_words('french')
    df = limiteur()

    texte = df.apply(concatenation, axis=1)
    titres_modif = list(map(nettoyage, texte))
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

    # TODO Selection de date ou de période
    data = trieur()

    return render_template("pages/classement.html", data=data)


@app.route("/nuage")
def nuage():
    cloudeur()

    return render_template("pages/nuage.html")


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