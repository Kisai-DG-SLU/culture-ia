import os
import json
import requests
from datetime import datetime, timedelta
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
        if self.api_key:
            # V2 API
            url = f"https://api.openagenda.com/v2/agendas/{self.agenda_uid}/events"
            params = {"key": self.api_key}
            response = requests.get(url, params=params)
        else:
            # Legacy JSON export (public)
            url = f"{self.base_url}/{self.agenda_uid}/events.json"
            response = requests.get(url)
        
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])

    def filter_recent_events(self, events, days=365):
        """
        Filter events that occurred within the last 'days' days or are in the future.
        """
        recent_events = []
        # Use timezone-aware UTC now for comparison
        from datetime import timezone
        limit_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        for event in events:
            # In OpenAgenda JSON export, timings is a list of {begin, end}
            timings = event.get("timings", [])
            is_recent = False
            for timing in timings:
                try:
                    # fromisoformat handles +00:00 and returns aware datetime
                    end_date = datetime.fromisoformat(timing["end"].replace("Z", "+00:00"))
                    # Ensure end_date is aware if it wasn't
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone.utc)
                        
                    if end_date >= limit_date:
                        is_recent = True
                        break
                except (ValueError, KeyError):
                    continue
            
            if is_recent:
                recent_events.append(event)
        
        return recent_events

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
