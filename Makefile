SYSTEM_PYTHON := $(shell which python2)
VENV          := venv
PYTHON        := $(VENV)/bin/python
PIP           := $(VENV)/bin/python -m pip

venv:
	$(SYSTEM_PYTHON) -m virtualenv venv
	$(PIP) install --upgrade pip wheel

.PHONY: install
install: venv
	$(PIP) install -r requirements.txt -c constraints.txt
	$(PIP) install -e .[test]

.PHONY: test
test:
	nosetests tests
