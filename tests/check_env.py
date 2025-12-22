# Script de vérification de l'environnement
import sys

try:
    # pylint: disable=unused-import
    import faiss
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from mistralai import Mistral

    print(
        "✅ Environnement de développement validé : Tous les imports critiques sont fonctionnels."
    )
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    sys.exit(1)
