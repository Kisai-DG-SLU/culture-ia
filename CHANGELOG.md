# Journal des modifications (Changelog)

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère au [Versionnage Sémantique](https://semver.org/spec/v2.0.0.html).

## [0.0.55] - 2026-01-07
### Corrigé
- Correction de la logique d'auto-merge dans la CI utilisant `gh pr create` et `gh pr merge`.

## [0.0.54] - 2026-01-07
### Changé
- Ajustement du seuil de couverture dans le README.
- Épinglage de l'image de build sur `ubuntu-22.04` pour la stabilité.
### Ajouté
- Ajout des fichiers de présentation (PDF et PPTX) dans `docs/`.

## [0.0.53] - 2026-01-07
### Changé
- Finalisation complète de la documentation.
- Mise à jour des styles de présentation.
- Validation finale de la licence MIT.

## [0.0.52] - 2026-01-07
### Ajouté
- Badges dynamiques dans le `README.md` (Version, CI, Licence).
- Fichier `CHANGELOG.md` pour le suivi des versions.

### Changé
- Correction du badge de licence dans le `README.md` (MIT au lieu de Proprietary).
- Amélioration de la documentation de présentation pour la soutenance.
- Focus sur l'installation Docker dans le `README.md`.

## [0.0.51] - 2026-01-06
### Changé
- Finalisation du rapport technique.
- Restructuration des décisions architecturales.

## [0.0.50] - 2026-01-05
### Ajouté
- Support complet de Docker avec image basée sur Miniconda.
- Pipeline CI/CD automatisé avec gestion des branches et auto-merge.
- Scripts de bump de version.
- Couverture de tests supérieure à 75%.
