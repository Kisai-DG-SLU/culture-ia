import os
from src.core.vectorstore import VectorStoreManager


def test_retrieval_efficiency():
    # S'assure que l'index existe (sinon le crée avec les données mock actuelles)
    manager = VectorStoreManager()
    if not os.path.exists(manager.index_path):
        manager.create_index()

    vectorstore = manager.load_index()
    assert vectorstore is not None

    # Test de recherche
    query = "cuisine sauvage"
    # On cherche les 2 docs les plus pertinents
    results = vectorstore.similarity_search(query, k=2)

    assert len(results) > 0
    # Vérifie que le premier résultat est pertinent (contient "cuisine" ou "sauvage")
    content = results[0].page_content.lower()
    assert "cuisine" in content or "sauvage" in content
