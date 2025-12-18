import pytest
from unittest.mock import patch, MagicMock
from src.core.rag_chain import RAGChain


@patch("src.core.rag_chain.VectorStoreManager")
@patch("src.core.rag_chain.ChatMistralAI")
def test_rag_chain_initialization(mock_llm, mock_vector_mgr):
    """Test l'initialisation de la chaîne RAG."""
    # Mock du vectorstore pour éviter l'erreur "Vector store not found"
    mock_mgr_instance = mock_vector_mgr.return_value
    mock_vectorstore = MagicMock()
    mock_mgr_instance.load_index.return_value = mock_vectorstore

    chain = RAGChain()

    assert chain.vectorstore == mock_vectorstore
    mock_mgr_instance.load_index.assert_called_once()
    mock_llm.assert_called_once()
    # On vérifie que la chaîne est construite
    assert chain.chain is not None


@patch("src.core.rag_chain.VectorStoreManager")
@patch("src.core.rag_chain.ChatMistralAI")
def test_rag_chain_ask(mock_llm, mock_vector_mgr):
    """Test la méthode ask."""
    # Setup pour init
    mock_mgr_instance = mock_vector_mgr.return_value
    mock_vectorstore = MagicMock()
    mock_mgr_instance.load_index.return_value = mock_vectorstore

    chain = RAGChain()

    # On remplace la vraie chaîne LangChain par un mock pour tester 'ask' isolément
    chain.chain = MagicMock()
    chain.chain.invoke.return_value = "Réponse générée"

    response = chain.ask("Question test")

    assert response == "Réponse générée"
    chain.chain.invoke.assert_called_with("Question test")


@patch("src.core.rag_chain.VectorStoreManager")
def test_rag_chain_init_failure(mock_vector_mgr):
    """Test si l'index n'est pas chargé."""
    mock_mgr_instance = mock_vector_mgr.return_value
    mock_mgr_instance.load_index.return_value = None

    with pytest.raises(
        ValueError, match="Vector store not found. Please run vectorstore.py first."
    ):
        RAGChain()
