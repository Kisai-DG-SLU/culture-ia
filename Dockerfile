# --- Étape 1: Le Constructeur ---
FROM condaforge/mambaforge:latest AS builder

WORKDIR /app

# Copie le fichier de lock
COPY conda-lock.yml .

# Configuration pour éviter les timeouts (IncompleteRead) lors des gros téléchargements
RUN conda config --set remote_read_timeout_secs 300 && \
    conda config --set remote_connect_timeout_secs 60 && \
    conda config --set ssl_verify true

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

# Copie sélective des fichiers nécessaires (évite d'inclure les fichiers privés/locaux)
COPY --from=builder /etc/ssl/certs /etc/ssl/certs
COPY src/ src/
COPY tests/ tests/
COPY scripts/ scripts/
COPY README.md Makefile entrypoint.sh environment.yml conda-lock.yml ./

# On s'assure que l'entrypoint est exécutable
USER root
RUN chmod +x entrypoint.sh

# Repasse en utilisateur non-privilégié si nécessaire (micromamba utilise 'mambauser')
USER $MAMBA_USER

EXPOSE 8000
EXPOSE 8501

CMD ["./entrypoint.sh"]