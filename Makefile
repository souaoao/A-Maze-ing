.PHONY: install run debug clean lint lint-strict

SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
FLAKE8 := $(VENV)/bin/flake8
MYPY := $(VENV)/bin/mypy
REQUIREMENTS := requirements.txt
CONFIG := config.txt
AMAZEING := a_maze_ing.py
INSTALL_STAMP := $(VENV)/.installed

$(VENV):
	python3 -m venv $(VENV)

$(INSTALL_STAMP): $(VENV) $(REQUIREMENTS)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(INSTALL_STAMP)

run: install
	source $(VENV)/bin/activate \
	&& python3 $(AMAZEING) $(CONFIG)

install: $(INSTALL_STAMP)

debug: install
	source $(VENV)/bin/activate \
	&& python3 -m pdb $(AMAZEING) $(CONFIG)

clean:
	rm -rf $(VENV)
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf maze.txt
	rm -rf dist mazegen.egg-info

lint: install
	$(FLAKE8) .
	$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

build: install
	$(PYTHON) -m pip install build
	$(PYTHON) -m build