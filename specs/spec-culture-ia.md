# Spécification Fonctionnelle - Projet Culture IA (Puls-Events)

## 1. Contexte
Puls-Events souhaite un chatbot intelligent (POC) capable de recommander des événements culturels récents (< 1 an) en utilisant les données de l'API Open Agenda.

## 2. Objectifs Techniques
- **Système RAG** : Retrieval-Augmented Generation utilisant LangChain, Mistral AI et FAISS.
- **API REST** : Exposer le système via FastAPI.
- **Évaluation** : Mesurer la performance avec un jeu de test annoté (via Ragas).
- **Déploiement** : Conteneurisation via Docker pour démo locale.

## 3. Stack Technique (Fixée)
- **Langage** : Python 3.10.18
- **Orchestrateur RAG** : LangChain
- **LLM** : Mistral AI
- **Vector DB** : FAISS (version CPU)
- **API** : FastAPI + Uvicorn
- **Données** : Open Agenda API
- **Évaluation** : Ragas
- **Conteneur** : Docker

## 4. Endpoints API attendus
- `POST /ask` : Prend une question, retourne une réponse augmentée.
- `POST /rebuild` : Reconstruit l'index vectoriel à partir des dernières données Open Agenda.

## 5. Livrables
- **Dépôt GitHub** : Structuré (scripts, tests, API, docs).
- **POC fonctionnel** : Système RAG complet.
- **API REST** : FastAPI, conteneurisée via Docker.
- **Rapport Technique** : Documentant l'architecture, les choix, les modèles, les résultats et les pistes d'amélioration.
- **Jeu de test annoté** : Questions/Réponses de référence.
- **Tests & Métriques** : Tests unitaires et automatisation de l'évaluation.
- **Présentation** : PowerPoint (10-15 slides).
- **Démo Live** : Démonstration de l'utilisation de l'API (via Swagger UI ou curl).
