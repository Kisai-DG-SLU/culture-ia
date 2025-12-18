#!/bin/bash
set -e

# Récupérer le dernier tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Latest tag: $LATEST_TAG"

# Parser la version (vX.Y.Z)
VERSION=${LATEST_TAG#v}
IFS='.' read -ra ADDR <<< "$VERSION"
MAJOR=${ADDR[0]}
MINOR=${ADDR[1]}
PATCH=${ADDR[2]}

# Incrémenter le patch
NEW_PATCH=$((PATCH + 1))
NEW_TAG="v$MAJOR.$MINOR.$NEW_PATCH"

echo "New version: $NEW_TAG"

# Configurer git pour le tag
git config user.name "GitHub Actions"
git config user.email "actions@github.com"

# Créer le tag et le pousser
git tag -a "$NEW_TAG" -m "Auto-bump version to $NEW_TAG"
git push origin "$NEW_TAG"
echo "new_tag=$NEW_TAG" >> "$GITHUB_OUTPUT"
