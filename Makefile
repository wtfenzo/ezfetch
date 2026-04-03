.PHONY: build clean install uninstall deps lint test

INSTALL_DIR ?= /usr/local/bin
BIN_NAME    := ezfetch
VENV_DIR    ?= .venv
PYTHON      := $(VENV_DIR)/bin/python
SYSTEM_PY   ?= /bin/python3
PY_FILES    := $(shell find ezfetch -name '*.py' -not -path '*__pycache__*')


deps:
	@BASE_PY="$(SYSTEM_PY)"; \
	test -x "$$BASE_PY" || BASE_PY="python3"; \
	test -x $(PYTHON) || $$BASE_PY -m venv $(VENV_DIR)
	@if $(PYTHON) -m pip --version >/dev/null 2>&1; then \
		$(PYTHON) -m pip install --upgrade pip; \
		$(PYTHON) -m pip install pyinstaller psutil; \
	else \
		BASE_PY="$(SYSTEM_PY)"; \
		test -x "$$BASE_PY" || BASE_PY="python3"; \
		echo "[Deps] pip unavailable in $(VENV_DIR); trying user-site install with $$BASE_PY"; \
		if $$BASE_PY -m pip --version >/dev/null 2>&1; then \
			$$BASE_PY -m pip install --user --break-system-packages pyinstaller psutil; \
		else \
			echo "[Deps] pip is unavailable on fallback Python as well"; \
		fi; \
	fi

build: deps
	@BASE_PY="$(SYSTEM_PY)"; \
	test -x "$$BASE_PY" || BASE_PY="python3"; \
	PY="$(PYTHON)"; \
	if $$PY -c "import PyInstaller" >/dev/null 2>&1; then \
		:; \
	elif $$BASE_PY -c "import PyInstaller" >/dev/null 2>&1; then \
		PY="$$BASE_PY"; \
	else \
		echo "[Build] PyInstaller is not installed. Install it with: $$BASE_PY -m pip install --user --break-system-packages pyinstaller"; \
		exit 1; \
	fi; \
	$$PY -m PyInstaller --name $(BIN_NAME) --onefile ezfetch/__main__.py --clean
	@printf '\n[Binary] ready: dist/%s\n' "$(BIN_NAME)"
	@ls -lh dist/$(BIN_NAME)*


install: build
	sudo cp dist/$(BIN_NAME) $(INSTALL_DIR)/$(BIN_NAME)
	sudo chmod +x $(INSTALL_DIR)/$(BIN_NAME)
	@echo "[Installed] to $(INSTALL_DIR)/$(BIN_NAME)"

uninstall:
	sudo rm -f $(INSTALL_DIR)/$(BIN_NAME)
	@echo "[Removed] $(INSTALL_DIR)/$(BIN_NAME)"


clean:
	rm -rf build/ dist/ __pycache__ ezfetch/__pycache__
	rm -rf *.egg-info
	@echo "[Cleaned] build artifacts"

lint: $(PY_FILES)
	@for f in $(PY_FILES); do \
		PY="$(PYTHON)"; \
		if ! test -x "$$PY"; then \
			PY="$(SYSTEM_PY)"; \
			test -x "$$PY" || PY="python3"; \
		fi; \
		$$PY -m py_compile "$$f" || exit 1; \
	done
	@echo "[Lint] all $(words $(PY_FILES)) files compile OK"

test: deps
	@PY="$(PYTHON)"; \
	if ! $$PY -c "import psutil" >/dev/null 2>&1; then \
		PY="$(SYSTEM_PY)"; \
		test -x "$$PY" || PY="python3"; \
	fi; \
	$$PY -m ezfetch --no-color --no-logo --no-color-blocks
	@echo "\n[Test] basic run OK"
	@PY="$(PYTHON)"; \
	if ! $$PY -c "import psutil" >/dev/null 2>&1; then \
		PY="$(SYSTEM_PY)"; \
		test -x "$$PY" || PY="python3"; \
	fi; \
	$$PY -m ezfetch --json --no-cache | $$PY -m json.tool > /dev/null
	@echo "[Test] JSON output OK"
