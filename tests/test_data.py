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

    # Filtering is enabled: keeps recent (1) and future (2). Drops old (3) and invalid (4).
    assert len(filtered) == 2
    uids = [e["uid"] for e in filtered]
    assert 1 in uids
    assert 2 in uids
    assert 3 not in uids
    assert 4 not in uids


def test_filter_robustness():
    collector = OpenAgendaCollector()
    # Events with bad dates or missing fields
    bad_events = [
        {"uid": 5, "timings": [{"end": "NOT A DATE"}]},
        {"uid": 6},  # No timings
    ]
    # Filtering enabled: drops invalid events
    filtered = collector.filter_recent_events(bad_events)
    assert len(filtered) == 0
