# Rapport Technique - POC Culture IA (Puls-Events)

## 1. Introduction
Ce rapport présente la conception et la réalisation du Proof of Concept (POC) d'un assistant intelligent de recommandation culturelle utilisant une architecture **RAG (Retrieval-Augmented Generation)**. L'objectif est de permettre aux utilisateurs d'interroger les événements de la plateforme **Open Agenda** en langage naturel.

## 2. Architecture du Système
L'architecture repose sur cinq piliers principaux :
1.  **Ingestion & Prétraitement** : Collecte des données via l'API OpenAgenda, filtrage temporel (événements de moins d'un an) et structuration.
2.  **Base de Données Vectorielle** : Utilisation de **FAISS** pour stocker les représentations sémantiques (embeddings) des événements.
3.  **Chaîne RAG** : Orchestration via **LangChain** pour lier la recherche vectorielle à la génération de texte.
4.  **Interface API** : Exposition des fonctionnalités via **FastAPI**.
5.  **Interface Frontend** : Dashboard interactif développé avec **Streamlit** pour la démonstration et le pilotage.

## 3. Choix Technologiques et Modèles
- **LLM : Mistral AI (`mistral-tiny`)**
    - *Raison* : Modèle performant, souverain (Français) et offrant un excellent compromis latence/précision pour un POC.
- **Embeddings : Mistral Embeddings** (avec fallback Local Sentence-Transformers)
    - *Raison* : Cohérence avec le LLM pour la similarité sémantique.
- **Vector Store : FAISS (CPU)**
    - *Raison* : Bibliothèque extrêmement rapide pour la recherche de plus proches voisins, facile à conteneuriser sans dépendance GPU.
- **Micro-framework API : FastAPI**
    - *Raison* : Performance asynchrone et documentation Swagger interactive intégrée.
- **Frontend : Streamlit**
    - *Raison* : Prototypage rapide d'interfaces Data/IA 100% Python, idéal pour visualiser les métriques Ragas (Graphiques Plotly) et chatter avec le bot.

## 4. Résultats et Évaluation
La qualité du système a été mesurée à l'aide de la bibliothèque **Ragas** sur un jeu de tests annoté de 4 questions de référence.

**Métriques observées (Après optimisation finale) :**
- **Fidélité (Faithfulness)** : ~82% (Amélioration nette via un prompt plus contraignant).
- **Pertinence de la réponse** : ~73%
- **Rappel (Context Recall)** : ~75% (Stable avec k=2).
- **Précision du Retrieval (Context Precision)** : ~50%.
    - *Analyse* : Ce score est mathématiquement contraint par la taille du jeu de données (2 événements). Le système étant configuré pour récupérer 2 documents (`k=2`), une requête pertinente pour un seul événement ramènera forcément 50% de bruit (1 pertinent / 2 récupérés). Ce n'est pas un défaut du modèle mais une caractéristique du POC.

## 5. Défis Techniques et Résolution

### La Collecte Temporelle (API OpenAgenda V2)
Un défi majeur rencontré lors du développement a été la récupération fiable des événements **futurs** pour garantir la pertinence des recommandations.

**Problème observé :**
Initialement, le collecteur ne récupérait que des événements passés (2023) ou rejetait tous les événements. L'analyse a révélé deux comportements par défaut de l'API V2 d'OpenAgenda :
1.  **Absence de dates :** Par défaut, l'API ne renvoie pas le champ `timings` (horaires détaillés) dans les listes d'événements pour optimiser la bande passante. Notre filtre temporel rejetait donc ces événements considérés comme "sans date".
2.  **Tri par défaut :** Sans filtre explicite, l'API tend à renvoyer des événements passés ou non pertinents en tête de liste.

**Solution technique implémentée :**
Nous avons dû configurer finement les appels API pour forcer la récupération des données nécessaires :
- **Extraction explicite des champs** : Ajout du paramètre `includeFields[]=timings` pour obliger l'API à renvoyer les dates de chaque événement.
- **Filtrage côté API** : Utilisation des paramètres `relative[]=["current", "upcoming"]` pour demander explicitement les événements en cours et à venir.
- **Filtrage côté Applicatif** : Maintien d'une validation stricte (date de fin > il y a 1 an) pour une double sécurité.

Cette approche a permis de passer de 0 événement pertinent récupéré à une base de données à jour contenant les événements programmés jusqu'en 2026.

### Optimisation de la précision et de la fidélité
Pour garantir une expérience utilisateur fiable, nous avons implémenté deux stratégies d'optimisation avancées :

1.  **Stratégie "Small-to-Big Retrieval" Temporelle** : 
    - Le moteur de recherche vectoriel utilise un champ `text` dense contenant le titre, la description et **l'intégralité des dates futures** de l'événement. Cela permet une recherche sémantique et par mots-clés infaillible sur n'importe quelle session programmée (ex: "événements en juillet 2026").
    - Le LLM reçoit quant à lui le `full_context` stocké dans les métadonnées, contenant l'intégralité des dates formatées (Passé et Futur).

2.  **Gestion Rigoureuse des Hallucinations Temporelles** :
    - Le processeur de données classe désormais explicitement les dates en deux catégories : **"DATES À VENIR"** et **"ARCHIVES"**.
    - Le Prompt système du RAG a été durci pour interdire formellement l'utilisation des archives et forcer la comparaison avec la date système courante fournie dynamiquement à chaque requête.

Ces ajustements ont permis d'éliminer les hallucinations où le bot proposait des dates passées ou inventait des créneaux inexistants.

## 6. Déploiement
Le système est entièrement conteneurisé via **Docker**.
- **Image de base** : `continuumio/miniconda3` pour garantir une compatibilité parfaite avec l'environnement de développement Conda.
- L'image inclut un script d'entrée (`entrypoint.sh`) qui lance à la fois l'API (port 8000) et le frontend Streamlit (port 8501).
- Une pipeline de **CI (GitHub Actions)** utilisant Conda a été mise en place pour valider les tests unitaires et la qualité du code à chaque modification.

## 7. Pistes d'Amélioration
1.  **Recherche Hybride** : Combiner la recherche sémantique avec des filtres par mots-clés ou par dates pour une précision accrue.
2.  **Interface Utilisateur** : Développer une interface Streamlit pour une démo encore plus engageante.
3.  **Mise à jour à chaud** : Implémenter un système de mise à jour incrémentale de l'index sans redémarrage de l'API.
4.  **Gestion de la mémoire** : Ajouter une fenêtre de contexte conversationnel pour permettre des questions de suivi (ex: "Et c'est gratuit ?").

---
*Damien Guesdon - Data Scientist Freelance*
