# Aide à l'Auto-Évaluation - Projet Culture IA

Utilisez cette liste pour vérifier vos livrables avant la soutenance.

## 1. Environnement & Reproductibilité
- [x] Python 3.8+ utilisé.
- [x] `environment.yml` présent et complet (gestion via Conda).
- [x] `README.md` expliquant l'installation (Docker/Conda) et l'utilisation.
- [x] Utilisation de variables d'environnement (`.env`) pour les clés API.
- [x] Pipeline CI (GitHub Actions) fonctionnelle.

## 2. Prétraitement des données
- [x] Données récupérées via l'API Open Agenda.
- [x] Filtrage par localisation et période (< 1 an).
- [x] Données structurées (JSON) avec métadonnées (lieux, dates, liens).

## 3. Stockage Vectoriel (FAISS)
- [x] Utilisation de LangChain pour interagir avec FAISS.
- [x] Découpage des textes en chunks (`RecursiveCharacterTextSplitter`).
- [x] Index sauvegardé localement.
- [x] Tests unitaires validant la recherche sémantique.

## 4. Construction du RAG
- [x] Orchestration via LangChain.
- [x] Utilisation du LLM Mistral.
- [x] Prompt optimisé pour éviter les hallucinations.
- [x] Évaluation automatisée via Ragas.

## 5. API REST (FastAPI)
- [x] Endpoint `POST /ask` opérationnel.
- [x] Endpoint `POST /rebuild` opérationnel.
- [x] Documentation Swagger accessible sur `/docs`.
- [x] Script de test fonctionnel (`tests/test_api_unit.py`) présent.

## 6. Déploiement & Présentation
- [x] Dockerfile fonctionnel.
- [x] Script d'initialisation automatique (`entrypoint.sh`).
- [x] Plan de présentation PowerPoint prêt (`docs/SLIDES_PLAN.md`).
- [x] Rapport technique complet (`docs/RAPPORT_TECHNIQUE.md`).
