SHELL := /bin/bash
BASE_CONTAINER = ubuntu:noble-20240127.1

# Detect the operating system in use and set the HOST_PWD variable accordingly
ifeq ($(OS),Windows_NT)
	HOST_PWD = $(shell echo %cd%)
	SETUP_FILE_SYSTEM = fs-windows
	DOCKER_RUN = docker run $$BASE_CONTAINER --rm base
else
	HOST_PWD = $(shell pwd)
	SETUP_FILE_SYSTEM = fs
	DOCKER_RUN = docker run $$BASE_CONTAINER --user ${UID}:${GID} --rm base
endif

# Default goal
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## List out all the commands and their usage
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[1m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

################
# Core Commands#
################

.PHONY: build
build: ## Build the docker containers. Note: code changes will hot reload but any key.env changes will require a rebuild
	docker compose build --parallel;

.PHONY: build-ci
build-ci: ## Build the docker containers. Note: code changes will hot reload but any key.env changes will require a rebuild
	docker compose build fastapi react --parallel;

.PHONY: up
up run: ## Startup AgentFramework
	@docker compose up

.PHONY: up-d
up-d: ## Startup AgentFramework in the background
	@docker compose up -d

.PHONY: up-d-ci
up-d-ci: ## Startup AgentFramework without Jupyter or Phoenix to getaround pipeline max size
	@docker compose up fastapi react qdrant -d


.PHONY: build-run
build-run: build up ## Build and run AgentFramework

.PHONY: down
down: ## Stop AgentFramework
	@echo "Stopping AgentFramework..."
	@docker compose down --remove-orphans --volumes

.PHONY: restart
restart: down up ## Stop and then start AgentFramework

.PHONY: clean-jupyter
clean-jupyter: ## Remove all jupyter containers and volumes
	@printf "Starting Jupyter cleanup...\n"
	@echo "Stop all containers before cleaning up jupyter"
	docker compose down --remove-orphans --volumes
	@echo "Delete the jupyter container"
	docker image rm agent_framework_jupyter_image || true # Do not fail if the image is not present
	@echo "Delete all checkpoints and cache files"
	rm -rf jupyter/**/.ipynb_checkpoints
	@echo "Delete all python virtual envs"
	rm -rf jupyter/**/.venv
	@echo "Delete lots of other stuff..."
	rm -rf   jupyter/src/.cache jupyter/src/.config jupyter/src/.ipython jupyter/src/.jupyter jupyter/src/.local jupyter/src/.npm jupyter/src/.yarn jupyter/src/.bash_history jupyter/src/.phoenix jupyter/**/.wget-hsts
	@printf "\nJupyter cleanup complete. You can now run make up or docker compose up jupyter to start the jupyter container.\n"

.PHONY: clean
clean: down ## run a prune all command to remove all unused containers, networks, images, volumes.
	@echo "Running a docker system prune... this will remove ALL docker containers and volumes."
	@echo "Caution! You may not want to actuall do this."
	docker compose down --remove-orphans --volumes
	rm -rf .data
	rm -rf backend/src/scraper/out
	rm -rf backend/src/scraper/scraped_data
	make fs

####################
# Utility Commands #
####################

.PHONY: fs
fs: ## Bootstrap filesystem for AgentFramework use
	@echo "Setting up the filesystem"
	mkdir -p .data/qdrant/ .data/chat/memory .data/sqlite .data/filedrop

.PHONY: fs-windows
fs-windows: ## Bootstrap Windows filesystem for AgentFramework use (use if bash cmd doesnt work)
	New-Item -ItemType "directory" -Path ".data/qdrant/", ".data/chat/memory", ".data/sqlite", ".data/filedrop"

.PHONY: shell
shell cli: ## Open a bash shell in the AGENT_FRAMEWORK_FASTAPI container
	@docker exec -it AGENT_FRAMEWORK_FASTAPI /bin/bash


# Setup key.ev file: first check if AZURE_OPENAI_API_KEY is an environment variable, if not, exit this step
# If AZURE_OPENAI_API_KEY, then copy key.env.example to key.env and replace the placeholder with the actual key
.PHONY: _setup_env_file
_setup_env_file: ## Setup the key.env file
	@echo "Setting up the key.env file..."
	@if [ ! -f key.env ]; then \
		if [ -z "$$AZURE_OPENAI_API_KEY" ]; then \
			echo "AZURE_OPENAI_API_KEY is not set. Will not attempt to autoconfigure key.env."; \
		else \
			cp key.env.example key.env; \
			sed -i  "s/TODO_put_azure_openai_key_here/$$AZURE_OPENAI_API_KEY/g" key.env; \
			echo "key.env file setup complete."; \
		fi; \
	else \
		echo "key.env file already exists. If you need to update the key, please do so manually."; \
	fi; \

.PHONE: setup
setup:
	@echo "Setting up file system"
	$$DOCKER_RUN make _setup_env_file
	$$DOCKER_RUN make fs

.PHONE: install
install: ## Install packages
	@pip install -r backend/requirements.txt
	@pip install --upgrade pip
	@pre-commit install

.PHONY: open-jupyter
open-jupyter: ## Open a jupyter notebook in the AGENT_FRAMEWORK_FASTAPI container
	@open $$(docker compose exec jupyter /opt/conda/bin/jupyter server list -- | grep -m 1 'http://' | awk '{print $$1}' | sed -E 's|//[^:/]+|//127.0.0.1|')

.PHONY: jupyter-token
jupyter-token: ## Used to pull the URL to hit with the proper token generated at startup
	@docker compose logs --no-log-prefix jupyter | head -79| tail -1 | awk '{ print $7}'

# Check disk space usage, useful for running in a virtual enviornment with limited space, like GitHub Codespaces
.PHONY: disk-usage
disk-usage: ## Check disk space usage
	@echo "Disk space usage:"
	df -h
	@printf "\nChecking Docker space usage...\n"
	docker system df
	@printf "\nChecking Docker images...\n"
	docker images


#####################
# Automated Testing #
#####################

.PHONY: test
test: ## Run all tests
	@docker compose exec fastapi /bin/bash -c "cd .. && make _test"
	@docker compose exec react npm test

.PHONY: _test
_test: ## Run all tests locally
	pytest -v --cov=src --cov-config=.coveragerc

.PHONY: test-unit
test-unit: ## Run only unit tests
	@docker compose run fastapi /bin/bash -c "cd .. && make _test-unit"

.PHONY: test-unit-ci # GitHub actions needs the -T to work.
test-unit-ci: ## Run only unit tests for CI
	@docker compose run -T fastapi /bin/bash -c "cd .. && make _test-unit"

.PHONY: _test-unit
_test-unit: ## Run only unit tests locally
	cd backend && pytest --cov=/app/backend/src --cov-config=.coveragerc -v /app/backend/tests/unit

.PHONY: test-integration
test-integration: ## Run only unit tests
	@docker compose exec fastapi /bin/bash -c "cd .. && make _test-integration"

.PHONY: test-integration-ci
test-integration-ci: ## Run only unit tests
	@docker compose exec -T fastapi /bin/bash -c "cd .. && make _test-integration"

.PHONY: _test-integration
_test-integration: ## Run only unit tests locally
	pytest -v /app/tests/integration

.PHONY: test-react
test-react: ## Run react unit tests
	@docker compose run react npm test

.PHONY: test-react-watch
test-react-watch: ## Run react unit tests
	@docker compose run react npm run test:watch

.PHONY: test-react-ci # GitHub actions needs the -T to work.
test-react-ci: ## Run react unit tests for CI
	@docker compose run -T react npm test

.PHONY: _test-react
_test-react: ## Run react unit tests locally
	cd frontend && npm test

.PHONY: lint
lint: ## Run the black code formatter on the backend code
	@docker run -it --rm --volume $(HOST_PWD):/app agent_framework_server_image black /app
