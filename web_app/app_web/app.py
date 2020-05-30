from flask import Flask, render_template, request
import datetime
import random

# Pour pouvoir importer ses propres packages, même depuis un dossier parent
import sys
sys.path.insert(0, "/src") # Avec Docker
from pack.fonctions import *


# Variables utilisées pour le tri
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
    suppression() # Pour vider le dossier d'images

    # Création d'un code aléatoire à concaténer au nom des images pour duper le cache des navigateurs
    code = {}
    code["jour"] = random.randint(0, 100000)
    code["heure"] = random.randint(0, 100000)

    graph_pos_jour(code["jour"])
    graph_pos_24_heure(code["heure"])

    return render_template("pages/graph.html", code=code)


@app.route("/classement")
def classement():
    data = trieur(periode=1)

    return render_template("pages/classement.html", data=data, choix_periode=choix_periode,
                           choix_ordre_pos=choix_ordre_pos)


@app.route("/classement", methods=["POST"])
def classement_actif():
    periode = int(request.form["periode"])
    ascendant = bool(int(request.form["asc"]))

    data = trieur(periode, ascendant)
    data["periode"] = periode
    data["ascendant"] = ascendant

    return render_template("pages/classement.html", data=data, choix_periode=choix_periode,
                           choix_ordre_pos=choix_ordre_pos)


@app.route("/articles_similaires", methods=["GET"])
def classement_similaire():
    df = read()
    df["chaine_matrice"] = df["matrice"].apply(texteur)
    corpus = df["chaine_matrice"].values

    retour = request.values["id"]
    df["_id"] = df["_id"].astype(str)
    texte = df[df._id == retour]
    texte = str(texte["chaine_matrice"].values)

    reponse = similaires(texte, corpus)[1:]
    reponse = df.iloc[reponse].T.to_dict()
    reponse = couleur_positivite(reponse)

    # TODO Rediriger vers une page spécifique ??
    return render_template("pages/classement.html", data=reponse, choix_periode=choix_periode,
                           choix_ordre_pos=choix_ordre_pos)


@app.route("/nuage")
def nuage():
    suppression() # Pour vider le dossier d'images

    code = {}
    code["cloud"] = random.randint(0, 100000)

    data = {}
    periode = 1
    data["periode"] = periode

    cloudeur(periode, code=code["cloud"])

    return render_template("pages/nuage.html", data=data, choix_periode=choix_periode, code=code)


@app.route("/nuage", methods=["POST"])
def nuage_actif():
    suppression() # Pour vider le dossier d'images

    code = {}
    code["cloud"] = random.randint(0, 100000)

    data = {}
    periode = int(request.form["periode"])
    data["periode"] = periode

    cloudeur(periode, code=code["cloud"])

    return render_template("pages/nuage.html", data=data, choix_periode=choix_periode, code=code)


@app.route("/statistiques")
def stat():
    data = statistiques()

    return render_template("pages/stat.html", data=data)


########### Exécution ###########
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # TODO Supprimer Debug mode