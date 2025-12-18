.PHONY: install test run view save-brain docker-build docker-run lint format

# Détection de l'environnement : utilise .venv si présent, sinon python système
VENV_EXISTS := $(shell [ -d .venv ] && echo 1 || echo 0)
ifeq ($(VENV_EXISTS), 1)
    PYTHON = .venv/bin/python
    PIP = .venv/bin/pip
    PYTEST = .venv/bin/pytest
    BLACK = .venv/bin/black
    PYLINT = .venv/bin/pylint
else
    PYTHON = python
    PIP = pip
    PYTEST = pytest
    BLACK = black
    PYLINT = pylint
endif

install:
	$(PIP) install -r requirements.txt

test:
	PYTHONPATH=. $(PYTEST) tests/

lint:
        $(PYLINT) src/ tests/ --disable=C0111,C0103,R0903,W0718,W0621,W0613
format:
	$(BLACK) src/ tests/

run:
	$(PYTHON) src/main.py

view:
	grip docs/ -b

docker-build:
	docker build -t culture-ia .

docker-run:
	docker run -p 8000:8000 --env-file .env culture-ia

save-brain:
	@echo "🧠 Sauvegarde Stealth vers Guesdon-Brain..."
	@mkdir -p "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet 7/culture-ia"
	@cp GEMINI.md "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet 7/culture-ia/" 2>/dev/null || true
	@cp -r specs/ "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet 7/culture-ia/specs/" 2>/dev/null || true
	@cd "/Users/daminou/Dev/Guesdon-Brain" && git add . && git commit -m "Backup: culture-ia" && git push origin main && echo "✅ Brain Synced!"