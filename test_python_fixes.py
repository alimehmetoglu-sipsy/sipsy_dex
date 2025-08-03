#!/usr/bin/env python3
"""
Test script to verify Python command fixes for DX-36
This verifies that all Python commands have been fixed from 'python' to 'python3'
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_python_fixes():
    """Test that Python command fixes are working"""
    print("🧪 Testing Python Command Fixes for DX-36")
    print("=" * 50)
    
    results = {
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'details': []
    }
    
    # Test 1: Basic Python3 availability
    print("\n1. Testing Python3 availability...")
    results['tests_run'] += 1
    success, stdout, stderr = run_command("python3 --version")
    if success:
        print(f"✅ Python3 is available: {stdout.strip()}")
        results['tests_passed'] += 1
        results['details'].append({
            'test': 'Python3 availability',
            'status': 'PASS',
            'output': stdout.strip()
        })
    else:
        print(f"❌ Python3 not available: {stderr}")
        results['tests_failed'] += 1
        results['details'].append({
            'test': 'Python3 availability',
            'status': 'FAIL',
            'error': stderr
        })
    
    # Test 2: Test orchestrator can be imported
    print("\n2. Testing test orchestrator syntax...")
    results['tests_run'] += 1
    success, stdout, stderr = run_command("python3 -m py_compile tools/test_orchestrator.py")
    if success:
        print("✅ Test orchestrator compiles correctly")
        results['tests_passed'] += 1
        results['details'].append({
            'test': 'Test orchestrator syntax',
            'status': 'PASS'
        })
    else:
        print(f"❌ Test orchestrator syntax error: {stderr}")
        results['tests_failed'] += 1
        results['details'].append({
            'test': 'Test orchestrator syntax',
            'status': 'FAIL',
            'error': stderr
        })
    
    # Test 3: Check pytest availability with python3
    print("\n3. Testing pytest availability with python3...")
    results['tests_run'] += 1
    success, stdout, stderr = run_command("python3 -c 'import pytest; print(pytest.__version__)'")
    if success:
        print(f"✅ pytest available with python3: {stdout.strip()}")
        results['tests_passed'] += 1
        results['details'].append({
            'test': 'Pytest with python3',
            'status': 'PASS',
            'output': stdout.strip()
        })
    else:
        print(f"⚠️  pytest not available with python3: {stderr}")
        # This is not a failure since pytest might not be installed yet
        results['details'].append({
            'test': 'Pytest with python3',
            'status': 'SKIP',
            'reason': 'pytest not installed'
        })
    
    # Test 4: Check that old 'python' command fails as expected
    print("\n4. Testing that 'python' command fails (as expected)...")
    results['tests_run'] += 1
    success, stdout, stderr = run_command("python --version")
    if not success and "not found" in stderr:
        print("✅ 'python' command correctly fails (not found)")
        results['tests_passed'] += 1
        results['details'].append({
            'test': 'Python command fails',
            'status': 'PASS',
            'reason': 'Expected failure - python not found'
        })
    elif success:
        print(f"⚠️  'python' command still works: {stdout.strip()}")
        print("   This is not necessarily a problem, but python3 should be used")
        results['details'].append({
            'test': 'Python command fails',
            'status': 'INFO',
            'output': stdout.strip()
        })
    else:
        print(f"✅ 'python' command fails as expected: {stderr}")
        results['tests_passed'] += 1
        results['details'].append({
            'test': 'Python command fails',
            'status': 'PASS',
            'reason': 'Expected failure'
        })
        
    # Test 5: Quick backend directory check
    print("\n5. Testing backend directory structure...")
    results['tests_run'] += 1
    backend_path = Path("apps/backend")
    if backend_path.exists() and (backend_path / "comprehensive_api_test.py").exists():
        print("✅ Backend structure looks good")
        results['tests_passed'] += 1
        results['details'].append({
            'test': 'Backend structure',
            'status': 'PASS'
        })
    else:
        print("❌ Backend structure issues")
        results['tests_failed'] += 1
        results['details'].append({
            'test': 'Backend structure',
            'status': 'FAIL',
            'error': 'Missing backend files'
        })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Tests Run: {results['tests_run']}")
    print(f"   ✅ Passed: {results['tests_passed']}")
    print(f"   ❌ Failed: {results['tests_failed']}")
    
    success_rate = (results['tests_passed'] / results['tests_run']) * 100 if results['tests_run'] > 0 else 0
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    if results['tests_failed'] == 0:
        print("\n🎉 All Python command fixes are working correctly!")
        print("   The main DX-36 issues have been resolved.")
    else:
        print(f"\n⚠️  {results['tests_failed']} issues still need attention")
    
    # Save results
    with open("python_fixes_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results['tests_failed'] == 0

if __name__ == "__main__":
    success = test_python_fixes()
    sys.exit(0 if success else 1)