#!/usr/bin/env python3
"""
DexAgent Test Suite Runner - Direct Execution
Alternative way to run comprehensive test suite when Claude Code /test command is not visible
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the comprehensive test suite directly"""
    
    project_root = Path.cwd()
    print(f"🚀 DexAgent Test Suite Runner")
    print(f"📁 Project Root: {project_root}")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not (project_root / "tools" / "test_orchestrator.py").exists():
        print("❌ Error: Not in correct project directory")
        print("Please cd to the sipsy_dex project root directory")
        return 1
    
    # Make orchestrator executable
    orchestrator_path = project_root / "tools" / "test_orchestrator.py"
    subprocess.run(["chmod", "+x", str(orchestrator_path)], check=False)
    
    # Run the test orchestrator
    print("🧪 Launching Test Orchestrator...")
    try:
        result = subprocess.run([
            sys.executable, 
            str(orchestrator_path)
        ], check=False)
        
        if result.returncode == 0:
            print("\n✅ Test suite completed successfully!")
            
            # Check if Jira report was generated
            jira_report = project_root / "jira_report.md"
            if jira_report.exists():
                print("📋 Jira report generated: jira_report.md")
                print("🎯 Results are ready for posting to Jira DX-30")
            
        else:
            print(f"\n⚠️  Test suite completed with issues (exit code: {result.returncode})")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running test suite: {e}")
        return 1

if __name__ == "__main__":
    exit(main())