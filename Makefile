.PHONY: help up down restart db-shell clean

help:
	@echo "Content Sharing Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make up        - Start the project (database and API)"
	@echo "  make down      - Stop the project"
	@echo "  make restart   - Restart the project"
	@echo "  make db-shell  - Open PostgreSQL shell"
	@echo "  make clean     - Stop and remove all containers and volumes"

up:
	@echo "Starting database..."
	docker-compose up -d postgres
	@echo "Starting API..."
	docker-compose up -d api

down:
	docker-compose down

restart:
	docker-compose restart

db-shell:
	docker-compose exec postgres psql -U postgres -d content_sharing_platform

clean:
	@echo "Removing all containers and volumes..."
	docker-compose down -v
