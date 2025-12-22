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

    def _extract_dates(self, timings):
        """Extract and format dates from timings."""
        dates_list = []
        for timing in timings:
            try:
                begin_str = timing.get("begin")
                end_str = timing.get("end")
                if begin_str and end_str:
                    dt_begin = datetime.fromisoformat(begin_str)
                    dt_end = datetime.fromisoformat(end_str)
                    dates_list.append(
                        f"Du {dt_begin.strftime('%d/%m/%Y à %H:%M')} "
                        f"au {dt_end.strftime('%d/%m/%Y à %H:%M')}"
                    )
            except ValueError:
                continue
        return "\n".join(dates_list) if dates_list else "Date non spécifiée"

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

            date_range = self._extract_dates(event.get("timings", []))

            url = event.get("canonicalUrl", "")

            # Combine into a single text block for embedding, but keep metadata
            full_text = (
                f"Titre: {title}\n"
                f"Description: {description}\n"
                f"Lieu: {location_str}\n"
                f"Dates: {date_range}\n"
                f"Mots-clés: {keywords}"
            )

            processed_events.append(
                {
                    "id": event.get("uid"),
                    "text": full_text,
                    "metadata": {
                        "title": title,
                        "location": location_str,
                        "dates": date_range,
                        "url": url,
                        "keywords": keywords,
                    },
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
