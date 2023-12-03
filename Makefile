include .env

POSTGRES_HOST=localhost
RABBITMQ_HOST=localhost

build:
	docker compose pull --ignore-buildable
	docker compose build
up:
	docker compose up -d && docker compose logs -f --tail 100 records_producer records_consumer
logs:
	docker compose logs -f --tail 100 records_producer records_consumer
down:
	docker compose down
stats:
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"
setup_test_env:
	docker compose -f docker-compose.test.yml up -d
teardown_test_env:
	docker compose -f docker-compose.test.yml down
test_producer:
	export POSTGRES_HOST=$(POSTGRES_HOST) && \
	export POSTGRES_PORT=$(POSTGRES_PORT) && \
	export POSTGRES_USERNAME=$(POSTGRES_USERNAME) && \
	export POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) && \
	export POSTGRES_DATABASE=$(POSTGRES_DATABASE) && \
	export RABBITMQ_HOST=$(RABBITMQ_HOST) && \
	export RABBITMQ_PORT=$(RABBITMQ_PORT) && \
	export RABBITMQ_USERNAME=$(RABBITMQ_USERNAME) && \
	export RABBITMQ_PASSWORD=$(RABBITMQ_PASSWORD) && \
	export QUEUE_NAME=$(QUEUE_NAME) && \
	COVERAGE_FILE=.coverage_producer coverage run -m pytest -vx --last-failed producer/tests
test_consumer:
	export POSTGRES_HOST=$(POSTGRES_HOST) && \
	export POSTGRES_PORT=$(POSTGRES_PORT) && \
	export POSTGRES_USERNAME=$(POSTGRES_USERNAME) && \
	export POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) && \
	export POSTGRES_DATABASE=$(POSTGRES_DATABASE) && \
	export RABBITMQ_HOST=$(RABBITMQ_HOST) && \
	export RABBITMQ_PORT=$(RABBITMQ_PORT) && \
	export RABBITMQ_USERNAME=$(RABBITMQ_USERNAME) && \
	export RABBITMQ_PASSWORD=$(RABBITMQ_PASSWORD) && \
	export QUEUE_NAME=$(QUEUE_NAME) && \
	export CSV_PARSER_RECOGNIZED_DATETIME_FORMATS=$(CSV_PARSER_RECOGNIZED_DATETIME_FORMATS) && \
	export CSV_PARSER_DELIMITER=$(CSV_PARSER_DELIMITER) && \
	COVERAGE_FILE=.coverage_consumer coverage run -m pytest -vx --last-failed consumer/tests
coverage_report:
	coverage combine .coverage_producer .coverage_consumer && \
	coverage report -m --omit="*/tests/*"
test: test_producer test_consumer coverage_report

generate_csv_demo:
	python test_generator.py \
		--num-sensors $(GEN_NUM_SENSORS) \
		--num-records $(GEN_NUM_RECORDS) \
		--record-interval $(GEN_RECORD_INTERVAL) \
		--start-date $(GEN_START_DATE) \
		--timezone $(GEN_TIMEZONE) \
		--dir $(TARGET_FILE_DIR)

generate_csv_end_to_end_test:
	python test_generator.py \
		--num-sensors 10 \
		--num-records 5 \
		--record-interval 1 \
		--start-date 2021-01-01 \
		--timezone Asia/Shanghai \
		--dir records_test
