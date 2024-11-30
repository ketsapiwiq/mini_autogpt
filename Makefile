.PHONY: list install run test test-ollama test-all clean show-prompt show-decision-prompt

list: ## List all enabled bot commands
	@echo "Available enabled bot commands:"
	@python -c "from action.commands.setup import register_commands; from action.commands.registry import CommandRegistry; register_commands(); print('\n'.join([f'{cmd[\"name\"]}: {cmd[\"description\"]}' for cmd in CommandRegistry.get_available_commands()]))"

show-prompt: ## Show prompt for a specific command (usage: make show-prompt cmd=<command_name>)
	@python -c "from action.commands.registry import CommandRegistry; \
		from action.commands.prompt_builder import CommandPrompt; \
		cmd = '$(cmd)'; \
		prompt = CommandPrompt.get_prompt(cmd) if cmd else None; \
		print(f'Prompt for command \"{cmd}\":\n{prompt}' if prompt else 'Command not found or no prompt available')"

show-decision-prompt: ## Show the decision-making prompt used by the system
	@python -c "from action.commands.setup import register_commands; import think.prompt as prompt; register_commands(); print(prompt.get_action_prompt())"

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
