PACKAGE := tabledata
BUILD_WORK_DIR := _work
DOCS_DIR := docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build
PKG_BUILD_DIR := $(BUILD_WORK_DIR)/$(PACKAGE)

PYTHON := python3

AUTHOR := Tsuyoshi Hombashi
FIRST_RELEASE_YEAR := 2017
LAST_UPDATE_YEAR := $(shell git log -1 --format=%cd --date=format:%Y)


.PHONY: build-remote
build-remote: clean
	@mkdir -p $(BUILD_WORK_DIR)
	@cd $(BUILD_WORK_DIR) && \
		git clone https://github.com/thombashi/$(PACKAGE).git --depth 1 && \
		cd $(PACKAGE) && \
		$(PYTHON) -m tox -e build
	ls -lh $(PKG_BUILD_DIR)/dist/*

.PHONY: build
build: clean
	@$(PYTHON) -m tox -e build
	ls -lh dist/*

.PHONY: check
check:
	@$(PYTHON) -m tox -e lint

.PHONY: clean
clean:
	@rm -rf $(BUILD_WORK_DIR)
	@$(PYTHON) -m tox -e clean

.PHONY: idocs
idocs:
	@$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade .
	@$(MAKE) docs

.PHONY: docs
docs:
	@$(PYTHON) -m tox -e docs

.PHONY: fmt
fmt:
	@$(PYTHON) -m tox -e fmt

.PHONY: readme
readme:
	@$(PYTHON) -m tox -e readme

.PHONY: release
release:
	$(PYTHON) -m tox -e release
	$(MAKE) clean

.PHONY: setup-ci
setup-ci:
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade pip
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade tox

.PHONY: setup-dev
setup-dev: setup-ci
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade -e .[test]
	$(PYTHON) -m pip check

.PHONY: update-copyright
update-copyright:
	sed -i "s/f\"Copyright .*/f\"Copyright $(FIRST_RELEASE_YEAR)-$(LAST_UPDATE_YEAR), {__author__}\"/" $(PACKAGE)/__version__.py
	sed -i "s/^Copyright (c) .* $(AUTHOR)/Copyright (c) $(FIRST_RELEASE_YEAR)-$(LAST_UPDATE_YEAR) $(AUTHOR)/" LICENSE
