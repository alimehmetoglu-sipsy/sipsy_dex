#!/usr/bin/env python3
"""
Git-Jira Integration Hooks
Provides automated Jira updates based on Git commits and branches
"""

import re
import subprocess
import sys
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import tempfile

# Import our Jira integration
try:
    from jira_integration import JiraIntegration
except ImportError:
    print("❌ jira_integration module not found. Please ensure it's in the same directory.")
    sys.exit(1)

class GitJiraHooks:
    """Git hooks integration with Jira"""
    
    def __init__(self):
        self.jira = JiraIntegration()
        self.issue_pattern = re.compile(r'\b([A-Z]+-\d+)\b')
        
    def extract_issue_keys(self, text: str) -> List[str]:
        """Extract Jira issue keys from text"""
        matches = self.issue_pattern.findall(text)
        return list(set(matches))  # Remove duplicates
        
    def get_current_branch(self) -> str:
        """Get current Git branch name"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
            
    def get_commit_message(self, commit_hash: str) -> str:
        """Get commit message for a specific commit"""
        try:
            result = subprocess.run(
                ['git', 'log', '--format=%B', '-n', '1', commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
            
    def get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit"""
        try:
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            return []
            
    def get_commit_stats(self, commit_hash: str) -> Dict[str, int]:
        """Get commit statistics (additions, deletions)"""
        try:
            result = subprocess.run(
                ['git', 'show', '--stat', '--format=', commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            
            stats = {'files': 0, 'insertions': 0, 'deletions': 0}
            
            # Parse git stat output
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'file' in line and 'changed' in line:
                    # Extract numbers from summary line
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        stats['files'] = int(numbers[0])
                        if len(numbers) > 1:
                            stats['insertions'] = int(numbers[1])
                        if len(numbers) > 2:
                            stats['deletions'] = int(numbers[2])
                            
            return stats
        except subprocess.CalledProcessError:
            return {'files': 0, 'insertions': 0, 'deletions': 0}
            
    def format_commit_comment(self, commit_hash: str, commit_message: str, 
                            files: List[str], stats: Dict[str, int]) -> str:
        """Format commit information as Jira comment"""
        
        short_hash = commit_hash[:8]
        
        comment = f"""
🔄 **Git Commit: {short_hash}**

**Commit Message:**
{commit_message}

**Statistics:**
- Files changed: {stats['files']}
- Lines added: {stats['insertions']}
- Lines deleted: {stats['deletions']}

**Files Modified:**
"""
        
        # Limit to first 10 files to avoid overly long comments
        display_files = files[:10]
        for file_path in display_files:
            comment += f"- `{file_path}`\n"
            
        if len(files) > 10:
            comment += f"... and {len(files) - 10} more files\n"
            
        comment += f"\n*Automatically generated from Git commit {commit_hash}*"
        
        return comment.strip()
        
    def post_commit_hook(self, commit_hash: str) -> bool:
        """Post-commit hook to update Jira issues"""
        
        print(f"🔄 Processing commit {commit_hash[:8]}...")
        
        # Get commit information
        commit_message = self.get_commit_message(commit_hash)
        if not commit_message:
            print("❌ Could not get commit message")
            return False
            
        # Extract issue keys from commit message
        issue_keys = self.extract_issue_keys(commit_message)
        
        if not issue_keys:
            print("ℹ️  No Jira issue keys found in commit message")
            return True
            
        # Get commit details
        files = self.get_commit_files(commit_hash)
        stats = self.get_commit_stats(commit_hash)
        
        # Update each referenced issue
        success = True
        for issue_key in issue_keys:
            try:
                print(f"📝 Updating issue {issue_key}...")
                
                # Format comment
                comment = self.format_commit_comment(commit_hash, commit_message, files, stats)
                
                # Add comment to issue
                if self.jira.add_comment(issue_key, comment):
                    print(f"✅ Updated {issue_key}")
                    
                    # Try to transition to "In Progress" if it's in "To Do"
                    issue = self.jira.get_issue(issue_key)
                    if issue:
                        status = issue.get('fields', {}).get('status', {}).get('name', '')
                        if status.lower() in ['to do', 'todo', 'open']:
                            if self.jira.transition_issue(issue_key, 'In Progress'):
                                print(f"🔄 Moved {issue_key} to 'In Progress'")
                else:
                    print(f"❌ Failed to update {issue_key}")
                    success = False
                    
            except Exception as e:
                print(f"❌ Error updating {issue_key}: {e}")
                success = False
                
        return success
        
    def pre_commit_hook(self, commit_message: str) -> bool:
        """Pre-commit hook to validate commit message"""
        
        # Extract issue keys
        issue_keys = self.extract_issue_keys(commit_message)
        
        if not issue_keys:
            print("⚠️  Warning: No Jira issue keys found in commit message")
            print("   Consider including issue keys like 'DX-123' in your commit message")
            return True  # Allow commit but warn
            
        # Validate that referenced issues exist
        for issue_key in issue_keys:
            try:
                issue = self.jira.get_issue(issue_key)
                if not issue:
                    print(f"❌ Issue {issue_key} not found in Jira")
                    return False
                    
                # Check if issue is in a valid state for commits
                status = issue.get('fields', {}).get('status', {}).get('name', '')
                if status.lower() in ['done', 'closed', 'resolved']:
                    print(f"⚠️  Warning: Issue {issue_key} is already {status}")
                    
            except Exception as e:
                print(f"❌ Error validating {issue_key}: {e}")
                return False
                
        print(f"✅ Validated {len(issue_keys)} issue(s): {', '.join(issue_keys)}")
        return True
        
    def branch_hook(self, branch_name: str, action: str) -> bool:
        """Handle branch creation/switching"""
        
        # Extract issue key from branch name (e.g., feature/DX-123-description)
        issue_keys = self.extract_issue_keys(branch_name)
        
        if not issue_keys:
            return True  # No issue referenced, that's fine
            
        issue_key = issue_keys[0]  # Use first found issue
        
        try:
            if action == 'create':
                comment = f"🌿 **Branch Created**: `{branch_name}`\n\nDevelopment branch created for this issue."
                self.jira.add_comment(issue_key, comment)
                
                # Try to move to In Progress
                self.jira.transition_issue(issue_key, 'In Progress')
                print(f"✅ Updated {issue_key} for branch creation")
                
            elif action == 'delete':
                comment = f"🗑️  **Branch Deleted**: `{branch_name}`\n\nDevelopment branch has been deleted."
                self.jira.add_comment(issue_key, comment)
                print(f"✅ Updated {issue_key} for branch deletion")
                
            return True
            
        except Exception as e:
            print(f"❌ Error updating {issue_key} for branch {action}: {e}")
            return False
            
    def pull_request_hook(self, pr_title: str, pr_description: str, 
                         pr_url: str, action: str) -> bool:
        """Handle pull request events"""
        
        # Extract issue keys from PR title and description
        issue_keys = self.extract_issue_keys(pr_title + " " + pr_description)
        
        if not issue_keys:
            return True
            
        try:
            for issue_key in issue_keys:
                if action == 'opened':
                    comment = f"""
🔀 **Pull Request Opened**

**Title:** {pr_title}
**URL:** {pr_url}

**Description:**
{pr_description}

*Ready for review*
"""
                elif action == 'merged':
                    comment = f"""
✅ **Pull Request Merged**

**Title:** {pr_title}
**URL:** {pr_url}

*Changes have been merged to main branch*
"""
                    # Try to move to Done
                    self.jira.transition_issue(issue_key, 'Done')
                    
                elif action == 'closed':
                    comment = f"""
❌ **Pull Request Closed**

**Title:** {pr_title}
**URL:** {pr_url}

*Pull request was closed without merging*
"""
                
                self.jira.add_comment(issue_key, comment)
                print(f"✅ Updated {issue_key} for PR {action}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error updating issues for PR {action}: {e}")
            return False

def install_git_hooks():
    """Install Git hooks in the current repository"""
    
    git_dir = Path('.git')
    if not git_dir.exists():
        print("❌ Not a Git repository")
        return False
        
    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    script_path = Path(__file__).absolute()
    
    # Pre-commit hook
    pre_commit_hook = hooks_dir / 'pre-commit'
    pre_commit_content = f"""#!/bin/bash
# DexAgent Jira Integration Pre-commit Hook

# Get staged commit message if available
if [ -f .git/COMMIT_EDITMSG ]; then
    COMMIT_MSG=$(cat .git/COMMIT_EDITMSG)
else
    COMMIT_MSG=""
fi

# Run pre-commit validation
python3 "{script_path}" pre-commit "$COMMIT_MSG"
exit $?
"""
    
    with open(pre_commit_hook, 'w') as f:
        f.write(pre_commit_content)
    pre_commit_hook.chmod(0o755)
    
    # Post-commit hook
    post_commit_hook = hooks_dir / 'post-commit'
    post_commit_content = f"""#!/bin/bash
# DexAgent Jira Integration Post-commit Hook

# Get the commit hash
COMMIT_HASH=$(git rev-parse HEAD)

# Run post-commit processing
python3 "{script_path}" post-commit "$COMMIT_HASH"
"""
    
    with open(post_commit_hook, 'w') as f:
        f.write(post_commit_content)
    post_commit_hook.chmod(0o755)
    
    print("✅ Git hooks installed successfully")
    print(f"   Pre-commit: {pre_commit_hook}")
    print(f"   Post-commit: {post_commit_hook}")
    
    return True

def main():
    """Main CLI interface"""
    
    if len(sys.argv) < 2:
        print("Usage: git_jira_hooks.py <command> [args...]")
        print("Commands:")
        print("  install-hooks          Install Git hooks")
        print("  pre-commit <message>   Pre-commit validation")
        print("  post-commit <hash>     Post-commit processing")
        print("  branch-create <name>   Handle branch creation")
        print("  branch-delete <name>   Handle branch deletion")
        print("  pr-opened <title> <description> <url>")
        print("  pr-merged <title> <description> <url>")
        print("  pr-closed <title> <description> <url>")
        return
        
    command = sys.argv[1]
    hooks = GitJiraHooks()
    
    try:
        if command == 'install-hooks':
            install_git_hooks()
            
        elif command == 'pre-commit':
            commit_message = sys.argv[2] if len(sys.argv) > 2 else ""
            if not hooks.pre_commit_hook(commit_message):
                sys.exit(1)
                
        elif command == 'post-commit':
            if len(sys.argv) < 3:
                print("❌ Commit hash required")
                sys.exit(1)
            commit_hash = sys.argv[2]
            if not hooks.post_commit_hook(commit_hash):
                sys.exit(1)
                
        elif command == 'branch-create':
            if len(sys.argv) < 3:
                print("❌ Branch name required")
                sys.exit(1)
            branch_name = sys.argv[2]
            if not hooks.branch_hook(branch_name, 'create'):
                sys.exit(1)
                
        elif command == 'branch-delete':
            if len(sys.argv) < 3:
                print("❌ Branch name required")
                sys.exit(1)
            branch_name = sys.argv[2]
            if not hooks.branch_hook(branch_name, 'delete'):
                sys.exit(1)
                
        elif command in ['pr-opened', 'pr-merged', 'pr-closed']:
            if len(sys.argv) < 5:
                print("❌ PR title, description, and URL required")
                sys.exit(1)
            pr_title = sys.argv[2]
            pr_description = sys.argv[3]
            pr_url = sys.argv[4]
            action = command.split('-')[1]
            if not hooks.pull_request_hook(pr_title, pr_description, pr_url, action):
                sys.exit(1)
                
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()