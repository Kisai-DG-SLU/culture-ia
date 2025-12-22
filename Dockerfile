FROM continuumio/miniconda3

WORKDIR /app

# Installation des outils de compilation basiques (parfois nécessaires pour certaines libs pip)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier d'environnement
COPY environment.yml .

# Création de l'environnement Conda
# On utilise --prune pour nettoyer les caches et réduire la taille
RUN conda env create -f environment.yml && conda clean -afy

# Activation de l'environnement par défaut dans le path
# Cela évite d'avoir à faire "conda activate" à chaque commande
ENV PATH=/opt/conda/envs/culture-ia/bin:$PATH
ENV PYTHONPATH=/app

# Copie du reste de l'application
COPY . .

# Exposition des ports API et Streamlit
EXPOSE 8000
EXPOSE 8501

# Script de démarrage
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]