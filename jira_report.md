## 🧪 DexAgent Test Execution Report
**Execution Date**: 2025-08-03T19:51:23.641391
**Total Duration**: 2.3m

### ✅ Test Summary
- **Total Tests**: 0
- **Passed**: 0 
- **Failed**: 0
- **Skipped**: 0
- **Success Rate**: N/A

### 📊 Test Results by Category

### 🚨 Failed Tests (6)
- Backend Unit Tests
- Comprehensive API Tests
- Frontend Tests
- Integration Tests
- Performance Tests
- End-to-End Tests

### 📄 Error Details
```
19:53:36: Integration tests failed: make: *** [Makefile:72: test-integration] Error 1

19:53:37: Command failed with exit code 1: ./tests/scripts/run_tests.sh integration
19:53:38: Command failed with exit code 2: make test-performance
19:53:38: STDERR: make: *** [Makefile:77: test-performance] Error 1
...
19:53:38: Performance tests failed: make: *** [Makefile:77: test-performance] Error 1

19:53:39: Command failed with exit code 1: ./tests/scripts/run_tests.sh performance
19:53:40: Command failed with exit code 2: make test-e2e
19:53:40: STDERR: make: *** [Makefile:82: test-e2e] Error 1
...
19:53:40: E2E tests failed: make: *** [Makefile:82: test-e2e] Error 1

19:53:41: Command failed with exit code 1: ./tests/scripts/run_tests.sh e2e
```

---
🤖 Generated with [Claude Code](https://claude.ai/code) Test Automation

Co-Authored-By: Claude <noreply@anthropic.com>