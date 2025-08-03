#!/usr/bin/env python3
"""
DexAgent Test Orchestrator
Comprehensive test execution and Jira reporting system for DX-30
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestOrchestrator:
    """Main test orchestration class for DexAgent comprehensive testing"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.results = {
            'execution_timestamp': datetime.now().isoformat(),
            'total_duration': 0,
            'categories': {
                'backend': {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0, 'coverage': 0},
                'frontend': {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0, 'coverage': 0},
                'integration': {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0},
                'performance': {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0, 'metrics': {}},
                'e2e': {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0}
            },
            'total_summary': {'tests': 0, 'passed': 0, 'failed': 0, 'skipped': 0},
            'coverage_summary': {'backend': 0, 'frontend': 0, 'overall': 0},
            'performance_metrics': {
                'api_response_time': 0,
                'websocket_latency': 0,
                'memory_usage': 0,
                'command_execution_time': 0
            },
            'failed_tests': [],
            'error_logs': [],
            'jira_task_id': 'DX-30'
        }
        self.start_time = time.time()
    
    def log_info(self, message: str):
        """Log info message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ℹ️  {message}")
    
    def log_success(self, message: str):
        """Log success message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✅ {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ {message}")
        self.results['error_logs'].append(f"{timestamp}: {message}")
    
    def run_command(self, command: str, cwd: Path = None, timeout: int = 600) -> Tuple[bool, str, str]:
        """Run shell command and return success, stdout, stderr with comprehensive error handling"""
        try:
            work_dir = cwd or self.project_root
            self.log_info(f"Running: {command} (in {work_dir})")
            
            # Validate working directory exists
            if not work_dir.exists():
                error_msg = f"Working directory does not exist: {work_dir}"
                self.log_error(error_msg)
                return False, "", error_msg
            
            # Check if command is potentially dangerous
            dangerous_commands = ['rm -rf /', 'sudo rm', 'format', 'del /s']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                error_msg = f"Potentially dangerous command blocked: {command}"
                self.log_error(error_msg)
                return False, "", error_msg
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'  # Handle encoding errors gracefully
            )
            
            # Log detailed info for failures
            if result.returncode != 0:
                self.log_error(f"Command failed with exit code {result.returncode}: {command}")
                if result.stderr:
                    self.log_error(f"STDERR: {result.stderr[:500]}...")  # Truncate long errors
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout}s: {command}"
            self.log_error(error_msg)
            # Try to kill the process if still running
            try:
                if hasattr(e, 'process') and e.process:
                    e.process.kill()
                    self.log_info("Killed timed out process")
            except:
                pass
            return False, "", error_msg
        except FileNotFoundError as e:
            error_msg = f"Command not found: {command} - {str(e)}"
            self.log_error(error_msg)
            return False, "", error_msg
        except PermissionError as e:
            error_msg = f"Permission denied for command: {command} - {str(e)}"
            self.log_error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error running command: {command} - {str(e)}"
            self.log_error(error_msg)
            self.log_error(f"Exception type: {type(e).__name__}")
            return False, "", error_msg
    
    def check_prerequisites(self) -> bool:
        """Check if all required services and dependencies are available"""
        self.log_info("Checking prerequisites...")
        
        prerequisites_ok = True
        
        # Check if backend is running
        success, stdout, stderr = self.run_command(
            "curl -s http://localhost:8080/api/v1/system/health || echo 'FAILED'",
            timeout=10
        )
        
        if not success or 'FAILED' in stdout:
            self.log_error("Backend is not running. Please start it with: make dev-up")
            prerequisites_ok = False
        else:
            self.log_success("Backend is running")
        
        # Check if pytest is available
        success, _, _ = self.run_command("python3 -c 'import pytest'", timeout=5)
        if not success:
            self.log_error("pytest not available. Installing...")
            success, _, _ = self.run_command("pip install -r tests/requirements.txt")
            if not success:
                prerequisites_ok = False
        
        # Check if npm is available for frontend tests
        success, _, _ = self.run_command("npm --version", timeout=5)
        if not success:
            self.log_error("npm not available for frontend tests")
            prerequisites_ok = False
        
        return prerequisites_ok
    
    def run_backend_tests(self) -> Dict[str, Any]:
        """Run backend unit tests and API tests using existing infrastructure"""
        self.log_info("Running Backend Tests...")
        start_time = time.time()
        
        category_result = {
            'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0, 'coverage': 0,
            'unit_tests': {'passed': 0, 'failed': 0},
            'api_tests': {'passed': 0, 'failed': 0}
        }
        
        # Use existing Makefile target for backend tests with coverage
        self.log_info("Running backend tests via Makefile...")
        success, stdout, stderr = self.run_command(
            "make test-backend",
            timeout=300
        )
        
        if success:
            self.log_success("Backend unit tests completed")
            # Parse pytest output for test counts
            unit_passed, unit_failed = self.parse_pytest_output(stdout)
            category_result['unit_tests']['passed'] = unit_passed
            category_result['unit_tests']['failed'] = unit_failed
        else:
            self.log_error(f"Backend unit tests failed: {stderr}")
            self.results['failed_tests'].append("Backend Unit Tests")
            
            # Try fallback with direct pytest
            self.log_info("Trying fallback pytest command...")
            success, stdout, stderr = self.run_command(
                "python3 -m pytest apps/backend/tests/ -v --cov=app --cov-report=json:tests/coverage/backend_coverage.json",
                timeout=300
            )
            if success:
                unit_passed, unit_failed = self.parse_pytest_output(stdout)
                category_result['unit_tests']['passed'] = unit_passed
                category_result['unit_tests']['failed'] = unit_failed
        
        # Run comprehensive API tests
        self.log_info("Running comprehensive API tests...")
        success, stdout, stderr = self.run_command(
            "python3 apps/backend/comprehensive_api_test.py",
            timeout=180
        )
        
        if success:
            self.log_success("API tests completed")
            # Parse API test output for counts
            api_passed, api_failed = self.parse_api_test_output(stdout)
            category_result['api_tests']['passed'] = api_passed
            category_result['api_tests']['failed'] = api_failed
        else:
            self.log_error(f"API tests failed: {stderr}")
            self.results['failed_tests'].append("Comprehensive API Tests")
        
        # Parse coverage
        coverage_file = self.project_root / "tests/coverage/backend_coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    category_result['coverage'] = coverage_data.get('totals', {}).get('percent_covered', 0)
            except Exception as e:
                self.log_error(f"Failed to parse coverage: {e}")
        
        # Calculate totals
        category_result['tests'] = (category_result['unit_tests']['passed'] + 
                                  category_result['unit_tests']['failed'] +
                                  category_result['api_tests']['passed'] + 
                                  category_result['api_tests']['failed'])
        category_result['passed'] = (category_result['unit_tests']['passed'] + 
                                   category_result['api_tests']['passed'])
        category_result['failed'] = (category_result['unit_tests']['failed'] + 
                                   category_result['api_tests']['failed'])
        category_result['duration'] = time.time() - start_time
        
        return category_result
    
    def run_frontend_tests(self) -> Dict[str, Any]:
        """Run frontend unit and E2E tests using existing infrastructure"""
        self.log_info("Running Frontend Tests...")
        start_time = time.time()
        
        category_result = {
            'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0, 'coverage': 0,
            'unit_tests': {'passed': 0, 'failed': 0},
            'e2e_tests': {'passed': 0, 'failed': 0}
        }
        
        # Use existing Makefile target for frontend tests
        self.log_info("Running frontend tests via Makefile...")
        success, stdout, stderr = self.run_command(
            "make test-frontend",
            timeout=400
        )
        
        if success:
            self.log_success("Frontend tests completed")
            # Parse output for both unit and E2E tests
            unit_passed, unit_failed = self.parse_jest_output(stdout)
            e2e_passed, e2e_failed = self.parse_playwright_output(stdout)
            
            category_result['unit_tests']['passed'] = unit_passed
            category_result['unit_tests']['failed'] = unit_failed
            category_result['e2e_tests']['passed'] = e2e_passed
            category_result['e2e_tests']['failed'] = e2e_failed
        else:
            self.log_error(f"Frontend tests failed: {stderr}")
            self.results['failed_tests'].append("Frontend Tests")
            
            # Try fallback individual commands
            frontend_dir = self.project_root / "apps/frontend"
            
            # Try unit tests
            self.log_info("Trying fallback unit tests...")
            success, stdout, stderr = self.run_command(
                "npm test -- --passWithNoTests --watchAll=false",
                cwd=frontend_dir,
                timeout=180
            )
            
            if success:
                unit_passed, unit_failed = self.parse_jest_output(stdout)
                category_result['unit_tests']['passed'] = unit_passed
                category_result['unit_tests']['failed'] = unit_failed
            
            # Try E2E tests
            self.log_info("Trying fallback E2E tests...")
            success, stdout, stderr = self.run_command(
                "npm run test:e2e",
                cwd=frontend_dir,
                timeout=300
            )
            
            if success:
                e2e_passed, e2e_failed = self.parse_playwright_output(stdout)
                category_result['e2e_tests']['passed'] = e2e_passed
                category_result['e2e_tests']['failed'] = e2e_failed
        
        # Calculate totals
        category_result['tests'] = (category_result['unit_tests']['passed'] + 
                                  category_result['unit_tests']['failed'] +
                                  category_result['e2e_tests']['passed'] + 
                                  category_result['e2e_tests']['failed'])
        category_result['passed'] = (category_result['unit_tests']['passed'] + 
                                   category_result['e2e_tests']['passed'])
        category_result['failed'] = (category_result['unit_tests']['failed'] + 
                                   category_result['e2e_tests']['failed'])
        category_result['duration'] = time.time() - start_time
        
        return category_result
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests using existing infrastructure"""
        self.log_info("Running Integration Tests...")
        start_time = time.time()
        
        # Use existing Makefile target
        success, stdout, stderr = self.run_command(
            "make test-integration",
            timeout=300
        )
        
        category_result = {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0}
        
        if success:
            self.log_success("Integration tests completed")
            passed, failed = self.parse_pytest_output(stdout)
            category_result['passed'] = passed
            category_result['failed'] = failed
        else:
            self.log_error(f"Integration tests failed: {stderr}")
            self.results['failed_tests'].append("Integration Tests")
            
            # Try fallback with direct command
            self.log_info("Trying fallback integration tests...")
            success, stdout, stderr = self.run_command(
                "./tests/scripts/run_tests.sh integration",
                timeout=300
            )
            if success:
                passed, failed = self.parse_pytest_output(stdout)
                category_result['passed'] = passed
                category_result['failed'] = failed
        
        category_result['tests'] = category_result['passed'] + category_result['failed']
        category_result['duration'] = time.time() - start_time
        
        return category_result
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests and collect metrics using existing infrastructure"""
        self.log_info("Running Performance Tests...")
        start_time = time.time()
        
        # Use existing Makefile target
        success, stdout, stderr = self.run_command(
            "make test-performance",
            timeout=300
        )
        
        category_result = {
            'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0,
            'metrics': {
                'api_response_time': 0,
                'websocket_latency': 0,
                'memory_usage': 0
            }
        }
        
        if success:
            self.log_success("Performance tests completed")
            passed, failed = self.parse_pytest_output(stdout)
            category_result['passed'] = passed
            category_result['failed'] = failed
            
            # Extract performance metrics from output
            category_result['metrics'] = self.extract_performance_metrics(stdout)
        else:
            self.log_error(f"Performance tests failed: {stderr}")
            self.results['failed_tests'].append("Performance Tests")
            
            # Try fallback with test script
            self.log_info("Trying fallback performance tests...")
            success, stdout, stderr = self.run_command(
                "./tests/scripts/run_tests.sh performance",
                timeout=300
            )
            if success:
                passed, failed = self.parse_pytest_output(stdout)
                category_result['passed'] = passed
                category_result['failed'] = failed
                category_result['metrics'] = self.extract_performance_metrics(stdout)
        
        category_result['tests'] = category_result['passed'] + category_result['failed']
        category_result['duration'] = time.time() - start_time
        
        return category_result
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests using existing infrastructure"""
        self.log_info("Running End-to-End Tests...")
        start_time = time.time()
        
        # Use existing Makefile target
        success, stdout, stderr = self.run_command(
            "make test-e2e",
            timeout=600
        )
        
        category_result = {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0}
        
        if success:
            self.log_success("E2E tests completed")
            passed, failed = self.parse_pytest_output(stdout)
            category_result['passed'] = passed
            category_result['failed'] = failed
        else:
            self.log_error(f"E2E tests failed: {stderr}")
            self.results['failed_tests'].append("End-to-End Tests")
            
            # Try fallback with test script
            self.log_info("Trying fallback E2E tests...")
            success, stdout, stderr = self.run_command(
                "./tests/scripts/run_tests.sh e2e",
                timeout=600
            )
            if success:
                passed, failed = self.parse_pytest_output(stdout)
                category_result['passed'] = passed
                category_result['failed'] = failed
        
        category_result['tests'] = category_result['passed'] + category_result['failed']
        category_result['duration'] = time.time() - start_time
        
        return category_result
    
    def parse_pytest_output(self, output: str) -> Tuple[int, int]:
        """Parse pytest output to extract pass/fail counts"""
        passed, failed = 0, 0
        try:
            for line in output.split('\n'):
                if 'passed' in line and 'failed' in line:
                    # Look for pattern like "5 passed, 2 failed in 10.5s"
                    import re
                    match = re.search(r'(\d+) passed.*?(\d+) failed', line)
                    if match:
                        passed = int(match.group(1))
                        failed = int(match.group(2))
                        break
                elif 'passed' in line and 'failed' not in line:
                    # Look for pattern like "5 passed in 10.5s"  
                    import re
                    match = re.search(r'(\d+) passed', line)
                    if match:
                        passed = int(match.group(1))
                        failed = 0
                        break
        except Exception as e:
            self.log_error(f"Failed to parse pytest output: {e}")
        
        return passed, failed
    
    def parse_jest_output(self, output: str) -> Tuple[int, int]:
        """Parse Jest output to extract pass/fail counts"""
        passed, failed = 0, 0
        try:
            # Jest outputs something like "Tests: 5 passed, 2 failed, 7 total"
            import re
            match = re.search(r'Tests:.*?(\d+) passed.*?(\d+) failed', output)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2))
        except Exception as e:
            self.log_error(f"Failed to parse Jest output: {e}")
        
        return passed, failed
    
    def parse_playwright_output(self, output: str) -> Tuple[int, int]:
        """Parse Playwright output to extract pass/fail counts"""
        passed, failed = 0, 0
        try:
            # Playwright outputs something like "5 passed (10s)"
            import re
            match = re.search(r'(\d+) passed', output)
            if match:
                passed = int(match.group(1))
            
            fail_match = re.search(r'(\d+) failed', output)
            if fail_match:
                failed = int(fail_match.group(1))
        except Exception as e:
            self.log_error(f"Failed to parse Playwright output: {e}")
        
        return passed, failed
    
    def parse_api_test_output(self, output: str) -> Tuple[int, int]:
        """Parse comprehensive API test output"""
        passed, failed = 0, 0
        try:
            # Look for our custom API test output format
            import re
            pass_match = re.search(r'✅ Passed: (\d+)', output)
            fail_match = re.search(r'❌ Failed: (\d+)', output)
            
            if pass_match:
                passed = int(pass_match.group(1))
            if fail_match:
                failed = int(fail_match.group(1))
        except Exception as e:
            self.log_error(f"Failed to parse API test output: {e}")
        
        return passed, failed
    
    def extract_performance_metrics(self, output: str) -> Dict[str, float]:
        """Extract performance metrics from test output"""
        metrics = {
            'api_response_time': 0,
            'websocket_latency': 0,
            'memory_usage': 0
        }
        
        try:
            import re
            # Look for performance metrics in output
            api_time_match = re.search(r'API Response Time: ([\d.]+)', output)
            if api_time_match:
                metrics['api_response_time'] = float(api_time_match.group(1))
            
            ws_latency_match = re.search(r'WebSocket Latency: ([\d.]+)', output)
            if ws_latency_match:
                metrics['websocket_latency'] = float(ws_latency_match.group(1))
            
            memory_match = re.search(r'Memory Usage: ([\d.]+)', output)
            if memory_match:
                metrics['memory_usage'] = float(memory_match.group(1))
        except Exception as e:
            self.log_error(f"Failed to extract performance metrics: {e}")
        
        return metrics
    
    def calculate_summary(self):
        """Calculate overall test summary"""
        for category, results in self.results['categories'].items():
            self.results['total_summary']['tests'] += results['tests']
            self.results['total_summary']['passed'] += results['passed']
            self.results['total_summary']['failed'] += results['failed']
        
        # Calculate coverage summary
        if self.results['categories']['backend']['coverage'] > 0:
            self.results['coverage_summary']['backend'] = self.results['categories']['backend']['coverage']
        if self.results['categories']['frontend']['coverage'] > 0:
            self.results['coverage_summary']['frontend'] = self.results['categories']['frontend']['coverage']
        
        # Calculate overall coverage (weighted average)
        backend_cov = self.results['coverage_summary']['backend']
        frontend_cov = self.results['coverage_summary']['frontend']
        if backend_cov > 0 and frontend_cov > 0:
            self.results['coverage_summary']['overall'] = (backend_cov + frontend_cov) / 2
        elif backend_cov > 0:
            self.results['coverage_summary']['overall'] = backend_cov
        elif frontend_cov > 0:
            self.results['coverage_summary']['overall'] = frontend_cov
        
        # Copy performance metrics
        perf_metrics = self.results['categories']['performance'].get('metrics', {})
        self.results['performance_metrics'].update(perf_metrics)
        
        # Calculate total duration
        self.results['total_duration'] = time.time() - self.start_time
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite with error handling"""
        self.log_info("🚀 Starting DexAgent Comprehensive Test Suite")
        self.log_info("=" * 60)
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                self.log_error("Prerequisites check failed. Cannot continue.")
                self.results['error_logs'].append("Prerequisites check failed")
                return self.results
            
            # Initialize test results with safe defaults
            test_categories = ['backend', 'frontend', 'integration', 'performance', 'e2e']
            
            for category in test_categories:
                self.log_info(f"🔄 Starting {category} tests...")
                
                try:
                    if category == 'backend':
                        result = self.run_backend_tests()
                    elif category == 'frontend': 
                        result = self.run_frontend_tests()
                    elif category == 'integration':
                        result = self.run_integration_tests()
                    elif category == 'performance':
                        result = self.run_performance_tests()
                    elif category == 'e2e':
                        result = self.run_e2e_tests()
                    else:
                        result = {'tests': 0, 'passed': 0, 'failed': 0, 'duration': 0}
                    
                    self.results['categories'][category] = result
                    self.log_success(f"✅ {category} tests completed")
                    
                except Exception as e:
                    error_msg = f"Critical error in {category} tests: {str(e)}"
                    self.log_error(error_msg)
                    
                    # Set safe default result for failed category
                    self.results['categories'][category] = {
                        'tests': 0, 'passed': 0, 'failed': 1, 'duration': 0,
                        'error': str(e)
                    }
                    self.results['failed_tests'].append(f"{category.title()} Tests (Critical Error)")
            
            # Calculate summary with error handling
            try:
                self.calculate_summary()
            except Exception as e:
                self.log_error(f"Error calculating summary: {str(e)}")
                # Provide basic summary if calculation fails
                self.results['total_summary'] = {
                    'tests': sum(cat.get('tests', 0) for cat in self.results['categories'].values()),
                    'passed': sum(cat.get('passed', 0) for cat in self.results['categories'].values()),
                    'failed': sum(cat.get('failed', 0) for cat in self.results['categories'].values()),
                    'skipped': 0
                }
            
            # Final reporting
            self.log_info("=" * 60)
            self.log_success(f"✅ Test suite completed in {self.results['total_duration']:.1f}s")
            self.log_info(f"📊 Total: {self.results['total_summary']['tests']} tests")
            self.log_info(f"✅ Passed: {self.results['total_summary']['passed']}")
            self.log_info(f"❌ Failed: {self.results['total_summary']['failed']}")
            
            if self.results['total_summary']['tests'] > 0:
                success_rate = (self.results['total_summary']['passed'] / 
                              self.results['total_summary']['tests']) * 100
                self.log_info(f"📈 Success Rate: {success_rate:.1f}%")
            
            # Log any critical errors
            if self.results['error_logs']:
                self.log_info(f"⚠️  {len(self.results['error_logs'])} errors occurred during execution")
            
        except Exception as e:
            self.log_error(f"Critical error in test suite execution: {str(e)}")
            self.results['error_logs'].append(f"Critical error: {str(e)}")
            
            # Ensure we have some basic structure even if everything fails
            if not self.results.get('total_summary'):
                self.results['total_summary'] = {'tests': 0, 'passed': 0, 'failed': 1, 'skipped': 0}
        
        return self.results
    
    def create_jira_comment(self) -> str:
        """Create formatted Jira comment from test results"""
        # This will call the Jira reporter to generate the markdown
        try:
            # Save results first
            results_file = self.project_root / "test_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            # Generate Jira report
            success, stdout, stderr = self.run_command(
                f"python3 tools/jira_reporter.py {results_file}",
                timeout=30
            )
            
            if success:
                self.log_success("Jira report generated successfully")
                
                # Read the generated report
                report_file = self.project_root / "jira_report.md"
                if report_file.exists():
                    with open(report_file, 'r') as f:
                        return f.read()
            else:
                self.log_error(f"Failed to generate Jira report: {stderr}")
                
        except Exception as e:
            self.log_error(f"Error creating Jira comment: {e}")
        
        return ""

def main():
    """Main entry point"""
    orchestrator = TestOrchestrator()
    results = orchestrator.run_all_tests()
    
    # Save results for reporting
    results_file = orchestrator.project_root / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate Jira report
    orchestrator.log_info("Generating Jira report...")
    jira_comment = orchestrator.create_jira_comment()
    
    if jira_comment:
        orchestrator.log_success("✅ Test execution and reporting completed!")
        orchestrator.log_info("📋 Jira comment is ready for posting to DX-30")
    else:
        orchestrator.log_error("❌ Failed to generate Jira report")
    
    # Return exit code based on test results
    return 0 if results['total_summary']['failed'] == 0 else 1

if __name__ == "__main__":
    exit(main())