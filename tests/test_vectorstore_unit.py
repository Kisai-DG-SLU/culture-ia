import os
import json
from unittest.mock import patch, MagicMock
from src.core.vectorstore import VectorStoreManager


@patch("src.core.vectorstore.MistralAIEmbeddings")
@patch("src.core.vectorstore.HuggingFaceEmbeddings")
def test_get_embeddings_selection(mock_hf, mock_mistral):
    """Test le choix des embeddings selon la clé API."""

    # Cas 1: Clé présente
    with patch.dict(os.environ, {"MISTRAL_API_KEY": "valid_key"}):
        VectorStoreManager()
        mock_mistral.assert_called_once()
        mock_hf.assert_not_called()

    mock_mistral.reset_mock()
    mock_hf.reset_mock()

    # Cas 2: Pas de clé
    with patch.dict(os.environ, {"MISTRAL_API_KEY": ""}):
        VectorStoreManager()
        mock_hf.assert_called_once()
        mock_mistral.assert_not_called()


@patch("src.core.vectorstore.FAISS")
@patch("src.core.vectorstore.RecursiveCharacterTextSplitter")
def test_create_index(mock_splitter, mock_faiss, tmp_path):
    """Test la création de l'index."""
    # Setup
    input_file = tmp_path / "processed_events.json"
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump([{"text": "Event 1", "metadata": {"id": 1}}], f)

    # Mock du splitter qui retourne une liste de docs fictifs
    mock_splitter_instance = mock_splitter.return_value
    mock_splitter_instance.split_documents.return_value = ["doc1", "doc2"]

    # Mock du vectorstore retourné par FAISS
    mock_vectorstore = MagicMock()
    mock_faiss.from_documents.return_value = mock_vectorstore

    # Action
    manager = VectorStoreManager(index_path=str(tmp_path / "faiss_index"))
    # On mock _get_embeddings pour éviter les vrais appels
    manager.embeddings = MagicMock()

    manager.create_index(processed_events_file=str(input_file))

    # Assertions
    mock_splitter.assert_called_once()  # Vérifie qu'on a init le splitter
    mock_splitter_instance.split_documents.assert_called_once()  # Vérifie qu'on a split
    mock_faiss.from_documents.assert_called_once()  # Vérifie la création FAISS
    mock_vectorstore.save_local.assert_called_once()  # Vérifie la sauvegarde


@patch("src.core.vectorstore.FAISS")
def test_load_index(mock_faiss, tmp_path):
    """Test le chargement de l'index."""
    index_path = tmp_path / "faiss_index"
    os.makedirs(index_path)  # Créer le dossier pour simuler l'existence

    manager = VectorStoreManager(index_path=str(index_path))
    manager.embeddings = MagicMock()

    manager.load_index()

    mock_faiss.load_local.assert_called_once()
