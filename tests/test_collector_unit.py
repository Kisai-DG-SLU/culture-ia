import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from src.collector import OpenAgendaCollector


# Données simulées pour le filtrage
def mock_event(uid, days_offset):
    """Crée un événement avec une date de fin relative à aujourd'hui."""
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days_offset)
    return {
        "uid": uid,
        "timings": [
            {
                "begin": (end_date - timedelta(hours=2)).isoformat(),
                "end": end_date.isoformat(),
            }
        ],
    }


def test_fetch_events_mock_mode():
    """Test fetch_events quand MOCK_DATA est actif."""
    with patch.dict(os.environ, {"MOCK_DATA": "true"}):
        collector = OpenAgendaCollector()
        events = collector.fetch_events()
        assert len(events) == 1
        assert events[0]["uid"] == 999999
        assert "Mock" in events[0]["title"]["fr"]


def test_fetch_events_api_call():
    """Test fetch_events avec un appel API simulé."""
    # Désactiver le mock data s'il est actif dans l'env global
    with patch.dict(os.environ, {"MOCK_DATA": "false"}), patch(
        "src.collector.requests.get"
    ) as mock_get:

        # Setup du mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"events": [{"uid": 1}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        collector = OpenAgendaCollector(api_key="test_key")
        events = collector.fetch_events()

        assert len(events) == 1
        assert events[0]["uid"] == 1
        mock_get.assert_called_once()
        # Vérifie que l'URL contient bien l'API key et les paramètres requis
        _, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert "key" in params
        assert "includeFields[]" in params
        assert "timings" in params["includeFields[]"]
        assert "relative[]" in params
        assert "current" in params["relative[]"]
        assert params["limit"] == 100


def test_fetch_events_legacy_call():
    """Test fetch_events sans API key (mode legacy)."""
    # On vide OPENAGENDA_API_KEY en plus de désactiver MOCK_DATA
    with patch.dict(
        os.environ, {"MOCK_DATA": "false", "OPENAGENDA_API_KEY": ""}
    ), patch("src.collector.requests.get") as mock_get:

        mock_response = MagicMock()
        mock_response.json.return_value = {"events": [{"uid": 2}]}
        mock_get.return_value = mock_response

        collector = OpenAgendaCollector(api_key=None)  # Pas de clé
        events = collector.fetch_events()

        assert len(events) == 1
        assert events[0]["uid"] == 2
        # Vérifie que l'URL ne contient pas /v2/
        args, _ = mock_get.call_args
        assert "/v2/" not in args[0]


def test_filter_recent_events():
    """Test le filtrage des événements récents."""
    collector = OpenAgendaCollector()

    events = [
        mock_event(1, -400),  # Trop vieux (> 365 jours)
        mock_event(2, -100),  # Passé récent
        mock_event(3, 10),  # Futur
    ]

    filtered = collector.filter_recent_events(events, days=365)

    uids = [e["uid"] for e in filtered]

    assert 1 not in uids
    assert 2 in uids
    assert 3 in uids
    assert len(filtered) == 2


def test_save_to_json(tmp_path):
    """Test la sauvegarde JSON."""
    collector = OpenAgendaCollector()
    events = [{"uid": 123}]
    output_file = tmp_path / "test_events.json"

    collector.save_to_json(events, filename=str(output_file))

    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["uid"] == 123
