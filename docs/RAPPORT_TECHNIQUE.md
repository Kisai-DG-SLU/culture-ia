# Rapport Technique - POC Culture IA (Puls-Events)

## 1. Introduction
Ce rapport présente la conception et la réalisation du Proof of Concept (POC) d'un assistant intelligent de recommandation culturelle utilisant une architecture **RAG (Retrieval-Augmented Generation)**. L'objectif est de permettre aux utilisateurs d'interroger les événements de la plateforme **Open Agenda** en langage naturel.

## 2. Architecture du Système
L'architecture repose sur quatre piliers principaux :
1.  **Ingestion & Prétraitement** : Collecte des données via l'API Open Agenda, filtrage temporel (événements de moins d'un an) et structuration.
2.  **Base de Données Vectorielle** : Utilisation de **FAISS** pour stocker les représentations sémantiques (embeddings) des événements.
3.  **Chaîne RAG** : Orchestration via **LangChain** pour lier la recherche vectorielle à la génération de texte.
4.  **Interface API** : Exposition des fonctionnalités via **FastAPI**.

## 3. Choix Technologiques et Modèles
- **LLM : Mistral AI (`mistral-tiny`)**
    - *Raison* : Modèle performant, souverain (Français) et offrant un excellent compromis latence/précision pour un POC.
- **Embeddings : Mistral Embeddings** (avec fallback Local Sentence-Transformers)
    - *Raison* : Cohérence avec le LLM pour la similarité sémantique.
- **Vector Store : FAISS (CPU)**
    - *Raison* : Bibliothèque extrêmement rapide pour la recherche de plus proches voisins, facile à conteneuriser sans dépendance GPU.
- **Micro-framework API : FastAPI**
    - *Raison* : Performance asynchrone et documentation Swagger interactive intégrée.

## 4. Résultats et Évaluation
La qualité du système a été mesurée à l'aide de la bibliothèque **Ragas** sur un jeu de tests annoté de 4 questions de référence.

**Métriques observées :**
- **Fidélité (Faithfulness)** : ~86% (Le système respecte bien les documents sources).
- **Pertinence de la réponse** : ~71% (Les réponses sont globalement liées aux questions).
- **Rappel (Context Recall)** : ~75% (Le système retrouve 3/4 des informations nécessaires).
- **Précision du Retrieval** : ~50% (Marge de progression sur le filtrage du bruit dans les documents récupérés).

## 5. Déploiement
Le système est entièrement conteneurisé via **Docker**.
- L'image inclut un script d'entrée (`entrypoint.sh`) qui automatise la construction de l'index au démarrage si celui-ci est absent, garantissant une démo "clés en main".
- Une pipeline de **CI (GitHub Actions)** a été mise en place pour valider les tests unitaires et l'environnement à chaque modification du code.

## 6. Pistes d'Amélioration
1.  **Recherche Hybride** : Combiner la recherche sémantique avec des filtres par mots-clés ou par dates pour une précision accrue.
2.  **Interface Utilisateur** : Développer une interface Streamlit pour une démo encore plus engageante.
3.  **Mise à jour à chaud** : Implémenter un système de mise à jour incrémentale de l'index sans redémarrage de l'API.
4.  **Gestion de la mémoire** : Ajouter une fenêtre de contexte conversationnel pour permettre des questions de suivi (ex: "Et c'est gratuit ?").

---
*Damien Guesdon - Data Scientist Freelance*
