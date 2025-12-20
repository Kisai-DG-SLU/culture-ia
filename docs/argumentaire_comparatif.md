# Argumentaire Comparatif : Projet Culture-IA vs Projet Recette (Personnel)

## Contexte

Le projet académique "Culture-IA" a permis une solide introduction aux concepts du RAG (Retrieval-Augmented Generation) avec une stack classique et performante (Mistral AI, FAISS). Cependant, l'expérience avec ce projet a mis en lumière certaines limites des solutions simples pour des cas d'usage plus complexes, menant à l'exploration d'architectures plus robustes sur un projet personnel ("Recette").

---

## Le problème : Les limites d'un RAG "simple" avec FAISS

Dans le projet `culture-ia`, nous utilisons FAISS pour l'indexation et la recherche vectorielle. FAISS est un outil formidable, optimisé pour la vitesse de recherche de similarités sémantiques dans un grand volume de vecteurs en mémoire. Par exemple, si l'on pose une question comme "Quels sont les événements musicaux ce week-end ?", FAISS est très efficace pour trouver les documents (événements) dont le sens est le plus proche de la question.

**MAIS...** il présente une limite majeure pour des applications réelles : il est intrinsèquement "aveugle" aux métadonnées structurées lors de la phase de recherche. Si l'on souhaite affiner une recherche sémantique avec des critères stricts (ex: "un événement musical *gratuit* qui se termine *après 20h* et qui a lieu à *Paris*"), FAISS seul ne peut pas gérer ces filtres directement et efficacement au moment du *retrieval*. Le processus consisterait à :
1.  Récupérer une large liste de résultats sémantiquement pertinents via FAISS.
2.  Appliquer ensuite des filtres programmatiques en Python sur ces résultats.
Cette approche peut être lente et peu optimale, car des documents sémantiquement pertinents mais ne respectant pas les filtres stricts sont tout de même récupérés inutilement.

---

## La solution : La recherche Hybride avec pgvector

Pour mon projet personnel "Recette", ce type de limitation était inacceptable. J'ai dû pouvoir formuler des requêtes complexes combinant sens et contraintes structurées :

> "Je veux une recette **saine et rapide pour ce soir** (recherche sémantique) qui soit aussi **végétarienne** et **sans gluten** (filtres stricts sur métadonnées)."

Pour résoudre ce défi, j'ai remplacé FAISS par **PostgreSQL et son extension `pgvector`**.

**Pourquoi c'est une solution supérieure pour ce cas d'usage :**
`pgvector` permet de stocker les vecteurs d'embeddings directement dans une table PostgreSQL. Cela ouvre la porte à des "requêtes hybrides" où la recherche vectorielle (similitude sémantique) est combinée de manière native avec le filtrage traditionnel de base de données (SQL).

### Exemple de requête hybride (pseudo-code) :

```sql
SELECT *
FROM recettes
WHERE vegetarien = TRUE
  AND sans_gluten = TRUE           -- Filtres SQL stricts sur métadonnées
ORDER BY embedding <-> 'vecteur_de_ma_question' -- Recherche vectorielle (similitude cosinus)
LIMIT 10;
```

---

## Comparaison des Stratégies RAG

| Concept                 | Projet École (Culture-IA)            | Projet Personnel (Recette)               | Avantage mis en évidence             |
| :---------------------- | :----------------------------------- | :--------------------------------------- | :----------------------------------- |
| **Embeddings**          | Mistral Embed (performant pour le FR) | Google Gemini Embeddings                 | Polyvalence et adaptabilité aux fournisseurs. Exploration d'offres multimodales. |
| **Vector Store**        | FAISS (Local, rapide en mémoire)     | PostgreSQL + `pgvector` (Cloud, hybride) | Maîtrise de solutions industrielles plus robustes, scalables et permettant des requêtes complexes. |
| **LLM**                 | Mistral Large / Medium               | Google Gemini Pro / Flash                | Agnosticisme vis-à-vis des modèles. Capacité à intégrer différents LLM selon les besoins (coût, performance, fonctionnalités). |
| **Architecture**        | PoC Monolithique (API locale)        | Microservices Cloud-Native (Neon, Cloudinary, Hugging Face) | Passage d'un PoC à une architecture distribuée, démontrant la compréhension des enjeux de production. |
| **Interface**           | API FastAPI seule                    | Streamlit (Frontend interactif)          | Capacité à construire des expériences utilisateur complètes et engageantes. |
| **CI/CD**               | CI basique (tests)                   | CI/CD multi-environnements (Dev/Test/Prod) | Maîtrise des pratiques DevOps avancées pour le déploiement continu. |

---

## L'argumentaire clé pour la soutenance

> "Cette expérience m'a appris qu'au-delà de la seule puissance d'un LLM, c'est **l'architecture globale des données et du système** qui fait la différence en production. Sur `culture-ia`, nous avons posé les bases du RAG. Mais avec `recette`, j'ai exploré comment intégrer cette intelligence dans une stack complète et moderne, capable de gérer des **requêtes hybrides complexes** (sémantique + filtres stricts) et de s'intégrer dans un écosystème **Cloud-Native**. Cela démontre ma capacité à choisir et implémenter les bonnes solutions techniques en fonction des contraintes et des ambitions d'un projet réel."
