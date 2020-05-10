import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from stop_words import get_stop_words
import nltk
import spacy # Lemmatiseur
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# nltk.download("punkt") # A charger la prmière fois
# nltk.download("wordnet") # A charger la prmière fois


class Traitement:
    """
    Classe chargée d'effectuer les divers traitements nécessaires
    """

    def __init__(self):
        self.french_stop_words = get_stop_words('french')

        # TODO Acev SpaCy, quelle différence entre "md" et "sm" ??
        self.nlp = spacy.load('fr_core_news_md') # Utilisé par SapCy pour la Lemmatisation et Stemmatisation


    def concatenation(self, sortie):
        """
        Concaténation du texte à traiter pour la matrice de termes
        """
        chaine = ""
        chaine += sortie["titre"] + " "
        if sortie["extrait"][:20] == sortie["texte"][:20]:
            chaine += sortie["texte"]
        else:
            chaine += sortie["extrait"] + " "
            chaine += sortie["texte"]

        return chaine


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


    def tokenisation(self, phrase):
        """
        Converti les phrases en liste de mots
        """
        return nltk.word_tokenize(phrase)


    def stematisation(self,phrase):
        """
        Supprime les suffixes
        """
        mots = self.tokenisation(phrase)
        stem = nltk.stem.snowball.FrenchStemmer()
        liste_de_mots = []
        for mot in mots:
            liste_de_mots.append(stem.stem(mot))

        return liste_de_mots


    def lemmatisation(self, phrase):
        """
        Renvoi la racine des mots
        """
        # nlp = spacy.load('fr_core_news_md')

        doc = self.nlp(phrase)
        sortie = []
        for token in doc:
            sortie.append(token.lemma_)
            # print(token, token.lemma_)
        sortie = " ".join(sortie)

        return sortie


    def positivite(self, phrase):
        """
        Calcule la positivité de l'article
        """
        return TextBlob(phrase).sentiment.polarity


    def subjectivite(self, phrase):
        """
        Calcule l'objectivité de l'article
        """
        return TextBlob(phrase).sentiment.subjectivity


    def matrice(self, x):
        """
        Renvoi la liste des termes et leur nombre d'occurences trié par ordre descendant
        """
        # TODO question à se poser : Matrice TFIDF ou pas ?
        cv = CountVectorizer(stop_words=self.french_stop_words)
        x_cv = cv.fit_transform(x)

        x_cv = pd.DataFrame(x_cv.toarray(), columns=cv.get_feature_names())

        x_cv = x_cv.sum()
        x_cv = x_cv.sort_values(ascending=False)

        return x_cv



# Test
if __name__ == "__main__":
    trait = Traitement()
