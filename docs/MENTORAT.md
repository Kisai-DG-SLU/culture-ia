# 📋 Revue de Projet Finale : Culture IA (Étapes 1 à 6)

**Document de préparation au mentorat et à la soutenance**
**Statut :** 🚀 Prêt pour livraison / Architecture Industrialisée

---

## 🏗️ Étape 1 : Environnement & Qualité (Validé)
- **Objectif** : Cadre reproductible et sécurisé.
- **Industrialisation** : Utilisation d'un `Makefile` pour automatiser l'installation et les tests.
- **Qualité de code** : Mise en place de **Pre-commit hooks** (Black pour le formatage, Pylint pour la qualité). Le code est bloqué s'il n'est pas "propre".
- **CI/CD** : Pipeline GitHub Actions qui valide les tests et la couverture (> 70%) à chaque push.
- **Sécurité** : Secrets gérés via `.env` (non versionné) et modèle `.env.template`.

---

## 🧹 Étape 2 : Collecte et Prétraitement (Validé & Optimisé)
- **Objectif** : Récupérer et structurer les données.
- **API OpenAgenda V2** : Paramétrage avancé (`includeFields`, `relative`) pour garantir la récupération des événements **futurs (2025-2026)**.
- **Résolution de Problème (Storytelling Soutenance)** : Expliquer comment l'analyse des réponses API vides a conduit à découvrir que les dates étaient masquées par défaut, et comment cela a été corrigé.
- **Nettoyage** : Structuration sémantique des données (Titre + Description + Lieu + Dates) pour maximiser la pertinence.
- **💡 Note Technique (Justification)** : Pas de "Pandas" car le JSON imbriqué d'OpenAgenda est plus efficace à traiter en Python natif (plus léger et plus rapide pour ce volume).

---

## 🧠 Étape 3 : Vectorisation & Indexation (Validé)

### ✂️ Stratégie de Chunking
Notre approche est **hybride et sécurisée** :
1.  **Par défaut (Sémantique)** : 1 Événement = 1 Vecteur. Préserve l'unité de l'information.
2.  **Sécurité (Technique)** : `RecursiveCharacterTextSplitter` (max 1000 chars) avec un **recouvrement (overlap) de 200 caractères**.
    - *Pourquoi le recouvrement ?* Pour garantir qu'aucune information n'est perdue à la "frontière" entre deux blocs. Cela permet de conserver le contexte sémantique des phrases qui seraient autrement coupées en deux.
    - *Impact* : Meilleure précision lors de la recherche (Retrieval) car le sens est maintenu même sur les textes longs.

### 📍 Comprendre l'Embedding (Le concept pour le Jury)
*Question : C'est quoi un embedding ? Faut-il comprendre le réseau neuronal ?*
**Réponse :** Non, c'est un **GPS des mots**.
- Le modèle transforme un texte en coordonnées mathématiques.
- Les textes ayant le même **sens** sont géographiquement **proches** dans cet espace.
- *Exemple* : "Cuisine sauvage" et "Plantes comestibles" sont voisins mathématiquement.

### 💎 Architecture Hybride (Mistral / Local)
Le système est capable de fonctionner de deux manières pour la vectorisation :
1.  **Principal (Cloud)** : Mistral AI Embeddings.
2.  **Fallback (Local)** : HuggingFace `all-MiniLM-L6-v2` (**100% Local sur le Mac**).
    - *Avantages* : Gratuité, Confidentialité, Fonctionne hors-ligne.

---

## 🤖 Étape 4 & 5 : Chatbot RAG & API (Validé)
- **Orchestration** : LangChain lie FAISS (le bibliothécaire) et Mistral (le cerveau).
- **Prompt Engineering** :
    - **Persona** : "Tu es un assistant expert..."
    - **Anti-Hallucination** : "Réponds UNIQUEMENT avec le contexte."
    - **Conscience Temporelle** : Injection de la date du jour (`"Nous sommes le..."`) pour éviter de proposer des événements passés.
- **API FastAPI** : Interface moderne avec documentation Swagger (`/docs`) et endpoint de reconstruction (`/rebuild`) avec Hot-Reload (mise à jour sans redémarrage).
- **Évaluation Ragas** : Mesure scientifique de la fidélité et de la pertinence.
    - *Résultats* : Fidélité (~82%), Rappel (~75%).
    - *Analyse Précision (50%)* : Identifié comme un artefact structurel (Dataset de 2 événements vs k=2). Le "bruit" est mathématiquement inévitable ici mais serait dilué avec plus de données.

---

## 📦 Étape 6 : Docker & Démo Live

### 🐳 Docker
- Le conteneur est "intelligent" (`entrypoint.sh`) : il détecte l'absence de données au démarrage et lance automatiquement la collecte et l'indexation.

### 🧪 Démo du "Mode Local" (HuggingFace)
Pour prouver la robustesse (fallback) sans toucher aux fichiers de config :

**La commande magique :**
```bash
MISTRAL_API_KEY=none PYTHONPATH=. .venv/bin/python src/core/vectorstore.py
```

**L'explication :**
"Je simule une panne de l'API Mistral. Le système le détecte et bascule instantanément sur le modèle local. Vous voyez les barres de téléchargement (la première fois) puis l'indexation réussie."

---

## 💡 Conseils pour la Soutenance

1.  **Lancez Docker en avance** : `make docker-build` dès maintenant, puis `make docker-run` juste avant la démo.
2.  **Le RAG expliqué à un enfant** : "C'est comme un examen à livre ouvert. Le LLM (l'élève) ne répond pas par cœur, il doit chercher la réponse dans le manuel (l'Agenda) que je lui donne."
3.  **Mettez en avant l'industrialisation** : Insistez sur la CI/CD, les tests automatiques et le Docker. C'est ce qui différencie un "bricolage" d'un projet "Ingénieur".
