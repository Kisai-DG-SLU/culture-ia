# --- Étape 1: Le Constructeur ---
FROM condaforge/mambaforge:latest AS builder

WORKDIR /app

# Copie le fichier de lock
COPY conda-lock.yml .

# Installe conda-lock pour pouvoir utiliser le fichier de lock
RUN mamba install conda-lock -y && \
    conda-lock install --name culture-ia conda-lock.yml && \
    conda clean -afy

# --- Étape 2: L'Image Finale ---
FROM mambaorg/micromamba:latest

# Copie l'environnement depuis le builder
COPY --from=builder /opt/conda/envs/culture-ia /opt/conda/envs/culture-ia

WORKDIR /app

# Configuration de l'environnement
ENV PATH=/opt/conda/envs/culture-ia/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copie le reste de l'application
COPY --from=builder /etc/ssl/certs /etc/ssl/certs
COPY . .

# On s'assure que l'entrypoint est exécutable
USER root
RUN chmod +x entrypoint.sh

# Repasse en utilisateur non-privilégié si nécessaire (micromamba utilise 'mambauser')
USER $MAMBA_USER

EXPOSE 8000
EXPOSE 8501

CMD ["./entrypoint.sh"]
