.PHONY: install run debug clean lint lint-strict

VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements.txt
AMAZEING := a_maze_ing/a_maze_ing.py
INSTALL_STAMP := $(VENV)/.installed

venv:
	$(VENV):
		python3 -m venv $(VENV)

$(INSTALL_STAMP): $(VENV) $(REQUIREMENTS)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(INSTALL_STAMP)

install: $(INSTALL_STAMP)

run: install
	$(PYTHON) $(AMAZEING) $(CONFIG)

debug:

clean:
	rm -rf __pycache__


