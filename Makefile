SYSTEM_PYTHON := $(shell which python2)
VENV          := venv
PIP           := pip
NOSETESTS     := nosetests

venv:
	$(SYSTEM_PYTHON) -m virtualenv $(VENV)
	$(PIP) install --upgrade pip wheel

.PHONY: install
install:
	$(PIP) install -r requirements.txt -c constraints.txt
	$(PIP) install -e .[test]

.PHONY: test
test:
	$(NOSETESTS) tests
