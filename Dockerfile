# --- Étape 1: Le Constructeur ---
# Utilise mambaforge pour créer l'environnement rapidement.
# Cette étape contiendra tous les outils de build et sera lourde, mais temporaire.
FROM condaforge/mambaforge AS builder

WORKDIR /app

# Copie uniquement le fichier de lock pour une mise en cache optimale
COPY conda-lock.yml .

# Crée l'environnement à partir du fichier de lock
# Le nom de l'environnement est crucial pour le retrouver plus tard
RUN mamba create --name culture-ia --file conda-lock.yml && conda clean -afy


# --- Étape 2: L'Image Finale ---
# Part d'une image miniconda légère qui ne contient que le strict nécessaire
FROM continuumio/miniconda3

# Le nom de l'environnement doit correspondre à celui créé dans l'étape 'builder'
ENV ENV_NAME=culture-ia

# Copie l'environnement Conda complet depuis l'étape 'builder'
# C'est beaucoup plus rapide que de le recréer
COPY --from=builder /opt/conda/envs/$ENV_NAME /opt/conda/envs/$ENV_NAME

WORKDIR /app

# Activation de l'environnement par défaut dans le path
ENV PATH=/opt/conda/envs/$ENV_NAME/bin:$PATH
ENV PYTHONPATH=/app

# Copie le code de l'application
# Cette couche sera la seule à être reconstruite lors des changements de code
COPY . .

# Exposition des ports API et Streamlit
EXPOSE 8000
EXPOSE 8501

# Le script de démarrage n'a pas besoin d'être copié séparément s'il est dans le `.`
# On s'assure qu'il est exécutable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]