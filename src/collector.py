import os
import json
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv

load_dotenv()


class OpenAgendaCollector:
    def __init__(self, api_key=None, agenda_uid=None):
        self.api_key = api_key or os.getenv("OPENAGENDA_API_KEY")
        self.agenda_uid = agenda_uid or os.getenv("OPENAGENDA_AGENDA_UID", "826334")
        self.base_url = "https://openagenda.com/agendas"

    def fetch_events(self):
        """
        Fetch events from OpenAgenda.
        Uses legacy JSON export if no API key is provided for public agendas.
        """
        # Mode Mock pour la CI/Tests (si activé)
        if os.getenv("MOCK_DATA") == "true":
            print("⚠️ Mode Mock activé : Génération d'événements factices.")
            now = datetime.now(timezone.utc)
            return [
                {
                    "uid": 999999,
                    "title": {"fr": "Atelier Cuisine Sauvage Mock"},
                    "description": {"fr": "Un événement factice pour les tests."},
                    "location": {
                        "name": "Bois de Vincennes",
                        "address": "Paris",
                        "city": "Paris",
                        "postalCode": "75012",
                    },
                    "timings": [
                        {
                            "begin": now.isoformat(),
                            "end": (now + timedelta(days=1)).isoformat(),
                        }
                    ],
                    "keywords": {"fr": ["cuisine", "sauvage"]},
                    "canonicalUrl": "http://mock.url",
                }
            ]

        if self.api_key:
            # V2 API
            url = f"https://api.openagenda.com/v2/agendas/{self.agenda_uid}/events"
            params = {
                "key": self.api_key,
                "includeFields[]": [
                    "uid",
                    "title",
                    "description",
                    "longDescription",
                    "location",
                    "timings",
                    "keywords",
                    "canonicalUrl",
                    "range",
                ],
                "relative[]": ["current", "upcoming"],
                "limit": 100,
            }
            response = requests.get(url, params=params, timeout=10)
        else:
            # Legacy JSON export (public)
            url = f"{self.base_url}/{self.agenda_uid}/events.json"
            response = requests.get(url, timeout=10)

        response.raise_for_status()
        data = response.json()
        return data.get("events", [])

    def filter_recent_events(self, events, days=365):
        """
        Filter events that occurred within the last 'days' days or are in the future.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        filtered_events = []

        for event in events:
            timings = event.get("timings", [])
            if not timings:
                continue

            is_recent = False
            for timing in timings:
                try:
                    end_str = timing.get("end")
                    if not end_str:
                        continue

                    # Handle Z for UTC if present (Python 3.10 compatibility)
                    end_str = end_str.replace("Z", "+00:00")
                    end_date = datetime.fromisoformat(end_str)

                    # Ensure comparison is timezone-aware
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone.utc)

                    if end_date >= cutoff_date:
                        is_recent = True
                        break
                except (ValueError, TypeError):
                    continue

            if is_recent:
                filtered_events.append(event)

        print(
            f"✅ Filtrage temporel activé ({days} jours) : "
            f"{len(filtered_events)}/{len(events)} événements conservés."
        )
        return filtered_events

    def save_to_json(self, events, filename="data/raw_events.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(events)} events to {filename}")


if __name__ == "__main__":
    collector = OpenAgendaCollector()
    print(f"Fetching events for agenda {collector.agenda_uid}...")
    try:
        all_events = collector.fetch_events()
        print(f"Found {len(all_events)} total events.")
        recent_events = collector.filter_recent_events(all_events)
        collector.save_to_json(recent_events)
    except Exception as e:
        print(f"Error: {e}")
