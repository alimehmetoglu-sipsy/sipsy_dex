#!/usr/bin/env python3
"""
Check test coverage and enforce minimum thresholds
"""

import sys
import json
import subprocess
from pathlib import Path

def check_python_coverage():
    """Check Python test coverage"""
    backend_dir = Path(__file__).parent.parent.parent / "apps" / "backend"
    
    if not backend_dir.exists():
        return True
    
    # Run coverage
    result = subprocess.run([
        "python", "-m", "pytest", "--cov=app", "--cov-report=json", "--cov-fail-under=70"
    ], cwd=backend_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Python test coverage below 70%")
        return False
    
    print("✅ Python test coverage passed")
    return True

def check_frontend_coverage():
    """Check frontend test coverage"""
    frontend_dir = Path(__file__).parent.parent.parent / "apps" / "frontend"
    
    if not frontend_dir.exists():
        return True
    
    # Check if jest coverage exists
    coverage_file = frontend_dir / "coverage" / "coverage-summary.json"
    if coverage_file.exists():
        with open(coverage_file) as f:
            coverage_data = json.load(f)
        
        total_coverage = coverage_data.get("total", {}).get("lines", {}).get("pct", 0)
        if total_coverage < 70:
            print(f"❌ Frontend test coverage below 70% (current: {total_coverage}%)")
            return False
        
        print(f"✅ Frontend test coverage passed ({total_coverage}%)")
    
    return True

def main():
    """Main function"""
    python_ok = check_python_coverage()
    frontend_ok = check_frontend_coverage()
    
    if not (python_ok and frontend_ok):
        sys.exit(1)

if __name__ == "__main__":
    main()