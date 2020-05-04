import re
from stop_words import get_stop_words
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from ../01_Scraping/scrapeur.py import Scrapeur

scrap = Scrapeur()
sortie = scrap.scrap()

import pprint
pprint.pprint(sortie)


# def nettoyage(x):
#     x = x.lower()
#     x = re.sub(r"\W", " ", x) # Enleve la ponctuation
#     x = re.sub(r"[éèêë]", "e", x)
#     x = re.sub(r"[àâäà]", "a", x)
#     x = re.sub(r"[ùûü]", "u", x)
#     x = re.sub(r"[ôöò]", "o", x)
#     x = re.sub(r"  +", " ", x)
#     return x
#
# titres_modif = list(map(nettoyage, titres))
# titres_modif = " ".join(titres_modif)
#
# french_stop_words = get_stop_words('french')
#
# text = titres_modif
#
# wordcloud = WordCloud(font_path="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
#                       stopwords=french_stop_words,
#                       background_color="red",
#                       min_word_length=0,
#                       min_font_size=4)
# wordcloud.generate(text)
#
# plt.figure(figsize=(18,8))
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")
# plt.show()
