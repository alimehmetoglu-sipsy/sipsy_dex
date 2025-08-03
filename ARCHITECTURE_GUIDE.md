# ARCHITECTURE_GUIDE.md

## System Architecture Overview

DexAgent follows a modern **distributed microservices architecture** designed for scalability, real-time communication, and enterprise deployment.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Windows       │    │   Monitoring    │
│   (Next.js)     │    │   Agents        │    │   (Grafana)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ HTTP/WebSocket       │ WebSocket            │ Metrics
          │                      │                      │
┌─────────▼─────────────────────▼──────────────────────▼───────┐
│                FastAPI Backend Server                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │     API      │ │   WebSocket  │ │   AI Service │        │
│  │   Endpoints  │ │   Manager    │ │   (ChatGPT)  │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────┬─────────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                 PostgreSQL Database                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │    Agents    │ │   Commands   │ │   Metrics    │        │
│  │   & Groups   │ │   & History  │ │   & Logs     │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Core Tables

#### 1. agents
- **id** (Primary Key)
- **name** - Agent display name
- **hostname** - Windows machine hostname
- **ip_address** - Network IP address
- **port** - Communication port
- **status** - Agent health status
- **last_heartbeat** - Last communication timestamp
- **group_id** - Foreign key to agent_groups
- **created_at** / **updated_at** - Timestamps

#### 2. users
- **id** (Primary Key)
- **username** - Login username
- **email** - User email address
- **password_hash** - Encrypted password
- **is_active** - Account status
- **created_at** / **updated_at** - Timestamps

#### 3. agent_groups
- **id** (Primary Key)
- **name** - Group display name
- **description** - Group description
- **created_at** / **updated_at** - Timestamps

#### 4. agent_metrics
- **id** (Primary Key)
- **agent_id** - Foreign key to agents
- **cpu_usage** - CPU utilization percentage
- **memory_usage** - Memory utilization percentage
- **disk_usage** - Disk utilization percentage
- **network_io** - Network I/O metrics
- **timestamp** - Metric collection time

#### 5. powershell_commands
- **id** (Primary Key)
- **name** - Command display name
- **command** - PowerShell command text
- **description** - Command description
- **category** - Command category
- **created_at** / **updated_at** - Timestamps

#### 6. command_history
- **id** (Primary Key)
- **agent_id** - Foreign key to agents
- **command_id** - Foreign key to powershell_commands
- **command_text** - Executed command
- **output** - Command execution result
- **exit_code** - Process exit code
- **execution_time** - Command duration
- **created_at** - Execution timestamp

#### 7. alerts
- **id** (Primary Key)
- **agent_id** - Foreign key to agents
- **type** - Alert type (warning, error, info)
- **message** - Alert message
- **is_acknowledged** - Acknowledgment status
- **created_at** - Alert timestamp

#### 8. audit_logs
- **id** (Primary Key)
- **user_id** - Foreign key to users
- **action** - Performed action
- **resource** - Affected resource
- **details** - Action details
- **ip_address** - Client IP address
- **created_at** - Action timestamp

#### 9. user_sessions
- **id** (Primary Key)
- **user_id** - Foreign key to users
- **session_token** - JWT session token
- **expires_at** - Token expiration
- **created_at** - Session start

#### 10. scheduled_tasks
- **id** (Primary Key)
- **name** - Task name
- **command_id** - Foreign key to powershell_commands
- **cron_expression** - Schedule definition
- **is_active** - Task status
- **created_at** / **updated_at** - Timestamps

### Database Relationships

```sql
agents.group_id → agent_groups.id
agent_metrics.agent_id → agents.id
command_history.agent_id → agents.id
command_history.command_id → powershell_commands.id
alerts.agent_id → agents.id
audit_logs.user_id → users.id
user_sessions.user_id → users.id
scheduled_tasks.command_id → powershell_commands.id
```

## API Architecture

### REST API Structure

```
/api/v1/
├── auth/
│   ├── login          # POST - User authentication
│   └── me             # GET - Current user info
├── agents/
│   ├── /              # GET - List agents, POST - Register agent
│   ├── /{id}          # GET - Agent details, PUT - Update, DELETE - Remove
│   ├── /{id}/metrics  # GET - Agent metrics
│   └── /{id}/commands # POST - Execute command
├── commands/
│   ├── saved/         # GET - List, POST - Create saved commands
│   ├── saved/{id}     # GET, PUT, DELETE - Manage saved commands
│   └── ai/            # POST - AI command generation
├── system/
│   ├── health         # GET - System health check
│   ├── info           # GET - System information
│   └── metrics        # GET - Overall system metrics
└── settings/
    ├── /              # GET - System settings, POST - Update settings
    └── chatgpt        # GET, POST - ChatGPT configuration
```

### WebSocket Endpoints

```
/api/v1/ws/
├── agent/{agent_id}   # Agent communication channel
└── dashboard          # Real-time dashboard updates
```

## Component Architecture

### Backend Components

#### 1. FastAPI Application (`apps/backend/app/main.py`)
- Central application entry point
- Middleware configuration
- Route registration
- CORS and security setup

#### 2. API Layer (`apps/backend/app/api/v1/`)
- **agents.py** - Agent management endpoints
- **auth.py** - Authentication endpoints
- **commands.py** - Command management and execution
- **system.py** - System information and health
- **websocket.py** - WebSocket communication handlers

#### 3. Core Services (`apps/backend/app/core/`)
- **auth.py** - Authentication logic
- **database.py** - Database connection and session management
- **websocket_manager.py** - WebSocket connection management
- **config.py** - Application configuration

#### 4. Business Logic (`apps/backend/app/services/`)
- **powershell_service.py** - PowerShell command execution
- **ai_service.py** - ChatGPT integration
- **agent_installer_service.py** - Agent deployment
- **python_agent_service.py** - Agent management

#### 5. Data Layer (`apps/backend/app/models/`)
- SQLAlchemy ORM models
- Database relationships
- Data validation

### Frontend Components

#### 1. Next.js App Structure (`apps/frontend/app/`)
- **layout.tsx** - Root application layout
- **(dashboard)/** - Main dashboard pages
- **login/** - Authentication pages
- **api/** - API route handlers

#### 2. React Components (`apps/frontend/components/`)
- **UI Components** - shadcn/ui based components
- **Business Components** - Application-specific components
- **Layout Components** - Navigation and layout

#### 3. State Management (`apps/frontend/contexts/`)
- **AuthContext.tsx** - Authentication state
- **API Integration** - Backend communication

### Agent Components

#### 1. Windows Agent (`apps/agent/windows_agent.py`)
- Main agent application
- PowerShell execution
- System monitoring
- WebSocket communication

#### 2. WebSocket Client (`apps/agent/websocket_agent.py`)
- Real-time communication with backend
- Command receiving and execution
- Heartbeat management

## Data Flow

### 1. Agent Registration Flow
```
Windows Agent → WebSocket Connection → Backend API → Database
                                    ↓
Dashboard ← WebSocket Notification ← WebSocket Manager
```

### 2. PowerShell Execution Flow
```
Dashboard → REST API → Backend Service → WebSocket Message → Windows Agent
                                                           ↓
Database ← Command History ← Execution Result ← PowerShell Execution
    ↓
Dashboard ← WebSocket Update ← WebSocket Manager
```

### 3. Real-time Monitoring Flow
```
Windows Agent → System Metrics → WebSocket → Backend → Database
                                           ↓
Dashboard ← WebSocket Stream ← WebSocket Manager
```

## Security Architecture

### 1. Authentication & Authorization
- **JWT Tokens** - Stateless session management
- **Password Hashing** - bcrypt encryption
- **Session Management** - Token expiration and refresh

### 2. Data Security
- **Input Validation** - Pydantic schemas
- **SQL Injection Protection** - SQLAlchemy ORM
- **XSS Protection** - React built-in protection

### 3. Network Security
- **HTTPS** - TLS encryption in production
- **WebSocket Security** - Authentication required
- **CORS Configuration** - Controlled cross-origin access

### 4. Deployment Security
- **Docker Isolation** - Containerized services
- **Environment Variables** - Secure configuration
- **Database Security** - Isolated database access

## Performance Considerations

### 1. Database Optimization
- **Indexes** - Optimized query performance
- **Connection Pooling** - Efficient database connections
- **Query Optimization** - Efficient data retrieval

### 2. Real-time Performance
- **WebSocket Management** - Efficient connection handling
- **Message Queuing** - Asynchronous processing
- **Connection Limiting** - Resource management

### 3. Frontend Performance
- **Next.js Optimization** - Static generation and SSR
- **Component Optimization** - React performance patterns
- **Bundle Optimization** - Code splitting and lazy loading

---

**Architecture Version**: 3.3 - Optimized for Claude Code integration