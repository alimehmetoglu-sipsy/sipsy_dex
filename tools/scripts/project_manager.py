#!/usr/bin/env python3
"""
DexAgent Project Manager
Advanced project management automation and workflows
"""

import json
import os
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Import our integrations
try:
    from jira_integration import JiraIntegration
except ImportError:
    print("❌ jira_integration module not found")
    sys.exit(1)

class ProjectManager:
    """Advanced project management automation"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize project manager"""
        self.jira = JiraIntegration(config_file)
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Any]:
        """Load issue templates"""
        templates_file = self.templates_dir / "jira_issue_templates.json"
        
        if not templates_file.exists():
            print(f"⚠️  Templates file not found: {templates_file}")
            return {}
            
        try:
            with open(templates_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading templates: {e}")
            return {}
            
    def create_from_template(self, template_name: str, **kwargs) -> Optional[str]:
        """Create issue from template with variable substitution"""
        
        if 'templates' not in self.templates:
            print("❌ No templates found")
            return None
            
        if template_name not in self.templates['templates']:
            available = list(self.templates['templates'].keys())
            print(f"❌ Template '{template_name}' not found. Available: {available}")
            return None
            
        template = self.templates['templates'][template_name]
        
        # Substitute variables in description
        description = template['description_template']
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            description = description.replace(placeholder, str(value))
            
        # Check for unsubstituted placeholders
        unsubstituted = re.findall(r'\{\{([^}]+)\}\}', description)
        if unsubstituted:
            print(f"⚠️  Unsubstituted placeholders: {unsubstituted}")
            for placeholder in unsubstituted:
                user_input = input(f"Enter value for {placeholder}: ")
                description = description.replace(f"{{{{{placeholder}}}}}", user_input)
                
        # Get required fields
        summary = kwargs.get('summary', input("Enter issue summary: "))
        epic_key = kwargs.get('epic_key')
        assignee = kwargs.get('assignee')
        priority = template.get('priority', 'Medium')
        
        # Create issue based on type
        issue_type = template['issuetype']
        
        if issue_type == 'Epic':
            epic_name = kwargs.get('epic_name', summary)
            return self.jira.create_epic(summary, description, epic_name, priority)
            
        elif issue_type == 'Story':
            story_points = template.get('fields', {}).get('story_points')
            return self.jira.create_story(summary, description, epic_key, story_points, priority, assignee)
            
        elif issue_type == 'Task':
            labels = template.get('fields', {}).get('labels', [])
            return self.jira.create_task(summary, description, epic_key, priority, assignee, labels)
            
        else:
            print(f"❌ Unsupported issue type: {issue_type}")
            return None
            
    def create_feature_epic_with_stories(self, feature_name: str, feature_description: str) -> Dict[str, str]:
        """Create a complete feature epic with standard stories"""
        
        print(f"🚀 Creating feature epic: {feature_name}")
        
        # Create epic
        epic_summary = f"Feature: {feature_name}"
        epic_description = f"""
# Feature Epic: {feature_name}

## Vision
{feature_description}

## Business Value
This feature will enhance the DexAgent platform by providing {feature_name.lower()} capabilities.

## Scope
### In Scope
- Core functionality implementation
- User interface components
- API endpoints
- Testing and validation
- Documentation updates

### Out of Scope
- Advanced customization options (future iteration)
- Third-party integrations (separate epic)

## Success Metrics
- Feature implemented and tested
- User acceptance criteria met
- Performance requirements satisfied
- Documentation complete

## Technical Approach
Implementation will follow standard DexAgent architecture patterns with proper separation of concerns.

## Timeline
Target completion: {(datetime.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')}
        """.strip()
        
        epic_key = self.jira.create_epic(
            epic_summary, 
            epic_description, 
            f"{feature_name} Epic",
            priority="High"
        )
        
        if not epic_key:
            print("❌ Failed to create epic")
            return {}
            
        created_issues = {'epic': epic_key}
        
        # Create standard stories
        stories_template = [
            {
                'name': 'Backend API Implementation',
                'description': f'Implement backend API endpoints for {feature_name} functionality',
                'points': 8
            },
            {
                'name': 'Frontend Components Development',
                'description': f'Develop frontend components and UI for {feature_name}',
                'points': 5
            },
            {
                'name': 'Database Schema Updates',
                'description': f'Update database schema to support {feature_name} data',
                'points': 3
            },
            {
                'name': 'Integration Testing',
                'description': f'Implement integration tests for {feature_name} functionality',
                'points': 3
            },
            {
                'name': 'User Documentation',
                'description': f'Create user documentation for {feature_name} feature',
                'points': 2
            }
        ]
        
        print(f"📋 Creating {len(stories_template)} stories for epic {epic_key}")
        
        for story_info in stories_template:
            story_summary = f"{feature_name}: {story_info['name']}"
            story_key = self.jira.create_story(
                summary=story_summary,
                description=story_info['description'],
                epic_key=epic_key,
                story_points=story_info['points'],
                priority="Medium"
            )
            
            if story_key:
                created_issues[story_info['name'].lower().replace(' ', '_')] = story_key
                
        return created_issues
        
    def create_sprint_plan(self, sprint_name: str, sprint_duration: int = 14) -> Dict[str, Any]:
        """Create a sprint plan with standard structure"""
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=sprint_duration)
        
        print(f"📅 Creating sprint plan: {sprint_name}")
        print(f"   Duration: {sprint_duration} days")
        print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
        print(f"   End: {end_date.strftime('%Y-%m-%d')}")
        
        # Create sprint epic
        sprint_summary = f"Sprint: {sprint_name}"
        sprint_description = f"""
# Sprint Plan: {sprint_name}

## Sprint Goal
Deliver high-quality features and improvements for the DexAgent platform.

## Duration
- **Start Date**: {start_date.strftime('%Y-%m-%d')}
- **End Date**: {end_date.strftime('%Y-%m-%d')}
- **Duration**: {sprint_duration} days

## Sprint Objectives
- Complete planned stories and tasks
- Maintain code quality standards
- Ensure proper testing coverage
- Update documentation

## Sprint Ceremonies
- **Daily Standups**: 9:00 AM daily
- **Sprint Review**: {end_date.strftime('%Y-%m-%d')} 3:00 PM
- **Sprint Retrospective**: {end_date.strftime('%Y-%m-%d')} 4:00 PM

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Feature tested in staging
- [ ] Security review completed (if applicable)

## Sprint Metrics
- **Planned Story Points**: TBD
- **Completed Story Points**: TBD
- **Velocity**: TBD
        """.strip()
        
        epic_key = self.jira.create_epic(
            sprint_summary,
            sprint_description,
            f"{sprint_name} Sprint",
            priority="High"
        )
        
        if not epic_key:
            print("❌ Failed to create sprint epic")
            return {}
            
        # Create standard sprint tasks
        sprint_tasks = [
            {
                'summary': f'{sprint_name}: Sprint Planning',
                'description': 'Plan sprint backlog and estimate story points',
                'labels': ['sprint', 'planning']
            },
            {
                'summary': f'{sprint_name}: Daily Standups',
                'description': 'Conduct daily standup meetings',
                'labels': ['sprint', 'ceremony']
            },
            {
                'summary': f'{sprint_name}: Sprint Review',
                'description': 'Present completed work to stakeholders',
                'labels': ['sprint', 'review']
            },
            {
                'summary': f'{sprint_name}: Sprint Retrospective',
                'description': 'Reflect on sprint and identify improvements',
                'labels': ['sprint', 'retrospective']
            }
        ]
        
        created_tasks = []
        for task_info in sprint_tasks:
            task_key = self.jira.create_task(
                summary=task_info['summary'],
                description=task_info['description'],
                epic_key=epic_key,
                priority="Medium",
                labels=task_info['labels']
            )
            
            if task_key:
                created_tasks.append(task_key)
                
        return {
            'epic_key': epic_key,
            'tasks': created_tasks,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'duration_days': sprint_duration
        }
        
    def create_release_plan(self, version: str, release_date: str) -> Dict[str, Any]:
        """Create a release plan with standard structure"""
        
        print(f"🚀 Creating release plan for version {version}")
        
        release_summary = f"Release {version}"
        release_description = f"""
# Release Plan: Version {version}

## Release Overview
This release includes new features, bug fixes, and improvements for the DexAgent platform.

## Release Information
- **Version**: {version}
- **Target Release Date**: {release_date}
- **Release Type**: Minor/Major Release

## Release Scope
### New Features
- TBD (link feature epics)

### Bug Fixes
- TBD (link bug tickets)

### Improvements
- TBD (link improvement tickets)

## Release Criteria
- [ ] All planned features completed
- [ ] All critical and high priority bugs resolved
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Release notes prepared

## Testing Requirements
- [ ] Unit test coverage > 80%
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests passing
- [ ] Security scan completed

## Deployment Plan
- [ ] Deploy to staging environment
- [ ] UAT completion
- [ ] Production deployment
- [ ] Post-deployment verification

## Rollback Plan
- Database backup completed
- Application backup completed
- Rollback procedures documented
- Rollback testing completed

## Communication Plan
- [ ] Release notes published
- [ ] Stakeholders notified
- [ ] User documentation updated
- [ ] Support team briefed
        """.strip()
        
        epic_key = self.jira.create_epic(
            release_summary,
            release_description,
            f"Release {version}",
            priority="Critical"
        )
        
        if not epic_key:
            print("❌ Failed to create release epic")
            return {}
            
        # Create release tasks
        release_tasks = [
            {
                'summary': f'Release {version}: Code Freeze',
                'description': 'Implement code freeze for release branch',
                'labels': ['release', 'milestone']
            },
            {
                'summary': f'Release {version}: QA Testing',
                'description': 'Complete QA testing for all release features',
                'labels': ['release', 'testing']
            },
            {
                'summary': f'Release {version}: Security Review',
                'description': 'Complete security review for release',
                'labels': ['release', 'security']
            },
            {
                'summary': f'Release {version}: Documentation',
                'description': 'Update documentation and release notes',
                'labels': ['release', 'documentation']
            },
            {
                'summary': f'Release {version}: Deployment',
                'description': 'Deploy release to production environment',
                'labels': ['release', 'deployment']
            }
        ]
        
        created_tasks = []
        for task_info in release_tasks:
            task_key = self.jira.create_task(
                summary=task_info['summary'],
                description=task_info['description'],
                epic_key=epic_key,
                priority="High",
                labels=task_info['labels']
            )
            
            if task_key:
                created_tasks.append(task_key)
                
        return {
            'epic_key': epic_key,
            'tasks': created_tasks,
            'version': version,
            'release_date': release_date
        }
        
    def generate_project_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive project report"""
        
        print("📊 Generating project report...")
        
        # Get all project issues
        issues = self.jira.get_project_issues()
        
        # Analyze issues
        total_issues = len(issues)
        epics = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Epic']
        stories = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Story']
        tasks = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Task']
        bugs = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Bug']
        
        # Status analysis
        status_counts = {}
        priority_counts = {}
        
        for issue in issues:
            fields = issue.get('fields', {})
            
            status = fields.get('status', {}).get('name', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            priority = fields.get('priority', {}).get('name', 'Unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
        # Generate report
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# DexAgent Project Management Report
**Generated**: {report_date}

## Project Overview
- **Total Issues**: {total_issues}
- **Epics**: {len(epics)}
- **Stories**: {len(stories)}
- **Tasks**: {len(tasks)}
- **Bugs**: {len(bugs)}

## Issue Status Distribution
"""
        
        for status, count in sorted(status_counts.items()):
            percentage = (count / total_issues * 100) if total_issues > 0 else 0
            report += f"- **{status}**: {count} ({percentage:.1f}%)\n"
            
        report += "\n## Priority Distribution\n"
        for priority, count in sorted(priority_counts.items()):
            percentage = (count / total_issues * 100) if total_issues > 0 else 0
            report += f"- **{priority}**: {count} ({percentage:.1f}%)\n"
            
        # Epic progress
        report += "\n## Epic Progress\n"
        for epic in epics[:10]:  # Show first 10 epics
            fields = epic.get('fields', {})
            summary = fields.get('summary', 'No summary')
            status = fields.get('status', {}).get('name', 'Unknown')
            report += f"- **{epic.get('key')}**: {summary} ({status})\n"
            
        # Recent activity
        report += "\n## Recent Issues (Last 10)\n"
        for issue in issues[:10]:
            fields = issue.get('fields', {})
            summary = fields.get('summary', 'No summary')
            status = fields.get('status', {}).get('name', 'Unknown')
            issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
            report += f"- **{issue.get('key')}**: {summary} ({issue_type}, {status})\n"
            
        # Recommendations
        report += "\n## Recommendations\n"
        
        if len(bugs) > len(stories):
            report += "- ⚠️  High bug count detected. Consider focusing on bug fixes.\n"
            
        todo_count = status_counts.get('To Do', 0)
        in_progress_count = status_counts.get('In Progress', 0)
        
        if in_progress_count > todo_count * 2:
            report += "- ⚠️  Many issues in progress. Consider limiting WIP.\n"
            
        if len(epics) > 0:
            epic_completion = status_counts.get('Done', 0) / len(epics) * 100
            report += f"- 📈 Epic completion rate: {epic_completion:.1f}%\n"
            
        report += f"\n## Next Steps\n"
        report += "- Review and prioritize backlog items\n"
        report += "- Ensure proper story point estimation\n"
        report += "- Monitor velocity and team capacity\n"
        report += "- Update project documentation\n"
        
        # Save report if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"✅ Report saved to: {output_file}")
            
        return report

def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description="DexAgent Project Manager")
    parser.add_argument('--config', help="Configuration file path")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create from template
    template_parser = subparsers.add_parser('create-from-template', help='Create issue from template')
    template_parser.add_argument('--template', required=True, help='Template name')
    template_parser.add_argument('--summary', help='Issue summary')
    template_parser.add_argument('--epic-key', help='Epic key to link to')
    template_parser.add_argument('--assignee', help='Assignee email')
    
    # Create feature
    feature_parser = subparsers.add_parser('create-feature', help='Create feature epic with stories')
    feature_parser.add_argument('--name', required=True, help='Feature name')
    feature_parser.add_argument('--description', required=True, help='Feature description')
    
    # Create sprint
    sprint_parser = subparsers.add_parser('create-sprint', help='Create sprint plan')
    sprint_parser.add_argument('--name', required=True, help='Sprint name')
    sprint_parser.add_argument('--duration', type=int, default=14, help='Sprint duration in days')
    
    # Create release
    release_parser = subparsers.add_parser('create-release', help='Create release plan')
    release_parser.add_argument('--version', required=True, help='Release version')
    release_parser.add_argument('--date', required=True, help='Release date (YYYY-MM-DD)')
    
    # Project report
    report_parser = subparsers.add_parser('project-report', help='Generate project report')
    report_parser.add_argument('--output', help='Output file path')
    
    # List templates
    subparsers.add_parser('list-templates', help='List available templates')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    try:
        pm = ProjectManager(args.config)
        
        if args.command == 'create-from-template':
            issue_key = pm.create_from_template(
                args.template,
                summary=args.summary,
                epic_key=args.epic_key,
                assignee=args.assignee
            )
            if issue_key:
                print(f"✅ Created issue: {issue_key}")
                
        elif args.command == 'create-feature':
            result = pm.create_feature_epic_with_stories(args.name, args.description)
            print(f"✅ Created feature with {len(result)} issues")
            for issue_type, issue_key in result.items():
                print(f"   {issue_type}: {issue_key}")
                
        elif args.command == 'create-sprint':
            result = pm.create_sprint_plan(args.name, args.duration)
            print(f"✅ Created sprint plan: {result['epic_key']}")
            
        elif args.command == 'create-release':
            result = pm.create_release_plan(args.version, args.date)
            print(f"✅ Created release plan: {result['epic_key']}")
            
        elif args.command == 'project-report':
            report = pm.generate_project_report(args.output)
            if not args.output:
                print(report)
                
        elif args.command == 'list-templates':
            if 'templates' in pm.templates:
                print("📋 Available templates:")
                for name, template in pm.templates['templates'].items():
                    print(f"   {name}: {template['name']}")
            else:
                print("❌ No templates found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()