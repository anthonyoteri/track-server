VIRTUALENV ?= env
PYTHONVERSION ?= python3
PYTHON = $(VIRTUALENV)/bin/$(PYTHONVERSION)
TESTRUNNER = $(VIRTUALENV)/bin/pytest
PYTHON_MODULES = $(dir $(wildcard */__init__.py))

.PHONY: all
all: build

$(VIRTUALENV): requirements.txt setup.py setup.cfg
	[ -e "$(PYTHON)" ] || $(PYTHONVERSION) -m venv $@
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install --requirement=$<
	@touch $@

.PHONY: build
build: $(VIRTUALENV)

.PHONY: test
test: $(VIRTUALENV)
	$(TESTRUNNER) $(args)


.PHONY: check
check: $(VIRTUALENV)
	$(VIRTUALENV)/bin/flake8
	$(VIRTUALENV)/bin/black --check .
	$(VIRTUALENV)/bin/mypy .


clean:
	git clean -Xdf

