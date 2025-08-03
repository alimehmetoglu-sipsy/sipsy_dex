# DexAgent Project Management Integration

Comprehensive project management integration with Atlassian Jira for tracking, planning, and workflow automation.

## Overview

The DexAgent project management system provides:

- **Jira Integration**: Complete API integration with Atlassian Jira
- **Git Workflow Integration**: Automatic issue updates from Git commits
- **Project Templates**: Pre-built templates for common issue types
- **Automation Scripts**: Advanced project management automation
- **Reporting**: Comprehensive project metrics and reports

## Quick Start

### 1. Setup Jira Integration

#### Prerequisites
- Atlassian Jira account with API access
- Project admin permissions for issue creation
- API token generated from Atlassian account

#### Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure Jira credentials** in `.env`:
   ```bash
   # Jira Integration Configuration
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your-jira-api-token
   JIRA_PROJECT_KEY=DX
   ```

3. **Get Jira API Token**:
   - Go to [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Copy the token to your `.env` file

4. **Test connection**:
   ```bash
   python tools/scripts/jira_integration.py test
   ```

### 2. Install Git Hooks

Enable automatic Jira updates from Git commits:

```bash
python tools/scripts/git_jira_hooks.py install-hooks
```

This installs:
- **Pre-commit hook**: Validates referenced Jira issues
- **Post-commit hook**: Automatically updates Jira with commit details

### 3. Basic Usage

#### Create Issues
```bash
# Create from template
python tools/scripts/project_manager.py create-from-template --template feature_story

# Create feature epic with stories
python tools/scripts/project_manager.py create-feature --name "User Authentication" --description "Implement user login and registration"

# Create sprint plan
python tools/scripts/project_manager.py create-sprint --name "Sprint 2024-01" --duration 14
```

#### Generate Reports
```bash
# Project status report
python tools/scripts/project_manager.py project-report --output reports/project_status.md

# Sprint report
python tools/scripts/jira_integration.py report --output reports/sprint_report.md
```

## Jira Integration Features

### Core Functionality

The `jira_integration.py` script provides comprehensive Jira operations:

#### Issue Management
```bash
# Test connection
python tools/scripts/jira_integration.py test

# Get project info
python tools/scripts/jira_integration.py info

# Create epic
python tools/scripts/jira_integration.py create-epic \
  --summary "Feature: Advanced Reporting" \
  --description "Implement advanced reporting capabilities" \
  --name "Advanced Reporting Epic"

# Create story
python tools/scripts/jira_integration.py create-story \
  --summary "User Dashboard Widgets" \
  --description "Implement configurable dashboard widgets" \
  --epic DX-123 \
  --points 5

# Create task
python tools/scripts/jira_integration.py create-task \
  --summary "Update API Documentation" \
  --description "Update API docs for new endpoints" \
  --epic DX-123 \
  --labels documentation api
```

#### Issue Operations
```bash
# Transition issue status
python tools/scripts/jira_integration.py transition --issue DX-123 --status "In Progress"

# Add comment
python tools/scripts/jira_integration.py comment --issue DX-123 --message "Work in progress"

# Search issues
python tools/scripts/jira_integration.py search --jql "project = DX AND status = 'To Do'"

# List project issues
python tools/scripts/jira_integration.py list --status "In Progress"
```

#### Development Workflows
```bash
# Create development epic for current sprint
python tools/scripts/jira_integration.py create-dev-epic

# Create standard development stories
python tools/scripts/jira_integration.py create-dev-stories --epic DX-124
```

### Git Integration Features

The `git_jira_hooks.py` script provides seamless Git-Jira integration:

#### Automatic Issue Updates

When you commit with Jira issue keys in the message:

```bash
git commit -m "DX-123: Implement user authentication API

- Add JWT token generation
- Implement password hashing
- Create user registration endpoint"
```

The system automatically:
- ✅ Validates that DX-123 exists in Jira
- 📝 Adds commit details as a comment to DX-123
- 🔄 Transitions issue to "In Progress" if in "To Do"
- 📊 Includes file changes and statistics

#### Branch Management

```bash
# Create feature branch (updates linked issue)
git checkout -b feature/DX-123-user-auth

# The system automatically:
# - Finds DX-123 from branch name
# - Adds comment about branch creation
# - Moves issue to "In Progress"
```

#### Pull Request Integration

```bash
# Manually trigger PR updates
python tools/scripts/git_jira_hooks.py pr-opened \
  "DX-123: User Authentication" \
  "Implements JWT-based user authentication" \
  "https://github.com/company/repo/pull/42"
```

## Project Templates

### Available Templates

The system includes pre-built templates for common scenarios:

#### 1. Feature Story Template
```bash
python tools/scripts/project_manager.py create-from-template --template feature_story
```

**Includes**:
- User story format
- Acceptance criteria checklist
- Technical requirements
- Definition of done
- Dependencies tracking

#### 2. Bug Report Template
```bash
python tools/scripts/project_manager.py create-from-template --template bug_report
```

**Includes**:
- Environment details
- Reproduction steps
- Expected vs actual behavior
- Screenshots/logs section
- Impact assessment

#### 3. Epic Template
```bash
python tools/scripts/project_manager.py create-from-template --template epic
```

**Includes**:
- Vision and business value
- Scope definition
- Success metrics
- Technical approach
- Risk assessment
- Timeline and milestones

#### 4. Security Review Template
```bash
python tools/scripts/project_manager.py create-from-template --template security_review
```

**Includes**:
- Security scope and requirements
- Threat model
- Security testing checklist
- Compliance requirements
- Remediation plan

#### 5. Performance Optimization Template
```bash
python tools/scripts/project_manager.py create-from-template --template performance_optimization
```

**Includes**:
- Performance baseline and targets
- Optimization solutions
- Testing strategy
- Monitoring metrics

### Custom Templates

Create custom templates by editing `tools/templates/jira_issue_templates.json`:

```json
{
  "templates": {
    "custom_template": {
      "name": "Custom Template",
      "issuetype": "Story",
      "priority": "Medium",
      "description_template": "# Custom Issue: {{title}}\n\n## Description\n{{description}}\n\n## Requirements\n- {{requirement_1}}\n- {{requirement_2}}",
      "fields": {
        "story_points": 3,
        "labels": ["custom", "template"]
      }
    }
  }
}
```

## Advanced Project Management

### Sprint Planning

Create comprehensive sprint plans:

```bash
python tools/scripts/project_manager.py create-sprint \
  --name "Sprint 2024-Q1-01" \
  --duration 14
```

**Creates**:
- Sprint epic with goals and timeline
- Sprint ceremony tasks (planning, standups, review, retrospective)
- Definition of done checklist
- Sprint metrics tracking

### Release Planning

Organize releases with proper structure:

```bash
python tools/scripts/project_manager.py create-release \
  --version "2.1.0" \
  --date "2024-03-15"
```

**Creates**:
- Release epic with scope and criteria
- Release milestone tasks
- Testing and deployment checklists
- Communication and rollback plans

### Feature Development

Complete feature planning with standard structure:

```bash
python tools/scripts/project_manager.py create-feature \
  --name "Real-time Notifications" \
  --description "Implement real-time notification system for users"
```

**Creates**:
- Feature epic with vision and scope
- Standard development stories:
  - Backend API Implementation (8 points)
  - Frontend Components Development (5 points)
  - Database Schema Updates (3 points)
  - Integration Testing (3 points)
  - User Documentation (2 points)

## Project Reporting

### Automated Reports

Generate comprehensive project insights:

```bash
# Full project report
python tools/scripts/project_manager.py project-report \
  --output reports/project_status_$(date +%Y%m%d).md

# Sprint-specific report
python tools/scripts/jira_integration.py report \
  --output reports/sprint_report.md
```

### Report Contents

#### Project Status Report
- **Issue Distribution**: Breakdown by type, status, priority
- **Epic Progress**: Status of all active epics
- **Recent Activity**: Latest issues and updates
- **Recommendations**: Data-driven improvement suggestions
- **Next Steps**: Actionable items for project health

#### Sprint Report
- **Sprint Metrics**: Velocity, completion rates, story points
- **Issue Analysis**: Status distribution and priority breakdown
- **Team Performance**: Individual and team contributions
- **Sprint Goals**: Progress against objectives

### Custom Reporting

Create custom reports using the Jira API:

```python
from tools.scripts.jira_integration import JiraIntegration

jira = JiraIntegration()

# Custom JQL queries
issues = jira.search_issues("project = DX AND created >= -7d")

# Custom analysis
for issue in issues:
    # Process issue data
    pass
```

## Workflow Automation

### Commit-based Automation

When commits reference Jira issues:

1. **Pre-commit Validation**:
   - Validates issue exists
   - Checks issue status
   - Warns about closed issues

2. **Post-commit Updates**:
   - Adds commit details to issue
   - Updates issue status
   - Links to code changes

### Branch-based Automation

When working with feature branches:

1. **Branch Creation**:
   - Extracts issue key from branch name
   - Updates issue with branch info
   - Transitions to "In Progress"

2. **Branch Deletion**:
   - Adds cleanup notification
   - Updates issue history

### Pull Request Integration

For PR workflows:

1. **PR Creation**:
   - Links PR to issues
   - Adds PR details to issues
   - Marks for review

2. **PR Merge**:
   - Transitions issues to "Done"
   - Records completion
   - Triggers release processes

## Best Practices

### Issue Management

1. **Consistent Naming**:
   ```
   DX-123: Feature description
   DX-124: Fix bug in component
   DX-125: Improve performance of API
   ```

2. **Proper Estimation**:
   - Use story points consistently
   - Estimate based on complexity, not time
   - Re-estimate when scope changes

3. **Clear Descriptions**:
   - Use templates for consistency
   - Include acceptance criteria
   - Link related issues

### Git Integration

1. **Commit Messages**:
   ```bash
   # Good
   git commit -m "DX-123: Implement user authentication

   - Add JWT token generation
   - Implement password hashing
   - Create user registration endpoint"

   # Bad
   git commit -m "fix auth"
   ```

2. **Branch Naming**:
   ```bash
   # Good
   feature/DX-123-user-authentication
   bugfix/DX-124-login-validation
   hotfix/DX-125-security-patch

   # Bad
   my-feature
   fix-bug
   ```

### Project Planning

1. **Epic Structure**:
   - Clear vision and scope
   - Measurable success criteria
   - Realistic timelines
   - Proper dependencies

2. **Sprint Planning**:
   - Consistent sprint duration
   - Realistic capacity planning
   - Clear sprint goals
   - Regular retrospectives

3. **Release Management**:
   - Version numbering strategy
   - Release criteria
   - Testing requirements
   - Rollback procedures

## Troubleshooting

### Common Issues

#### Jira Connection Problems

```bash
# Test connection
python tools/scripts/jira_integration.py test

# Check credentials
echo $JIRA_EMAIL
echo $JIRA_API_TOKEN
echo $JIRA_URL
```

**Solutions**:
- Verify API token is correct and not expired
- Check email address matches Jira account
- Ensure Jira URL includes protocol (https://)
- Verify project key exists and you have access

#### Git Hook Issues

```bash
# Check if hooks are installed
ls -la .git/hooks/

# Reinstall hooks
python tools/scripts/git_jira_hooks.py install-hooks

# Test pre-commit hook
python tools/scripts/git_jira_hooks.py pre-commit "DX-123: Test commit"
```

**Solutions**:
- Ensure hooks have execute permissions
- Check Python path in hook scripts
- Verify Git repository is initialized
- Test Jira integration separately

#### Template Problems

```bash
# List available templates
python tools/scripts/project_manager.py list-templates

# Check template file
cat tools/templates/jira_issue_templates.json | jq .
```

**Solutions**:
- Validate JSON syntax in template file
- Check template variable names
- Ensure required fields are present
- Test with simple template first

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Set debug environment
export DEBUG=true

# Run with verbose output
python tools/scripts/jira_integration.py test -v
```

## Integration with CI/CD

### GitHub Actions

Add Jira updates to your CI/CD pipeline:

```yaml
# .github/workflows/jira-integration.yml
name: Jira Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    types: [opened, closed]

jobs:
  update-jira:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install requests
        
      - name: Update Jira on PR
        if: github.event_name == 'pull_request'
        env:
          JIRA_EMAIL: ${{ secrets.JIRA_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_PROJECT_KEY: DX
        run: |
          python tools/scripts/git_jira_hooks.py pr-${{ github.event.action }} \
            "${{ github.event.pull_request.title }}" \
            "${{ github.event.pull_request.body }}" \
            "${{ github.event.pull_request.html_url }}"
```

### Pre-commit Configuration

Add Jira validation to pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: jira-validation
        name: Validate Jira Issue References
        entry: python tools/scripts/git_jira_hooks.py pre-commit
        language: system
        stages: [commit-msg]
```

## Support and Maintenance

### Regular Maintenance

1. **Update Templates**: Review and update issue templates quarterly
2. **Clean Old Issues**: Archive completed issues older than 6 months
3. **Review Automation**: Check automation rules and update as needed
4. **Update Documentation**: Keep project management docs current

### Monitoring

Track project management metrics:

```bash
# Weekly project report
python tools/scripts/project_manager.py project-report \
  --output reports/weekly_$(date +%Y%W).md

# Sprint velocity tracking
python tools/scripts/jira_integration.py search \
  --jql "project = DX AND updated >= -7d" \
  --max-results 100
```

### Support Contacts

For issues with project management integration:

1. **Technical Issues**: Check this documentation and troubleshooting section
2. **Jira Administration**: Contact your Jira administrator
3. **Process Questions**: Review team project management guidelines
4. **Feature Requests**: Create enhancement requests in Jira

## License

This project management integration is part of the DexAgent project and follows the same license terms.