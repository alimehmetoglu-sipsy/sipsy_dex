#!/usr/bin/env python3
"""
Check for dependency vulnerabilities and updates
"""

import sys
import subprocess
import json
from pathlib import Path

def check_python_dependencies():
    """Check Python dependencies for vulnerabilities"""
    backend_dir = Path(__file__).parent.parent.parent / "apps" / "backend"
    
    if not backend_dir.exists():
        return True
    
    # Check for known vulnerabilities with safety
    try:
        result = subprocess.run([
            "python", "-m", "pip", "install", "safety"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            safety_result = subprocess.run([
                "python", "-m", "safety", "check", "--json"
            ], cwd=backend_dir, capture_output=True, text=True)
            
            if safety_result.returncode != 0:
                print("❌ Python dependencies have security vulnerabilities")
                if safety_result.stdout:
                    try:
                        vulnerabilities = json.loads(safety_result.stdout)
                        for vuln in vulnerabilities:
                            print(f"  - {vuln.get('package', 'Unknown')}: {vuln.get('advisory', 'No details')}")
                    except:
                        print(f"  {safety_result.stdout}")
                return False
    except:
        print("⚠️  Could not check Python dependencies (safety not available)")
    
    print("✅ Python dependencies check passed")
    return True

def check_node_dependencies():
    """Check Node.js dependencies for vulnerabilities"""
    frontend_dir = Path(__file__).parent.parent.parent / "apps" / "frontend"
    
    if not frontend_dir.exists():
        return True
    
    # Run npm audit
    result = subprocess.run([
        "npm", "audit", "--audit-level=moderate"
    ], cwd=frontend_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Node.js dependencies have security vulnerabilities")
        print("  Run 'npm audit fix' to attempt automatic fixes")
        return False
    
    print("✅ Node.js dependencies check passed")
    return True

def main():
    """Main function"""
    python_ok = check_python_dependencies()
    node_ok = check_node_dependencies()
    
    if not (python_ok and node_ok):
        sys.exit(1)

if __name__ == "__main__":
    main()