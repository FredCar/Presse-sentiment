from pymongo import MongoClient


class Enregistrement:
    """
    Classe insérant les données dans une base MongoDB
    """

    def __init__(self):
        """Connection à la base"""
        self.client = MongoClient('base_mongo', username="root", password="example") # Avec Docker
        self.dbase = self.client["presse-sentiment"]
        self.collec = self.dbase["corpus"]


    def insert(self, data={}):
        """Insertion des données"""
        self.collec.insert_one(data)

    def read(self, key={}):
        """Lecture des données"""
        self.result = self.collec.find(key)
        return self.result

    def logeur(self, log):
        """Écrit les logs dans un fichier"""
        with open("/src/scrap.log", "a") as logs:
            logs.write(log)
