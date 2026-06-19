# Chatbot de diagnostic médical préliminaire

## Présentation

Ce projet est un chatbot web médical capable de proposer un diagnostic préliminaire à partir de symptômes décrits en français. Il combine du traitement du langage naturel (NLP) pour extraire les symptômes et un modèle de machine learning entraîné sur un jeu de données médical en anglais.

L'application est développée avec Flask et MongoDB, et offre une interface utilisateur pour :

- consulter le diagnostic préliminaire,
- afficher l'historique des échanges,
- gérer les comptes utilisateurs (inscription, connexion, profil).

> Attention : ce chatbot est un outil d'information et ne remplace pas un avis médical professionnel.

## Fonctionnalités

- Extraction de symptômes en français via NLP
- Traduction de ces symptômes vers le vocabulaire du modèle
- Prédiction d'une maladie probable avec un modèle Random Forest
- Traduction des maladies et symptômes en français pour l'utilisateur
- Historique des conversations stocké dans MongoDB
- Authentification et gestion utilisateur avec Flask-Login
- Pages front-end pour le tableau de bord et l'historique

## Architecture

- `run.py` : point d'entrée de l'application Flask
- `app/__init__.py` : création et configuration de l'application
- `app/config.py` : configuration de l'environnement
- `app/routes/` : routes et endpoints Flask
  - `main.py` : page d'accueil, API chatbot, historique, infos modèle
  - `auth.py` : connexion, inscription, déconnexion, profil
  - `dashboard.py` : tableau de bord et historique utilisateur
- `app/models/` : modèles métier
  - `disease_model.py` : charge, entraîne et prédit avec le modèle ML
  - `user.py` : gestion des utilisateurs et de l'historique
- `app/services/` : services applicatifs
  - `nlp_service.py` : extraction et prétraitement de texte
  - `ml_service.py` : initialisation, prédiction et information sur le modèle
  - `translations.py` : traduction des maladies et symptômes
- `data/` : données d'entraînement et documents d'analyse
- `models/` : modèles sauvegardés (`.joblib`)
- `static/` et `templates/` : ressources front-end

## Installation

1. Cloner le dépôt :

```bash
git clone <url_du_projet>
cd Projet_de_fin_Etude
```

2. Créer et activer un environnement Python :

```bash
python -m venv venv
source venv/bin/activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Créer un fichier `.env` à la racine avec les variables suivantes :

```env
SECRET_KEY=une_cle_secrete
MONGO_URI=mongodb://localhost:27017/chatbot_medical
FLASK_ENV=development
```

5. Démarrer MongoDB si ce n'est pas déjà fait.

## Utilisation

1. Lancer l'application :

```bash
python run.py
```

2. Ouvrir le navigateur à l'adresse :

```text
http://localhost:5000
```

3. S'inscrire ou se connecter pour accéder au chatbot.

## Test du modèle

Le fichier `test_modele.py` permet de tester l'entraînement et la prédiction du modèle :

```bash
python test_modele.py
```

## Entraînement et modèle

- Le modèle est entraîné sur `data/training_cleaned.csv`
- Le fichier `models/disease_model.joblib` contient le modèle entraîné
- Si le modèle existe, l'application le charge au démarrage. Sinon, elle réentraîne le modèle automatiquement.

## Variables d'environnement

- `SECRET_KEY` : clé secrète Flask
- `MONGO_URI` : URI de connexion MongoDB
- `FLASK_ENV` : mode d'exécution (`development` ou `production`)

## Remarques

- L'objectif du projet est de fournir un diagnostic préliminaire uniquement à des fins pédagogiques.
- Il est recommandé d'améliorer la couverture des symptômes et la qualité du mapping de traduction.
- Le chatbot ne remplace pas un médecin.

## Licence

Ce projet est fourni sans licence explicite.
