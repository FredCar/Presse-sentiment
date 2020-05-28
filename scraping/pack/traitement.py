import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from stop_words import get_stop_words
import spacy # Lemmatiseur et Stemmatiseur
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer


#==============================================
# \\\\\\\\\\\\\\ ---Fonctions--- //////////////
#==============================================
def concatenation(sortie):
    """Concaténation du texte à traiter pour la matrice de termes"""
    chaine = ""
    chaine += sortie["titre"] + " "
    if sortie["extrait"][:20] == sortie["texte"][:20]:
        chaine += sortie["texte"]
    else:
        chaine += sortie["extrait"] + " "
        chaine += sortie["texte"]

    return chaine


def nettoyage(x):
    """Fonction de nettoyage du texte"""
    x = x.lower()
    x = re.sub(r"\W", " ", x)  # Enleve la ponctuation
    x = re.sub(r"[éèêë]", "e", x)
    x = re.sub(r"[àâäà]", "a", x)
    x = re.sub(r"[ùûü]", "u", x)
    x = re.sub(r"[ôöò]", "o", x)
    x = re.sub(r"  +", " ", x)  # Enleve les espaces multiples
   
    return x


#==============================================#
# \\\\\\\\\\\\\\\\ ---Classe--- ////////////////
#==============================================#
class Traitement:
    """
    Classe chargée d'effectuer les divers traitements nécessaires
    """

    def __init__(self):
        self.french_stop_words = get_stop_words('french')

        # TODO Acev SpaCy, quelle différence entre "md" et "sm" ??
        self.nlp = spacy.load('fr_core_news_md') # Utilisé par SapCy pour la Lemmatisation et Stemmatisation

        self.blob = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer()) # Analyse de sentiments


    def lemmatisation_stemmatisation(self, phrase):
        """Renvoi la racine des mots et supprime les suffixes"""
        doc = self.nlp(phrase)
        sortie = []
        for token in doc:
            sortie.append(token.lemma_)
        sortie = " ".join(sortie)

        return sortie


    def positivite(self, phrase):
        """Calcule la positivité de l'article"""
        bloby = self.blob(phrase)
        return bloby.sentiment[0]


    def subjectivite(self, phrase):
        """Calcule l'objectivité de l'article"""
        bloby = self.blob(phrase)
        return bloby.sentiment[1]


    def matrice(self, x):
        """Renvoi la liste des termes et leur nombre d'occurences trié par ordre decroissant"""
        cv = CountVectorizer(stop_words=self.french_stop_words)
        x_cv = cv.fit_transform(x)

        x_cv = pd.DataFrame(x_cv.toarray(), columns=cv.get_feature_names())

        x_cv = x_cv.sum()
        x_cv = x_cv.sort_values(ascending=False)

        return x_cv