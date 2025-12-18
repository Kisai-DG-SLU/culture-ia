import json
import os
import pytest
from src.processor import EventProcessor

# Données brutes simulées (mock)
MOCK_RAW_EVENTS = [
    {
        "uid": "123",
        "title": {"fr": "Concert de Jazz"},
        "longDescription": {"fr": "Un super concert de jazz au parc."},
        "location": {
            "name": "Parc Floral",
            "address": "Route de la Pyramide",
            "city": "Paris",
            "postalCode": "75012",
        },
        "keywords": {"fr": ["jazz", "concert", "musique"]},
        "range": {"fr": "Du 10 au 12 juin"},
        "canonicalUrl": "https://openagenda.com/event/123",
    },
    {
        "uid": "456",
        # Cas limite : champs manquants
        "title": {"fr": "Expo Photo"},
        "description": {
            "fr": "Une belle expo."
        },  # Utilisation de description courte si longDescription absente
        "location": {"city": "Lyon"},
        "keywords": {},  # Pas de keywords
        # Pas de range, pas d'url
    },
]


def test_process_creates_output_file(tmp_path):
    """Test que la méthode process génère bien un fichier de sortie correct."""
    # Setup : Création des fichiers temporaires
    input_file = tmp_path / "raw_events.json"
    output_file = tmp_path / "processed_events.json"

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(MOCK_RAW_EVENTS, f)

    # Action
    processor = EventProcessor(input_file=str(input_file), output_file=str(output_file))
    processor.process()

    # Assertions
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 2

    # Vérification du premier événement (complet)
    event1 = data[0]
    assert event1["id"] == "123"
    assert "Concert de Jazz" in event1["text"]
    assert "Parc Floral" in event1["text"]
    assert "jazz, concert, musique" in event1["metadata"]["keywords"]
    assert event1["metadata"]["url"] == "https://openagenda.com/event/123"

    # Vérification du deuxième événement (partiel)
    event2 = data[1]
    assert event2["id"] == "456"
    assert "Expo Photo" in event2["text"]
    assert "Une belle expo" in event2["text"]
    assert "Lyon" in event2["metadata"]["location"]  # Doit contenir au moins la ville
    assert event2["metadata"]["dates"] == ""  # Vide si manquant


def test_process_handles_missing_input_file(tmp_path, capsys):
    """Test que le processeur gère l'absence de fichier d'entrée sans crasher."""
    input_file = tmp_path / "non_existent.json"
    output_file = tmp_path / "output.json"

    processor = EventProcessor(input_file=str(input_file), output_file=str(output_file))
    processor.process()

    # Vérifier qu'il a print un message d'erreur
    captured = capsys.readouterr()
    assert "not found" in captured.out

    # Vérifier qu'aucun fichier n'a été créé
    assert not output_file.exists()
