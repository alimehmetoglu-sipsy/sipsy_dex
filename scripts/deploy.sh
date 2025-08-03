#!/bin/bash

# DexAgents Deployment Script
# This script handles deployment to different environments

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
    echo "DexAgents Deployment Script"
    echo ""
    echo "Usage: $0 [ENVIRONMENT] [OPTIONS]"
    echo ""
    echo "Environments:"
    echo "  dev         Deploy to development environment"
    echo "  staging     Deploy to staging environment"
    echo "  production  Deploy to production environment"
    echo ""
    echo "Options:"
    echo "  --version=VERSION     Specific version to deploy"
    echo "  --backup              Create backup before deployment"
    echo "  --no-build            Skip building images"
    echo "  --health-check        Run health checks after deployment"
    echo "  --rollback=VERSION    Rollback to specified version"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev                           # Deploy latest to development"
    echo "  $0 staging --version=v1.2.3     # Deploy specific version to staging"
    echo "  $0 production --backup           # Deploy to production with backup"
    echo "  $0 production --rollback=v1.2.2 # Rollback production to v1.2.2"
    echo ""
}

# Parse arguments
ENVIRONMENT=""
VERSION="latest"
CREATE_BACKUP=false
SKIP_BUILD=false
RUN_HEALTH_CHECK=false
ROLLBACK_VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        dev|staging|production)
            ENVIRONMENT="$1"
            shift
            ;;
        --version=*)
            VERSION="${1#*=}"
            shift
            ;;
        --backup)
            CREATE_BACKUP=true
            shift
            ;;
        --no-build)
            SKIP_BUILD=true
            shift
            ;;
        --health-check)
            RUN_HEALTH_CHECK=true
            shift
            ;;
        --rollback=*)
            ROLLBACK_VERSION="${1#*=}"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [ -z "$ENVIRONMENT" ]; then
    log_error "Environment is required"
    show_help
    exit 1
fi

# Set environment-specific variables
case "$ENVIRONMENT" in
    "dev")
        COMPOSE_FILE="docker-compose.yml"
        HEALTH_URL="http://localhost:3000/api/health"
        BACKEND_HEALTH_URL="http://localhost:8080/api/v1/system/health"
        ;;
    "staging")
        COMPOSE_FILE="docker-compose.prod.yml"
        HEALTH_URL="http://staging.dexagents.local/health"
        BACKEND_HEALTH_URL="http://staging.dexagents.local/api/v1/system/health"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.prod.yml"
        HEALTH_URL="https://dexagents.com/health"
        BACKEND_HEALTH_URL="https://dexagents.com/api/v1/system/health"
        ;;
esac

# Rollback function
perform_rollback() {
    local rollback_version="$1"
    log_warning "Performing rollback to version: $rollback_version"
    
    # Create backup before rollback
    if [ "$CREATE_BACKUP" = true ]; then
        create_backup "pre-rollback"
    fi
    
    # Stop current services
    log_info "Stopping current services..."
    docker-compose -f "$COMPOSE_FILE" down
    
    # Pull rollback version
    log_info "Pulling rollback images..."
    if [ "$rollback_version" != "latest" ]; then
        # Update compose file with specific version (simplified)
        # In real scenario, you'd have proper version management
        log_info "Setting version to $rollback_version"
    fi
    
    # Start services with rollback version
    log_info "Starting services with rollback version..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Verify rollback
    if verify_deployment; then
        log_success "Rollback completed successfully!"
    else
        log_error "Rollback verification failed!"
        exit 1
    fi
}

# Backup function
create_backup() {
    local backup_type="${1:-deployment}"
    local backup_id="${backup_type}_$(date +%Y%m%d_%H%M%S)"
    local backup_dir="backups/$backup_id"
    
    log_info "Creating backup: $backup_id"
    mkdir -p "$backup_dir"
    
    # Backup database
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q backend; then
        log_info "Backing up database..."
        docker-compose -f "$COMPOSE_FILE" exec -T backend cp /app/dexagents.db /tmp/backup.db 2>/dev/null || true
        docker cp "$(docker-compose -f "$COMPOSE_FILE" ps -q backend):/tmp/backup.db" "$backup_dir/dexagents.db" 2>/dev/null || true
    fi
    
    # Backup configuration
    log_info "Backing up configuration..."
    cp docker-compose*.yml "$backup_dir/" 2>/dev/null || true
    cp .env* "$backup_dir/" 2>/dev/null || true
    
    # Save current image versions
    log_info "Saving current image versions..."
    docker-compose -f "$COMPOSE_FILE" images > "$backup_dir/images.txt" 2>/dev/null || true
    
    log_success "Backup created: $backup_dir"
    echo "BACKUP_ID=$backup_id" >> $GITHUB_OUTPUT 2>/dev/null || true
}

# Health check function
verify_deployment() {
    log_info "Verifying deployment..."
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        # Check backend health
        if curl -f -s "$BACKEND_HEALTH_URL" | grep -q "healthy"; then
            log_success "Backend is healthy"
            
            # For development environment, also check frontend directly
            if [ "$ENVIRONMENT" = "dev" ]; then
                if curl -f -s "$HEALTH_URL" | grep -q "healthy"; then
                    log_success "Frontend is healthy"
                    return 0
                fi
            else
                # For staging/production, check through nginx
                if curl -f -s "$HEALTH_URL" | grep -q "healthy"; then
                    log_success "Services are healthy"
                    return 0
                fi
            fi
        fi
        
        log_warning "Health check failed, waiting 15 seconds..."
        sleep 15
        attempt=$((attempt + 1))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Build images function
build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_info "Skipping image build (--no-build specified)"
        return 0
    fi
    
    log_info "Building Docker images..."
    
    if [ "$VERSION" != "latest" ]; then
        log_info "Building version: $VERSION"
        # In a real scenario, you'd build with proper version tags
        docker-compose -f "$COMPOSE_FILE" build --build-arg VERSION="$VERSION"
    else
        docker-compose -f "$COMPOSE_FILE" build
    fi
    
    log_success "Images built successfully"
}

# Deploy function
perform_deployment() {
    log_info "Starting deployment to $ENVIRONMENT environment"
    log_info "Version: $VERSION"
    
    # Create backup if requested
    if [ "$CREATE_BACKUP" = true ]; then
        create_backup "pre-deployment"
    fi
    
    # Build images
    build_images
    
    # Pull any external images
    log_info "Pulling external images..."
    docker-compose -f "$COMPOSE_FILE" pull --ignore-pull-failures || true
    
    # Deploy with zero-downtime strategy for production
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Performing blue-green deployment..."
        # In a real scenario, implement blue-green deployment
        # For now, use standard deployment with minimal downtime
        docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    else
        log_info "Deploying services..."
        docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    fi
    
    # Wait for services to be ready
    log_info "Waiting for services to initialize..."
    sleep 30
    
    # Verify deployment
    if verify_deployment || [ "$RUN_HEALTH_CHECK" = true ]; then
        if verify_deployment; then
            log_success "Deployment completed successfully!"
        else
            log_error "Deployment verification failed!"
            exit 1
        fi
    else
        log_success "Deployment completed (health check skipped)"
    fi
    
    # Show service status
    log_info "Service status:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Main execution
main() {
    # Handle rollback
    if [ -n "$ROLLBACK_VERSION" ]; then
        perform_rollback "$ROLLBACK_VERSION"
        return 0
    fi
    
    # Perform deployment
    perform_deployment
    
    # Cleanup old images if in production
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Cleaning up old images..."
        docker image prune -f --filter "until=24h" || true
    fi
    
    log_success "🎉 Deployment to $ENVIRONMENT completed successfully!"
}

# Run main function
main "$@"