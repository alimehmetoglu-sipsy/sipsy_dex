# DEVELOPMENT_SETUP.md

## Prerequisites

### Required Software
- **Docker** (20.10+) & **Docker Compose** (2.0+)
- **Git** (2.30+)
- **Node.js** (18+) & **npm** (9+)
- **Python** (3.11+) & **pip**
- **Make** (for development commands)

### Optional (for local development)
- **PostgreSQL** (15+)
- **VS Code** with recommended extensions

## Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd dex_agent

# 2. Copy environment variables
cp apps/backend/.env.example apps/backend/.env

# 3. Configure environment (edit .env file)
# - Set OPENAI_API_KEY for AI features
# - Configure database credentials
# - Set JWT secret key

# 4. Start all services
make dev-up

# 5. Access the application
open http://localhost:3000
# Login: admin / admin123
```

## Development Environment Details

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| **frontend** | 3000 | Next.js development server |
| **backend** | 8080 | FastAPI backend (internal: 8000) |
| **postgres** | 5433 | PostgreSQL database |
| **nginx** | 80 | Reverse proxy (production only) |

### Environment Variables

#### Backend Configuration (`.env`)
```env
# Database
DATABASE_URL=postgresql://postgres:postgres123@localhost:5433/dex_agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=dex_agent

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Integration
OPENAI_API_KEY=your-openai-api-key-here

# Application
DEBUG=true
LOG_LEVEL=INFO
```

#### Frontend Configuration
- Environment variables automatically loaded from backend
- No additional configuration required for development

## Local Development (Without Docker)

### Backend Setup
```bash
# Navigate to backend
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb dex_agent
python app/migrations/migration_manager.py

# Run development server
python run.py
```

### Frontend Setup
```bash
# Navigate to frontend
cd apps/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Database Setup (Local PostgreSQL)
```bash
# Install PostgreSQL 15+
brew install postgresql  # macOS
# or apt-get install postgresql-15  # Ubuntu

# Create database and user
createdb dex_agent
psql dex_agent -c "CREATE USER postgres WITH PASSWORD 'postgres123';"
psql dex_agent -c "GRANT ALL PRIVILEGES ON DATABASE dex_agent TO postgres;"

# Run migrations
cd apps/backend
python app/migrations/migration_manager.py
```

## Agent Development

### Python Agent Setup
```bash
# Navigate to agent directory
cd apps/agent

# Install dependencies
pip install -r requirements.txt

# Configure agent
cp config.json.example config.json
# Edit config.json with backend URL

# Test agent (Windows only)
python windows_agent.py
```

### Building Agent Executable
```bash
# Install build dependencies
pip install -r modern_requirements.txt

# Build executable
python modern_build_exe.py

# Output: dist/DexAgent.exe
```

## Development Tools

### Makefile Commands
```bash
# Development Environment
make dev-up          # Start all services
make dev-down        # Stop all services
make dev-restart     # Restart all services
make dev-logs        # View logs

# Testing
make test-all        # Run all tests
make test-backend    # Backend tests only
make test-frontend   # Frontend tests only
make test-e2e        # End-to-end tests

# Code Quality
make lint-all        # Run linting
make format-all      # Format code
make type-check      # TypeScript type checking

# Database
make db-migrate      # Run database migrations
make db-reset        # Reset database
make db-seed         # Seed test data

# Production
make build-prod      # Build production images
make deploy-prod     # Deploy to production
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Quality Tools

#### Backend (Python)
- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pytest** - Testing framework

#### Frontend (TypeScript)
- **ESLint** - Linting and code quality
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **Playwright** - E2E testing
- **Jest** - Unit testing

## Testing

### Backend Tests
```bash
# Run all backend tests
cd apps/backend
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_api.py

# Run comprehensive API tests
python comprehensive_api_test.py
```

### Frontend Tests
```bash
# Unit tests
cd apps/frontend
npm test

# E2E tests
npm run test:e2e

# E2E tests with UI
npm run test:e2e:headed

# Interactive test mode
npm run test:e2e:ui
```

### Integration Tests
```bash
# Full workflow tests
cd tests/integration
python -m pytest test_full_workflow.py

# Performance tests
cd tests/performance
python test_load.py
```

## Database Management

### Migrations
```bash
# Create new migration
cd apps/backend
python app/migrations/create_migration.py "description"

# Run migrations
python app/migrations/migration_manager.py

# Check migration status
python app/migrations/migration_manager.py --status
```

### Database Access
```bash
# Connect to database
psql postgresql://postgres:postgres123@localhost:5433/dex_agent

# Or via Docker
docker-compose exec postgres psql -U postgres -d dex_agent
```

### Backup and Restore
```bash
# Backup database
pg_dump postgresql://postgres:postgres123@localhost:5433/dex_agent > backup.sql

# Restore database
psql postgresql://postgres:postgres123@localhost:5433/dex_agent < backup.sql
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check port usage
lsof -i :3000  # Frontend
lsof -i :8080  # Backend
lsof -i :5433  # Database

# Kill processes using ports
kill -9 $(lsof -t -i:3000)
```

#### 2. Docker Issues
```bash
# Clean Docker environment
make dev-down
docker system prune -f
docker volume prune -f

# Rebuild containers
make dev-up --build
```

#### 3. Database Connection Problems
```bash
# Check database status
docker-compose logs postgres

# Reset database
make db-reset

# Check connection
psql postgresql://postgres:postgres123@localhost:5433/dex_agent -c "SELECT 1;"
```

#### 4. Permission Issues
```bash
# Fix file ownership (Linux/macOS)
sudo chown -R $USER:$USER .

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### 5. Node.js Dependencies
```bash
# Clear node_modules and reinstall
cd apps/frontend
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
```

#### 6. Python Dependencies
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
cd apps/backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Log Locations

#### Docker Environment
```bash
# View all logs
docker-compose logs

# Specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f backend
```

#### Local Development
- **Backend**: `apps/backend/logs/`
- **Frontend**: Console output
- **Agent**: `apps/agent/logs/`

### Environment Validation
```bash
# Check all services
make health-check

# Validate backend API
curl http://localhost:8080/api/v1/system/health

# Validate frontend
curl http://localhost:3000/api/health

# Test database connection
psql postgresql://postgres:postgres123@localhost:5433/dex_agent -c "SELECT version();"
```

## IDE Configuration

### VS Code Recommended Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-playwright.playwright",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./apps/backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

## Performance Optimization

### Development Mode
- Hot reload enabled for frontend and backend
- Debug mode enabled with detailed logging
- Source maps enabled for debugging

### Production Mode
- Optimized Docker images
- Static asset optimization
- Database connection pooling
- Nginx reverse proxy configuration

---

**Setup Version**: 3.3 - Optimized for Claude Code integration

For additional help, see:
- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) - Project overview
- [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - System architecture  
- [API_REFERENCE.md](./API_REFERENCE.md) - API documentation