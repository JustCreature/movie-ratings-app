SERVER_PORT=8054
ifneq (,$(wildcard ./.dev.env))
	include .env
	export
endif
.PHONY : install setup tests check-types check check-full migrate

install:
	poetry install
	source .venv/bin/activate

setup: install
	poetry run pre-commit install

clean-start:
	docker compose up --build moviedb -d
	sleep 3
	PYTHONPATH=$(shell pwd)/src poetry run alembic revision --autogenerate -m "Initial tables"
	PYTHONPATH=$(shell pwd)/src poetry run alembic upgrade head
	docker exec -i moviedb psql -U postgres -d moviedb < ./init_db/init_data.sql
	docker compose up --build movie-ratings-app


start-db: down_volume
	docker compose up --build moviedb -d
	sleep 3
	PYTHONPATH=$(shell pwd)/src poetry run alembic upgrade head
	docker exec -i moviedb psql -U postgres -d moviedb < ./init_db/init_data.sql

new-db-start: down_volume
	docker compose up --build moviedb -d
	sleep 3
	PYTHONPATH=$(shell pwd)/src poetry run alembic upgrade head
	docker exec -i moviedb psql -U postgres -d moviedb < ./init_db/init_data.sql
	docker compose up --build movie-ratings-app

down_volume:
	docker compose down -v --remove-orphans

test:
	ENV_FILES=".env.test" poetry run pytest src/tests

up:
	docker compose up --build movie-ratings-app

test-with-coverage:
	ENV_FILES=".env.test .env.test-dev" poetry run pytest src/tests --cov=src/app --cov-report term-missing:skip-covered --cov-report xml:.test-reports/coverage.xml --junitxml=.test-reports/test-run.xml

local-integration-test:
	docker-compose up -d && sleep 5 && ENV_FILES=".env.test" poetry run pytest src/tests/integration && docker-compose down -v

check-types:
	poetry run mypy src/app

lint:
	poetry run pre-commit run --all-files

lint-changed:
	git status --porcelain | egrep -v '^(D |RM|R )' | cut -b 4- | xargs poetry run pre-commit run --files

lint-full-check: lint # TODO: add mypy here later, it fails with  error: Error importing plugin "sqlmypy": No module named 'sqlmypy'

run:
	cd src && ENV_FILES="../.env.local" poetry run python -m app.main

# clean pyc files/dirs
pyclean:
	find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +
