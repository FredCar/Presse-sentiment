import requests
from bs4 import BeautifulSoup as bs
import numpy as np

class Scrapeur:
    """
    Classe chargée d'éxécuter le scrapping
    """

    def __init__(self, lien="https://news.google.com/topstories?hl=fr&gl=FR&ceid=FR%3Afr"):
        self.lien = lien


    def scrap(self):
        page_response = requests.get(self.lien)
        soupe = bs(page_response.content, "html.parser")

        blocs = soupe.find_all("article", {"jscontroller": "mhFxVb"})

        sortie = {}
        compteur = 0
        for bloc in blocs:
            compteur += 1
            titre = bloc.find("a", {"class": "DY5T1d"}).text

            auteur = bloc.find("a", {"class": "wEwyrc AVN2gc uQIVzc Sksgp"}).text

            temps = bloc.find("time")
            if temps:
                temps = temps["datetime"][:-1]
                temps = temps.replace("T", " ").split()
                date = temps[0]
                heure = temps[1]
            else:
                date = "--"
                heure = "--"

            extrait = bloc.find("span", {"class": "xBbh9"})
            if extrait:
                extrait = extrait.text
            else:
                extrait = "--"

            lien_article = bloc.find("a", {"class": "DY5T1d"})["href"][1:]
            lien_article = "https://news.google.com" + lien_article


            if auteur.lower() == "le monde":
                texte = self.le_monde(lien_article)
            elif auteur.lower() == "le figaro":
                texte = self.le_figaro(lien_article)
            elif auteur.lower() == "franceinfo":
                texte = self.france_info(lien_article)
            else:
                texte = "--"


            sortie[compteur] = {"titre": titre,
                                "auteur": auteur,
                                "date": date,
                                "heure": heure,
                                "extrait": extrait,
                                "lien": lien_article,
                                "texte": texte}

        return sortie


    def le_monde(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        blocs_2 = soupe.find("section", {"class": "article__wrapper"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p", {"class": "article__paragraph"})
        texte = ""
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def le_figaro(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        blocs_2 = soupe.find("div", {"class": "css-1lz652c ey7xkwt0"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p", {"class": "css-s6jpj4 ekabp3u0"})
        texte = ""
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def france_info(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        blocs_2 = soupe.find("div", {"class": "text"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p")
        texte = ""
        for para in paragraphes:
            texte += para.text + "\n"

        print(texte[:-1])
        print("==================================================")

        return texte[:-1]



# Test
if __name__ == "__main__":
    scrap = Scrapeur()
    sortie = scrap.scrap()

    import pprint
    pprint.pprint(sortie)


