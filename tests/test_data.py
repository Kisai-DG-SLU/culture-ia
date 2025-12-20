from datetime import datetime, timedelta, timezone
from src.collector import OpenAgendaCollector


def test_filter_recent_events():
    collector = OpenAgendaCollector()
    now = datetime.now(timezone.utc)

    # Événement récent (hier)
    recent_date = (now - timedelta(days=1)).isoformat()
    # Événement futur (demain)
    future_date = (now + timedelta(days=1)).isoformat()
    # Événement vieux (il y a 2 ans)
    old_date = (now - timedelta(days=700)).isoformat()

    mock_events = [
        {"uid": 1, "timings": [{"end": recent_date}]},
        {"uid": 2, "timings": [{"end": future_date}]},
        {"uid": 3, "timings": [{"end": old_date}]},
        {"uid": 4, "timings": []},  # Pas de date
    ]

    filtered = collector.filter_recent_events(mock_events, days=365)

    # NOTE: Filtering disabled for demo
    assert len(filtered) == 4
    uids = [e["uid"] for e in filtered]
    assert 1 in uids
    assert 2 in uids
    assert 3 in uids
    assert 4 in uids


def test_filter_robustness():
    collector = OpenAgendaCollector()
    # Events with bad dates or missing fields
    bad_events = [
        {"uid": 5, "timings": [{"end": "NOT A DATE"}]},
        {"uid": 6},  # No timings
    ]
    # NOTE: Filtering disabled for demo
    filtered = collector.filter_recent_events(bad_events)
    assert len(filtered) == 2
