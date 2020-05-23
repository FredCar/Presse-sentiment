FROM python:3

# Pour automatiser l'exécution du scraping
RUN apt-get update && apt-get -y install cron
COPY automated_crontab /etc/cron.d/automated_crontab
RUN chmod 0644 /etc/cron.d/automated_crontab
RUN crontab /etc/cron.d/automated_crontab
CMD cron && tail -f /src/scrap.log

COPY requirements.txt /src/
RUN pip install -r /src/requirements.txt

# TODO Pour la stématisation en Français
RUN python -m spacy download fr_core_news_md

COPY /pack/ /src/pack/
COPY scrapeur.py /src/
COPY scrap.log /src/

# CMD python /src/scrapeur.py