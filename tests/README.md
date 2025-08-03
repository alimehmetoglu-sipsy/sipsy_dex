# DexAgent Testing Infrastructure

Comprehensive testing infrastructure for the DexAgent Windows Endpoint Management Platform.

## Overview

This testing infrastructure provides multiple levels of testing to ensure the reliability, performance, and correctness of the DexAgent system:

- **Integration Tests**: Test component interactions and workflows
- **Performance Tests**: Load testing and performance benchmarking
- **End-to-End Tests**: Browser-based user workflow testing
- **Unit Tests**: Component-level testing (located in individual apps)

## Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Docker & Docker Compose** (for containerized testing)
3. **Node.js 18+** (for frontend testing)
4. **PostgreSQL** (for database testing)

### Installation

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Install Playwright browsers (for E2E tests)
playwright install

# Set up test environment
cp .env.example .env
# Edit .env with test configuration
```

### Running Tests

#### Using the Test Runner Script (Recommended)

```bash
# Run all tests
./tests/scripts/run_tests.sh all

# Run specific test types
./tests/scripts/run_tests.sh integration
./tests/scripts/run_tests.sh performance
./tests/scripts/run_tests.sh e2e

# Run with options
./tests/scripts/run_tests.sh all --parallel --coverage
./tests/scripts/run_tests.sh e2e --headed  # Show browser
./tests/scripts/run_tests.sh all --docker  # Run in containers
```

#### Using Docker Compose

```bash
# Start test environment
docker-compose -f tests/docker-compose.test.yml up -d

# Run tests in container
docker-compose -f tests/docker-compose.test.yml exec test-runner /tests/entrypoint.sh integration

# View test reports
open http://localhost:8082  # Test reports server
```

#### Using pytest Directly

```bash
# Run integration tests
pytest tests/integration -v

# Run performance tests
pytest tests/performance -v

# Run E2E tests
pytest tests/e2e -v

# Run with coverage
pytest tests --cov=apps --cov-report=html
```

## Test Structure

```
tests/
├── integration/           # Integration tests
│   ├── test_full_workflow.py
│   └── conftest.py
├── performance/           # Performance and load tests
│   └── test_load.py
├── e2e/                  # End-to-end browser tests
│   └── test_complete_workflows.py
├── scripts/              # Test utilities and scripts
│   ├── run_tests.sh
│   ├── wait_for_services.py
│   └── generate_performance_report.py
├── requirements.txt      # Test dependencies
├── pytest.ini          # Pytest configuration
├── docker-compose.test.yml  # Test environment
└── README.md           # This file
```

## Test Types

### Integration Tests

Located in `tests/integration/`, these tests verify that different components work together correctly:

- **Agent Registration Workflow**: WebSocket connection, authentication, status updates
- **Command Execution Workflow**: End-to-end command execution from API to agent
- **Metrics Collection Workflow**: Real-time metrics gathering and storage
- **WebSocket Communication**: Bidirectional messaging patterns
- **System Health Monitoring**: Health checks and monitoring endpoints

#### Key Test Cases

```python
# Test agent registration
test_agent_registration_complete_workflow()

# Test PowerShell command execution
test_powershell_command_execution_workflow()

# Test real-time metrics
test_metrics_collection_workflow()

# Test WebSocket communication
test_websocket_connection_and_messaging()
```

### Performance Tests

Located in `tests/performance/`, these tests measure system performance under load:

- **API Response Times**: Measure API endpoint performance
- **Concurrent Requests**: Test system under concurrent load
- **WebSocket Latency**: Measure WebSocket message latency
- **Command Execution Performance**: Benchmark command processing
- **Resource Usage**: Monitor memory and CPU usage

#### Performance Thresholds

```python
PERFORMANCE_THRESHOLDS = {
    'api_response_time': 2.0,      # seconds
    'websocket_latency': 0.5,      # seconds
    'command_execution_time': 5.0,  # seconds
    'memory_usage_mb': 512,        # MB
    'cpu_usage_percent': 80,       # %
}
```

### End-to-End Tests

Located in `tests/e2e/`, these tests use Playwright to test complete user workflows:

- **User Authentication**: Login/logout workflows
- **Agent Management**: Agent list, details, and management
- **Command Management**: Create, edit, execute commands
- **Dashboard Monitoring**: Real-time dashboard updates
- **Settings Configuration**: System configuration workflows
- **Error Handling**: Error scenarios and recovery
- **Accessibility**: Keyboard navigation and responsive design

#### E2E Test Examples

```python
# Test complete user workflow
async def test_complete_agent_management_workflow()

# Test command execution from UI
async def test_complete_command_execution_workflow()

# Test real-time dashboard
async def test_dashboard_monitoring_workflow()

# Test accessibility
async def test_keyboard_navigation()
```

## Configuration

### Environment Variables

```bash
# Test configuration
TEST_BACKEND_URL=http://localhost:8080
TEST_FRONTEND_URL=http://localhost:3000
TEST_DATABASE_URL=postgresql://postgres:postgres123@localhost:5433/dexagent_test

# Test credentials
TEST_USERNAME=admin
TEST_PASSWORD=admin123

# Test options
TEST_HEADLESS=true
TEST_PARALLEL=false
TEST_COVERAGE=false
```

### Pytest Configuration

Key pytest settings in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests/integration tests/performance tests/e2e
markers = 
    integration: Integration tests
    performance: Performance tests
    e2e: End-to-end tests
    slow: Tests that take longer than 30 seconds
addopts = --verbose --tb=short --color=yes
timeout = 300
```

## Test Data Management

### Database Setup

Tests use a separate test database with:

- Test fixtures and sample data
- Automatic cleanup between tests
- Performance optimization for testing

### Test Data Cleanup

```python
# Automatic cleanup in conftest.py
@pytest.fixture
def clean_database():
    cleanup_test_database()
    yield
    cleanup_test_database()

# Manual cleanup
def cleanup_test_database():
    # Removes all test data with 'test_' prefix
    pass
```

## Continuous Integration

The test suite integrates with GitHub Actions for automated testing:

```yaml
# .github/workflows/test.yml
- name: Run Integration Tests
  run: ./tests/scripts/run_tests.sh integration --coverage

- name: Run Performance Tests
  run: ./tests/scripts/run_tests.sh performance

- name: Run E2E Tests
  run: ./tests/scripts/run_tests.sh e2e --headless
```

## Test Reports

### HTML Reports

Generated automatically with test results:

- **Test Results**: `tests/results/report.html`
- **Coverage Report**: `tests/coverage/html/index.html`
- **Performance Report**: `tests/results/performance_report.html`

### Accessing Reports

```bash
# Local development
open tests/results/report.html

# Docker environment
http://localhost:8082  # Test reports server
```

## Performance Benchmarks

### Expected Performance Metrics

| Metric | Expected Value | Critical Threshold |
|--------|----------------|-------------------|
| API Response Time | < 2s | < 5s |
| WebSocket Latency | < 0.5s | < 1s |
| Command Execution | < 5s | < 10s |
| Memory Usage | < 512MB | < 1GB |
| Success Rate | > 95% | > 90% |

### Load Testing Scenarios

- **Concurrent Users**: 50 users, 100 requests each
- **Agent Connections**: 100 simultaneous agent connections
- **Command Execution**: 50 concurrent commands
- **WebSocket Messages**: 1000 messages/second

## Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check service status
docker-compose -f tests/docker-compose.test.yml ps

# View service logs
docker-compose -f tests/docker-compose.test.yml logs backend-test

# Restart services
docker-compose -f tests/docker-compose.test.yml restart
```

#### Database Connection Issues

```bash
# Check database connectivity
psql -h localhost -p 5434 -U postgres -d dexagent_test

# Reset test database
docker-compose -f tests/docker-compose.test.yml down -v
docker-compose -f tests/docker-compose.test.yml up -d postgres-test
```

#### Browser Tests Failing

```bash
# Install/update browsers
playwright install

# Run with browser visible (debugging)
./tests/scripts/run_tests.sh e2e --headed

# Check browser logs
pytest tests/e2e -v --browser-channel=chromium --video=on
```

#### Performance Test Failures

```bash
# Check system resources
htop  # or Task Manager on Windows

# Reduce concurrent load
export TEST_CONCURRENT_USERS=10

# Run with debug output
pytest tests/performance -v -s
```

### Debug Mode

```bash
# Run tests with debug output
pytest tests -v -s --tb=long

# Add debug breakpoints in code
import pdb; pdb.set_trace()

# Use pytest debugger
pytest tests --pdb

# Capture logs
pytest tests --log-cli-level=DEBUG
```

## Best Practices

### Writing Tests

1. **Use descriptive test names** that explain what is being tested
2. **Follow the AAA pattern**: Arrange, Act, Assert
3. **Use fixtures** for common setup and cleanup
4. **Mock external dependencies** when appropriate
5. **Test both happy path and error cases**
6. **Keep tests independent** and atomic

### Test Organization

1. **Group related tests** in the same file
2. **Use markers** to categorize tests
3. **Separate test data** from test logic
4. **Document complex test scenarios**
5. **Maintain test data consistency**

### Performance Testing

1. **Set realistic thresholds** based on requirements
2. **Test under various load conditions**
3. **Monitor resource usage** during tests
4. **Use consistent test environments**
5. **Generate actionable reports**

## Contributing

### Adding New Tests

1. **Choose the appropriate test type** (unit, integration, performance, e2e)
2. **Follow existing naming conventions**
3. **Add appropriate markers and documentation**
4. **Update test configuration** if needed
5. **Ensure tests are deterministic** and repeatable

### Test Review Checklist

- [ ] Tests are well-named and documented
- [ ] Tests cover both success and failure cases
- [ ] Tests are independent and don't rely on order
- [ ] Performance tests have appropriate thresholds
- [ ] E2E tests use proper selectors and waits
- [ ] Tests clean up after themselves
- [ ] CI integration works correctly

## Support

For questions or issues with the testing infrastructure:

1. Check this documentation
2. Review existing test examples
3. Check CI/CD pipeline logs
4. Create an issue with detailed reproduction steps

## License

This testing infrastructure is part of the DexAgent project and follows the same license terms.