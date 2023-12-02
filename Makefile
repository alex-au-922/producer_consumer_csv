include .env

POSTGRES_HOST=localhost
RABBITMQ_HOST=localhost

build:
	docker compose build
up:
	docker compose up
up_d:
	docker compose up -d
down:
	docker compose down
stats:
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"
export_requirements:
	cd producer && \
	poetry export -f requirements.txt --output requirements.txt --without-hashes && \
	cd ../consumer && \
	poetry export -f requirements.txt --output requirements.txt --without-hashes
setup_test_env:
	docker compose -f docker-compose.test.yml up -d
test_producer:
	export POSTGRES_HOST=localhost && \
	export POSTGRES_PORT=$(POSTGRES_PORT) && \
	export POSTGRES_USERNAME=$(POSTGRES_USERNAME) && \
	export POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) && \
	export POSTGRES_DATABASE=$(POSTGRES_DB) && \
	export RABBITMQ_HOST=localhost && \
	export RABBITMQ_PORT=$(RABBITMQ_PORT) && \
	export RABBITMQ_USERNAME=$(RABBITMQ_USERNAME) && \
	export RABBITMQ_PASSWORD=$(RABBITMQ_PASSWORD) && \
	export QUEUE_NAME=$(QUEUE_NAME) && \
	COVERAGE_FILE=.coverage_producer coverage run -m pytest -vx producer/tests
test_consumer:
	export POSTGRES_HOST=localhost && \
	export POSTGRES_PORT=$(POSTGRES_PORT) && \
	export POSTGRES_USERNAME=$(POSTGRES_USERNAME) && \
	export POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) && \
	export POSTGRES_DATABASE=$(POSTGRES_DB) && \
	export RABBITMQ_HOST=localhost && \
	export RABBITMQ_PORT=$(RABBITMQ_PORT) && \
	export RABBITMQ_USERNAME=$(RABBITMQ_USERNAME) && \
	export RABBITMQ_PASSWORD=$(RABBITMQ_PASSWORD) && \
	export QUEUE_NAME=$(QUEUE_NAME) && \
	COVERAGE_FILE=.coverage_consumer coverage run -m pytest -vx consumer/tests
