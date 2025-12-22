# 🎭 Culture IA - Assistant de Recommandation Culturelle

![Build Status](https://github.com/Kisai-DG-SLU/culture-ia/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Environment](https://img.shields.io/badge/environment-conda-green)

Culture IA est un assistant intelligent (RAG) développé pour **Puls-Events**. Il permet d'interroger en langage naturel la base de données des événements culturels d'OpenAgenda.

---

## 🚀 Installation & Démarrage

### 0. Configuration (Indispensable)
Avant de lancer l'application, vous devez configurer vos accès API :
1. Copiez le fichier d'exemple : `cp .env.template .env`
2. Éditez le fichier `.env` et renseignez vos clés :
   - `MISTRAL_API_KEY` : Obtenue sur [console.mistral.ai](https://console.mistral.ai/)
   - `OPENAGENDA_API_KEY` : Obtenue sur [openagenda.com](https://openagenda.com/settings/apikeys) (nécessaire pour la collecte des données).

### Option A : Via Docker (Recommandé pour la démo)
C'est la méthode la plus simple et la plus fiable.
*Le conteneur est basé sur une image **Miniconda3**, garantissant que l'environnement d'exécution est strictement identique à l'environnement de développement Conda.*

1.  **Prérequis** : Docker installé.
2.  **Construire l'image** :
    ```bash
    make docker-build
    ```
3.  **Lancer l'application** :
    ```bash
    make docker-run
    ```
    *(Cette commande lance l'API + l'Interface sur les ports 8000 et 8501)*

### Option B : Installation Locale (Développement)
Pour les développeurs souhaitant modifier le code ou exécuter les tests.

1.  **Prérequis** : [Miniconda](https://docs.conda.io/en/latest/miniconda.html) ou Anaconda installé.
2.  **Créer l'environnement** :
    ```bash
    conda env create -f environment.yml
    conda activate culture-ia
    ```
3.  **Lancer l'application** :
    *   **Lancer l'API** (Terminal 1) :
        ```bash
        make run
        ```
    *   **Lancer l'Interface** (Terminal 2) :
        ```bash
        make frontend
        ```

---

## 🖥️ Utilisation

Une fois l'application lancée, deux interfaces sont disponibles :

### 1. 🎨 Interface Utilisateur (Streamlit)
👉 **URL : [http://localhost:8501](http://localhost:8501)**

C'est le cockpit de pilotage de l'assistant. Il contient 3 onglets :
*   **🤖 Assistant** : Chattez avec l'IA. Posez des questions comme *"Quoi faire ce week-end ?"* ou *"Des concerts de Jazz ?"*.
*   **⚙️ Administration** : Vérifiez l'état de l'API et forcez la mise à jour des données (Bouton "Reconstruire l'index").
*   **📊 Performances** : Visualisez les métriques de qualité (Ragas) sous forme de graphiques.

### 2. ⚙️ API Backend (FastAPI)
👉 **URL : [http://localhost:8000/docs](http://localhost:8000/docs)**

Documentation interactive Swagger.
*   `GET /` : Vérification de santé (Health Check).
*   `POST /ask` : Pose une question à l'assistant.
    *   *Input* : `{"question": "..."}`
*   `POST /rebuild` : Déclenche le pipeline ETL (Collecte OpenAgenda -> Vectorisation FAISS).
*   `GET /metrics` : Récupère les scores d'évaluation Ragas (Fidélité, Pertinence...).

---

## 🏗️ Architecture Technique

*   **Gestionnaire d'Environnement** : **Conda** (via `environment.yml`).
*   **Vector Store** : FAISS (Recherche de similarité).
*   **LLM** : Mistral AI (`mistral-tiny`) via API.
*   **Orchestration** : LangChain.
*   **Frontend** : Streamlit.
*   **Qualité** :
    *   **CI/CD** : GitHub Actions (basé sur Miniconda).
    *   **Pre-commit** : Black, Pylint.
    *   **Tests** : Pytest (> 80% coverage).

## 📂 Structure du Projet

```
.
├── .github/            # Pipelines CI/CD
├── data/               # Stockage local (Index FAISS, JSONs) - gitignored
├── docs/               # Documentation projet (Rapport, Slides...)
├── specs/              # Spécifications fonctionnelles
├── src/
│   ├── api/            # Code de l'API FastAPI
│   ├── core/           # Logique métier (RAG, VectorStore, Eval)
│   ├── frontend/       # Interface Streamlit
│   ├── collector.py    # Script de collecte OpenAgenda
│   ├── processor.py    # Nettoyage et structuration des données
│   └── main.py         # Point d'entrée API
├── tests/              # Tests unitaires et d'intégration
├── Dockerfile          # Image Docker (Miniconda base)
├── environment.yml     # Dépendances Conda (Source unique de vérité)
├── Makefile            # Commandes d'automatisation
└── README.md           # Ce fichier
```

## 👤 Auteur
**Damien Guesdon** - *Formation IA - Projet 7*