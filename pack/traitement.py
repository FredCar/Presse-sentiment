import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from stop_words import get_stop_words
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class Traitement:
    """
    Classe chargée d'effectuer les divers traitements nécessaires
    """

    def __init__(self):
        self.french_stop_words = get_stop_words('french')

    def nettoyage(self, x):
        """
        Fonction de nettoyage du texte
        """
        x = x.lower()
        x = re.sub(r"\W", " ", x)  # Enleve la ponctuation
        x = re.sub(r"[éèêë]", "e", x)
        x = re.sub(r"[àâäà]", "a", x)
        x = re.sub(r"[ùûü]", "u", x)
        x = re.sub(r"[ôöò]", "o", x)
        x = re.sub(r"  +", " ", x) # Enleve les espaces multiples
        return x


    def lematisation(self):
        pass


    def matrice(self, x):
        cv = CountVectorizer(stop_words=self.french_stop_words)
        x_cv = cv.fit_transform(x)

        x_cv = pd.DataFrame(x_cv.toarray(), columns=cv.get_feature_names())

        x_cv = x_cv.sum()
        x_cv = x_cv.sort_values(ascending=False)

        return x_cv



# Test
if __name__ == "__main__":
    pass