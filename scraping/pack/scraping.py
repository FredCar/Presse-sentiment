import requests
from bs4 import BeautifulSoup as bs

class Scrapeur:
    """
    Classe chargée d'éxécuter le scrapping
    """

    def __init__(self, lien="https://news.google.com/topstories?hl=fr&gl=FR&ceid=FR%3Afr"):
        self.lien = lien
        self.editeurs = ["le monde", "le figaro", "franceinfo", "20 minutes", "sud ouest",
                         "le parisien", "lci", "boursorama", "actu orange"]
        self.site_bloques = ["Ouest-France"]

    def scrap(self):
        """
        Fonction principale scrapant Google Actu
        """
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
            elif auteur.lower() == "20 minutes":
                texte = self.vingt_minutes(lien_article)
            elif auteur.lower() == "sud ouest":
                texte = self.sud_ouest(lien_article)
            elif auteur.lower() == "le parisien":
                texte = self.le_parisien(lien_article)
            elif auteur.lower() == "lci":
                texte = self.lci(lien_article)
            elif auteur.lower() == "rtl.fr":
                texte = self.rtl(lien_article)
            elif auteur.lower() == "boursorama":
                texte = self.boursorama(lien_article)
            elif auteur.lower() == "actu orange":
                texte = self.actu_orange(lien_article)
            else:
                texte = "--"

            # TODO Récupérer la catégorie des articles

            sortie[compteur] = {"titre": titre,
                                "auteur": auteur,
                                "date": date,
                                "heure": heure,
                                "extrait": extrait,
                                "lien": lien_article,
                                "texte": texte}

        return sortie


#########################################
#\\\\\\\\\\\\\\\  SITES  ///////////////#
#########################################

    def le_monde(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            extrait = soupe.find("p", {"class": "article__desc"})
            texte += extrait.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("section", {"class": "article__wrapper"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p", {"class": "article__paragraph"})

        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def le_figaro(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            blocs_2 = soupe.find("header", {"class": "css-r32ezy"})

            paragraphes = blocs_2.find_all("p")
            for para in paragraphes:
                texte += para.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("div", {"class": "css-1lz652c ey7xkwt0"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p", {"class": "css-s6jpj4 ekabp3u0"})
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def france_info(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            extrait = soupe.find("p", {"class": "chapo"})
            texte += extrait.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("div", {"class": "text"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p")
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def vingt_minutes(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            extrait = soupe.find("p", {"class": "hat"})
            texte += extrait.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("div", {"class": "lt-endor-body"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p")

        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def sud_ouest(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        blocs_2 = soupe.find("div", {"class": "article-content"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p")
        texte = ""
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]

    def le_parisien(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            blocs_2 = soupe.find("header", {"class": "article_header"})

            paragraphes = blocs_2.find_all("h2")
            for para in paragraphes:
                texte += para.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("div", {"class": "article-section"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p")
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def lci(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            extrait = soupe.find("h2", {"class": "article-chapo"})
            texte += extrait.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("main", {"class": "main-page-entity"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("section", {"class": "paragraph-block"})
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]


    def rtl(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        try:
            extrait = soupe.find("h2", {"class": "article-chapo"})
            texte += extrait.text + "\n"
        except:
            pass

        blocs_2 = soupe.find("div", {"class": "article-mask"})
        if blocs_2 == None:
            return "--"
        paragraphes = blocs_2.find_all("p")
        for para in paragraphes:
            texte += para.text + "\n"

        return texte[:-1]

    def boursorama(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        blocs_2 = soupe.find("div", {"class": "c-news-detail"})
        if blocs_2 == None:
            return "--"

        try:
            extrait = blocs_2.find("h2")
            texte += extrait.text + "\n"
        except:
            pass

        paragraphes = blocs_2.find_all("p")
        for para in paragraphes[2:]:
            texte += para.text + "\n"

        return texte[:-1]


    def actu_orange(self, lien_article):
        page_response = requests.get(lien_article)
        soupe = bs(page_response.content, "html.parser")

        texte = ""

        blocs_2 = soupe.find("div", {"itemprop": "articleBody"})
        if blocs_2 == None:
            return "--"

        paragraphes = blocs_2.find_all("p")
        for para in paragraphes[1:]:
            texte += para.text + "\n"

        return texte[:-1]

