# Sys_Rec — Immo.AI Property Recommendation

## Problème

Ce projet est une application de recommandation immobilière pour la Mauritanie. Il vise à aider un utilisateur à trouver des annonces pertinentes dans un catalogue de biens sans disposer de données d'interaction utilisateur (comme des clics ou des achats). L'objectif est de retourner les meilleures annonces en fonction de la description, du budget et de la localisation recherchés.

## Dataset

- Fichier principal : `e-commerce-mr.csv`
- Provenance : annonces immobilières (voursa.com) pour la Mauritanie
- Colonnes clés :
  - `Title` : titre de l'annonce
  - `Price` / `Price_MRU` : prix en MRU
  - `Location` / `Main_Location` : localisation de l'annonce
  - `Status` : disponibilité
  - `Views` : nombre de vues
  - `Date_Posted` / `Days_Ago` : ancienneté de l'annonce
  - `Category` : catégorie du produit, notamment `real_estate`

## Features

Le système utilise des caractéristiques extraites et dérivées à partir des données brutes :

- Textuelles
  - Construction d'un champ texte combinant `Title`, `Location`, `Main_Location` et un label de fourchette de prix
  - Vectorisation TF-IDF en caractères n-grammes (2–4)
- Prix
  - Parsing de prix pour obtenir `Price_MRU`
  - Bucket de prix en cinq classes : budget, affordable, mid-range, premium, luxury
  - Compatibilité de prix contre le budget maximal fourni
- Popularité
  - Score normalisé basé sur `Views` avec `log1p` pour atténuer les extrêmes
- Récence
  - Score exponentiel sur `Days_Ago` pour favoriser les annonces récentes

## Méthode

Le moteur principal est un système de **Content-Based Filtering** hybride :

- Le texte de la requête est comparé aux annonces via une similarité cosinus sur vecteurs TF-IDF
- Le score final combine :
  - 65% similarité textuelle
  - 15% compatibilité de prix
  - 12% popularité
  - 8% récence

### Pipeline

1. Nettoyage des données dans `src/data_cleaning.py`
   - parsing des prix
   - extraction de la localisation principale
   - suppression des annonces sans titre ou prix fiable
   - suppression des outliers et doublons
2. Enrichissement dans `src/recommender.py`
   - calcul de `price_bucket`, `popularity_score` et `recency_score`
   - generation du champ `_text`
3. Entraînement et recommandation
   - `Recommender.fit(df)` entraîne le vecteur TF-IDF
   - `Recommender.recommend(query, min_price, max_price, location)` renvoie les meilleures annonces

## Captures d'écran / UI

L'interface principale est une application Streamlit située dans `app.py`.

- Barre latérale de configuration
- Carte de résultats avec informations de prix, localisation, statut et score
- Chat vocal / texte
- Chaque annonce est présentée sous forme de carte avec titre, prix, localisation et score

> Note : les captures d'écran ne sont pas incluses dans ce dépôt. Vous pouvez générer une image via Streamlit ou utiliser un enregistreur d'écran lorsque l'application est en cours d'exécution.

## Évaluation

L'évaluation est limitée par l'absence de vérité terrain détaillée. Un indicateur simple implémenté dans `Recommender.evaluate()` est :

- `precision_at_k` : fraction des résultats du top-K avec un score hybride significatif
- `avg_hybrid_score` : score moyen des recommandations pour une liste de requêtes tests

Jeux de requêtes tests présents dans `app.py` :

- `villa Tevragh Zeina luxury`
- `cheap house Arafat`
- `apartment Ksar affordable`
- `land terrain constructible`
- `commercial space office`

## Limites

- Pas de données utilisateurs / clics : difficile d'utiliser le collaborative filtering
- Le modèle repose uniquement sur les métadonnées textuelles et de prix
- La qualité de la recommandation dépend de la richesse et de la propreté du dataset
- La compréhension du texte est limitée par TF-IDF ; les synonymes et paraphrases sont mal gérés
- Les informations géographiques sont basiques (`Location` / `Main_Location`) et ne bénéficient pas de cartographie avancée
- La partie voix dépend d'une clé d'API Mistral et de `gTTS`

## Installation

1. Créez et activez un environnement virtuel Python :

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Installez les dépendances :

```bash
python -m pip install -r requirements.txt
```

3. Si vous utilisez les fonctionnalités vocales et le chatbot, créez un fichier `.env` à la racine avec :

```text
MISTRAL_API_KEY=your_api_key_here
```

## Comment exécuter

### Application Streamlit

```bash
streamlit run app.py
```

Puis ouvrez l'URL affichée par Streamlit dans votre navigateur.

### Chatbot vocal / console

```bash
python chatbot.py
```

- Le chatbot nécessite une connexion Internet et une clé Mistral valide
- Il utilise `SpeechRecognition`, `gTTS` et `pygame` pour l'entrée et la sortie audio

## Structure des fichiers principaux

- `app.py` : interface Streamlit
- `chatbot.py` : assistant vocal / conversationnel
- `src/data_cleaning.py` : chargement et nettoyage du dataset
- `src/recommender.py` : modèle de recommandation et scoring
- `src/mistral_client.py` : intégration avec l'API Mistral
- `src/voice.py` : synthèse vocale et reconnaissance audio

## Remarques

- Le dataset `e-commerce-mr.csv` doit rester à la racine du dépôt
- Le projet est optimisé pour les annonces immobilières (`Category == real_estate`)
- Pour des résultats plus robustes, il est recommandé d'ajouter une collecte de feedback utilisateur et des données géospatiales
