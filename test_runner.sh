#!/bin/bash
# Simple Test Runner for DexAgent - Alternative to /test command
# Usage: ./test_runner.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧪 DexAgent Test Suite Runner${NC}"
echo -e "${BLUE}============================${NC}"

# Check if we're in the right directory
if [[ ! -f "tools/test_orchestrator.py" ]]; then
    echo "❌ Error: Please run this from the sipsy_dex project root directory"
    exit 1
fi

echo -e "${YELLOW}📁 Current directory: $(pwd)${NC}"
echo -e "${YELLOW}🚀 Starting comprehensive test suite...${NC}"
echo ""

# Make scripts executable
chmod +x tools/test_orchestrator.py
chmod +x tools/jira_reporter.py

# Run the test orchestrator
python3 tools/test_orchestrator.py

# Check results
if [[ -f "test_results.json" ]]; then
    echo ""
    echo -e "${GREEN}✅ Test results generated: test_results.json${NC}"
    
    if [[ -f "jira_report.md" ]]; then
        echo -e "${GREEN}✅ Jira report generated: jira_report.md${NC}"
        echo -e "${BLUE}📋 Report is ready for Jira DX-30${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No test results file generated${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Test suite execution completed!${NC}"