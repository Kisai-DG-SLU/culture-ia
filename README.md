# Culture IA - Assistant de Recommandation d'Événements Culturels

[![CI/CD Pipeline](https://github.com/Kisai-DG-SLU/culture-ia/actions/workflows/ci.yml/badge.svg)](https://github.com/Kisai-DG-SLU/culture-ia/actions/workflows/ci.yml)
[![GitHub version](https://img.shields.io/github/v/tag/Kisai-DG-SLU/culture-ia?label=version)](https://github.com/Kisai-DG-SLU/culture-ia/tags)
[![Coverage Report](https://img.shields.io/badge/Coverage-Report-blue)](https://Kisai-DG-SLU.github.io/culture-ia/)

## 🚀 Présentation du Projet
Ce projet est un POC (Proof of Concept) développé pour **Puls-Events**. L'objectif est de mettre en place un système **RAG (Retrieval-Augmented Generation)** capable de répondre aux questions des utilisateurs sur les événements culturels récents en s'appuyant sur les données de l'API Open Agenda.

### Fonctionnalités clés
- **Collecte de données** : Intégration avec l'API Open Agenda.
- **Moteur RAG** : Utilisation de LangChain, Mistral AI et FAISS pour une recherche sémantique performante.
- **API REST** : Interface FastAPI permettant de poser des questions et de reconstruire l'index.
- **Évaluation** : Mesure de la qualité des réponses via la bibliothèque Ragas.
- **Conteneurisation** : Déploiement simplifié via Docker.

---

## 🛠️ Structure du Projet
```text
culture-ia/
├── data/               # Données brutes et index FAISS local
├── docs/               # Documentation et rapport technique
├── specs/              # Spécifications et suivi du projet
├── src/                # Code source
│   ├── api/            # Endpoints FastAPI
│   ├── core/           # Logique RAG (LangChain, Mistral)
│   ├── data/           # Scripts de collecte et processing
│   └── main.py         # Point d'entrée de l'application
├── tests/              # Tests unitaires et d'intégration
├── Makefile            # Automatisation des tâches
├── requirements.txt    # Dépendances Python
└── Dockerfile          # Configuration du conteneur
```

---

## ⚙️ Installation et Reproduction

### Prérequis
- Python 3.10.x
- [pyenv](https://github.com/pyenv/pyenv) (recommandé pour gérer la version Python)
- Un compte [Mistral AI](https://console.mistral.ai/) pour obtenir une clé API.

### Configuration de l'environnement
1. **Cloner le dépôt** :
   ```bash
   git clone <url-du-depot>
   cd culture-ia
   ```

2. **Installer les dépendances** :
   Le projet utilise un environnement virtuel Python 3.10 géré via un `Makefile`.
   ```bash
   make install
   ```

3. **Vérifier l'environnement** :
   Lancez le script de validation des imports critiques (Faiss, LangChain, Mistral) :
   ```bash
   .venv/bin/python tests/check_env.py
   ```

4. **Configurer les variables d'environnement** :
   Copiez le fichier `.env.template` en `.env` (ce fichier est ignoré par Git) et remplissez vos clés API :
   ```bash
   cp .env.template .env
   ```

### Utilisation
- **Lancer les tests** : `make test`
- **Lancer l'application** : `make run`

---

## 📊 Évaluation et Qualité
Le système inclut un jeu de tests annotés et utilise **Ragas** pour évaluer :
- La pertinence de la réponse.
- La fidélité au contexte extrait.
- La précision du retrieval.

---

## 👨‍💻 Auteur
**Damien Guesdon** - Data Scientist Freelance pour Puls-Events.