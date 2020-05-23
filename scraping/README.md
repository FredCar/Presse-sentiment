# Pour automatiser l'exécution

## Crontab
Depuis un terminal:    
    - ```crontab -e```    
Puis éditer le fichier:      
    - ```*/15 * * * * cd /chemin/vers/le/dossier/scraping/; python scrapeur.py >> scrap.log 2>&1```
> */15 s'exécutera toutes les 15 minutes