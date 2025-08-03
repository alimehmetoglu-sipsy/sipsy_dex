#!/usr/bin/env python3
"""
DexAgent Jira Integration Script
Provides comprehensive project management integration with Atlassian Jira
"""

import os
import json
import requests
import argparse
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import configparser
from pathlib import Path

# Configuration constants
DEFAULT_CONFIG = {
    'jira_url': 'https://sipsy.atlassian.net',
    'project_key': 'DX',
    'epic_link_field': 'customfield_10014',
    'story_points_field': 'customfield_10016',
    'timeout': 30,
    'max_results': 100
}

class JiraIntegration:
    """Main class for Jira integration operations"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize Jira integration with configuration"""
        self.config = self._load_config(config_file)
        self.session = requests.Session()
        self._setup_authentication()
        
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        config = DEFAULT_CONFIG.copy()
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            if 'jira' in parser:
                config.update(dict(parser['jira']))
                
        # Override with environment variables
        env_mappings = {
            'JIRA_URL': 'jira_url',
            'JIRA_PROJECT_KEY': 'project_key',
            'JIRA_EPIC_LINK_FIELD': 'epic_link_field',
            'JIRA_STORY_POINTS_FIELD': 'story_points_field'
        }
        
        for env_var, config_key in env_mappings.items():
            if os.getenv(env_var):
                config[config_key] = os.getenv(env_var)
                
        return config
        
    def _setup_authentication(self):
        """Setup authentication for Jira API"""
        email = os.getenv('JIRA_EMAIL')
        api_token = os.getenv('JIRA_API_TOKEN')
        
        if not email or not api_token:
            raise ValueError(
                "JIRA_EMAIL and JIRA_API_TOKEN environment variables are required. "
                "Please set them in your .env file or environment."
            )
            
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Jira API"""
        url = f"{self.config['jira_url']}/rest/api/3/{endpoint}"
        
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=self.config['timeout'],
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Jira API request failed: {e}")
            raise
            
    def test_connection(self) -> bool:
        """Test connection to Jira instance"""
        try:
            response = self._make_request('GET', 'myself')
            user_data = response.json()
            print(f"✅ Connected to Jira as: {user_data.get('displayName', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Jira: {e}")
            return False
            
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        try:
            response = self._make_request('GET', f"project/{self.config['project_key']}")
            project_data = response.json()
            
            print(f"📋 Project: {project_data.get('name', 'Unknown')}")
            print(f"🔑 Key: {project_data.get('key', 'Unknown')}")
            print(f"📝 Description: {project_data.get('description', 'No description')}")
            
            return project_data
        except Exception as e:
            print(f"❌ Failed to get project info: {e}")
            return {}
            
    def create_epic(self, 
                   summary: str, 
                   description: str, 
                   epic_name: str,
                   priority: str = "Medium") -> Optional[str]:
        """Create a new epic"""
        
        epic_data = {
            "fields": {
                "project": {"key": self.config['project_key']},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Epic"},
                "priority": {"name": priority},
                "customfield_10011": epic_name  # Epic Name field
            }
        }
        
        try:
            response = self._make_request('POST', 'issue', json=epic_data)
            result = response.json()
            epic_key = result.get('key')
            
            print(f"✅ Created epic: {epic_key}")
            print(f"   Summary: {summary}")
            print(f"   Epic Name: {epic_name}")
            
            return epic_key
        except Exception as e:
            print(f"❌ Failed to create epic: {e}")
            return None
            
    def create_story(self, 
                    summary: str, 
                    description: str,
                    epic_key: Optional[str] = None,
                    story_points: Optional[int] = None,
                    priority: str = "Medium",
                    assignee: Optional[str] = None) -> Optional[str]:
        """Create a new story"""
        
        story_data = {
            "fields": {
                "project": {"key": self.config['project_key']},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Story"},
                "priority": {"name": priority}
            }
        }
        
        # Add epic link if provided
        if epic_key:
            story_data["fields"][self.config['epic_link_field']] = epic_key
            
        # Add story points if provided
        if story_points:
            story_data["fields"][self.config['story_points_field']] = story_points
            
        # Add assignee if provided
        if assignee:
            story_data["fields"]["assignee"] = {"emailAddress": assignee}
            
        try:
            response = self._make_request('POST', 'issue', json=story_data)
            result = response.json()
            story_key = result.get('key')
            
            print(f"✅ Created story: {story_key}")
            print(f"   Summary: {summary}")
            if epic_key:
                print(f"   Epic: {epic_key}")
            if story_points:
                print(f"   Story Points: {story_points}")
                
            return story_key
        except Exception as e:
            print(f"❌ Failed to create story: {e}")
            return None
            
    def create_task(self, 
                   summary: str, 
                   description: str,
                   epic_key: Optional[str] = None,
                   priority: str = "Medium",
                   assignee: Optional[str] = None,
                   labels: Optional[List[str]] = None) -> Optional[str]:
        """Create a new task"""
        
        task_data = {
            "fields": {
                "project": {"key": self.config['project_key']},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Task"},
                "priority": {"name": priority}
            }
        }
        
        # Add epic link if provided
        if epic_key:
            task_data["fields"][self.config['epic_link_field']] = epic_key
            
        # Add assignee if provided
        if assignee:
            task_data["fields"]["assignee"] = {"emailAddress": assignee}
            
        # Add labels if provided
        if labels:
            task_data["fields"]["labels"] = labels
            
        try:
            response = self._make_request('POST', 'issue', json=task_data)
            result = response.json()
            task_key = result.get('key')
            
            print(f"✅ Created task: {task_key}")
            print(f"   Summary: {summary}")
            if epic_key:
                print(f"   Epic: {epic_key}")
            if labels:
                print(f"   Labels: {', '.join(labels)}")
                
            return task_key
        except Exception as e:
            print(f"❌ Failed to create task: {e}")
            return None
            
    def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """Transition an issue to a new status"""
        
        try:
            # Get available transitions
            response = self._make_request('GET', f'issue/{issue_key}/transitions')
            transitions = response.json().get('transitions', [])
            
            # Find the transition by name
            transition_id = None
            for transition in transitions:
                if transition['name'].lower() == transition_name.lower():
                    transition_id = transition['id']
                    break
                    
            if not transition_id:
                available = [t['name'] for t in transitions]
                print(f"❌ Transition '{transition_name}' not found. Available: {available}")
                return False
                
            # Execute transition
            transition_data = {
                "transition": {"id": transition_id}
            }
            
            self._make_request('POST', f'issue/{issue_key}/transitions', json=transition_data)
            print(f"✅ Transitioned {issue_key} to '{transition_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to transition issue: {e}")
            return False
            
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an issue"""
        
        comment_data = {
            "body": comment
        }
        
        try:
            self._make_request('POST', f'issue/{issue_key}/comment', json=comment_data)
            print(f"✅ Added comment to {issue_key}")
            return True
        except Exception as e:
            print(f"❌ Failed to add comment: {e}")
            return False
            
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get issue details"""
        
        try:
            response = self._make_request('GET', f'issue/{issue_key}')
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get issue: {e}")
            return None
            
    def search_issues(self, jql: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for issues using JQL"""
        
        if max_results is None:
            max_results = self.config['max_results']
            
        search_data = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["summary", "status", "assignee", "priority", "created", "updated"]
        }
        
        try:
            response = self._make_request('POST', 'search', json=search_data)
            result = response.json()
            return result.get('issues', [])
        except Exception as e:
            print(f"❌ Failed to search issues: {e}")
            return []
            
    def get_project_issues(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all issues for the project"""
        
        jql = f"project = {self.config['project_key']}"
        if status:
            jql += f" AND status = '{status}'"
        jql += " ORDER BY created DESC"
        
        return self.search_issues(jql)
        
    def create_development_epic(self) -> Optional[str]:
        """Create a development epic for the current sprint"""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        summary = f"DexAgent Development Sprint - {current_date}"
        description = f"""
# Development Sprint Epic

## Objective
Track development progress and feature implementation for DexAgent platform.

## Scope
- Feature development tasks
- Bug fixes and improvements
- Code quality enhancements
- Testing and validation

## Timeline
Created: {current_date}

## Success Criteria
- All linked stories and tasks completed
- Code quality standards maintained
- Tests passing
- Documentation updated

## Notes
This epic was automatically created for project management tracking.
        """.strip()
        
        epic_name = f"Development Sprint {current_date}"
        
        return self.create_epic(summary, description, epic_name, priority="High")
        
    def create_feature_stories_from_template(self, epic_key: str) -> List[str]:
        """Create standard feature development stories"""
        
        stories = [
            {
                "summary": "Frontend Component Development",
                "description": "Develop and implement frontend components with proper styling and responsiveness",
                "story_points": 5
            },
            {
                "summary": "Backend API Implementation",
                "description": "Implement backend API endpoints with proper validation and error handling",
                "story_points": 8
            },
            {
                "summary": "Database Schema Updates",
                "description": "Update database schema and implement migrations",
                "story_points": 3
            },
            {
                "summary": "Testing Implementation",
                "description": "Implement unit tests, integration tests, and E2E tests",
                "story_points": 5
            },
            {
                "summary": "Documentation Updates",
                "description": "Update API documentation, user guides, and technical documentation",
                "story_points": 2
            }
        ]
        
        created_stories = []
        for story in stories:
            story_key = self.create_story(
                summary=story["summary"],
                description=story["description"],
                epic_key=epic_key,
                story_points=story["story_points"],
                priority="Medium"
            )
            if story_key:
                created_stories.append(story_key)
                
        return created_stories
        
    def generate_sprint_report(self, output_file: Optional[str] = None) -> str:
        """Generate a sprint report"""
        
        issues = self.get_project_issues()
        
        # Categorize issues
        by_status = {}
        by_priority = {}
        by_type = {}
        
        for issue in issues:
            fields = issue.get('fields', {})
            
            # By status
            status = fields.get('status', {}).get('name', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1
            
            # By priority
            priority = fields.get('priority', {}).get('name', 'Unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # By type
            issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
            by_type[issue_type] = by_type.get(issue_type, 0) + 1
            
        # Generate report
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# DexAgent Project Sprint Report
Generated: {report_date}

## Summary
- **Total Issues**: {len(issues)}
- **Project**: {self.config['project_key']}

## Issues by Status
"""
        
        for status, count in sorted(by_status.items()):
            report += f"- **{status}**: {count}\n"
            
        report += "\n## Issues by Priority\n"
        for priority, count in sorted(by_priority.items()):
            report += f"- **{priority}**: {count}\n"
            
        report += "\n## Issues by Type\n"
        for issue_type, count in sorted(by_type.items()):
            report += f"- **{issue_type}**: {count}\n"
            
        report += f"\n## Recent Issues\n"
        for issue in issues[:10]:  # Show first 10 issues
            fields = issue.get('fields', {})
            summary = fields.get('summary', 'No summary')
            status = fields.get('status', {}).get('name', 'Unknown')
            report += f"- **{issue.get('key')}**: {summary} ({status})\n"
            
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"✅ Report saved to: {output_file}")
            
        return report

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DexAgent Jira Integration")
    parser.add_argument('--config', help="Configuration file path")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test connection
    subparsers.add_parser('test', help='Test Jira connection')
    
    # Project info
    subparsers.add_parser('info', help='Get project information')
    
    # Create epic
    epic_parser = subparsers.add_parser('create-epic', help='Create a new epic')
    epic_parser.add_argument('--summary', required=True, help='Epic summary')
    epic_parser.add_argument('--description', required=True, help='Epic description')
    epic_parser.add_argument('--name', required=True, help='Epic name')
    epic_parser.add_argument('--priority', default='Medium', help='Epic priority')
    
    # Create story
    story_parser = subparsers.add_parser('create-story', help='Create a new story')
    story_parser.add_argument('--summary', required=True, help='Story summary')
    story_parser.add_argument('--description', required=True, help='Story description')
    story_parser.add_argument('--epic', help='Epic key to link to')
    story_parser.add_argument('--points', type=int, help='Story points')
    story_parser.add_argument('--priority', default='Medium', help='Story priority')
    story_parser.add_argument('--assignee', help='Assignee email')
    
    # Create task
    task_parser = subparsers.add_parser('create-task', help='Create a new task')
    task_parser.add_argument('--summary', required=True, help='Task summary')
    task_parser.add_argument('--description', required=True, help='Task description')
    task_parser.add_argument('--epic', help='Epic key to link to')
    task_parser.add_argument('--priority', default='Medium', help='Task priority')
    task_parser.add_argument('--assignee', help='Assignee email')
    task_parser.add_argument('--labels', nargs='*', help='Task labels')
    
    # Transition issue
    transition_parser = subparsers.add_parser('transition', help='Transition an issue')
    transition_parser.add_argument('--issue', required=True, help='Issue key')
    transition_parser.add_argument('--status', required=True, help='New status')
    
    # Add comment
    comment_parser = subparsers.add_parser('comment', help='Add comment to issue')
    comment_parser.add_argument('--issue', required=True, help='Issue key')
    comment_parser.add_argument('--message', required=True, help='Comment message')
    
    # Search issues
    search_parser = subparsers.add_parser('search', help='Search issues')
    search_parser.add_argument('--jql', required=True, help='JQL query')
    search_parser.add_argument('--max-results', type=int, help='Maximum results')
    
    # List issues
    list_parser = subparsers.add_parser('list', help='List project issues')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Development workflows
    subparsers.add_parser('create-dev-epic', help='Create development epic')
    
    dev_stories_parser = subparsers.add_parser('create-dev-stories', help='Create development stories')
    dev_stories_parser.add_argument('--epic', required=True, help='Epic key to link stories to')
    
    # Reports
    report_parser = subparsers.add_parser('report', help='Generate sprint report')
    report_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    try:
        jira = JiraIntegration(args.config)
        
        if args.command == 'test':
            jira.test_connection()
            
        elif args.command == 'info':
            jira.get_project_info()
            
        elif args.command == 'create-epic':
            jira.create_epic(args.summary, args.description, args.name, args.priority)
            
        elif args.command == 'create-story':
            jira.create_story(
                args.summary, 
                args.description, 
                args.epic, 
                args.points, 
                args.priority, 
                args.assignee
            )
            
        elif args.command == 'create-task':
            jira.create_task(
                args.summary, 
                args.description, 
                args.epic, 
                args.priority, 
                args.assignee, 
                args.labels
            )
            
        elif args.command == 'transition':
            jira.transition_issue(args.issue, args.status)
            
        elif args.command == 'comment':
            jira.add_comment(args.issue, args.message)
            
        elif args.command == 'search':
            issues = jira.search_issues(args.jql, args.max_results)
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                fields = issue.get('fields', {})
                summary = fields.get('summary', 'No summary')
                status = fields.get('status', {}).get('name', 'Unknown')
                print(f"  {issue.get('key')}: {summary} ({status})")
                
        elif args.command == 'list':
            issues = jira.get_project_issues(args.status)
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                fields = issue.get('fields', {})
                summary = fields.get('summary', 'No summary')
                status = fields.get('status', {}).get('name', 'Unknown')
                priority = fields.get('priority', {}).get('name', 'Unknown')
                print(f"  {issue.get('key')}: {summary} ({status}, {priority})")
                
        elif args.command == 'create-dev-epic':
            epic_key = jira.create_development_epic()
            if epic_key:
                print(f"✅ Created development epic: {epic_key}")
                
        elif args.command == 'create-dev-stories':
            stories = jira.create_feature_stories_from_template(args.epic)
            print(f"✅ Created {len(stories)} development stories")
            
        elif args.command == 'report':
            report = jira.generate_sprint_report(args.output)
            if not args.output:
                print(report)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()