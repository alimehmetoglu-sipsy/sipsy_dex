#!/usr/bin/env python3
"""
Claude Code script to post test results to Jira DX-30
This script is designed to be executed by Claude Code with MCP integration
"""

import json
import sys
from pathlib import Path

def main():
    """
    Main function that Claude Code will execute to post test results to Jira
    This reads the generated report and provides the information needed for Claude Code
    to make the MCP call to post to Jira DX-30
    """
    
    print("🚀 Claude Code Jira Integration - DX-30 Test Results")
    print("=" * 60)
    
    # Check if report file exists
    report_file = Path("jira_report.md")
    if not report_file.exists():
        print("❌ No Jira report found. Please run the test suite first.")
        return 1
    
    try:
        # Read the generated report
        with open(report_file, 'r') as f:
            report_content = f.read()
        
        print(f"📋 Report loaded ({len(report_content)} characters)")
        print("🎯 Target: Jira task DX-30")
        print("🌐 Cloud: sipsy.atlassian.net")
        
        # Output the MCP integration request details
        print("\n" + "="*60)
        print("MCP INTEGRATION REQUEST:")
        print("="*60)
        print("Function: mcp__atlassian-mcp__createConfluenceFooterComment")  
        print("Cloud ID: e9ed7bab-c21a-4b0c-b996-fa7146d8e58b")
        print("Issue ID: DX-30")
        print("\nComment Content Preview (first 200 chars):")
        print("-" * 40)
        print(report_content[:200] + "..." if len(report_content) > 200 else report_content)
        print("-" * 40)
        
        # Save the full content for Claude Code to use
        jira_data = {
            "cloud_id": "e9ed7bab-c21a-4b0c-b996-fa7146d8e58b",
            "issue_id": "DX-30", 
            "comment_body": report_content,
            "timestamp": str(Path(report_file).stat().st_mtime),
            "action": "post_test_results"
        }
        
        with open("claude_jira_data.json", 'w') as f:
            json.dump(jira_data, f, indent=2)
        
        print("\n✅ Jira data prepared for Claude Code MCP integration")
        print("📁 Data saved to: claude_jira_data.json")
        print("\n🤖 Claude Code: Please use the MCP Atlassian integration to post this comment to Jira DX-30")
        
        # Show success message
        print("\n" + "="*60)
        print("READY FOR CLAUDE CODE MCP POSTING")
        print("="*60)
        print("The test results are now ready to be posted to Jira DX-30.")
        print("Claude Code will now use the MCP Atlassian integration to create the comment.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error preparing Jira data: {e}")
        return 1

if __name__ == "__main__":
    exit(main())