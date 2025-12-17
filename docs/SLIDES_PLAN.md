# Plan de Présentation - Culture IA (Puls-Events)

## Slide 1 : Titre
- **Titre** : Culture IA - Assistant Intelligent de Recommandation Culturelle
- **Sous-titre** : POC RAG pour Puls-Events
- **Auteur** : Damien Guesdon
- **Contexte** : Mission freelance pour Puls-Events

## Slide 2 : Contexte et Objectifs
- **Le Besoin** : Puls-Events souhaite enrichir sa plateforme avec un assistant conversationnel.
- **La Problématique** : Comment recommander des événements pertinents et récents en langage naturel ?
- **Les Objectifs du POC** :
    1.  Démontrer la faisabilité technique d'un système RAG (Retrieval-Augmented Generation).
    2.  Utiliser des données réelles (Open Agenda).
    3.  Fournir une API exploitable par les équipes produit.

## Slide 3 : Architecture Technique (Vue d'ensemble)
- **Schéma simplifié** :
    - [Utilisateur] -> [API FastAPI]
    - [API] -> [RAG Chain]
    - [RAG Chain] -> [Vector Store (FAISS)] (Retrieval)
    - [RAG Chain] -> [LLM (Mistral)] (Generation)
    - [Data Pipeline] -> [Open Agenda API] -> [FAISS]

## Slide 4 : Stack Technologique
- **Langage** : Python 3.10
- **LLM** : Mistral AI (Modèle `mistral-tiny` / `mistral-large`) - Choix : Performance/Coût, acteur européen.
- **Vector Database** : FAISS (Facebook AI Similarity Search) - Choix : Efficacité locale, pas de dépendance cloud lourde.
- **Orchestration** : LangChain - Choix : Standard du marché, flexibilité.
- **API** : FastAPI - Choix : Vitesse, documentation auto (Swagger).

## Slide 5 : Pipeline de Données (ETL)
- **Source** : API Open Agenda (Focus : Événements culturels récents).
- **Extraction** : Script `collector.py` (Filtrage date < 1 an).
- **Transformation** : Script `processor.py` (Nettoyage, structuration texte + métadonnées).
- **Chargement** : Indexation vectorielle via Mistral Embeddings.

## Slide 6 : Le Moteur RAG (Retrieval-Augmented Generation)
- **Concept** : Combiner la recherche d'information précise (Retrieval) avec la capacité de synthèse du LLM (Generation).
- **Fonctionnement** :
    1.  Question utilisateur -> Vectorisation.
    2.  Recherche des 3 événements les plus proches dans FAISS.
    3.  Construction du Prompt (Contexte + Question).
    4.  Génération de la réponse par Mistral.

## Slide 7 : Démonstration (Live Demo)
- *[Transition vers la démo live de l'API via Swagger UI ou Script]*
- **Scénario 1** : "Quels sont les événements sur la cuisine sauvage ?" (Test de pertinence).
- **Scénario 2** : Question hors sujet ou sans réponse (Test de robustesse).
- **Scénario 3** : "Reconstruire l'index" (Test du pipeline de données).

## Slide 8 : Évaluation et Résultats
- **Méthodologie** : Utilisation de la librairie **Ragas**.
- **Métriques** :
    - **Fidélité (Faithfulness)** : ~98% (Le modèle respecte le contexte fourni).
    - **Pertinence (Answer Relevancy)** : ~96% (La réponse répond à la question).
- **Jeu de test** : Dataset annoté manuellement (`evaluation_dataset.json`).

## Slide 9 : Conteneurisation et Déploiement
- **Docker** : Application encapsulée dans une image Docker légère (`python:3.10-slim`).
- **Reproductibilité** : Fichier `entrypoint.sh` pour gérer l'initialisation des données au démarrage.
- **CI/CD** : Workflow GitHub Actions pour les tests automatiques à chaque push.

## Slide 10 : Limites et Pistes d'Amélioration
- **Limites actuelles** :
    - Données statiques (nécessite un rebuild pour mettre à jour).
    - Pas de gestion de l'historique de conversation (stateless).
- **Perspectives (V2)** :
    - Mise à jour incrémentale de l'index (CRON).
    - Ajout d'une mémoire conversationnelle.
    - Interface utilisateur Grand Public (Streamlit / React).
    - Filtrage avancé (par date/lieu) *avant* la recherche vectorielle (Hybrid Search).

## Slide 11 : Conclusion
- Le POC est **fonctionnel** et **performant**.
- La stack technique est **robuste** et **évolutive**.
- Prêt pour une intégration dans l'écosystème Puls-Events.
- **Questions / Réponses**
