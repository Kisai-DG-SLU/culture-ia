import pytest
from fastapi.testclient import TestClient
from src.api.app import app
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API Culture IA !"}

def test_ask_question():
    # This might fail if the index is not created, but it should be
    response = client.post("/ask", json={"question": "Quels sont les événements sur la cuisine sauvage ?"})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert len(response.json()["answer"]) > 0
