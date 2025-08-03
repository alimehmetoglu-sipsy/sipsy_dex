# Test Command

Run comprehensive DexAgent test suite and create new Jira task with results

## Usage

```bash
/test
```

## Description

This command executes the complete DexAgent test suite including all test categories and automatically creates a new Jira task with comprehensive test results.

## What it does

- **Backend Tests**: Unit tests + API tests with coverage reporting
- **Frontend Tests**: Unit tests + E2E tests using Playwright  
- **Integration Tests**: Full workflow and component integration testing
- **Performance Tests**: Load testing with metrics collection
- **End-to-End Tests**: Complete user scenario validation
- **Coverage Reports**: Generates HTML coverage reports (target: >80%)
- **Performance Metrics**: API response time, WebSocket latency, memory usage
- **Jira Integration**: Automatically creates new Jira task with comprehensive test results
- **Task Creation**: Each test run creates a unique task with execution timestamp and results

## Implementation

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 DexAgent Comprehensive Test Suite${NC}"
echo -e "${BLUE}====================================${NC}"

# Get project root
PROJECT_ROOT="$(pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📁 Project Root: $PROJECT_ROOT${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.${NC}"
    exit 1
fi

# Check required directories
if [[ ! -d "tools" ]]; then
    echo -e "${RED}❌ Tools directory not found. Make sure you're in the project root.${NC}"
    exit 1
fi

# Make scripts executable
chmod +x tools/test_orchestrator.py
chmod +x tools/jira_reporter.py
chmod +x tools/claude_post_to_jira.py

echo -e "${BLUE}🚀 Launching Test Orchestrator...${NC}"
echo ""

# Run comprehensive tests
python3 tools/test_orchestrator.py

# Check if test results were generated
if [[ -f "test_results.json" ]]; then
    echo ""
    echo -e "${BLUE}📊 Test Results Generated${NC}"
    echo -e "${YELLOW}Results saved to: test_results.json${NC}"
    
    # Check if Jira report was generated
    if [[ -f "jira_report.md" ]]; then
        echo -e "${GREEN}✅ Jira report generated successfully${NC}"
        
        # Create new Jira task with test results
        echo -e "${BLUE}🎯 Creating new Jira task with test results...${NC}"
        python3 tools/jira_task_creator.py test_results.json
        
        if [[ -f "jira_task_request.json" ]]; then
            echo -e "${GREEN}✅ Jira task creation request prepared${NC}"
            echo -e "${BLUE}🚀 Ready for Claude Code MCP task creation${NC}"
        else
            echo -e "${YELLOW}⚠️  Jira task creation request not prepared${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Jira report not generated${NC}"
        echo -e "${YELLOW}Results are available in test_results.json${NC}"
    fi
else
    echo -e "${RED}❌ Test results file not generated${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Test suite execution completed!${NC}"
echo -e "${BLUE}📋 Check the output above for detailed results${NC}"
```

## Expected Results

- **Test Execution Report**: Comprehensive results with pass/fail counts
- **Coverage Report**: Backend and frontend coverage percentages
- **Performance Metrics**: API response times, WebSocket latency, memory usage
- **Failed Test Details**: Detailed logs for any failed tests
- **New Jira Task**: Automatically created task with unique title and comprehensive results
- **Task Classification**: Automatically classified as Bug/Task based on test failures

## Files Generated

- `test_results.json` - Detailed test results data
- `jira_report.md` - Markdown-formatted report for Jira
- `jira_task_request.json` - New task creation request for MCP integration
- `tests/coverage/html/index.html` - HTML coverage report

## Requirements

- Python 3.x with pytest, coverage, and other test dependencies
- Node.js and npm for frontend tests
- Backend services running (for API tests)
- Playwright browsers installed (for E2E tests)

## Architecture

```
Claude Code /test Command (MD)
    ↓
Test Orchestrator (tools/test_orchestrator.py)
    ↓
├── Backend Tests (make test-backend + comprehensive_api_test.py)
├── Frontend Tests (make test-frontend) 
├── Integration Tests (make test-integration)
├── Performance Tests (make test-performance)
└── E2E Tests (make test-e2e)
    ↓
Result Collection & Parsing
    ↓
Jira Report Generation (tools/jira_reporter.py)
    ↓
Jira Task Creation (tools/jira_task_creator.py)
    ↓
MCP Atlassian Integration → New Jira Task Creation
```