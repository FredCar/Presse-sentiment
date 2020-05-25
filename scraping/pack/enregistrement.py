from pymongo import MongoClient


class Enregistrement:
    """
    Classe insérant les données dans une base MongoDB
    """

    def __init__(self):
        # Connection à la base
        # self.client = MongoClient("localhost", 27017) # Sans Docker
        self.client = MongoClient('base_mongo', username="root", password="example") # Avec Docker
        self.dbase = self.client["presse-sentiment"]
        self.collec = self.dbase["corpus"]


    def insert(self, data={}, method="one"):
        """
        Insertion des données
        """
        if method == "one":
            self.collec.insert_one(data)
        else:
            self.collec.insert_many(data)


    def read(self, key={}):
        """
        Lecture des données
        """
        self.result = self.collec.find(key)
        return self.result


    # def update(self, filtre={}, updata={}, method="one"):
    #     """
    #     Modification des données
    #     """
    #     if method == "one":
    #         self.collec.update_one(filtre, {"$set": updata})
    #     else:
    #         self.collec.update_many(filtre, {"$set": updata})


    # def delete(self, filtre={}, method="one"):
    #     """
    #     Suppression des données
    #     """
    #     if method == "one":
    #         self.collec.delete_one(filtre)
    #     else:
    #         self.collec.delete_many(filtre)





# Test
if __name__ == "__main__":
    pass
