# PROJECT_CONTEXT.md

## Quick Overview

DexAgent is a **Modern Windows Endpoint Management Platform** that enables real-time PowerShell command execution and system monitoring across Windows endpoints through a web-based dashboard.

## Technology Stack

- **Backend**: FastAPI + PostgreSQL + WebSocket
- **Frontend**: Next.js 15 + shadcn/ui + TypeScript  
- **Agent**: Python + PowerShell integration
- **Deployment**: Docker Compose + Nginx
- **Testing**: pytest + Jest + Playwright E2E

## Key Features

- ✅ Real-time PowerShell execution on Windows endpoints
- ✅ WebSocket-based agent communication
- ✅ Modern web dashboard with real-time updates
- ✅ Agent monitoring and heartbeat tracking
- ✅ Comprehensive Docker deployment
- ✅ AI-powered command generation with ChatGPT integration

## Development Commands

| Command | Description |
|---------|-------------|
| `make dev-up` | Start development environment |
| `make dev-down` | Stop development environment |
| `make test-all` | Run comprehensive test suite |
| `make lint-all` | Run linting across all packages |
| `make build-prod` | Build for production |

## Key Endpoints

- **Frontend**: http://localhost:3000 (admin/admin123)
- **Backend API**: http://localhost:8080/docs
- **WebSocket**: ws://localhost:8080/api/v1/ws/agent
- **Health Check**: http://localhost:8080/api/v1/system/health

## Project Structure

```
dex_agent/
├── apps/                    # Applications
│   ├── backend/            # FastAPI backend
│   ├── frontend/           # Next.js frontend
│   ├── agent/              # Windows agent
│   └── docs/               # Documentation
├── packages/               # Shared packages
│   ├── shared-types/       # TypeScript types
│   ├── shared-utils/       # Common utilities
│   ├── shared-components/  # React components
│   └── shared-constants/   # Application constants
├── tests/                  # Testing infrastructure
│   ├── e2e/               # End-to-end tests
│   ├── integration/       # Integration tests
│   └── performance/       # Performance tests
├── tools/                  # Development tools
│   ├── scripts/           # Build/deployment scripts
│   ├── generators/        # Code generators
│   └── analyzers/         # Code analysis tools
├── monitoring/            # Monitoring setup
│   ├── grafana/          # Grafana dashboards
│   ├── prometheus/       # Metrics collection
│   └── alerts/           # Alerting configuration
└── docs/                 # Project documentation
```

## Critical Files

- **Backend**: `apps/backend/app/main.py` - FastAPI application entry point
- **Frontend**: `apps/frontend/app/layout.tsx` - Next.js root layout
- **Agent**: `apps/agent/windows_agent.py` - Windows agent main file
- **API Routes**: `apps/backend/app/api/v1/` - REST API endpoints
- **WebSocket**: `apps/backend/app/api/v1/websocket.py` - Real-time communication
- **Database**: `apps/backend/app/models/` - SQLAlchemy models
- **Frontend Components**: `apps/frontend/components/` - React components

## Recent Changes (Version 3.3)

- ✅ Project structure reorganized for monorepo pattern
- ✅ Comprehensive documentation added
- ✅ AI-powered command generation integrated
- ✅ Enhanced testing infrastructure with Playwright
- ✅ PostgreSQL database migration completed
- ✅ Modern development workflow with Make commands

## Quick Start

```bash
# 1. Clone and setup
git clone <repository>
cd dex_agent

# 2. Copy environment variables
cp apps/backend/.env.example apps/backend/.env
# Edit .env with your API keys

# 3. Start all services
make dev-up

# 4. Access the application
open http://localhost:3000
```

## Next Steps

1. Review [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) for system design
2. Follow [DEVELOPMENT_SETUP.md](./DEVELOPMENT_SETUP.md) for local development
3. Check [API_REFERENCE.md](./API_REFERENCE.md) for API documentation
4. Run `make test-all` to validate your setup

---

**Latest Update**: Project restructured for Claude Code optimization (Phase 1 Complete)