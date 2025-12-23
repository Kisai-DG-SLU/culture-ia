import json
import os
from datetime import datetime


class EventProcessor:
    def __init__(
        self,
        input_file="data/raw_events.json",
        output_file="data/processed_events.json",
    ):
        self.input_file = input_file
        self.output_file = output_file

    def _parse_timings(self, timings):
        """Parse timings to extract formatted dates and timestamps."""
        timestamps = []
        dates_objects = []
        now = datetime.now().astimezone()

        for timing in timings:
            try:
                begin_str = timing.get("begin")
                end_str = timing.get("end")
                if begin_str and end_str:
                    dt_begin = datetime.fromisoformat(begin_str)
                    dt_end = datetime.fromisoformat(end_str)
                    timestamps.append(dt_begin.timestamp())
                    timestamps.append(dt_end.timestamp())
                    dates_objects.append(dt_begin)
            except (ValueError, TypeError):
                continue

        # Tri chronologique absolu
        dates_objects.sort()

        # Séparation Passé / Futur
        future_dates = [d for d in dates_objects if d >= now]
        past_dates = [d for d in dates_objects if d < now]

        formatted_parts = []
        next_dates_str = ""

        if future_dates:
            formatted_parts.append("DATES À VENIR (OFFICIELLES) :")
            formatted_parts.extend(
                [f"- {d.strftime('%A %d %B %Y à %H:%M')}" for d in future_dates]
            )
            # Pour le résumé de recherche (TOUTES les dates futures pour un retrieval précis)
            all_future_str = [d.strftime("%d/%m/%Y") for d in future_dates]
            next_dates_str = "Prochaines sessions : " + ", ".join(all_future_str)

        if past_dates:
            formatted_parts.append("\nARCHIVES (DATES PASSÉES - NE PAS PROPOSER) :")
            formatted_parts.extend(
                [f"- {d.strftime('%A %d %B %Y à %H:%M')}" for d in reversed(past_dates)]
            )

        # Si aucune date n'est trouvée
        if not formatted_parts:
            return ["Date non spécifiée"], timestamps, ""

        return formatted_parts, timestamps, next_dates_str

    def _create_metadata(
        self,
        event,
        location,
        location_str,
        title,
        description,
        keywords,
        url,
        timestamps,
        full_dates_str,
        next_dates_short_str,
    ):
        """Create metadata dictionary and search text."""
        # Résumé des dates pour le vecteur (Recherche sémantique)
        if timestamps:
            min_date = datetime.fromtimestamp(min(timestamps)).strftime("%d/%m/%Y")
            max_date = datetime.fromtimestamp(max(timestamps)).strftime("%d/%m/%Y")
            summary_dates_str = (
                f"Événement du {min_date} au {max_date}. {next_dates_short_str}"
            )
        else:
            summary_dates_str = "Date non spécifiée"

        # Métadonnées structurées
        start_ts = min(timestamps) if timestamps else 0
        end_ts = max(timestamps) if timestamps else 0
        city = location.get("city", "Inconnu")

        # 1. Search Text (Optimisé pour la recherche vectorielle)
        search_text = (
            f"Titre: {title}\n"
            f"Description: {description}\n"
            f"Lieu: {location_str}\n"
            f"Période: {summary_dates_str}\n"
            f"Mots-clés: {keywords}"
        )

        # 2. Full Context (Pour le LLM : contient TOUT)
        full_context = (
            f"Titre: {title}\n"
            f"Description: {description}\n"
            f"Lieu: {location_str}\n"
            f"Détail des dates:\n{full_dates_str}\n"
            f"Mots-clés: {keywords}\n"
            f"URL: {url}"
        )

        return search_text, {
            "title": title,
            "location": location_str,
            "url": url,
            "keywords": keywords,
            "city": city,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "all_sessions_ts": timestamps,
            "full_context": full_context,
        }

    def process(self):
        if not os.path.exists(self.input_file):
            print(f"Input file {self.input_file} not found.")
            return

        with open(self.input_file, "r", encoding="utf-8") as f:
            events = json.load(f)

        processed_events = []
        for event in events:
            # Basic extraction
            title = event.get("title", {}).get("fr", "Sans titre")
            description = event.get("longDescription", {}).get("fr") or event.get(
                "description", {}
            ).get("fr", "")

            location = event.get("location", {})
            location_str = (
                f"{location.get('name', '')}, {location.get('address', '')}, "
                f"{location.get('city', '')} {location.get('postalCode', '')}"
            ).strip(", ")

            keywords = ", ".join(event.get("keywords", {}).get("fr", []))
            url = event.get("canonicalUrl", "")

            # Extraction des dates via helper
            dates_list, timestamps, next_dates_short_str = self._parse_timings(
                event.get("timings", [])
            )

            full_dates_str = (
                "\n".join(dates_list) if dates_list else "Date non spécifiée"
            )

            # Création des métadonnées et du texte de recherche
            search_text, metadata = self._create_metadata(
                event,
                location,
                location_str,
                title,
                description,
                keywords,
                url,
                timestamps,
                full_dates_str,
                next_dates_short_str,
            )

            processed_events.append(
                {
                    "id": event.get("uid"),
                    "text": search_text,
                    "metadata": metadata,
                }
            )

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(processed_events, f, ensure_ascii=False, indent=4)

        print(
            f"Processed {len(processed_events)} events and saved to {self.output_file}"
        )


if __name__ == "__main__":
    processor = EventProcessor()
    processor.process()
