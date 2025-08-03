#!/usr/bin/env python3
"""
DexAgents Frontend Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False

def check_npm_installed():
    """Check if npm is installed"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm found: {result.stdout.strip()}")
            return True
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not installed")
        return False

def install_dependencies():
    """Install npm dependencies"""
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def start_frontend():
    """Start the Next.js frontend"""
    print("🚀 Starting DexAgents Frontend...")
    
    # Check if package.json exists
    if not Path("package.json").exists():
        print("❌ package.json not found in current directory")
        return False
    
    # Start development server
    cmd = ["npm", "run", "dev"]
    
    try:
        print("🌐 Frontend starting on http://localhost:3000")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🔧 DexAgents Frontend Setup")
    print("=" * 40)
    
    # Check Node.js and npm
    if not check_node_installed():
        print("❌ Please install Node.js from https://nodejs.org/")
        sys.exit(1)
    
    if not check_npm_installed():
        print("❌ Please install npm")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start frontend
    if not start_frontend():
        sys.exit(1)

if __name__ == "__main__":
    main() 