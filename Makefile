.PHONY: install test run view save-brain

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

install:
	$(PIP) install -r requirements.txt

test:
	PYTHONPATH=. $(PYTEST) tests/

run:
	$(PYTHON) src/main.py

view:
	grip docs/ -b

save-brain:
	@echo "🧠 Sauvegarde Stealth vers Guesdon-Brain..."
	@mkdir -p "/Users/daminou/Dev/Guesdon-Brain/Formation IA/Projet 7/culture-ia"
	@cp GEMINI.md "/Users/daminou/Dev/Guesdon-Brain/Formation IA/Projet 7/culture-ia/" 2>/dev/null || true
	@cp -r specs/ "/Users/daminou/Dev/Guesdon-Brain/Formation IA/Projet 7/culture-ia/specs/" 2>/dev/null || true
	@cd "/Users/daminou/Dev/Guesdon-Brain" && git add . && git commit -m "Backup: culture-ia" && git push origin master && echo "✅ Brain Synced!"
