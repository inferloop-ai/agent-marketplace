# Agent Workflow Builder - Development Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help setup dev build test clean deploy docker-build docker-push

# Default target
help: ## Show this help message
	@echo "Agent Workflow Builder - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

setup: ## Setup development environment
	@echo "🚀 Setting up development environment..."
	@chmod +x scripts/*.sh
	@./scripts/setup-dev.sh

install: ## Install all dependencies
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "📦 Installing backend dependencies..."
	@cd backend/api && pip install -r requirements.txt
	@cd backend/agent-engine && pip install -r requirements.txt
	@cd backend/workflow-engine && pip install -r requirements.txt

# =============================================================================
# DEVELOPMENT
# =============================================================================

dev: ## Start development environment
	@echo "🔥 Starting development environment..."
	@docker-compose -f docker-compose.yml up --build

dev-detached: ## Start development environment in background
	@echo "🔥 Starting development environment (detached)..."
	@docker-compose -f docker-compose.yml up -d --build

dev-frontend: ## Start only frontend development server
	@echo "🎨 Starting frontend development server..."
	@cd frontend && npm run dev

dev-api: ## Start only API development server
	@echo "🚀 Starting API development server..."
	@cd backend/api && python main.py

dev-logs: ## Show development logs
	@docker-compose logs -f

stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	@docker-compose down

restart: ## Restart development environment
	@echo "🔄 Restarting development environment..."
	@docker-compose restart

# =============================================================================
# DATABASE
# =============================================================================

db-migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	@./scripts/migrate-db.sh

db-seed: ## Seed database with initial data
	@echo "🌱 Seeding database..."
	@./scripts/seed-data.sh

db-reset: ## Reset database (WARNING: Destroys all data)
	@echo "⚠️ Resetting database..."
	@docker-compose down -v
	@docker-compose up -d postgres
	@sleep 5
	@make db-migrate
	@make db-seed

db-backup: ## Backup database
	@echo "💾 Backing up database..."
	@./scripts/backup-db.sh

# =============================================================================
# TESTING
# =============================================================================

test: ## Run all tests
	@echo "🧪 Running all tests..."
	@make test-frontend
	@make test-backend

test-frontend: ## Run frontend tests
	@echo "🎨 Running frontend tests..."
	@cd frontend && npm run test

test-backend: ## Run backend tests
	@echo "🚀 Running backend tests..."
	@cd backend/api && pytest
	@cd backend/agent-engine && pytest
	@cd backend/workflow-engine && pytest

test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	@cd frontend && npm run test:coverage
	@cd backend/api && pytest --cov=. --cov-report=html
	@cd backend/agent-engine && pytest --cov=. --cov-report=html

test-e2e: ## Run end-to-end tests
	@echo "🎭 Running E2E tests..."
	@cd tests/e2e && npm run test

# =============================================================================
# CODE QUALITY
# =============================================================================

lint: ## Run linting on all code
	@echo "🔍 Running linters..."
	@cd frontend && npm run lint
	@cd backend/api && flake8 . && black --check . && isort --check .
	@cd backend/agent-engine && flake8 . && black --check . && isort --check .

lint-fix: ## Fix linting issues
	@echo "🔧 Fixing linting issues..."
	@cd frontend && npm run lint:fix
	@cd backend/api && black . && isort .
	@cd backend/agent-engine && black . && isort .

format: ## Format all code
	@echo "✨ Formatting code..."
	@cd frontend && npm run format
	@make lint-fix

type-check: ## Run type checking
	@echo "🔒 Running type checks..."
	@cd frontend && npm run type-check
	@cd backend/api && mypy .
	@cd backend/agent-engine && mypy .

# =============================================================================
# BUILD & DEPLOYMENT
# =============================================================================

build: ## Build all services
	@echo "🏗️ Building all services..."
	@./scripts/build.sh

build-frontend: ## Build frontend only
	@echo "🎨 Building frontend..."
	@cd frontend && npm run build

build-docker: ## Build Docker images
	@echo "🐳 Building Docker images..."
	@docker-compose build

docker-build: ## Build and tag Docker images for deployment
	@echo "🐳 Building Docker images for deployment..."
	@docker build -t agent-workflow-frontend:latest ./frontend
	@docker build -t agent-workflow-api:latest ./backend/api
	@docker build -t agent-workflow-agent-engine:latest ./backend/agent-engine
	@docker build -t agent-workflow-workflow-engine:latest ./backend/workflow-engine

docker-push: ## Push Docker images to registry
	@echo "📤 Pushing Docker images..."
	@docker push agent-workflow-frontend:latest
	@docker push agent-workflow-api:latest
	@docker push agent-workflow-agent-engine:latest
	@docker push agent-workflow-workflow-engine:latest

# =============================================================================
# DEPLOYMENT
# =============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@./scripts/deploy.sh staging

deploy-prod: ## Deploy to production environment
	@echo "🚀 Deploying to production..."
	@./scripts/deploy.sh production

k8s-deploy: ## Deploy to Kubernetes
	@echo "☸️ Deploying to Kubernetes..."
	@kubectl apply -f deploy/kubernetes/

k8s-status: ## Check Kubernetes deployment status
	@echo "📊 Checking Kubernetes status..."
	@kubectl get pods,services,ingress -n agent-workflows

# =============================================================================
# MONITORING & MAINTENANCE
# =============================================================================

logs: ## View application logs
	@echo "📋 Viewing logs..."
	@docker-compose logs -f --tail=100

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ API unhealthy"
	@curl -f http://localhost:3000 || echo "❌ Frontend unhealthy"
	@curl -f http://localhost:8001/health || echo "❌ Agent Engine unhealthy"

clean: ## Clean up development environment
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@docker system prune -f
	@cd frontend && rm -rf node_modules .next
	@cd backend && find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@cd backend && find . -name "*.pyc" -delete 2>/dev/null || true

reset: ## Reset entire development environment
	@echo "🔄 Resetting development environment..."
	@make clean
	@make setup
	@make install
	@make dev

# =============================================================================
# UTILITIES
# =============================================================================

shell-api: ## Open shell in API container
	@docker-compose exec api bash

shell-agent: ## Open shell in Agent Engine container
	@docker-compose exec agent-engine bash

shell-postgres: ## Open PostgreSQL shell
	@docker-compose exec postgres psql -U postgres -d agent_workflows

shell-redis: ## Open Redis shell
	@docker-compose exec redis redis-cli

update-deps: ## Update all dependencies
	@echo "📦 Updating dependencies..."
	@cd frontend && npm update
	@cd backend/api && pip list --outdated
	@cd backend/agent-engine && pip list --outdated

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@cd docs && mkdocs serve

# =============================================================================
# SECURITY
# =============================================================================

security-scan: ## Run security vulnerability scan
	@echo "🔒 Running security scan..."
	@cd frontend && npm audit
	@cd backend/api && safety check
	@cd backend/agent-engine && safety check

# =============================================================================
# INFORMATION
# =============================================================================

info: ## Show project information
	@echo "ℹ️ Agent Workflow Builder Information:"
	@echo "   Frontend: React/Next.js (Port 3000)"
	@echo "   API: FastAPI (Port 8000)"
	@echo "   Agent Engine: Python (Port 8001)"
	@echo "   Workflow Engine: Python (Port 8002)"
	@echo "   Database: PostgreSQL (Port 5432)"
	@echo "   Cache: Redis (Port 6379)"
	@echo "   Vector DB: Qdrant (Port 6333)"
	@echo ""
	@echo "📚 Documentation: http://localhost:8000/docs"
	@echo "🎨 Application: http://localhost:3000"
	@echo ""