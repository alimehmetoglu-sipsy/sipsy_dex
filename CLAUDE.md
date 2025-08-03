# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT: When Claude Code starts a new session, immediately display the "Available Custom Commands" section to show the user what commands are available.**

## 🚀 Available Custom Commands

When Claude Code starts, these custom commands are available:

| Command | Description | Action |
|---------|-------------|--------|
| **"test raporunu oku"** | Read and fix test report | Reads `C:\test_report.md`, analyzes findings, implements fixes, tests in Docker, and requests commit approval |
| **"projeyi başlat"** | Start the project | Runs `docker-compose up -d --build` to start all services |
| **"testleri çalıştır"** | Run comprehensive tests | Restarts Docker services and runs complete test suite including new AI features |

Simply type any of these commands to execute the corresponding workflow.

## Project Overview

DexAgents is a Windows endpoint management platform for remote PowerShell command execution and system monitoring. It consists of:
- **Backend**: FastAPI-based server with PostgreSQL database, WebSocket support, and comprehensive API
- **Frontend**: Next.js 15 application with shadcn/ui components and real-time features
- **Agent**: Python-based Windows client with PowerShell integration
- **Infrastructure**: Docker Compose setup with nginx reverse proxy

## 🏗️ Architecture

### Backend (FastAPI)
- **Location**: `/backend/`
- **Port**: 8080 (containerized: 8000)
- **Database**: PostgreSQL (port 5433)
- **Authentication**: JWT-based with admin/admin123 default credentials
- **WebSocket**: Real-time agent communication
- **API Docs**: http://localhost:8080/docs

### Frontend (Next.js 15)
- **Location**: `/frontend/`
- **Port**: 3000
- **Framework**: Next.js 15 with App Router
- **UI**: shadcn/ui components + Tailwind CSS
- **State**: React Context for authentication
- **Tests**: Playwright E2E tests

### Agent (Python)
- **Location**: `/agent/`
- **Platform**: Windows PowerShell integration
- **Communication**: WebSocket to backend
- **Features**: Command execution, system monitoring, heartbeat

## 🚀 Quick Start

### Development Setup
```bash
# 1. Copy environment variables
cp .env.example .env
# Edit .env with your API keys (especially OPENAI_API_KEY for AI features)

# 2. Start all services
docker-compose up -d --build

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access Points
- **Frontend**: http://localhost:3000 (admin/admin123)
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Database**: localhost:5433 (postgres/postgres123)

### Testing
```bash
# Frontend E2E tests
cd frontend
npm run test:e2e

# Backend API tests
cd backend
python comprehensive_api_test.py

# Run specific test
cd frontend
npx playwright test auth.spec.ts --headed
```

## 📁 Project Structure

```
dex_agent/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Auth, database, config
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── app/                # App router pages
│   ├── components/         # React components
│   ├── tests/e2e/          # Playwright tests
│   └── package.json
├── agent/                  # Windows agent
│   ├── windows_agent.py    # Main agent
│   ├── websocket_agent.py  # WebSocket client
│   └── requirements.txt
├── docker-compose.yml      # Development setup
└── CLAUDE.md              # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login (admin/admin123)
- `GET /api/v1/auth/me` - Get current user info

### Agents Management
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{id}` - Get agent details
- `DELETE /api/v1/agents/{id}` - Remove agent

### Commands
- `GET /api/v1/commands/saved` - List saved commands
- `POST /api/v1/commands` - Create new command
- `PUT /api/v1/commands/{id}` - Update command
- `DELETE /api/v1/commands/{id}` - Delete command
- `POST /api/v1/commands/agent/{id}/execute` - Execute command on agent

### AI Features
- `GET /api/v1/commands/ai/status` - Check AI service availability
- `POST /api/v1/ai/generate-command` - Generate commands using AI (ChatGPT/OpenAI)

### System
- `GET /api/v1/system/health` - System health check
- `GET /api/v1/system/info` - System information

### Settings
- `GET /api/v1/settings` - Get system settings (includes ChatGPT API key)
- `POST /api/v1/settings` - Update settings (including ChatGPT configuration)

## 🧪 Testing Strategy

### Prerequisites for Testing

#### Environment Setup
- **Required**: Copy `.env.example` to `.env` and configure:
  - `OPENAI_API_KEY`: Required for AI features testing
  - Database credentials
  - JWT settings
- **Note**: AI feature tests will fail without valid OpenAI API key

#### Python Requirements (Backend)
- **Python**: 3.11+ recommended
- **Core Dependencies**: 
  - fastapi>=0.104.1
  - uvicorn[standard]>=0.24.0
  - psycopg2-binary>=2.9.7 (PostgreSQL driver)
  - openai>=1.0.0 (AI features)
  - requests>=2.31.0 (API testing)
  - cryptography>=41.0.0 (Settings encryption)
- **Installation**: `pip install -r backend/requirements.txt`

#### Node.js Requirements (Frontend)
- **Node.js**: 18+ recommended
- **Core Dependencies**:
  - next: 15.2.4
  - react: ^18.3.1
  - @playwright/test: ^1.46.0 (E2E testing)
- **Installation**: `npm install` in frontend directory
- **Playwright Setup**: `npx playwright install` (downloads browsers)

#### System Requirements
- **Docker & Docker Compose**: For containerized development
- **PostgreSQL**: Version 15+ (containerized via docker-compose)
- **Chrome/Chromium**: For Playwright tests (auto-installed)

### Frontend Tests (Playwright)
- **Location**: `/frontend/tests/e2e/`
- **Coverage**: Authentication, Dashboard, Agents, Commands, API Integration, AI Features
- **AI Features**: Tests "Create Command with AI" button functionality and ChatGPT settings UI
- **Credentials**: admin/admin123
- **Base URL**: http://localhost:3000
- **Prerequisites**: 
  - `npm install` in frontend directory
  - `npx playwright install` (installs browsers)
  - Services running via `docker-compose up -d`

### Backend Tests
- **API Tests**: `comprehensive_api_test.py`
- **Coverage**: All major endpoints, authentication, error handling, AI features (command generation, ChatGPT settings)
- **Database**: Uses PostgreSQL test database
- **AI Features**: Tests AI command generation endpoint and ChatGPT settings management
- **Prerequisites**:
  - Python 3.11+ with requests library
  - Services running via `docker-compose up -d`
  - No additional dependencies (uses only Python standard library + requests)

### Test Files
```
frontend/tests/e2e/
├── auth.spec.ts           # Authentication tests
├── dashboard.spec.ts      # Dashboard functionality
├── agents.spec.ts         # Agent management
├── commands.spec.ts       # Command management
├── ai-features.spec.ts    # AI command generation and ChatGPT settings tests
├── api-integration.spec.ts # API testing
├── comprehensive.spec.ts   # End-to-end scenarios
└── helpers/
    ├── auth.ts           # Auth helper functions
    └── api-mocks.ts      # API mocking utilities
```

## 🧪 Test Process

### Comprehensive Test Suite
The **"testleri çalıştır"** command runs a complete test suite that includes:

1. **Docker Restart**: Stops and restarts all services for a clean test environment
2. **Backend API Tests**: Tests all endpoints including new AI features:
   - AI command generation (`/api/v1/ai/generate-command`)
   - ChatGPT settings management (`/api/v1/settings`)
   - All existing API endpoints (auth, agents, commands, system)
3. **Frontend E2E Tests**: Playwright tests including new AI features:
   - "Create Command with AI" button functionality
   - ChatGPT settings UI tests
   - All existing E2E tests (auth, dashboard, agents, commands)
4. **Pre-commit Tests**: Additional validation and security checks
5. **Performance Tests**: Basic response time validation
6. **Test Reporting**: Generates comprehensive HTML and markdown reports

### Test Execution Order
1. Docker services restart (`docker-compose down && docker-compose up -d --build`)
2. Backend API tests (45s timeout) - includes AI feature validation
3. Frontend E2E tests (120s timeout) - includes AI UI testing
4. Pre-commit comprehensive tests (45s timeout)
5. Performance validation
6. Report generation in `test-reports/[timestamp]/`

### New AI Feature Tests
- **Backend**: Multiple AI-related tests in comprehensive_api_test.py:
  - `test_ai_command_generation()` - Tests AI command generation endpoint
  - `test_chatgpt_settings()` - Tests ChatGPT settings management
  - `test_ai_button_always_visible()` - Tests AI status endpoint availability
  - `test_ai_redirect_to_settings()` - Tests AI behavior when not configured
- **Frontend**: Complete AI workflow testing in ai-features.spec.ts:
  - "Create Command with AI" button always visible test
  - ChatGPT configuration workflow test
  - Redirect to settings when not configured test
  - Direct AI functionality when configured test
  - Settings page ChatGPT configuration test
- **Coverage**: API endpoints, UI components, error handling, configuration management, user workflow

## 🔧 Development Commands

### Docker Management
```bash
# Start project
docker-compose up -d --build

# Stop project
docker-compose down

# View logs
docker-compose logs -f [service]

# Rebuild specific service
docker-compose up -d --build backend
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test:e2e
npm run test:e2e:headed    # With browser
npm run test:e2e:ui        # Interactive mode
```

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py

# Run tests
python comprehensive_api_test.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :3000
   lsof -i :8080
   
   # Stop conflicting processes
   docker-compose down
   ```

2. **Database Connection**
   ```bash
   # Check PostgreSQL container
   docker-compose logs postgres
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Frontend Build Issues**
   ```bash
   cd frontend
   rm -rf node_modules .next
   npm install
   npm run build
   ```

4. **Test Failures**
   ```bash
   # Install Playwright browsers
   cd frontend
   npx playwright install
   
   # Run with debug
   npx playwright test --debug
   ```

### Log Locations
- **Backend**: `docker-compose logs backend`
- **Frontend**: `docker-compose logs frontend`
- **Database**: `docker-compose logs postgres`

## 📝 Development Guidelines

### Code Style
- **Backend**: Follow PEP 8, use Black formatter
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Commits**: Conventional commits format

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Run test suite: `npm run test:e2e`
4. Create PR with description
5. Ensure CI passes

### Security Considerations
- JWT tokens expire in 24 hours
- API requires authentication (except /health)
- Input validation on all endpoints
- SQL injection protection with SQLAlchemy
- XSS protection in frontend

## 🔐 Authentication & Authorization

### Default Credentials
- **Username**: admin
- **Password**: admin123

### JWT Configuration
- **Secret**: Configure in `.env` file (JWT_SECRET_KEY)
- **Expiry**: 24 hours (configurable via JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
- **Algorithm**: HS256

### Protected Routes
- Frontend: All routes except `/login`
- Backend: All API routes except `/health` and `/login`

### API Keys Configuration
- **OpenAI API Key**: Required for AI features, set in `.env` (OPENAI_API_KEY)
- **GitHub Token**: Optional, for GitHub integration, set in `.env` (GITHUB_TOKEN)
- See `.env.example` for all available API key configurations

## 📊 Monitoring & Observability

### Health Checks
- **Backend**: `/api/v1/system/health`
- **Frontend**: Docker health check on port 3000
- **Database**: PostgreSQL health check

### Logging
- **Backend**: Structured logging with timestamps
- **Frontend**: Console logging in development
- **Agent**: File-based logging

## 🚀 Deployment

### Production Setup
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Environment variables
cp .env.example .env
# Edit .env with production values
```

### Environment Variables
- **Configuration**: Copy `.env.example` to `.env`
- **Required Keys**:
  - `OPENAI_API_KEY`: For AI command generation features
  - `DATABASE_URL`: PostgreSQL connection string
  - `JWT_SECRET_KEY`: Secure key for JWT tokens
- **Optional Keys**:
  - `GITHUB_TOKEN`: For GitHub integration
  - Additional AI provider keys (see `.env.example`)
- **Important**: Never commit `.env` file to git

## Memories and Notes

- ☒ Read test report from C:\test_report.md için benden her seferinde izin istemesin
- ☒ Project uses admin/admin123 for default authentication
- ☒ Playwright tests cover comprehensive frontend functionality
- ☒ Docker Compose manages all services in development
- ☒ PostgreSQL replaced SQLite for better production readiness

## Recent Updates

- ✅ Added comprehensive Playwright E2E test suite
- ✅ Implemented helper functions for authentication and API mocking
- ✅ Created detailed test documentation and guidelines
- ✅ Enhanced CLAUDE.md with complete project information
- ✅ Updated project architecture to use PostgreSQL
- ✅ Added custom commands for Claude Code integration