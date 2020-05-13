from flask import Flask, render_template, request
import datetime

from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import base64


client = MongoClient("localhost", 27017)
dbase  = client["test_presse"]
collec = dbase["test"]


#==============================================
# \\\\\\\\\\\\\\ ---Fonctions--- //////////////
#==============================================
def read(collec=collec, filtre={}):
    """
    Récupère les données de la base et les mets en DataFrame
    """
    requete = collec.find(filtre)

    df = pd.DataFrame(list(requete))
    df = df.dropna(axis=0)

    # df.date = pd.to_datetime(df.date)
    # df.pos = pd.to_numeric(df.positivite)
    # df.subj = pd.to_numeric(df.subjectivite)
    df.sort_values(by=["date"], axis=0, inplace=True)
    df.reset_index()

    return df


def graph_pos_jour():
    df = read()

    df = df[df["positivite"] != 0]
    df = df[df["date"] != "--"]

    df = df.pivot_table(index=["date"], values="positivite")


    plt.figure(figsize=(18, 8))
    plt.plot(df.index, df.positivite, label="Coubre de positivite")
    plt.axhline(y=0, linestyle="--", c="red", label="Neutre")
    plt.title("Positivité moyenne des articles de presse par jours")
    plt.xticks(rotation=70)
    plt.legend()

    plt.savefig("static/graph-jour", format="png")


def date_heure(x):
    a = str(x["date"]) + "-" + str(x["heure"][:2])
    return a


# TODO Limiter aux 24 dernières heures
def graph_pos_heure():
    df = read()

    df = df[df["positivite"] != 0]

    df["date-heure"] = df.apply(date_heure, axis=1)


    df = df.pivot_table(index=["date-heure"], values="positivite")
    df = df[1:]

    plt.figure(figsize=(18, 8))
    plt.plot(df.index, df.positivite, label="Coubre de positivite")
    plt.axhline(y=0, linestyle="--", c="red", label="Neutre")
    plt.title("Positivité moyenne des articles de presse par heures")
    plt.xticks(rotation=70)
    plt.legend()

    plt.savefig("static/graph-heure", format="png")


def trieur(ascendant=False):
    df = read()

    df.sort_values(by=["positivite"], axis=0, inplace=True, ascending=ascendant)

    data = {}
    for id in df.index:
        data[id] = {}
        data[id]["titre"] = df.loc[id]["titre"]
        data[id]["lien"] = df.loc[id]["lien"]
        data[id]["extrait"] = df.loc[id]["extrait"]
        data[id]["positivite"] = df.loc[id]["positivite"]
        data[id]["auteur"] = df.loc[id]["auteur"]
        data[id]["date"] = df.loc[id]["date"]
        data[id]["heure"] = df.loc[id]["heure"]

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
    graph_pos_heure()

    return render_template("pages/graph.html")


@app.route("/classement")
def classement():
    data = trieur()

    return render_template("pages/classement.html", data=data)


@app.route("/about")
def a_propos():
    return render_template("pages/about.html")


##########################
if __name__ == "__main__":
    app.run(debug=True)