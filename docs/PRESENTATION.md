# Présentation de Soutenance - Culture IA

Ce document sert de support pour la présentation orale (slides) et détaille le contenu à exposer.

---

## Slide 1 : Titre & Introduction
**Titre :** Assistant Intelligent de Recommandation Culturelle (Projet 7)
**Sous-titre :** Une approche RAG pour dynamiser la découverte d'événements
**Présenté par :** Damien Guesdon
**Contexte :** Mission pour Puls-Events

*(Discours : Bonjour, je suis Damien Guesdon. Aujourd'hui, je vais vous présenter le POC réalisé pour Puls-Events, visant à créer un assistant virtuel capable de recommander des événements culturels de manière naturelle et pertinente.)*

---

## Slide 2 : Le Besoin & La Problématique
**Contexte :**
- Puls-Events dispose de nombreuses données (OpenAgenda) mais leur exploration via des filtres classiques est limitée.
- Les utilisateurs veulent des recommandations personnalisées ("Quoi faire ce week-end à Paris ?").

**Problématique :**
*Comment permettre à un utilisateur d'interroger une base d'événements en langage naturel tout en garantissant des réponses factuelles et à jour ?*

**Objectifs du POC :**
1.  Connecter des données réelles (API OpenAgenda).
2.  Implémenter une architecture RAG (Retrieval-Augmented Generation).
3.  Fournir une API robuste et testée.

---

## Slide 3 : La Solution Technique : Architecture RAG
*(Schéma d'architecture à afficher)*

**Fonctionnement global :**
1.  **Collecte (ETL)** : Récupération des événements depuis l'API OpenAgenda.
2.  **Vectorisation** : Transformation des textes en vecteurs mathématiques (Embeddings) stockés dans **FAISS**.
3.  **Interrogation** :
    - L'utilisateur pose une question.
    - Le système recherche les 3 événements les plus proches sémantiquement dans FAISS.
    - Le **LLM (Mistral AI)** génère une réponse en utilisant ces événements comme contexte.

---

## Slide 4 : Choix Technologiques (Stack)
Pourquoi ces choix ?

- **Python 3.10** : Standard actuel pour l'IA/Data.
- **Mistral AI (`mistral-tiny`)** :
    - *Pourquoi ?* Modèle français, performant, rapide et moins coûteux que GPT-4 pour cette tâche.
- **FAISS (Facebook AI Similarity Search)** :
    - *Pourquoi ?* Base vectorielle locale, très rapide, ne nécessite pas de serveur externe complexe (idéal pour un POC).
- **FastAPI** :
    - *Pourquoi ?* Asynchrone, performant et génère automatiquement la documentation (Swagger).

---

## Slide 5 : Pipeline de Données & Défi Technique
**Le Processus ETL :**
1.  **Extraction** : API OpenAgenda V2.
2.  **Filtrage** : Exclusion des événements passés (> 1 an).
3.  **Indexation** : Création des embeddings.

**Focus Challenge Technique (La gestion du temps) :**
- *Problème* : L'API OpenAgenda, par défaut, masque les horaires et priorise les vieux événements, rendant le RAG obsolète.
- *Solution* : Configuration avancée de l'API (`includeFields[]=timings`, `relative[]=current,upcoming`) pour forcer la récupération des événements futurs (2025-2026).

---

## Slide 6 : Démonstration (Scénarios)
*(Transition vers la démo live de l'API)*

Nous allons tester 3 cas :
1.  **Recherche Thématique** : "Je cherche une activité autour de la nature et de la cuisine."
    - *Attendu* : L'assistant doit retrouver "Balade découverte et cuisine sauvage".
2.  **Recherche Temporelle** : "Y a-t-il des événements en 2025 ?"
    - *Attendu* : L'assistant doit citer les dates futures récupérées.
3.  **Question Hors-Périmètre** : "Quelle est la capitale de la France ?"
    - *Attendu* : L'assistant doit rester courtois mais se concentrer sur les événements (ou répondre brièvement).

---

## Slide 7 : Résultats & Évaluation
Comment mesurer la qualité ? Utilisation de la librairie **Ragas**.

**Métriques Clés (sur jeu de test) :**
- **Fidélité (Faithfulness) : ~86%**
    - Le modèle n'invente pas d'informations (hallucinations faibles).
- **Pertinence (Relevancy) : ~71%**
    - Les réponses sont directes et utiles.
- **Rappel (Context Recall) : ~75%**
    - Le système retrouve la majorité des informations pertinentes dans la base.

---

## Slide 8 : Qualité Code & Industrialisation
Ce n'est pas qu'un script, c'est un projet logiciel.

- **Tests Unitaires** : Couverture de code > 80% (vérifiée par `pytest`).
- **CI/CD** : Pipeline GitHub Actions qui lance les tests à chaque modification.
- **Docker** : Application livrée sous forme de conteneur, prête à déployer n'importe où.
- **Documentation** : README complet, Rapport Technique et doc API (Swagger).

---

## Slide 9 : Limites & Perspectives
**Limites du POC :**
- Index statique (nécessite un redémarrage pour ingérer de nouveaux événements).
- Pas de mémoire de conversation (chaque question est indépendante).

**Roadmap V2 (Améliorations) :**
1.  **Mise à jour incrémentale** : Tâche planifiée (CRON) pour mettre à jour FAISS la nuit.
2.  **Recherche Hybride** : Combiner mots-clés (BM25) et vecteurs pour plus de précision sur les noms propres.
3.  **Interface UI** : Développer un frontend (Streamlit ou React) pour le grand public.

---

## Slide 10 : Conclusion
En résumé :
- Un système **fonctionnel** qui répond aux exigences de Puls-Events.
- Une architecture **maîtrisée** et **souveraine** (Mistral).
- Une base solide pour l'industrialisation (Docker, Tests, CI).

**Merci de votre attention. Avez-vous des questions ?**