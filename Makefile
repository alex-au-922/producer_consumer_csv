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