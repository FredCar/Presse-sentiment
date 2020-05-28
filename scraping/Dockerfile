FROM python:3.7

RUN apt-get update && apt-get -y install cron

# Pour installer les modules
COPY requirements.txt /src/
RUN pip3.7 install -r /src/requirements.txt

# Pour la stématisation en Français
RUN python3.7 -m spacy download fr_core_news_md

# Pour les fichiers et scripts
COPY pack/ /src/pack/
COPY scrapeur.py /src/
COPY scrap.log /src/

# Pour automatiser l'exécution du scraping
COPY automated_crontab /etc/cron.d/automated_crontab
RUN chmod 0644 /etc/cron.d/automated_crontab
RUN chmod 0744 /src/scrapeur.py
RUN crontab /etc/cron.d/automated_crontab
CMD cron -f