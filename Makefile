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
test_env:
	docker compose -f docker-compose.test.yml up -d
