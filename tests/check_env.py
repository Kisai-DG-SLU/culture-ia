# Script de vérification de l'environnement
try:
    import faiss
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from mistralai import Mistral
    print("✅ Environnement de développement validé : Tous les imports critiques sont fonctionnels.")
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    exit(1)
