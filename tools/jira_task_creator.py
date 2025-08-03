#!/usr/bin/env python3
"""
Jira Task Creator for Test Results
Creates a new Jira task for each test execution and posts results
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class JiraTaskCreator:
    """Creates new Jira tasks for test execution results"""
    
    def __init__(self):
        self.cloud_id = "e9ed7bab-c21a-4b0c-b996-fa7146d8e58b"  # sipsy.atlassian.net
        self.project_key = "DX"  # DexAgent project
        
    def generate_task_title(self, results: Dict[str, Any]) -> str:
        """Generate a descriptive task title based on test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Get summary stats
        summary = results.get('total_summary', {})
        total_tests = summary.get('tests', 0)
        passed_tests = summary.get('passed', 0)
        failed_tests = summary.get('failed', 0)
        
        if failed_tests == 0:
            status = "✅ PASSED"
        elif failed_tests < passed_tests:
            status = "⚠️ PARTIAL"
        else:
            status = "❌ FAILED"
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return f"Test Execution Report - {status} ({success_rate:.1f}%) - {timestamp}"
    
    def generate_task_description(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive task description with test results"""
        
        # Get basic info
        execution_time = results.get('execution_timestamp', datetime.now().isoformat())
        total_duration = results.get('total_duration', 0)
        
        # Format duration
        if total_duration < 60:
            duration_str = f"{total_duration:.1f}s"
        elif total_duration < 3600:
            duration_str = f"{total_duration/60:.1f}m"
        else:
            duration_str = f"{total_duration/3600:.1f}h"
        
        # Get summary stats
        summary = results.get('total_summary', {})
        total_tests = summary.get('tests', 0)
        passed_tests = summary.get('passed', 0)
        failed_tests = summary.get('failed', 0)
        skipped_tests = summary.get('skipped', 0)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Build description
        description = f"""# 🧪 DexAgent Test Execution Report

## 📊 Executive Summary
- **Execution Date**: {execution_time}
- **Total Duration**: {duration_str}
- **Success Rate**: {success_rate:.1f}%

## 📈 Test Results Overview
- **Total Tests**: {total_tests}
- **✅ Passed**: {passed_tests}
- **❌ Failed**: {failed_tests}
- **⏭️ Skipped**: {skipped_tests}

"""
        
        # Add coverage summary if available
        coverage = results.get('coverage_summary', {})
        overall_coverage = coverage.get('overall', 0)
        if overall_coverage > 0:
            backend_cov = coverage.get('backend', 0)
            frontend_cov = coverage.get('frontend', 0)
            
            coverage_status = "✅" if overall_coverage >= 80 else "⚠️" if overall_coverage >= 60 else "❌"
            
            description += f"""## 📋 Coverage Summary
- **Overall Coverage**: {coverage_status} {overall_coverage:.1f}%
- **Backend Coverage**: {backend_cov:.1f}%
- **Frontend Coverage**: {frontend_cov:.1f}%

"""
        
        # Add category breakdown
        categories = results.get('categories', {})
        if categories:
            description += "## 🎯 Test Categories\n\n"
            
            for category, data in categories.items():
                if data.get('tests', 0) > 0:
                    cat_passed = data.get('passed', 0)
                    cat_failed = data.get('failed', 0)
                    cat_total = data.get('tests', 0)
                    cat_duration = data.get('duration', 0)
                    
                    status_emoji = "✅" if cat_failed == 0 else "⚠️" if cat_failed < cat_passed else "❌"
                    
                    description += f"### {status_emoji} {category.title()} Tests\n"
                    description += f"- **Results**: {cat_passed}/{cat_total} passed\n"
                    description += f"- **Duration**: {cat_duration:.1f}s\n"
                    
                    # Add category-specific details
                    if category == 'backend' and 'coverage' in data:
                        description += f"- **Coverage**: {data['coverage']:.1f}%\n"
                    elif category == 'performance' and 'metrics' in data:
                        metrics = data['metrics']
                        description += f"- **API Response**: {metrics.get('api_response_time', 0):.2f}s\n"
                        description += f"- **WebSocket Latency**: {metrics.get('websocket_latency', 0):.2f}s\n"
                        description += f"- **Memory Usage**: {metrics.get('memory_usage', 0):.1f}MB\n"
                    
                    description += "\n"
        
        # Add failed tests if any
        failed_tests_list = results.get('failed_tests', [])
        if failed_tests_list:
            description += f"## 🚨 Failed Tests ({len(failed_tests_list)})\n\n"
            for failed_test in failed_tests_list:
                description += f"- {failed_test}\n"
            description += "\n"
        
        # Add performance metrics summary
        perf_metrics = results.get('performance_metrics', {})
        if any(perf_metrics.values()):
            description += "## ⚡ Performance Metrics\n\n"
            description += "| Metric | Value | Target | Status |\n"
            description += "|--------|-------|--------|---------|\n"
            
            api_time = perf_metrics.get('api_response_time', 0)
            if api_time > 0:
                status = "✅ Pass" if api_time < 2 else "⚠️ Warning" if api_time < 5 else "❌ Fail"
                description += f"| API Response Time | {api_time:.2f}s | <2s | {status} |\n"
            
            ws_latency = perf_metrics.get('websocket_latency', 0)
            if ws_latency > 0:
                status = "✅ Pass" if ws_latency < 0.5 else "⚠️ Warning" if ws_latency < 1 else "❌ Fail"
                description += f"| WebSocket Latency | {ws_latency:.2f}s | <0.5s | {status} |\n"
            
            memory = perf_metrics.get('memory_usage', 0)
            if memory > 0:
                status = "✅ Pass" if memory < 512 else "⚠️ Warning" if memory < 1024 else "❌ Fail"
                description += f"| Memory Usage | {memory:.1f}MB | <512MB | {status} |\n"
            
            description += "\n"
        
        # Add error logs if any
        error_logs = results.get('error_logs', [])
        if error_logs:
            description += f"## 📄 Error Logs ({len(error_logs)} entries)\n\n"
            description += "```\n"
            for error in error_logs[-5:]:  # Show last 5 errors
                description += f"{error}\n"
            description += "```\n\n"
        
        # Add footer
        description += """## 🔗 Related Files
- Test results: `test_results.json`
- Coverage report: `tests/coverage/html/index.html`
- Jira report: `jira_report.md`

## 🤖 Automation
This task was automatically created by the DexAgent test automation system.

---
🤖 Generated with [Claude Code](https://claude.ai/code) Test Automation

Co-Authored-By: Claude <noreply@anthropic.com>"""
        
        return description
    
    def create_task_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create task data for Jira API"""
        
        title = self.generate_task_title(results)
        description = self.generate_task_description(results)
        
        # Determine issue type based on results
        failed_tests = results.get('total_summary', {}).get('failed', 0)
        if failed_tests > 0:
            issue_type = "Bug"
        else:
            issue_type = "Task"
        
        # Determine priority based on failure rate
        total_tests = results.get('total_summary', {}).get('tests', 0)
        if total_tests > 0:
            failure_rate = (failed_tests / total_tests) * 100
            if failure_rate > 50:
                priority = "High"
            elif failure_rate > 20:
                priority = "Medium"
            else:
                priority = "Low"
        else:
            priority = "Medium"
        
        return {
            "cloud_id": self.cloud_id,
            "project_key": self.project_key,
            "issue_type": issue_type,
            "summary": title,
            "description": description,
            "priority": priority,
            "labels": ["automated-test", "test-execution", "dexagent"],
            "components": ["Testing", "Automation"]
        }
    
    def save_task_request(self, results: Dict[str, Any], output_file: str = "jira_task_request.json"):
        """Save task creation request for Claude Code MCP integration"""
        
        task_data = self.create_task_data(results)
        
        # Add metadata for Claude Code
        request_data = {
            "action": "create_jira_task",
            "timestamp": datetime.now().isoformat(),
            "task_data": task_data
        }
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(request_data, f, indent=2)
        
        print(f"✅ Jira task creation request saved to: {output_file}")
        print(f"📝 Task Title: {task_data['summary']}")
        print(f"🎯 Issue Type: {task_data['issue_type']}")
        print(f"⚡ Priority: {task_data['priority']}")
        
        return task_data

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python jira_task_creator.py <results_file.json>")
        return 1
    
    results_file = Path(sys.argv[1])
    
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        return 1
    
    try:
        # Load test results
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Create task creator
        creator = JiraTaskCreator()
        
        # Generate and save task request
        task_data = creator.save_task_request(results)
        
        print("\n🚀 Ready for Claude Code MCP integration!")
        print("Claude Code will create the Jira task using the saved request data.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating Jira task request: {e}")
        return 1

if __name__ == "__main__":
    exit(main())