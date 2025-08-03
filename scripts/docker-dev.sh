#!/bin/bash

# DexAgents Development Docker Management Script

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

# Help function
show_help() {
    echo "DexAgents Development Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build all Docker images"
    echo "  up        Start all services"
    echo "  down      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      Show logs for all services"
    echo "  status    Show status of all services"
    echo "  clean     Clean up containers, networks, and volumes"
    echo "  backend   Manage backend service only"
    echo "  frontend  Manage frontend service only"
    echo "  shell     Open shell in backend container"
    echo "  help      Show this help message"
    echo ""
}

# Build images
build_images() {
    log_info "Building Docker images..."
    docker-compose build --no-cache
    log_success "Docker images built successfully"
}

# Start services
start_services() {
    log_info "Starting DexAgents development environment..."
    docker-compose up -d
    log_success "Services started successfully"
    show_status
}

# Stop services
stop_services() {
    log_info "Stopping DexAgents services..."
    docker-compose down
    log_success "Services stopped successfully"
}

# Restart services
restart_services() {
    log_info "Restarting DexAgents services..."
    docker-compose restart
    log_success "Services restarted successfully"
    show_status
}

# Show logs
show_logs() {
    if [ -z "$2" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$2"
    fi
}

# Show status
show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    log_info "Health Checks:"
    echo "Frontend: http://localhost:3000/api/health"
    echo "Backend: http://localhost:8000/api/v1/system/health"
}

# Clean up
cleanup() {
    log_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up Docker resources..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Backend only operations
manage_backend() {
    case "$2" in
        up)
            docker-compose up -d backend
            ;;
        down)
            docker-compose stop backend
            ;;
        logs)
            docker-compose logs -f backend
            ;;
        restart)
            docker-compose restart backend
            ;;
        build)
            docker-compose build backend
            ;;
        *)
            echo "Backend commands: up, down, logs, restart, build"
            ;;
    esac
}

# Frontend only operations
manage_frontend() {
    case "$2" in
        up)
            docker-compose up -d frontend
            ;;
        down)
            docker-compose stop frontend
            ;;
        logs)
            docker-compose logs -f frontend
            ;;
        restart)
            docker-compose restart frontend
            ;;
        build)
            docker-compose build frontend
            ;;
        *)
            echo "Frontend commands: up, down, logs, restart, build"
            ;;
    esac
}

# Open shell in backend container
open_shell() {
    log_info "Opening shell in backend container..."
    docker-compose exec backend /bin/bash || docker-compose exec backend /bin/sh
}

# Main command handler
case "$1" in
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
    clean)
        cleanup
        ;;
    backend)
        manage_backend "$@"
        ;;
    frontend)
        manage_frontend "$@"
        ;;
    shell)
        open_shell
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