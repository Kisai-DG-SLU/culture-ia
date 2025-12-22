.PHONY: install test run view save-brain docker-build docker-run lint format

# Détection de l'environnement
VENV_CONDA_EXISTS := $(shell [ -f .venv_conda/bin/python ] && echo 1 || echo 0)
VENV_PIP_EXISTS := $(shell [ -f .venv/bin/python ] && echo 1 || echo 0)

ifeq ($(VENV_CONDA_EXISTS), 1)
	VENV_DIR = .venv_conda
	PYTHON = $(VENV_DIR)/bin/python
	PIP = $(VENV_DIR)/bin/pip
	PYTEST = $(VENV_DIR)/bin/pytest
	BLACK = $(VENV_DIR)/bin/black
	PYLINT = $(VENV_DIR)/bin/pylint
else ifeq ($(VENV_PIP_EXISTS), 1)
	VENV_DIR = .venv
	PYTHON = $(VENV_DIR)/bin/python
	PIP = $(VENV_DIR)/bin/pip
	PYTEST = $(VENV_DIR)/bin/pytest
	BLACK = $(VENV_DIR)/bin/black
	PYLINT = $(VENV_DIR)/bin/pylint
else
	PYTHON = python
	PIP = pip
	PYTEST = pytest
	BLACK = black
	PYLINT = pylint
endif

install:
	conda env update -f environment.yml --prune

test:
	PYTHONPATH=. $(PYTEST) tests/

lint:
	$(PYLINT) src/ tests/ --disable=C0111,C0103,R0903,W0718,W0621,W0613,R0913,R0917,R0914
format:
	$(BLACK) src/ tests/

run:
	PYTHONPATH=. $(PYTHON) src/main.py

frontend:
	PYTHONPATH=. $(VENV_DIR)/bin/streamlit run src/frontend/ui.py

evaluate:
	PYTHONPATH=. $(PYTHON) src/core/evaluator.py

view:
	grip docs/ -b

docker-build:
	docker build -t culture-ia .

docker-run:
	docker run -p 8000:8000 -p 8501:8501 --env-file .env culture-ia

save-brain:
	@echo "🧠 Sauvegarde Stealth vers Guesdon-Brain..."
	@mkdir -p "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_7/culture-ia"
	@cp GEMINI.md "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_7/culture-ia/" 2>/dev/null || true
	@cp -r specs/ "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_7/culture-ia/specs/" 2>/dev/null || true
	@cd "/Users/daminou/Dev/Guesdon-Brain" && git add . && git commit -m "Backup: culture-ia" && git push origin main && echo "✅ Brain Synced!"
