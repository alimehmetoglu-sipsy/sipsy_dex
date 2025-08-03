#!/usr/bin/env python3
"""
Post test results to Jira DX-30 using Claude Code MCP integration
This script will be called by Claude Code to post the formatted report
"""

import sys
import json
from pathlib import Path

def post_test_results_to_jira():
    """
    This function will be called by Claude Code to post test results to Jira DX-30
    It reads the generated jira_report.md and posts it as a comment to the task
    """
    
    # Configuration
    CLOUD_ID = "e9ed7bab-c21a-4b0c-b996-fa7146d8e58b"  # sipsy.atlassian.net
    TASK_ID = "DX-30"
    
    # Read the generated report
    report_file = Path("jira_report.md")
    
    if not report_file.exists():
        print("❌ Jira report file not found. Run the test suite first.")
        return False
    
    try:
        with open(report_file, 'r') as f:
            report_content = f.read()
        
        print(f"📝 Posting test results to Jira {TASK_ID}...")
        print(f"Report length: {len(report_content)} characters")
        
        # This is where Claude Code will use the MCP Atlassian integration
        # The actual MCP call will be made by Claude Code when it executes this script
        
        # For now, output the information needed for Claude Code to make the MCP call
        jira_request = {
            "action": "create_jira_comment",
            "cloud_id": CLOUD_ID,
            "issue_id": TASK_ID,
            "comment_body": report_content
        }
        
        # Save the request for Claude Code to process
        with open("jira_request.json", 'w') as f:
            json.dump(jira_request, f, indent=2)
        
        print("✅ Jira request prepared successfully")
        print("📋 Claude Code will now post this to Jira using MCP integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to prepare Jira posting: {e}")
        return False

def main():
    """Main entry point"""
    success = post_test_results_to_jira()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())