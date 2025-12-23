from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.core.rag_chain import RAGChain


@pytest.fixture
def mock_rag_chain_instance():
    """Fixture pour un instance de RAGChain mockée pour les tests de logique interne."""
    mock_vector_mgr = patch("src.core.rag_chain.VectorStoreManager").start()
    patch("src.core.rag_chain.ChatMistralAI").start()

    mock_mgr_instance = mock_vector_mgr.return_value
    mock_vectorstore = MagicMock()
    mock_mgr_instance.load_index.return_value = mock_vectorstore

    rag_instance = RAGChain()
    yield rag_instance

    patch.stopall()


def test_get_date_range_from_query_tomorrow(mock_rag_chain_instance):
    """Test l'extraction de la plage de dates pour 'demain'."""
    with patch("src.core.rag_chain.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 22)  # Lundi
        mock_dt.fromtimestamp.side_effect = datetime.fromtimestamp
        mock_dt.timedelta = timedelta

        query = "Que faire demain ?"
        # pylint: disable=protected-access
        date_context = mock_rag_chain_instance._get_date_range_from_query(query)

        assert date_context["type"] == "day"
        assert datetime.fromtimestamp(date_context["start_ts"]).day == 23
        assert datetime.fromtimestamp(date_context["end_ts"]).day == 23
        assert date_context["display"].lower() == "mardi 23 décembre 2025"


def test_get_date_range_from_query_weekend_midweek(mock_rag_chain_instance):
    """Test l'extraction de la plage de dates pour 'ce week-end' en milieu de
    semaine."""
    with patch("src.core.rag_chain.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 22)  # Lundi
        mock_dt.fromtimestamp.side_effect = datetime.fromtimestamp
        mock_dt.timedelta = timedelta

        query = "Que faire ce week-end ?"
        # pylint: disable=protected-access
        date_context = mock_rag_chain_instance._get_date_range_from_query(query)

        saturday = datetime.fromtimestamp(date_context["start_ts"])
        sunday = datetime.fromtimestamp(date_context["end_ts"])

        assert date_context["type"] == "weekend"
        assert saturday.day == 27
        assert saturday.month == 12
        assert sunday.day == 28
        assert sunday.month == 12
        assert date_context["display"].lower() == "samedi 27/12 et dimanche 28/12"


def test_get_date_range_from_query_weekend_saturday(mock_rag_chain_instance):
    """Test l'extraction de la plage de dates pour 'ce week-end' un samedi."""
    with patch("src.core.rag_chain.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 27)  # Samedi
        mock_dt.fromtimestamp.side_effect = datetime.fromtimestamp
        mock_dt.timedelta = timedelta

        query = "Que faire ce week-end ?"
        # pylint: disable=protected-access
        date_context = mock_rag_chain_instance._get_date_range_from_query(query)

        saturday = datetime.fromtimestamp(date_context["start_ts"])
        sunday = datetime.fromtimestamp(date_context["end_ts"])

        assert saturday.day == 27
        assert sunday.day == 28


def test_filter_retrieved_docs(mock_rag_chain_instance):
    """Test le filtrage des documents récupérés par plage de dates."""
    doc1 = Document(
        page_content="event 1",
        metadata={
            "title": "Event 1",
            "start_ts": datetime(2025, 12, 25).timestamp(),
            "end_ts": datetime(2025, 12, 25).timestamp(),
        },
    )
    doc2 = Document(
        page_content="event 2",
        metadata={
            "title": "Event 2",
            "start_ts": datetime(2026, 1, 1).timestamp(),
            "end_ts": datetime(2026, 1, 10).timestamp(),
        },
    )
    doc3 = Document(
        page_content="event 3",
        metadata={
            "title": "Event 3",
            "start_ts": datetime(2024, 1, 1).timestamp(),
            "end_ts": datetime(2024, 1, 5).timestamp(),
        },
    )
    docs = [doc1, doc2, doc3]

    date_context_tomorrow = {
        "start_ts": datetime(2025, 12, 23, 0, 0, 0).timestamp(),
        "end_ts": datetime(2025, 12, 23, 23, 59, 59, 999999).timestamp(),
        "type": "day",
    }
    # pylint: disable=protected-access
    filtered = mock_rag_chain_instance._filter_retrieved_docs(
        docs, date_context_tomorrow
    )
    assert len(filtered) == 0

    date_context_january = {
        "start_ts": datetime(2026, 1, 1, 0, 0, 0).timestamp(),
        "end_ts": datetime(2026, 1, 31, 23, 59, 59, 999999).timestamp(),
        "type": "month",
    }
    # pylint: disable=protected-access
    filtered = mock_rag_chain_instance._filter_retrieved_docs(
        docs, date_context_january
    )
    assert len(filtered) == 1
    assert filtered[0].metadata["title"] == "Event 2"

    date_context_any_future = {
        "start_ts": datetime(2025, 12, 22).timestamp(),  # partir d'aujourd'hui
        "end_ts": float("inf"),
        "type": "any_future",
    }
    # pylint: disable=protected-access
    filtered = mock_rag_chain_instance._filter_retrieved_docs(
        docs, date_context_any_future
    )
    assert len(filtered) == 2
    assert filtered[0].metadata["title"] == "Event 1"
    assert filtered[1].metadata["title"] == "Event 2"
