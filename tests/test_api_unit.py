import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.app import app

# On doit mocker RAGChain avant que app ne soit importé/utilisé si possible,
# mais comme TestClient charge app, le module est déjà exécuté.
# On va donc patcher l'objet rag_chain directement dans le module app.


@pytest.fixture
def client():
    return TestClient(app)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API Culture IA !"}


@patch("src.api.app.rag_chain")
def test_ask_question_nominal(mock_rag, client):
    """Test nominal de /ask."""
    mock_rag.ask.return_value = "Réponse mockée"

    response = client.post("/ask", json={"question": "Test"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Réponse mockée"}
    mock_rag.ask.assert_called_with("Test")


def test_ask_question_empty(client):
    """Test question vide."""
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
    assert "vide" in response.json()["detail"]


@patch("src.api.app.rag_chain")
def test_ask_rag_not_initialized(mock_rag, client):
    """Test erreur 503 si RAGChain est None."""
    # On force rag_chain à None
    with patch("src.api.app.rag_chain", None):
        response = client.post("/ask", json={"question": "Test"})
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"]


@patch("src.api.app.rag_chain")
def test_ask_internal_error(mock_rag, client):
    """Test erreur 500 si le RAG plante."""
    mock_rag.ask.side_effect = Exception("Boom")

    response = client.post("/ask", json={"question": "Test"})
    assert response.status_code == 500
    assert "Boom" in response.json()["detail"]


@patch("src.api.app.OpenAgendaCollector")
@patch("src.api.app.EventProcessor")
@patch("src.api.app.VectorStoreManager")
@patch("src.api.app.RAGChain")  # Pour le reload
def test_rebuild_index(mock_rag_cls, mock_vector, mock_proc, mock_coll, client):
    """Test de la route /rebuild."""

    # Setup mocks
    mock_collector = mock_coll.return_value
    mock_collector.fetch_events.return_value = []

    response = client.post("/rebuild")

    assert response.status_code == 200
    assert "reconstruit avec succès" in response.json()["message"]

    # Vérifie que toute la chaîne a été appelée
    mock_collector.fetch_events.assert_called_once()
    mock_collector.save_to_json.assert_called()
    mock_proc.return_value.process.assert_called_once()
    mock_vector.return_value.create_index.assert_called_once()
    # Vérifie que RAGChain a été réinstancié
    mock_rag_cls.assert_called()


@patch("src.api.app.OpenAgendaCollector")
def test_rebuild_index_error(mock_coll, client):
    """Test erreur 500 dans /rebuild."""
    mock_coll.side_effect = Exception("Rebuild fail")

    response = client.post("/rebuild")
    assert response.status_code == 500
    assert "Rebuild fail" in response.json()["detail"]
