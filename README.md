# Culture IA - Assistant de Recommandation d'Événements Culturels

[![CI/CD Pipeline](https://github.com/Kisai-DG-SLU/culture-ia/actions/workflows/ci.yml/badge.svg)](https://github.com/Kisai-DG-SLU/culture-ia/actions/workflows/ci.yml)
[![GitHub version](https://img.shields.io/github/v/tag/Kisai-DG-SLU/culture-ia?label=version)](https://github.com/Kisai-DG-SLU/culture-ia/tags)
[![Coverage Report](https://img.shields.io/badge/Coverage-Report-blue)](https://Kisai-DG-SLU.github.io/culture-ia/)

## 🚀 Présentation du Projet
Ce projet est un POC (Proof of Concept) développé pour **Puls-Events**. Il implémente un assistant virtuel **RAG (Retrieval-Augmented Generation)** capable de recommander des événements culturels en langage naturel, en s'appuyant sur les données temps réel de l'API **OpenAgenda**.

### Points Forts & Fonctionnalités
- **RAG Hybride & Robuste** :
    - **Mode Cloud** : Utilise Mistral AI pour les embeddings (haute qualité).
    - **Mode Local (Secours)** : Bascule automatiquement sur HuggingFace (`all-MiniLM-L6-v2`) si l'API Mistral est indisponible (Fonctionne hors-ligne/CPU).
- **Collecte Intelligente** : Algorithme de filtrage avancé pour récupérer les événements futurs (jusqu'en 2026) malgré les limitations par défaut de l'API OpenAgenda.
- **Architecture "Stateless"** : API REST performante, sans rétention de contexte, optimisée pour la scalabilité.
- **Qualité Industrielle** : CI/CD, Tests unitaires (Cover > 80%), Évaluation Ragas, Docker.

---

## 🛠️ Prérequis
Avant de démarrer, assurez-vous d'avoir :
- **Python 3.10** (Recommandé via `pyenv`).
- **Docker** (Pour le déploiement).
- **Compte OpenAgenda** (Pour récupérer la clé API).
- **Compte Mistral AI** (Pour la génération de texte et embeddings Cloud).

---

## ⚙️ Installation et Configuration

### 1. Clonage et Installation
```bash
git clone <url-du-depot>
cd culture-ia
make install
```
*Cette commande crée l'environnement virtuel et installe les dépendances.*

### 2. Configuration des Clés API (Critique)
Le projet nécessite des clés API pour fonctionner pleinement.
Copiez le modèle :
```bash
cp .env.template .env
```
Éditez le fichier `.env` :
- `MISTRAL_API_KEY` : Votre clé Mistral (Si laissée à `none` ou vide, le mode embedding **Local** s'active).
- `OPENAGENDA_API_KEY` : **Requis** pour récupérer les horaires et les événements futurs (V2).
- `OPENAGENDA_AGENDA_UID` : L'ID de l'agenda à cibler (Par défaut : `826334`).

### 3. Vérification de l'environnement
Lancez le script de diagnostic pour valider vos clés et dépendances :
```bash
.venv/bin/python tests/check_env.py
```

---

## 🚀 Utilisation

### Mode Docker (Recommandé pour la Démo)
L'image Docker est autonome : elle détecte si l'index existe, sinon elle lance la collecte et l'indexation au démarrage.

1. **Construire l'image** :
   ```bash
   make docker-build
   ```
2. **Lancer l'application** :
   ```bash
   make docker-run
   ```
   *L'API sera accessible sur [http://localhost:8000](http://localhost:8000).*

### Mode Local (Développement)
Si vous souhaitez développer ou tester sans Docker :

1. **Reconstruire l'index (ETL)** :
   ```bash
   # Collecte -> Process -> Vectorisation
   PYTHONPATH=. .venv/bin/python src/main.py --rebuild-only
   # Ou via le script dédié si disponible, ou en lançant l'API et en appelant /rebuild
   ```
   *Note : Le script `entrypoint.sh` détaille les étapes manuelles : `src/collector.py` -> `src/processor.py` -> `src/core/vectorstore.py`.*

2. **Lancer l'API** :
   ```bash
   make run
   ```

---

## 📚 Documentation API (Swagger)
Une fois l'application lancée, accédez à la documentation interactive :
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Endpoints Principaux
- `POST /ask` : Poser une question au RAG.
  ```json
  { "question": "Quels événements culinaires en 2025 ?" }
  ```
- `POST /rebuild` : Forcer la mise à jour des données (Collecte + Indexation) sans redémarrer le serveur.

---

## 📊 Qualité et Tests
Le projet intègre une suite de tests rigoureuse.

- **Lancer les tests unitaires** :
  ```bash
  make test
  ```
- **Évaluation Ragas** :
  Les tests incluent une évaluation de la qualité des réponses (Fidélité, Pertinence) via le framework Ragas. Les résultats s'affichent dans la sortie standard lors du test `tests/test_evaluator_unit.py`.

---

## 🏗️ Structure du Projet
```text
culture-ia/
├── .github/            # CI/CD Workflows
├── data/               # Données (ignoré par git)
├── docs/               # Présentation, Rapport Technique
├── src/
│   ├── api/            # FastAPI App
│   ├── collector.py    # Connecteur OpenAgenda V2
│   ├── processor.py    # Nettoyage et Structuration
│   └── core/
│       ├── vectorstore.py  # Gestion FAISS (Hybride)
│       ├── rag_chain.py    # Orchestration LangChain
│       └── evaluator.py    # Moteur Ragas
├── tests/              # Tests (Unitaires, Intégration, Eval)
├── Dockerfile          # Image de production
├── Makefile            # Commandes raccourcies
└── requirements.txt    # Dépendances épinglées
```

---

## 👨‍💻 Auteur
**Damien Guesdon** - Data Scientist Freelance.
*Projet réalisé dans le cadre de la certification "Développeur IA".*
