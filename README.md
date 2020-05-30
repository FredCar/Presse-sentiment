# Projet **Presse Sentiment**

Projet réalisé dans le cadre de la formation [Développeur·se Data IA](https://simplon.co/formation/ecole-ia-microsoft/23).

L’application “Presse-Sentiment” récupère depuis le web les articles de presse en français.   
Après un traitement analysant les textes, toutes ces données sont enregistrées dans une base de données.    
Un site internet permet de consulter ces données sous différentes formes (graphiques, statistiques, positivité, articles similaires, nuage de mots, ...) .     

## Exécution
Téléchargez le projet puis dézippez le.  
Ou bien clonez le :   
```git clone https://github.com/Simplon-IA-Biarritz-1/projet-final-devdataia-FredCar.git```  

Éditez le fichier ```docker-compose.yml``` et modifiez le chemin à la ligne ```21```       
```/chemin/vers/le/dossier/du/projet-final-devdataia-FredCar-master```/database/:/docker-entrypoint-initdb.d/:ro  

Depuis un terminal, rendez-vous dans le dossier du projet puis :  
```docker-compose up```

    Le premier lancement peut prendre un certain temps !   

Trois conteneurs Docker vont se lancer :   

- **Un conteneur sera en charge du scraping**.   
Un script exécuté régulièrement et automatiquement qui parcourt 
les sites de presse francophones pour en récupérer le texte des articles.  
Ces textes sont ensuite traités selon des procédés de [NLP](https://fr.wikipedia.org/wiki/Traitement_automatique_du_langage_naturel).  
Avant d'être enregistrés dans une base de données.

- **Un autre conteneur contiendra la base de donnée**.    
Une base de donnée non-relationnelle **MongoDB**  
Au premier démarrage, elle s'initialise avec des données issues d'un fichier ```.json```

- **Le dernier conteneur démarre le site**.   
Accessible à l'adresse : [```0.0.0.0:5010```](0.0.0.0:5010)