PROJECT_DIR			= app
APP_API				= $(PROJECT_DIR)/admin_api
APP_BOT				= $(PROJECT_DIR)/blackjack_bot
TESTS_DIR			= tests
DB_CONTAINER_NAME	= postgres_db

CONFIG_FILE			= config.env
CONFIG_FILE_MAKE	= $(CONFIG_FILE).mk
CONFIG_FILE_SAMPLE	= $(CONFIG_FILE).sample
ifeq ("$(wildcard $(CONFIG_FILE))","")
	_ := $(shell echo "\# App configuration:\n" > $(CONFIG_FILE))
	_ := $(shell cat $(CONFIG_FILE_SAMPLE) >> $(CONFIG_FILE))
endif
_ := $(shell sed "s: =: ?=:" $(CONFIG_FILE) > $(CONFIG_FILE_MAKE))
include $(CONFIG_FILE_MAKE)

ifndef DATABASE__PORT
	DATABASE__PORT = 5432
endif

NPROCS		= 4
MAKEFLAGS	+= -j$(NPROCS)
args		:= $(wordlist 2, 100, $(MAKECMDGOALS))

all:
	@echo "make venv           - Create python virtual environment (poetry)"
	@echo "make db             - Run docker DB server"
	@echo "make db_stop        - Stop docker DB server"
	@echo "make migrate        - Apply API service migrations to DB"
	@echo "make revision NAME  - Create new DB migration"
	@echo "make run            - Run API service"
	@echo "make test           - Run tests for API service"
	@echo "make test-cov       - Run tests with coverage report generation"
	@echo "make lint           - Check code with isort, black, mypy, pylint"

venv:
	pip install poetry
	poetry install

db: export POSTGRES_USER	 = $(DATABASE__USERNAME)
db: export POSTGRES_PASSWORD = $(DATABASE__PASSWORD)
db: export POSTGRES_DB		 = $(DATABASE__NAME)
db:
	@test $(DATABASE__USERNAME) || ( echo ">> DATABASE__USERNAME is not set"; exit 1 )
	@test $(DATABASE__PASSWORD) || ( echo ">> DATABASE__PASSWORD is not set"; exit 1 )
	@test $(DATABASE__NAME) || ( echo ">> DATABASE__NAME is not set"; exit 1 )
	@echo Database credentials: user=$(POSTGRES_USER) password="(hidden)" db=$(POSTGRES_DB)
	docker run --env POSTGRES_USER \
		--env POSTGRES_PASSWORD \
		--env POSTGRES_DB \
		--publish $(DATABASE__PORT):$(DATABASE__PORT) \
		--name $(DB_CONTAINER_NAME) \
		--detach \
		--rm \
		postgres -p $(DATABASE__PORT)
db_stop:
	docker stop $(DB_CONTAINER_NAME)

migrate:
	poetry run alembic upgrade head
revision:
	poetry run alembic revision --autogenerate -m $(args)

run_api:
	poetry run adev runserver $(APP_API) --port 8080 --livereload
run_bot:
	poetry run python $(APP_BOT)/main.py

test:
	poetry run pytest
test-cov:
	poetry run pytest --cov=$(PROJECT_DIR) --cov-report html

lint: isort black pylint #mypy
isort:
	poetry run isort $(PROJECT_DIR) $(TESTS_DIR)
black:
	poetry run black $(PROJECT_DIR) $(TESTS_DIR)
pylint:
	poetry run pylint -j $(NPROCS) $(PROJECT_DIR) $(TESTS_DIR)
mypy:
	poetry run mypy $(PROJECT_DIR)

.PHONY: all venv db db_stop migrate revision run test test-cov lint isort black pylint mypy
