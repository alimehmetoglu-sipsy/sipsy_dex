#!/usr/bin/env python3
"""
Claude Code MCP Integration for Jira Task Creation
This script handles the MCP integration to create new Jira tasks
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_task_request(file_path: str = "jira_task_request.json") -> dict:
    """Load task creation request from file"""
    
    request_file = Path(file_path)
    if not request_file.exists():
        print(f"❌ Task request file not found: {file_path}")
        return None
    
    try:
        with open(request_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading task request: {e}")
        return None

def create_jira_task_via_mcp(task_data: dict) -> bool:
    """Create Jira task using MCP integration"""
    
    print("🚀 Claude Code MCP Jira Task Creation")
    print("=" * 50)
    
    # Extract task data
    cloud_id = task_data.get('cloud_id')
    project_key = task_data.get('project_key')
    issue_type = task_data.get('issue_type')
    summary = task_data.get('summary')
    description = task_data.get('description')
    priority = task_data.get('priority', 'Medium')
    
    print(f"🎯 Target Project: {project_key}")
    print(f"📝 Issue Type: {issue_type}")
    print(f"⚡ Priority: {priority}")
    print(f"📋 Summary: {summary}")
    print(f"📄 Description Length: {len(description)} characters")
    
    # Prepare MCP call data
    mcp_call_data = {
        "function": "mcp__atlassian-mcp__createJiraIssue",
        "parameters": {
            "cloudId": cloud_id,
            "projectKey": project_key,
            "issueTypeName": issue_type,
            "summary": summary,
            "description": description
        }
    }
    
    # Save MCP call data for Claude Code to execute
    with open("claude_mcp_call.json", 'w') as f:
        json.dump(mcp_call_data, f, indent=2)
    
    print("\n" + "="*50)
    print("🤖 READY FOR CLAUDE CODE MCP EXECUTION")
    print("="*50)
    print("Claude Code will now execute the MCP call to create the Jira task.")
    print(f"📁 MCP call data saved to: claude_mcp_call.json")
    
    return True

def main():
    """Main execution function"""
    
    # Load the task request
    task_request = load_task_request()
    if not task_request:
        return 1
    
    # Extract task data
    task_data = task_request.get('task_data', {})
    if not task_data:
        print("❌ No task data found in request")
        return 1
    
    # Create task via MCP
    success = create_jira_task_via_mcp(task_data)
    
    if success:
        print("\n✅ Jira task creation request prepared successfully!")
        print("🎯 Claude Code is ready to create the task via MCP integration")
        return 0
    else:
        print("\n❌ Failed to prepare Jira task creation")
        return 1

if __name__ == "__main__":
    exit(main())