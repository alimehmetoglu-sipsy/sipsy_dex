# DexAgent Monorepo Makefile
# Modern Windows Endpoint Management Platform

.PHONY: help dev-up dev-down dev-restart dev-logs test-all test-integration test-performance test-e2e test-smoke test-backend test-frontend test-frontend-e2e test-docker test-coverage test-reports test-env-up test-env-down test-cleanup lint-all build-prod clean-all

# Default target
.DEFAULT_GOAL := help

# Colors for output
YELLOW := \033[33m
GREEN := \033[32m
BLUE := \033[34m
RED := \033[31m
NC := \033[0m # No Color

# Help target
help: ## Show this help message
	@echo "$(BLUE)DexAgent Development Commands$(NC)"
	@echo "$(YELLOW)=============================$(NC)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Environment Commands
dev-up: ## Start development environment
	@echo "$(BLUE)Starting DexAgent development environment...$(NC)"
	docker compose up -d --build
	@echo "$(GREEN)✅ Development environment started$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend API: http://localhost:8080/docs$(NC)"
	@echo "$(YELLOW)Database: localhost:5433$(NC)"

dev-down: ## Stop development environment
	@echo "$(BLUE)Stopping DexAgent development environment...$(NC)"
	docker compose down
	@echo "$(GREEN)✅ Development environment stopped$(NC)"

dev-restart: ## Restart development environment
	@echo "$(BLUE)Restarting DexAgent development environment...$(NC)"
	$(MAKE) dev-down
	$(MAKE) dev-up

dev-logs: ## View development logs
	@echo "$(BLUE)Viewing development logs (Ctrl+C to exit)...$(NC)"
	docker compose logs -f

dev-logs-backend: ## View backend logs only
	@echo "$(BLUE)Viewing backend logs (Ctrl+C to exit)...$(NC)"
	docker compose logs -f backend

dev-logs-frontend: ## View frontend logs only
	@echo "$(BLUE)Viewing frontend logs (Ctrl+C to exit)...$(NC)"
	docker compose logs -f frontend

dev-status: ## Check development environment status
	@echo "$(BLUE)Development Environment Status:$(NC)"
	@docker compose ps

status: dev-status ## Alias for dev-status
dev: dev-up ## Alias for dev-up
logs: dev-logs ## Alias for dev-logs  
stop: dev-down ## Alias for dev-down
restart: dev-restart ## Alias for dev-restart
clean: clean-all ## Alias for clean-all

# Testing Commands
test-all: ## Run comprehensive test suite
	@echo "$(BLUE)Running comprehensive test suite...$(NC)"
	./tests/scripts/run_tests.sh all --parallel --coverage
	@echo "$(GREEN)✅ All tests completed$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	./tests/scripts/run_tests.sh integration
	@echo "$(GREEN)✅ Integration tests completed$(NC)"

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	./tests/scripts/run_tests.sh performance
	@echo "$(GREEN)✅ Performance tests completed$(NC)"

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	./tests/scripts/run_tests.sh e2e
	@echo "$(GREEN)✅ E2E tests completed$(NC)"

test-smoke: ## Run smoke tests
	@echo "$(BLUE)Running smoke tests...$(NC)"
	./tests/scripts/run_tests.sh smoke
	@echo "$(GREEN)✅ Smoke tests completed$(NC)"

test-backend: ## Run backend unit tests
	@echo "$(BLUE)Running backend unit tests...$(NC)"
	cd apps/backend && python -m pytest tests/ -v
	cd apps/backend && python comprehensive_api_test.py
	@echo "$(GREEN)✅ Backend tests completed$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd apps/frontend && npm test
	cd apps/frontend && npm run test:e2e
	@echo "$(GREEN)✅ Frontend tests completed$(NC)"

test-frontend-e2e: ## Run frontend E2E tests only
	@echo "$(BLUE)Running frontend E2E tests...$(NC)"
	cd apps/frontend && npm run test:e2e
	@echo "$(GREEN)✅ Frontend E2E tests completed$(NC)"

test-docker: ## Run tests in Docker environment
	@echo "$(BLUE)Running tests in Docker environment...$(NC)"
	./tests/scripts/run_tests.sh all --docker
	@echo "$(GREEN)✅ Docker tests completed$(NC)"

test-coverage: ## Generate test coverage report
	@echo "$(BLUE)Generating test coverage report...$(NC)"
	./tests/scripts/run_tests.sh all --coverage
	@echo "$(GREEN)✅ Coverage report generated at tests/coverage/html/index.html$(NC)"

test-reports: ## Generate test reports
	@echo "$(BLUE)Generating test reports...$(NC)"
	python tests/scripts/generate_performance_report.py
	@echo "$(GREEN)✅ Test reports generated$(NC)"

test-env-up: ## Start test environment
	@echo "$(BLUE)Starting test environment...$(NC)"
	docker compose -f tests/docker-compose.test.yml up -d
	@echo "$(GREEN)✅ Test environment started$(NC)"
	@echo "$(YELLOW)Test Reports: http://localhost:8082$(NC)"

test-env-down: ## Stop test environment
	@echo "$(BLUE)Stopping test environment...$(NC)"
	docker compose -f tests/docker-compose.test.yml down
	@echo "$(GREEN)✅ Test environment stopped$(NC)"

test-cleanup: ## Clean up test data and artifacts
	@echo "$(BLUE)Cleaning up test data...$(NC)"
	rm -rf tests/results/* tests/logs/* tests/coverage/* tests/screenshots/*
	docker compose -f tests/docker-compose.test.yml down -v
	@echo "$(GREEN)✅ Test cleanup completed$(NC)"

test-e2e-ui: ## Run E2E tests with UI
	@echo "$(BLUE)Running E2E tests with UI...$(NC)"
	cd apps/frontend && npm run test:e2e:ui

# Code Quality Commands
lint-all: ## Run linting on all code
	@echo "$(BLUE)Running linting on all code...$(NC)"
	@echo "$(YELLOW)Frontend linting...$(NC)"
	cd apps/frontend && npm run lint || true
	@echo "$(YELLOW)Backend linting...$(NC)"
	cd apps/backend && python -m flake8 . || true
	@echo "$(GREEN)✅ Linting completed$(NC)"

format-all: ## Format all code
	@echo "$(BLUE)Formatting all code...$(NC)"
	@echo "$(YELLOW)Frontend formatting...$(NC)"
	cd apps/frontend && npm run format || true
	@echo "$(YELLOW)Backend formatting...$(NC)"
	cd apps/backend && python -m black . && python -m isort . || true
	@echo "$(GREEN)✅ Code formatting completed$(NC)"

type-check: ## Run TypeScript type checking
	@echo "$(BLUE)Running TypeScript type checking...$(NC)"
	cd apps/frontend && npm run type-check

# Build Commands
build-all: ## Build all applications
	@echo "$(BLUE)Building all applications...$(NC)"
	$(MAKE) build-packages
	$(MAKE) build-apps
	@echo "$(GREEN)✅ All applications built$(NC)"

build-packages: ## Build shared packages
	@echo "$(BLUE)Building shared packages...$(NC)"
	cd packages/shared-types && npm run build || true
	cd packages/shared-utils && npm run build || true
	@echo "$(GREEN)✅ Packages built$(NC)"

build-apps: ## Build applications
	@echo "$(BLUE)Building applications...$(NC)"
	cd apps/frontend && npm run build
	@echo "$(GREEN)✅ Applications built$(NC)"

build-prod: ## Build production Docker images
	@echo "$(BLUE)Building production Docker images...$(NC)"
	docker compose -f docker-compose.prod.yml build
	@echo "$(GREEN)✅ Production images built$(NC)"

# Database Commands
db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd apps/backend && python app/migrations/migration_manager.py
	@echo "$(GREEN)✅ Database migrations completed$(NC)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠️  WARNING: This will destroy all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Resetting database...$(NC)"; \
		$(MAKE) dev-down; \
		docker volume prune -f; \
		$(MAKE) dev-up; \
		sleep 15; \
		$(MAKE) db-migrate; \
		echo "$(GREEN)✅ Database reset completed$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

db-seed: ## Seed database with default data
	@echo "$(BLUE)Seeding database with default data...$(NC)"
	cd apps/backend && python app/scripts/insert_default_commands.py
	@echo "$(GREEN)✅ Database seeded$(NC)"

db-backup: ## Backup database
	@echo "$(BLUE)Creating database backup...$(NC)"
	docker compose exec postgres pg_dump -U dexagents -d dexagents > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backup created$(NC)"

# Agent Commands
agent-build: ## Build Windows agent executable
	@echo "$(BLUE)Building Windows agent executable...$(NC)"
	cd apps/agent && python modern_build_exe.py
	@echo "$(GREEN)✅ Agent executable built in apps/agent/dist/$(NC)"

agent-test: ## Test Windows agent
	@echo "$(BLUE)Testing Windows agent...$(NC)"
	cd apps/agent && python test_modern_agent.py

# Utility Commands
clean-all: ## Clean all build artifacts and dependencies
	@echo "$(BLUE)Cleaning all build artifacts...$(NC)"
	$(MAKE) clean-node-modules
	$(MAKE) clean-build
	$(MAKE) clean-docker
	@echo "$(GREEN)✅ All artifacts cleaned$(NC)"

clean-node-modules: ## Remove all node_modules directories
	@echo "$(BLUE)Removing node_modules directories...$(NC)"
	find . -name 'node_modules' -type d -prune -exec rm -rf '{}' + 2>/dev/null || true

clean-build: ## Remove build directories
	@echo "$(BLUE)Removing build directories...$(NC)"
	find . -name 'dist' -o -name 'build' -o -name '.next' | grep -v node_modules | xargs rm -rf 2>/dev/null || true

clean-docker: ## Clean Docker environment
	@echo "$(BLUE)Cleaning Docker environment...$(NC)"
	docker compose down -v
	docker system prune -f

# Health Checks
health: ## Check system health
	@echo "$(BLUE)Checking system health...$(NC)"
	@echo "$(YELLOW)Backend health:$(NC)"
	@curl -sf http://localhost:8080/api/v1/system/health > /dev/null && echo "$(GREEN)✅ Backend is healthy$(NC)" || echo "$(RED)❌ Backend not responding$(NC)"
	@echo "$(YELLOW)Frontend health:$(NC)"
	@curl -sf http://localhost:3000/api/health > /dev/null && echo "$(GREEN)✅ Frontend is healthy$(NC)" || echo "$(RED)❌ Frontend not responding$(NC)"

health-detailed: ## Detailed health check with metrics
	@echo "$(BLUE)Detailed health check...$(NC)"
	@echo "$(YELLOW)System Info:$(NC)"
	curl -s http://localhost:8080/api/v1/system/info | python -m json.tool || echo "$(RED)Backend not responding$(NC)"
	@echo "$(YELLOW)Docker Status:$(NC)"
	docker compose ps

# Installation Commands
install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	npm install
	cd apps/frontend && npm install
	cd apps/backend && pip install -r requirements.txt
	@echo "$(GREEN)✅ All dependencies installed$(NC)"

install-pre-commit: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks installed$(NC)"

# Production Commands
prod-up: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	docker compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production environment started$(NC)"

prod-down: ## Stop production environment
	@echo "$(BLUE)Stopping production environment...$(NC)"
	docker compose -f docker-compose.prod.yml down

prod-logs: ## View production logs
	@echo "$(BLUE)Viewing production logs...$(NC)"
	docker compose -f docker-compose.prod.yml logs -f

prod-deploy: ## Deploy production with health checks
	@echo "$(BLUE)Deploying production environment...$(NC)"
	docker compose -f docker-compose.prod.yml up -d --build
	@echo "$(YELLOW)Waiting for services to be healthy...$(NC)"
	sleep 30
	$(MAKE) docker-health
	@echo "$(GREEN)✅ Production deployment completed$(NC)"

# Docker Optimization Commands
docker-stats: ## Show container resource usage
	@echo "$(BLUE)Container resource usage:$(NC)"
	docker stats --no-stream

docker-health: ## Check all container health statuses
	@echo "$(BLUE)Container health status:$(NC)"
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

docker-prune: ## Clean up unused Docker resources
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker system prune -f
	docker volume prune -f
	docker network prune -f
	@echo "$(GREEN)✅ Docker cleanup completed$(NC)"

docker-optimize: ## Optimize Docker images and containers
	@echo "$(BLUE)Optimizing Docker environment...$(NC)"
	$(MAKE) docker-prune
	docker image prune -a -f
	@echo "$(GREEN)✅ Docker optimization completed$(NC)"

docker-size: ## Show Docker image sizes
	@echo "$(BLUE)Docker image sizes:$(NC)"
	docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Monitoring Commands
monitor-up: ## Start monitoring services
	@echo "$(BLUE)Starting monitoring stack...$(NC)"
	docker compose -f monitoring/docker-compose.monitoring.yml up -d
	@echo "$(GREEN)✅ Monitoring services started$(NC)"
	@echo "$(YELLOW)Grafana: http://localhost:3001 (admin/admin123)$(NC)"
	@echo "$(YELLOW)Prometheus: http://localhost:9090$(NC)"
	@echo "$(YELLOW)AlertManager: http://localhost:9093$(NC)"

monitor-down: ## Stop monitoring services
	@echo "$(BLUE)Stopping monitoring services...$(NC)"
	docker compose -f monitoring/docker-compose.monitoring.yml down

monitor-restart: ## Restart monitoring services
	@echo "$(BLUE)Restarting monitoring services...$(NC)"
	$(MAKE) monitor-down
	$(MAKE) monitor-up

monitor-logs: ## View monitoring logs
	@echo "$(BLUE)Viewing monitoring logs (Ctrl+C to exit)...$(NC)"
	docker compose -f monitoring/docker-compose.monitoring.yml logs -f

monitor-status: ## Check monitoring services status
	@echo "$(BLUE)Monitoring services status:$(NC)"
	docker compose -f monitoring/docker-compose.monitoring.yml ps

monitor-metrics: ## View current metrics
	@echo "$(BLUE)Current system metrics:$(NC)"
	curl -s http://localhost:8080/api/v1/stats | python -m json.tool || echo "$(RED)Backend metrics not available$(NC)"

monitor-alerts: ## Check active alerts
	@echo "$(BLUE)Active alerts:$(NC)"
	curl -s http://localhost:9093/api/v1/alerts | python -m json.tool || echo "$(RED)AlertManager not available$(NC)"

monitor-start: monitor-up ## Alias for monitor-up
monitor-stop: monitor-down ## Alias for monitor-down

# Documentation Commands
docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	cd docs && python -m http.server 8000

# Quick Start
quick-start: ## Quick start development environment
	@echo "$(BLUE)🚀 DexAgent Quick Start$(NC)"
	@echo "$(YELLOW)1. Installing dependencies...$(NC)"
	$(MAKE) install
	@echo "$(YELLOW)2. Starting development environment...$(NC)"
	$(MAKE) dev-up
	@echo "$(YELLOW)3. Waiting for services to be ready...$(NC)"
	sleep 10
	@echo "$(YELLOW)4. Running database migrations...$(NC)"
	$(MAKE) db-migrate
	@echo "$(YELLOW)5. Seeding database...$(NC)"
	$(MAKE) db-seed
	@echo "$(GREEN)✅ Quick start completed!$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000 (admin/admin123)$(NC)"
	@echo "$(BLUE)Backend: http://localhost:8080/docs$(NC)"

# Development workflow
dev-workflow: ## Run complete development workflow
	@echo "$(BLUE)Running complete development workflow...$(NC)"
	$(MAKE) format-all
	$(MAKE) lint-all
	$(MAKE) type-check
	$(MAKE) test-all
	@echo "$(GREEN)✅ Development workflow completed$(NC)"