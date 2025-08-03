#!/bin/bash

# DexAgents Production Docker Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            log_warning "Please edit .env file with your production settings before continuing!"
            log_warning "Pay special attention to SECRET_KEY and CORS settings!"
            exit 1
        else
            log_error ".env.example not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Help function
show_help() {
    echo "DexAgents Production Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy to production (build + up)"
    echo "  build     Build all Docker images"
    echo "  up        Start all services"
    echo "  down      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      Show logs for all services"
    echo "  status    Show status of all services"
    echo "  backup    Backup application data"
    echo "  restore   Restore application data"
    echo "  update    Update to latest version"
    echo "  health    Check health of all services"
    echo "  help      Show this help message"
    echo ""
}

# Deploy to production
deploy() {
    log_info "Deploying DexAgents to production..."
    check_env
    
    # Build images
    log_info "Building production images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Start services
    log_info "Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check health
    check_health
    
    log_success "Production deployment completed!"
}

# Build images
build_images() {
    check_env
    log_info "Building production Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    log_success "Production Docker images built successfully"
}

# Start services
start_services() {
    check_env
    log_info "Starting DexAgents production environment..."
    docker-compose -f docker-compose.prod.yml up -d
    log_success "Production services started successfully"
    show_status
}

# Stop services
stop_services() {
    log_info "Stopping DexAgents production services..."
    docker-compose -f docker-compose.prod.yml down
    log_success "Production services stopped successfully"
}

# Restart services
restart_services() {
    log_info "Restarting DexAgents production services..."
    docker-compose -f docker-compose.prod.yml restart
    log_success "Production services restarted successfully"
    show_status
}

# Show logs
show_logs() {
    if [ -z "$2" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose -f docker-compose.prod.yml logs -f "$2"
    fi
}

# Show status
show_status() {
    log_info "Production Service Status:"
    docker-compose -f docker-compose.prod.yml ps
}

# Health check
check_health() {
    log_info "Checking service health..."
    
    # Check frontend
    if curl -f -s http://localhost:3000/api/health > /dev/null; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend health check failed"
    fi
    
    # Check backend
    if curl -f -s http://localhost:8000/api/v1/system/health > /dev/null; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
    fi
    
    # Check nginx (if running)
    if docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
        if curl -f -s http://localhost/health > /dev/null; then
            log_success "Nginx is healthy"
        else
            log_error "Nginx health check failed"
        fi
    fi
}

# Backup data
backup_data() {
    log_info "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    docker-compose -f docker-compose.prod.yml exec -T backend cp /app/dexagents.db /tmp/backup.db
    docker cp dexagents-backend-prod:/tmp/backup.db "$BACKUP_DIR/dexagents.db"
    
    # Backup logs
    docker-compose -f docker-compose.prod.yml exec -T backend tar -czf /tmp/logs_backup.tar.gz /app/logs
    docker cp dexagents-backend-prod:/tmp/logs_backup.tar.gz "$BACKUP_DIR/logs.tar.gz"
    
    # Backup agent installers
    docker-compose -f docker-compose.prod.yml exec -T backend tar -czf /tmp/installers_backup.tar.gz /app/agent_installers
    docker cp dexagents-backend-prod:/tmp/installers_backup.tar.gz "$BACKUP_DIR/installers.tar.gz"
    
    log_success "Backup created in $BACKUP_DIR"
}

# Restore data
restore_data() {
    if [ -z "$2" ]; then
        log_error "Please specify backup directory: $0 restore [backup_directory]"
        exit 1
    fi
    
    BACKUP_DIR="$2"
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi
    
    log_warning "This will replace current data with backup from $BACKUP_DIR"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restoring from backup..."
        
        # Stop services
        docker-compose -f docker-compose.prod.yml stop
        
        # Restore database
        if [ -f "$BACKUP_DIR/dexagents.db" ]; then
            docker cp "$BACKUP_DIR/dexagents.db" dexagents-backend-prod:/app/dexagents.db
            log_success "Database restored"
        fi
        
        # Restore logs
        if [ -f "$BACKUP_DIR/logs.tar.gz" ]; then
            docker cp "$BACKUP_DIR/logs.tar.gz" dexagents-backend-prod:/tmp/logs_backup.tar.gz
            docker-compose -f docker-compose.prod.yml exec -T backend tar -xzf /tmp/logs_backup.tar.gz -C /
            log_success "Logs restored"
        fi
        
        # Restore installers
        if [ -f "$BACKUP_DIR/installers.tar.gz" ]; then
            docker cp "$BACKUP_DIR/installers.tar.gz" dexagents-backend-prod:/tmp/installers_backup.tar.gz
            docker-compose -f docker-compose.prod.yml exec -T backend tar -xzf /tmp/installers_backup.tar.gz -C /
            log_success "Agent installers restored"
        fi
        
        # Start services
        docker-compose -f docker-compose.prod.yml start
        
        log_success "Restore completed"
    else
        log_info "Restore cancelled"
    fi
}

# Update to latest version
update() {
    log_info "Updating DexAgents to latest version..."
    
    # Pull latest code (if using git)
    if [ -d ".git" ]; then
        log_info "Pulling latest code..."
        git pull
    fi
    
    # Create backup before update
    log_info "Creating pre-update backup..."
    backup_data
    
    # Rebuild and restart
    log_info "Rebuilding and restarting services..."
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
    
    # Health check
    sleep 30
    check_health
    
    log_success "Update completed successfully"
}

# Main command handler
case "$1" in
    deploy)
        deploy
        ;;
    build)
        build_images
        ;;
    up)
        start_services
        ;;
    down)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs "$@"
        ;;
    status)
        show_status
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$@"
        ;;
    update)
        update
        ;;
    health)
        check_health
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac