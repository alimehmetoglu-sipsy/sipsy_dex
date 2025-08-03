# DexAgent - Windows Endpoint Management Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://docker.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)

> 🚀 **Modern, scalable Windows endpoint management platform for remote PowerShell command execution and comprehensive system monitoring through an intuitive web dashboard.**

## 🌟 Features

### 🎯 Core Capabilities
- **Real-time Command Execution**: Execute PowerShell commands on remote Windows endpoints instantly
- **Live Agent Monitoring**: Monitor agent status, heartbeat, and system metrics in real-time
- **WebSocket Communication**: Bi-directional real-time communication between agents and server
- **Multi-Agent Management**: Centrally manage multiple Windows endpoints from a single dashboard
- **Command Library**: Save, organize, and reuse frequently used PowerShell commands
- **AI-Powered Commands**: Generate PowerShell commands using ChatGPT integration

### 🔐 Security & Authentication
- **JWT Authentication**: Secure token-based authentication system
- **Role-Based Access**: Admin and user role separation
- **Input Validation**: Comprehensive input sanitization and validation
- **Audit Logging**: Complete audit trail of all user actions and system events
- **Secure WebSocket**: WSS/TLS encrypted real-time communications

### 📊 Monitoring & Analytics
- **System Metrics**: CPU, memory, disk usage, and network statistics
- **Performance Dashboards**: Real-time system performance visualization
- **Alert Management**: Configurable alerts for system events and thresholds
- **Historical Data**: Track system performance trends over time
- **Health Checks**: Automated endpoint health monitoring

### 🛠️ Developer Experience
- **Modern Tech Stack**: Next.js 15, FastAPI, PostgreSQL, TypeScript
- **Monorepo Architecture**: Well-organized codebase with shared packages
- **Comprehensive Testing**: Unit, integration, E2E, and performance tests
- **CI/CD Pipeline**: Automated testing and deployment workflows
- **Docker Support**: Complete containerization for development and production
- **Project Management**: Integrated Jira workflows and Git automation

## 🏗️ Architecture

```
DexAgent/
├── apps/                    # Application modules
│   ├── backend/            # FastAPI server
│   ├── frontend/           # Next.js dashboard
│   └── agent/              # Windows PowerShell agent
├── packages/               # Shared libraries
│   ├── shared-types/       # TypeScript type definitions
│   ├── shared-utils/       # Common utilities
│   └── shared-constants/   # Application constants
├── tests/                  # Comprehensive test suite
├── tools/                  # Development and automation tools
├── monitoring/             # Observability infrastructure
└── docs/                   # Project documentation
```

### 🎯 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 15, React 18, TypeScript | Modern web dashboard |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy | REST API and WebSocket server |
| **Database** | PostgreSQL 15+ | Primary data storage |
| **Agent** | Python 3.11+, PowerShell | Windows endpoint client |
| **UI Framework** | shadcn/ui, Tailwind CSS | Modern component library |
| **State Management** | React Context, SWR | Client-side state |
| **Authentication** | JWT, bcrypt | Secure authentication |
| **Real-time** | WebSockets, FastAPI WebSocket | Live communication |
| **Testing** | Playwright, pytest, Jest | Comprehensive testing |
| **DevOps** | Docker, GitHub Actions | Containerization and CI/CD |

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Node.js 18+** (for local development)
- **Python 3.11+** (for local development)
- **PostgreSQL 15+** (if not using Docker)

### 🐳 Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dex_agent
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - **Dashboard**: http://localhost:3000
   - **API Documentation**: http://localhost:8080/docs
   - **Default Login**: admin / admin123

### ⚡ Quick Commands

```bash
# Start development environment
make dev

# Run all tests
make test-all

# View service status
make status

# View logs
make logs

# Stop all services
make stop

# Clean and restart
make clean && make dev
```

### 🛠️ Local Development Setup

<details>
<summary>Click to expand local development instructions</summary>

#### Backend Development
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

#### Frontend Development
```bash
cd apps/frontend
npm install
npm run dev
```

#### Database Setup
```bash
# Using Docker
docker run -d \
  --name dexagent-postgres \
  -e POSTGRES_DB=dexagents \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres123 \
  -p 5433:5432 \
  postgres:15
```

</details>

## 📚 Documentation

### 📖 Core Documentation
- **[Project Context](PROJECT_CONTEXT.md)** - Project overview and quick reference
- **[Architecture Guide](ARCHITECTURE_GUIDE.md)** - Detailed system architecture
- **[Development Setup](DEVELOPMENT_SETUP.md)** - Local development guide
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Project Management](docs/PROJECT_MANAGEMENT.md)** - Jira integration and workflows

### 🧪 Testing Documentation
- **[Test README](tests/README.md)** - Testing strategy and execution
- **[Frontend E2E Tests](apps/frontend/tests/e2e/)** - Playwright test suite
- **[Backend API Tests](apps/backend/tests/)** - FastAPI test suite

### 🔧 Development Guides
- **[Makefile Commands](Makefile)** - Available development commands
- **[Docker Configuration](docker-compose.yml)** - Container orchestration
- **[CI/CD Pipeline](.github/workflows/)** - GitHub Actions workflows

## 🎯 Key Features Deep Dive

### 🖥️ Windows Agent
The DexAgent Windows client provides:
- **PowerShell Integration**: Native PowerShell command execution
- **System Monitoring**: Real-time system metrics collection
- **Heartbeat Mechanism**: Continuous connectivity verification
- **Auto-Reconnection**: Robust connection management
- **GUI & Console**: Both graphical and command-line interfaces

### 🌐 Web Dashboard
Modern React-based dashboard featuring:
- **Real-time Updates**: Live agent status and metrics
- **Command Management**: Save, organize, and execute commands
- **Agent Overview**: Comprehensive agent information and history
- **System Monitoring**: Performance graphs and system health
- **Settings Management**: Configuration and user preferences

### 🔌 REST API
Comprehensive FastAPI backend providing:
- **Agent Management**: Registration, status, and lifecycle management
- **Command Execution**: Synchronous and asynchronous command processing
- **WebSocket Support**: Real-time bidirectional communication
- **Authentication**: JWT-based secure authentication
- **System Information**: Health checks and system status

### 🤖 AI Integration
ChatGPT-powered features:
- **Command Generation**: AI-assisted PowerShell command creation
- **Smart Suggestions**: Context-aware command recommendations
- **Error Analysis**: AI-powered error diagnosis and solutions
- **Documentation**: Automated command documentation generation

## 🧪 Testing Strategy

### 📋 Test Coverage
- **Unit Tests**: Individual component and function testing
- **Integration Tests**: Full workflow and API testing
- **E2E Tests**: Complete user journey validation
- **Performance Tests**: Load testing and performance benchmarks
- **Security Tests**: Authentication and authorization validation

### 🎯 Test Execution
```bash
# Run all tests in parallel
make test-all

# Run specific test suites
make test-frontend      # Playwright E2E tests
make test-backend       # Python API tests
make test-integration   # Full integration tests
make test-performance   # Load and performance tests

# Run tests with coverage
make test-coverage

# Run tests in Docker
make test-docker
```

### 📊 Test Reports
Tests generate comprehensive reports in `test-reports/`:
- **HTML Reports**: Interactive test results
- **Coverage Reports**: Code coverage analysis
- **Performance Reports**: Performance metrics and benchmarks
- **Screenshots**: Visual test evidence (E2E tests)

## 🔧 Development Workflow

### 🌿 Git Workflow
1. **Create Feature Branch**: `git checkout -b feature/DX-123-description`
2. **Commit with Jira Key**: `git commit -m "DX-123: Add new feature"`
3. **Automated Jira Updates**: Git hooks automatically update Jira issues
4. **Pull Request**: Create PR with linked Jira issues
5. **CI/CD Pipeline**: Automated testing and deployment

### 🎯 Project Management
- **Jira Integration**: Automated issue tracking and updates
- **Epic Management**: Feature planning with standard story breakdown
- **Sprint Planning**: Automated sprint creation and management
- **Reporting**: Comprehensive project and sprint reports

### 🛠️ Development Tools
```bash
# Project management
python tools/scripts/project_manager.py create-feature --name "New Feature"

# Jira integration
python tools/scripts/jira_integration.py create-epic --summary "Epic Title"

# Git hooks
python tools/scripts/git_jira_hooks.py install-hooks
```

## 🚀 Deployment

### 🐳 Production Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d --build

# Environment setup
cp .env.example .env.production
# Configure production values

# Deploy with monitoring
make deploy-production
```

### 📊 Monitoring & Observability
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Performance dashboards and visualization
- **Health Checks**: Automated service health monitoring
- **Log Aggregation**: Centralized logging and analysis

### 🔐 Security Considerations
- **Environment Variables**: Secure configuration management
- **JWT Tokens**: Token-based authentication with expiration
- **Input Validation**: Comprehensive input sanitization
- **Network Security**: Encrypted communications (HTTPS/WSS)
- **Database Security**: Connection encryption and access controls

## 🤝 Contributing

### 📋 Contribution Guidelines
1. **Fork Repository**: Create your own fork
2. **Create Feature Branch**: Use Jira issue keys in branch names
3. **Follow Code Standards**: Maintain consistent code style
4. **Write Tests**: Include comprehensive test coverage
5. **Update Documentation**: Keep documentation current
6. **Submit Pull Request**: Include detailed description and testing evidence

### 🎯 Development Standards
- **Code Style**: Follow language-specific conventions (PEP 8, ESLint)
- **Testing**: Maintain >80% test coverage
- **Documentation**: Document all public APIs and complex logic
- **Security**: Follow security best practices
- **Performance**: Consider performance implications

### 🔍 Code Review Process
1. **Automated Checks**: CI/CD pipeline validation
2. **Peer Review**: Code review by team members
3. **Testing Validation**: All tests must pass
4. **Documentation Review**: Ensure documentation accuracy
5. **Security Review**: Security implications assessment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### 📞 Getting Help
- **Documentation**: Check comprehensive docs in `/docs/`
- **Issues**: Report issues via GitHub Issues
- **Discussions**: Community discussions via GitHub Discussions
- **Wiki**: Additional resources in project wiki

### 🔧 Troubleshooting
- **[Development Setup](DEVELOPMENT_SETUP.md#troubleshooting)** - Common setup issues
- **[Project Management](docs/PROJECT_MANAGEMENT.md#troubleshooting)** - Jira integration issues
- **[Docker Issues](DEVELOPMENT_SETUP.md#docker-troubleshooting)** - Container problems

### 📊 System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 10GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 20GB storage
- **Production**: 16GB RAM, 8 CPU cores, 50GB+ storage

## 📈 Roadmap

### 🎯 Current Version Features
- ✅ Multi-agent Windows endpoint management
- ✅ Real-time PowerShell command execution
- ✅ Modern React dashboard with real-time updates
- ✅ Comprehensive testing infrastructure
- ✅ Jira integration and project management
- ✅ AI-powered command generation

### 🚀 Upcoming Features
- 🔄 **Enhanced Security**: Multi-factor authentication, role-based permissions
- 🔄 **Advanced Monitoring**: Custom dashboards, alerting, and reporting
- 🔄 **Agent Improvements**: Auto-updates, enhanced error handling
- 🔄 **API Enhancements**: GraphQL support, advanced filtering
- 🔄 **Mobile Support**: Responsive mobile interface

### 💡 Future Enhancements
- 📱 **Mobile Application**: Native mobile apps for iOS and Android
- 🔐 **Enterprise Features**: LDAP/AD integration, advanced security
- 🤖 **AI Enhancements**: Predictive maintenance, automated troubleshooting
- 🌐 **Multi-Platform**: Linux and macOS agent support
- ☁️ **Cloud Integration**: AWS/Azure/GCP integration and deployment

---

<div align="center">

**Built with ❤️ by the DexAgent Team**

[Documentation](docs/) • [API Reference](API_REFERENCE.md) • [Contributing Guidelines](CONTRIBUTING.md) • [Change Log](CHANGELOG.md)

</div>