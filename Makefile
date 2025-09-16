.PHONY: venv install clean test run

# Variables
VENV_NAME = venv
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_NAME)
	@echo "Virtual environment created in $(VENV_NAME)/"
	@echo "To activate it manually, run: source $(VENV_NAME)/bin/activate"

# Install dependencies
install: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Clean virtual environment
clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_NAME)
	@echo "Virtual environment removed."

# Run tests (if you have any)
test: install
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ || echo "No tests found or pytest not installed"

# Run the main application
run: install
	@echo "Starting Benson Bot..."
	$(PYTHON) benson_api.py

# Show help
help:
	@echo "Available commands:"
	@echo "  make venv     - Create virtual environment"
	@echo "  make install  - Install dependencies (creates venv if needed)"
	@echo "  make clean    - Remove virtual environment"
	@echo "  make test     - Run tests"
	@echo "  make run      - Run the main application"
	@echo "  make help     - Show this help message"