#!/usr/bin/env python3
"""
Jira Test Results Reporter for DX-30
Posts comprehensive test results to Jira task as formatted comment
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class JiraTestReporter:
    """Reports test results to Jira task DX-30"""
    
    def __init__(self, results_file: Path):
        self.results_file = results_file
        self.results = {}
        self.cloud_id = "e9ed7bab-c21a-4b0c-b996-fa7146d8e58b"  # sipsy.atlassian.net
        self.task_id = "DX-30"
        
    def load_results(self) -> bool:
        """Load test results from JSON file with comprehensive error handling"""
        try:
            if not self.results_file.exists():
                print(f"❌ Results file does not exist: {self.results_file}")
                return False
            
            if self.results_file.stat().st_size == 0:
                print(f"❌ Results file is empty: {self.results_file}")
                return False
            
            with open(self.results_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"❌ Results file contains no data: {self.results_file}")
                    return False
                
                self.results = json.loads(content)
                
                # Validate basic structure
                if not isinstance(self.results, dict):
                    print(f"❌ Results file does not contain valid JSON object")
                    return False
                
                # Ensure required keys exist with defaults
                self.results.setdefault('total_summary', {'tests': 0, 'passed': 0, 'failed': 0, 'skipped': 0})
                self.results.setdefault('categories', {})
                self.results.setdefault('failed_tests', [])
                self.results.setdefault('error_logs', [])
                self.results.setdefault('total_duration', 0)
                self.results.setdefault('execution_timestamp', datetime.now().isoformat())
                
                print(f"✅ Successfully loaded {len(self.results)} result entries")
                return True
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in results file: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ Results file not found: {self.results_file}")
            return False
        except PermissionError:
            print(f"❌ Permission denied reading results file: {self.results_file}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error loading results: {e}")
            print(f"Error type: {type(e).__name__}")
            return False
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def get_status_emoji(self, passed: int, failed: int) -> str:
        """Get status emoji based on test results"""
        if failed == 0:
            return "✅"
        elif failed < passed:
            return "⚠️"
        else:
            return "❌"
    
    def format_percentage(self, passed: int, total: int) -> str:
        """Format success percentage"""
        if total == 0:
            return "N/A"
        return f"{(passed/total)*100:.1f}%"
    
    def generate_report_markdown(self) -> str:
        """Generate comprehensive markdown report"""
        if not self.results:
            return "❌ No test results available"
        
        # Header
        execution_time = self.results.get('execution_timestamp', datetime.now().isoformat())
        total_duration = self.results.get('total_duration', 0)
        
        report = f"""## 🧪 DexAgent Test Execution Report
**Execution Date**: {execution_time}
**Total Duration**: {self.format_duration(total_duration)}

"""
        
        # Test Summary
        summary = self.results.get('total_summary', {})
        total_tests = summary.get('tests', 0)
        total_passed = summary.get('passed', 0)
        total_failed = summary.get('failed', 0)
        total_skipped = summary.get('skipped', 0)
        
        overall_emoji = self.get_status_emoji(total_passed, total_failed)
        success_rate = self.format_percentage(total_passed, total_tests)
        
        report += f"""### {overall_emoji} Test Summary
- **Total Tests**: {total_tests}
- **Passed**: {total_passed} 
- **Failed**: {total_failed}
- **Skipped**: {total_skipped}
- **Success Rate**: {success_rate}

"""
        
        # Coverage Summary
        coverage = self.results.get('coverage_summary', {})
        backend_cov = coverage.get('backend', 0)
        frontend_cov = coverage.get('frontend', 0)
        overall_cov = coverage.get('overall', 0)
        
        if overall_cov > 0:
            cov_emoji = "✅" if overall_cov >= 80 else "⚠️" if overall_cov >= 60 else "❌"
            report += f"""### {cov_emoji} Coverage Summary
- **Backend Coverage**: {backend_cov:.1f}%
- **Frontend Coverage**: {frontend_cov:.1f}%
- **Overall Coverage**: {overall_cov:.1f}%

"""
        
        # Test Results by Category
        report += "### 📊 Test Results by Category\n\n"
        
        categories = self.results.get('categories', {})
        
        # Backend Tests
        backend = categories.get('backend', {})
        if backend.get('tests', 0) > 0:
            status_emoji = self.get_status_emoji(backend.get('passed', 0), backend.get('failed', 0))
            unit_tests = backend.get('unit_tests', {})
            api_tests = backend.get('api_tests', {})
            
            report += f"""#### {status_emoji} Backend Tests (Python/FastAPI)
- **Unit Tests**: {unit_tests.get('passed', 0)}/{unit_tests.get('passed', 0) + unit_tests.get('failed', 0)} passed
- **API Tests**: {api_tests.get('passed', 0)}/{api_tests.get('passed', 0) + api_tests.get('failed', 0)} passed
- **Duration**: {self.format_duration(backend.get('duration', 0))}
- **Coverage**: {backend.get('coverage', 0):.1f}%

"""
        
        # Frontend Tests
        frontend = categories.get('frontend', {})
        if frontend.get('tests', 0) > 0:
            status_emoji = self.get_status_emoji(frontend.get('passed', 0), frontend.get('failed', 0))
            unit_tests = frontend.get('unit_tests', {})
            e2e_tests = frontend.get('e2e_tests', {})
            
            report += f"""#### {status_emoji} Frontend Tests (React/Next.js)
- **Unit Tests**: {unit_tests.get('passed', 0)}/{unit_tests.get('passed', 0) + unit_tests.get('failed', 0)} passed
- **E2E Tests**: {e2e_tests.get('passed', 0)}/{e2e_tests.get('passed', 0) + e2e_tests.get('failed', 0)} passed
- **Duration**: {self.format_duration(frontend.get('duration', 0))}

"""
        
        # Integration Tests
        integration = categories.get('integration', {})
        if integration.get('tests', 0) > 0:
            status_emoji = self.get_status_emoji(integration.get('passed', 0), integration.get('failed', 0))
            report += f"""#### {status_emoji} Integration Tests
- **Tests**: {integration.get('passed', 0)}/{integration.get('tests', 0)} passed
- **Duration**: {self.format_duration(integration.get('duration', 0))}

"""
        
        # Performance Tests
        performance = categories.get('performance', {})
        if performance.get('tests', 0) > 0:
            status_emoji = self.get_status_emoji(performance.get('passed', 0), performance.get('failed', 0))
            metrics = performance.get('metrics', {})
            
            # Performance criteria check
            api_time = metrics.get('api_response_time', 0)
            ws_latency = metrics.get('websocket_latency', 0)
            memory = metrics.get('memory_usage', 0)
            
            api_status = "✅" if api_time < 2 else "⚠️" if api_time < 5 else "❌"
            ws_status = "✅" if ws_latency < 0.5 else "⚠️" if ws_latency < 1 else "❌"
            mem_status = "✅" if memory < 512 else "⚠️" if memory < 1024 else "❌"
            
            report += f"""#### {status_emoji} Performance Tests
- **Tests**: {performance.get('passed', 0)}/{performance.get('tests', 0)} passed
- **Duration**: {self.format_duration(performance.get('duration', 0))}

##### Performance Metrics
- **API Response Time**: {api_status} {api_time:.2f}s (target: <2s)
- **WebSocket Latency**: {ws_status} {ws_latency:.2f}s (target: <0.5s)
- **Memory Usage**: {mem_status} {memory:.1f}MB (target: <512MB)

"""
        
        # E2E Tests
        e2e = categories.get('e2e', {})
        if e2e.get('tests', 0) > 0:
            status_emoji = self.get_status_emoji(e2e.get('passed', 0), e2e.get('failed', 0))
            report += f"""#### {status_emoji} End-to-End Tests
- **Tests**: {e2e.get('passed', 0)}/{e2e.get('tests', 0)} passed
- **Duration**: {self.format_duration(e2e.get('duration', 0))}

"""
        
        # Failed Tests
        failed_tests = self.results.get('failed_tests', [])
        if failed_tests:
            report += f"""### 🚨 Failed Tests ({len(failed_tests)})
"""
            for failed_test in failed_tests:
                report += f"- {failed_test}\n"
            report += "\n"
        
        # Error Logs
        error_logs = self.results.get('error_logs', [])
        if error_logs:
            report += f"""### 📄 Error Details
```
"""
            for error in error_logs[-10:]:  # Show last 10 errors
                report += f"{error}\n"
            report += "```\n\n"
        
        # Performance Summary
        perf_metrics = self.results.get('performance_metrics', {})
        if any(perf_metrics.values()):
            report += """### 📈 Performance Summary
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
"""
            
            api_time = perf_metrics.get('api_response_time', 0)
            ws_latency = perf_metrics.get('websocket_latency', 0)
            memory = perf_metrics.get('memory_usage', 0)
            cmd_time = perf_metrics.get('command_execution_time', 0)
            
            if api_time > 0:
                status = "✅ Pass" if api_time < 2 else "⚠️ Warning" if api_time < 5 else "❌ Fail"
                report += f"| API Response Time | {api_time:.2f}s | <2s | {status} |\n"
            
            if ws_latency > 0:
                status = "✅ Pass" if ws_latency < 0.5 else "⚠️ Warning" if ws_latency < 1 else "❌ Fail"
                report += f"| WebSocket Latency | {ws_latency:.2f}s | <0.5s | {status} |\n"
            
            if memory > 0:
                status = "✅ Pass" if memory < 512 else "⚠️ Warning" if memory < 1024 else "❌ Fail"
                report += f"| Memory Usage | {memory:.1f}MB | <512MB | {status} |\n"
            
            if cmd_time > 0:
                status = "✅ Pass" if cmd_time < 5 else "⚠️ Warning" if cmd_time < 10 else "❌ Fail"
                report += f"| Command Execution | {cmd_time:.2f}s | <5s | {status} |\n"
            
            report += "\n"
        
        # Footer
        report += """---
🤖 Generated with [Claude Code](https://claude.ai/code) Test Automation

Co-Authored-By: Claude <noreply@anthropic.com>"""
        
        return report
    
    def post_to_jira(self, report: str) -> bool:
        """Post report to Jira task DX-30"""
        print("📝 Posting test results to Jira DX-30...")
        
        try:
            # This would normally use Claude Code's MCP integration
            # For now, we'll print the report and save it for manual posting
            print("\n" + "="*80)
            print("JIRA COMMENT CONTENT:")
            print("="*80)
            print(report)
            print("="*80)
            
            # Save report for Claude Code to post via MCP
            report_file = Path("jira_report.md")
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"\n✅ Report saved to {report_file}")
            print("📋 Use Claude Code to post this report to Jira DX-30")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to post to Jira: {e}")
            return False
    
    def run(self) -> bool:
        """Run the complete reporting process"""
        print(f"🚀 DexAgent Jira Test Reporter")
        print(f"Results file: {self.results_file}")
        print(f"Target task: {self.task_id}")
        
        if not self.load_results():
            return False
        
        report = self.generate_report_markdown()
        
        if not report:
            print("❌ Failed to generate report")
            return False
        
        return self.post_to_jira(report)

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python jira_reporter.py <results_file.json>")
        return 1
    
    results_file = Path(sys.argv[1])
    
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        return 1
    
    reporter = JiraTestReporter(results_file)
    success = reporter.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())