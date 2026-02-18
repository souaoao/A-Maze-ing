.PHONY: install run debug clean lint lint-strict

SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements.txt
CONFIG := config.txt
AMAZEING := a_maze_ing.py
INSTALL_STAMP := $(VENV)/.installed

$(VENV):
	python3 -m venv $(VENV)

$(INSTALL_STAMP): $(VENV) $(REQUIREMENTS)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(INSTALL_STAMP)

install: $(INSTALL_STAMP)

run: install
	source $(VENV)/bin/activate \
	&& python3 $(AMAZEING) $(CONFIG)

debug:

clean:
	rm -rf $(VENV)
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .mypy_cache

lint: install
	flake8 a_maze_ing
	source $(VENV)/bin/activate \
	&& mypy a_maze_ing --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	flake8 a_maze_ing
	source $(VENV)/bin/activate \
	&& mypy a_maze_ing --strict
