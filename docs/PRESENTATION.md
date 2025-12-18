# Culture IA - Assistant Intelligent de Recommandation Culturelle

## Slide 1 : Titre

*   **Titre** : Culture IA - Assistant Intelligent de Recommandation Culturelle
*   **Sous-titre** : POC RAG pour Puls-Events
*   **Auteur** : Damien Guesdon
*   **Contexte** : Mission freelance pour Puls-Events

---

## Slide 2 : Contexte et Objectifs

*   **Le Besoin** : Puls-Events souhaite enrichir sa plateforme avec un assistant conversationnel pour recommander des événements culturels.
*   **La Problématique** : Comment fournir des recommandations pertinentes et récentes en langage naturel, basées sur des données dynamiques ?
*   **Les Objectifs du POC** :
    1.  Démontrer la faisabilité technique d'un système RAG (Retrieval-Augmented Generation).
    2.  Utiliser des données réelles et à jour (API Open Agenda).
    3.  Fournir une API REST exploitable par les équipes produit.
    4.  Évaluer objectivement la qualité des réponses générées.

---

## Slide 3 : Architecture Technique (Vue d'ensemble)

*   **Schéma simplifié** :
    *   **Utilisateur** interagit avec l'**API FastAPI**.
    *   L'**API** sollicite la **Chaîne RAG**.
    *   La **Chaîne RAG** effectue un **Retrieval** (recherche) dans le **Vector Store (FAISS)**.
    *   La **Chaîne RAG** utilise un **LLM (Mistral)** pour la **Génération** de réponse.
    *   Une **Data Pipeline** alimente le **Vector Store (FAISS)** à partir de l'**API Open Agenda**.

---

## Slide 4 : Stack Technologique

*   **Langage** : Python 3.10 - Pour sa richesse d'écosystème IA et sa productivité.
*   **LLM (Large Language Model)** : Mistral AI (`mistral-tiny` en production, `mistral-large-latest` pour l'évaluation) - Choix stratégique pour la performance, le coût et l'ancrage européen.
*   **Vector Database** : FAISS (Facebook AI Similarity Search) - Choix pour son efficacité en recherche de similarité locale et sa facilité de déploiement conteneurisé.
*   **Orchestration RAG** : LangChain - Framework standard facilitant l'assemblage de composants LLM.
*   **API REST** : FastAPI - Reconnu pour sa rapidité, ses performances asynchrones et sa documentation interactive automatique (Swagger UI).

---

## Slide 5 : Pipeline de Données (ETL)

*   **Source de Données** : API Open Agenda - Pour accéder à une base riche et régulièrement mise à jour d'événements culturels.
*   **Extraction (`collector.py`)** : Script dédié à la récupération des événements, incluant un filtrage temporel pour ne retenir que les événements de moins d'un an, garantissant la fraîcheur des données.
*   **Transformation (`processor.py`)** : Nettoyage et structuration des données brutes, enrichissement avec des métadonnées pertinentes (lieux, dates, liens) pour améliorer le contexte et la recherche.
*   **Chargement & Indexation** : Vectorisation des textes structurés via les **Mistral Embeddings** et indexation dans **FAISS**, créant une base de données optimisée pour la recherche sémantique.

---

## Slide 6 : Le Moteur RAG (Retrieval-Augmented Generation)

*   **Concept Fondamental** : Le RAG combine la précision de la recherche d'informations dans une base de connaissances (Retrieval) avec la capacité de génération de texte fluide et contextuelle d'un LLM (Generation).
*   **Fonctionnement Détaillé** :
    1.  **Question Utilisateur** : La requête de l'utilisateur est reçue et vectorisée.
    2.  **Recherche Contextuelle (Retrieval)** : L'embedding de la question est utilisé pour interroger FAISS et récupérer les **3 événements les plus sémantiquement proches** du Vector Store.
    3.  **Augmentation du Prompt** : Les informations pertinentes des événements récupérés sont insérées comme "contexte" dans un **Prompt structuré**.
    4.  **Génération de la Réponse** : Le LLM **Mistral** reçoit le prompt augmenté et génère une réponse concise, pertinente et factuellement fondée sur le contexte fourni, évitant ainsi les hallucinations.

---

## Slide 7 : Démonstration (Live Demo)

*   *[Transition vers la démo live de l'API FastAPI, idéalement via l'interface Swagger UI (`/docs`) pour une expérience interactive.]*

*   **Scénario 1 : Recherche de Pertinence**
    *   **Question** : "Quels sont les événements sur la cuisine sauvage ?"
    *   **Attendu** : Le système identifie et synthétise les événements liés à la "cuisine sauvage" et aux plantes comestibles, en citant les lieux et dates.

*   **Scénario 2 : Robustesse et Gestion de l'Inconnu**
    *   **Question** : "Quel est le programme du cinéma Grand Rex ce soir ?"
    *   **Attendu** : Le système doit poliment indiquer qu'il n'a pas cette information dans sa base de données actuelle, démontrant sa capacité à gérer les requêtes hors contexte sans inventer.

*   **Scénario 3 : Rebuilding l'Index (Opérationnel)**
    *   **Action** : Appel à l'endpoint `/rebuild`.
    *   **Attendu** : Le système relance le pipeline de données (collecte, traitement, indexation), montrant sa capacité à mettre à jour dynamiquement sa base de connaissances.

---

## Slide 8 : Évaluation et Résultats (Ragas)

*   **Méthodologie** : Utilisation de la bibliothèque spécialisée **Ragas** (RAG Assessment) pour une évaluation objective et automatisée de la qualité du système RAG.
*   **Jeu de Test** : Basé sur un dataset de questions/réponses annoté manuellement (`evaluation_dataset.json`), servant de "vérité terrain".
*   **Métriques Clés (scores de 0 à 1) et Résultats Réels** :
    *   **Fidélité (Faithfulness)** : **~86%** - Indique que la réponse générée est fortement basée sur le contexte récupéré, réduisant les hallucinations.
    *   **Pertinence de la Réponse (Answer Relevancy)** : **~71%** - Mesure si la réponse est directement liée à la question posée.
    *   **Rappel du Contexte (Context Recall)** : **~75%** - Évalue si les informations pertinentes de la vérité terrain sont bien présentes dans le contexte récupéré.
    *   **Précision du Contexte (Context Precision)** : **~50%** - Mesure la proportion d'informations pertinentes dans le contexte récupéré par rapport au bruit.

---

## Slide 9 : Conteneurisation et Déploiement

*   **Docker** : L'intégralité de l'application est encapsulée dans une image Docker légère, basée sur `python:3.10-slim`, assurant une portabilité et une isolation parfaites.
*   **Reproductibilité & Auto-Initialisation** : Le script `entrypoint.sh` gère l'initialisation de l'environnement, y compris la construction automatique de l'index FAISS au démarrage du conteneur si celui-ci n'est pas déjà présent, rendant le déploiement "clés en main".
*   **Intégration Continue (CI/CD)** : Un workflow robuste avec GitHub Actions est mis en place pour :
    *   Lancer les tests unitaires et de couverture à chaque push sur les branches.
    *   Assurer une couverture de code > 70%.
    *   Garantir la qualité du code (formatage Black, linting Pylint) via des pre-commit hooks.
    *   Déployer automatiquement les rapports de couverture sur GitHub Pages et les versions.

---

## Slide 10 : Limites et Pistes d'Amélioration

*   **Limites Actuelles du POC** :
    *   **Données Statiques** : L'index FAISS nécessite une reconstruction manuelle ou planifiée pour intégrer de nouvelles données d'Open Agenda.
    *   **Sans Mémoire** : Le système est "stateless" ; il ne garde pas en mémoire l'historique de conversation, traitant chaque question indépendamment.

*   **Perspectives et Prochaines Étapes (Vision V2)** :
    *   **Mise à Jour Incrémentale** : Implémentation d'un CRON ou d'un mécanisme asynchrone pour des mises à jour régulières et automatiques de l'index FAISS sans interruption de service.
    *   **Mémoire Conversationnelle** : Intégration d'un mécanisme de gestion de l'historique pour des dialogues plus fluides et la prise en compte du contexte des questions précédentes.
    *   **Interface Utilisateur Avancée** : Développement d'une interface graphique conviviale (ex: Streamlit, React) pour une expérience utilisateur enrichie.
    *   **Recherche Hybride** : Combiner la recherche sémantique avec des filtres par mots-clés, dates ou localisation pour une précision accrue du retrieval.

---

## Slide 11 : Conclusion

*   **Le POC est un Succès** : Le système d'assistant intelligent RAG est fonctionnel, performant et démontre une réelle valeur ajoutée pour la recommandation d'événements culturels.
*   **Stack Technique Robuste** : L'architecture mise en place est solide, moderne et conçue pour être évolutive.
*   **Prêt pour l'Intégration** : Le projet est désormais prêt à être intégré et enrichi au sein de l'écosystème de Puls-Events.
*   **Questions / Réponses** : Nous sommes à votre disposition pour toute question.
