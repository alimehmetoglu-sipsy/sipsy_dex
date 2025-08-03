#!/bin/bash
# DexAgent Test Runner Script
# Usage: ./run_tests.sh [test_type] [options]

set -e

# Default values
TEST_TYPE="all"
HEADLESS="true"
PARALLEL="false"
COVERAGE="false"
CLEANUP="true"
DOCKER_MODE="false"
REPORT_FORMAT="html"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
DexAgent Test Runner

Usage: $0 [test_type] [options]

Test Types:
    integration     Run integration tests
    performance     Run performance tests  
    e2e            Run end-to-end tests
    smoke          Run smoke tests
    all            Run all tests (default)

Options:
    --headless         Run E2E tests in headless mode (default: true)
    --headed           Run E2E tests with browser UI
    --parallel         Run tests in parallel
    --coverage         Generate coverage report
    --no-cleanup       Don't clean up after tests
    --docker           Run tests in Docker containers
    --report=FORMAT    Report format: html, json, xml (default: html)
    --help             Show this help message

Examples:
    $0 integration                    # Run integration tests
    $0 e2e --headed                   # Run E2E tests with browser UI
    $0 all --parallel --coverage      # Run all tests with coverage
    $0 smoke --docker                 # Run smoke tests in Docker

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        integration|performance|e2e|smoke|all)
            TEST_TYPE="$1"
            shift
            ;;
        --headless)
            HEADLESS="true"
            shift
            ;;
        --headed)
            HEADLESS="false"
            shift
            ;;
        --parallel)
            PARALLEL="true"
            shift
            ;;
        --coverage)
            COVERAGE="true"
            shift
            ;;
        --no-cleanup)
            CLEANUP="false"
            shift
            ;;
        --docker)
            DOCKER_MODE="true"
            shift
            ;;
        --report=*)
            REPORT_FORMAT="${1#*=}"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set up environment
setup_environment() {
    print_info "Setting up test environment..."
    
    # Create necessary directories
    mkdir -p tests/logs tests/results tests/screenshots tests/coverage
    
    # Set environment variables
    export PYTHONPATH="${PWD}/tests:${PWD}/apps:${PYTHONPATH}"
    export TEST_HEADLESS="$HEADLESS"
    export TEST_PARALLEL="$PARALLEL"
    
    if [ "$DOCKER_MODE" = "true" ]; then
        export BACKEND_URL="http://backend-test:8000"
        export FRONTEND_URL="http://frontend-test:3000"
        export DATABASE_URL="postgresql://postgres:postgres123@postgres-test:5432/dexagent_test"
    else
        export BACKEND_URL="http://localhost:8080"
        export FRONTEND_URL="http://localhost:3000"
        export DATABASE_URL="postgresql://postgres:postgres123@localhost:5433/dexagent_test"
    fi
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if required Python packages are installed
    if ! python3 -c "import pytest" 2>/dev/null; then
        print_warning "Installing test dependencies..."
        pip install -r tests/requirements.txt
    fi
    
    # Check if Playwright browsers are installed (for E2E tests)
    if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
        if ! python3 -m playwright show-browser 2>/dev/null; then
            print_warning "Installing Playwright browsers..."
            python3 -m playwright install
        fi
    fi
}

# Start services
start_services() {
    if [ "$DOCKER_MODE" = "true" ]; then
        print_info "Starting services in Docker..."
        docker-compose -f tests/docker-compose.test.yml up -d
        
        print_info "Waiting for services to be ready..."
        python3 tests/scripts/wait_for_services.py
    else
        print_info "Checking if services are running locally..."
        
        # Check if backend is running
        if ! curl -s http://localhost:8080/api/v1/system/health > /dev/null; then
            print_warning "Backend is not running. Please start it manually or use --docker option"
        fi
        
        # Check if frontend is running (for E2E tests)
        if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
            if ! curl -s http://localhost:3000/api/health > /dev/null; then
                print_warning "Frontend is not running. Please start it manually or use --docker option"
            fi
        fi
    fi
}

# Build pytest command
build_pytest_command() {
    local cmd="pytest"
    
    # Add test path based on type
    case $TEST_TYPE in
        integration)
            cmd="$cmd tests/integration"
            ;;
        performance)
            cmd="$cmd tests/performance"
            ;;
        e2e)
            cmd="$cmd tests/e2e"
            ;;
        smoke)
            cmd="$cmd -m smoke"
            ;;
        all)
            cmd="$cmd tests"
            ;;
    esac
    
    # Add common options
    cmd="$cmd -v --tb=short --color=yes"
    
    # Add parallel execution
    if [ "$PARALLEL" = "true" ]; then
        cmd="$cmd -n auto"
    fi
    
    # Add coverage
    if [ "$COVERAGE" = "true" ]; then
        cmd="$cmd --cov=apps --cov-report=html:tests/coverage/html --cov-report=xml:tests/coverage/coverage.xml"
    fi
    
    # Add report format
    case $REPORT_FORMAT in
        html)
            cmd="$cmd --html=tests/results/report.html --self-contained-html"
            ;;
        xml)
            cmd="$cmd --junitxml=tests/results/junit.xml"
            ;;
        json)
            cmd="$cmd --json-report --json-report-file=tests/results/report.json"
            ;;
    esac
    
    # Add headless mode for E2E tests (passed via environment variable)
    if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
        if [ "$HEADLESS" = "true" ]; then
            export PLAYWRIGHT_HEADLESS=true
        else
            export PLAYWRIGHT_HEADLESS=false
        fi
    fi
    
    echo "$cmd"
}

# Run tests
run_tests() {
    print_info "Running $TEST_TYPE tests..."
    
    local start_time=$(date +%s)
    local pytest_cmd=$(build_pytest_command)
    
    print_info "Command: $pytest_cmd"
    
    # Run the tests
    if $pytest_cmd; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_success "Tests completed successfully in ${duration}s"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Tests failed after ${duration}s"
        return 1
    fi
}

# Generate reports
generate_reports() {
    print_info "Generating test reports..."
    
    # Generate coverage report if enabled
    if [ "$COVERAGE" = "true" ] && [ -f "tests/coverage/coverage.xml" ]; then
        print_info "Coverage report generated at: tests/coverage/html/index.html"
    fi
    
    # Generate performance report for performance tests
    if [ "$TEST_TYPE" = "performance" ] || [ "$TEST_TYPE" = "all" ]; then
        if [ -f "tests/results/performance.json" ]; then
            python3 tests/scripts/generate_performance_report.py
        fi
    fi
    
    print_info "Test reports available in: tests/results/"
}

# Cleanup
cleanup() {
    if [ "$CLEANUP" = "true" ]; then
        print_info "Cleaning up..."
        
        if [ "$DOCKER_MODE" = "true" ]; then
            docker-compose -f tests/docker-compose.test.yml down
        fi
        
        # Clean up temporary files
        find tests -name "*.pyc" -delete 2>/dev/null || true
        find tests -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    print_info "DexAgent Test Runner"
    print_info "===================="
    print_info "Test Type: $TEST_TYPE"
    print_info "Headless: $HEADLESS"
    print_info "Parallel: $PARALLEL"
    print_info "Coverage: $COVERAGE"
    print_info "Docker Mode: $DOCKER_MODE"
    print_info "Report Format: $REPORT_FORMAT"
    print_info ""
    
    setup_environment
    check_dependencies
    start_services
    
    if run_tests; then
        generate_reports
        print_success "All tests completed successfully!"
        exit 0
    else
        print_error "Tests failed!"
        exit 1
    fi
}

# Run main function
main