#!/bin/bash

# Vérifier si l'index FAISS existe
if [ ! -d "data/faiss_index" ]; then
    echo "⚠️  Index FAISS non trouvé. Lancement de la reconstruction..."
    
    # 1. Collecte
    echo "1. Collecte des données..."
    python src/collector.py
    
    # 2. Processing
    echo "2. Traitement des données..."
    python src/processor.py
    
    # 3. Vectorisation
    echo "3. Création de l'index vectoriel..."
    python src/core/vectorstore.py
    
    echo "✅ Index construit avec succès."
else
    echo "✅ Index FAISS trouvé."
fi

# Fonction pour arrêter proprement les processus
cleanup() {
    echo "🛑 Arrêt en cours..."
    pkill -P $$
    exit 0
}

# Capturer SIGINT (Ctrl+C) et SIGTERM
trap cleanup SIGINT SIGTERM

# Lancement de l'API en background
echo "🚀 Lancement de l'API..."
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 &

# Lancement du Frontend en background
echo "🎨 Lancement du Frontend Streamlit..."
streamlit run src/frontend/ui.py --server.port 8501 --server.address 0.0.0.0 &

# Attendre indéfiniment
wait
