.PHONY: list install run test test-ollama test-all clean

list: ## List all available bot commands
	@echo "Available bot commands:"
	@find ./action/commands -name "*.py" ! -name "__init__.py" -type f -exec grep -h "class.*Command" {} \; | \
		grep -v "Command:" | \
		grep -v "command_class" | \
		grep -v "CommandRegistry" | \
		sed 's/class //g' | \
		sed 's/(Command)://g' | \
		sed 's/:$$//g' | \
		grep -v "^[[:space:]]*def" | \
		sort | \
		sed 's/^[[:space:]]*//g'

install: ## Install project dependencies
	pip install -r requirements.txt

run: ## Run the mini AutoGPT
	python main.py

test: ## Run tests
	python -m pytest

test-ollama: ## Run Ollama-specific tests
	python -m pytest utils/llm_test.py -v -k "test_ollama"

test-all: test test-ollama ## Run all tests including Ollama tests

clean: ## Clean up Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
