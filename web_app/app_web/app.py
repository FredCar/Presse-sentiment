from flask import Flask, render_template, request
import datetime

# Pour pouvoir importer mes propres packages, même depuis un dossier parent
import sys
sys.path.insert(0, "/home/fred/Formation/Simplon/Exercisses/Projet_Mai2020/Projet_final/web_app") #Sans Docker
# sys.path.insert(0, "/src") # Avec Docker
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

    graph_pos_jour()
    graph_pos_24_heure()

    return render_template("pages/graph.html")





###########################################""


@app.route("/classement")
def classement():
    data = trieur(periode=1)


    nb_pages = int(len(data)/100)

    return render_template("pages/classement.html", data=data, choix_periode=choix_periode,
                           choix_ordre_pos=choix_ordre_pos, nb_pages=nb_pages)


@app.route("/classement", methods=["POST"])
def classement_actif():
    periode = int(request.form["periode"])
    ascendant = int(request.form["asc"])
    ascendant = bool(ascendant)

    data = trieur(periode, ascendant)
    data["periode"] = periode
    data["ascendant"] = ascendant

    return render_template("pages/classement.html", data=data, choix_periode=choix_periode, choix_ordre_pos=choix_ordre_pos)


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
    return render_template("pages/classement.html", data=reponse, choix_periode=choix_periode, choix_ordre_pos=choix_ordre_pos)


###############################################################"



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