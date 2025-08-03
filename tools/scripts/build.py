#!/usr/bin/env python3
"""
DexAgent Build Script
Comprehensive build automation for the DexAgent monorepo
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil
import time

class DexAgentBuilder:
    """Build automation for DexAgent project"""
    
    def __init__(self, root_dir: Optional[str] = None):
        """Initialize builder with project root directory"""
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).parent.parent.parent
        self.apps_dir = self.root_dir / "apps"
        self.packages_dir = self.root_dir / "packages"
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        
    def run_command(self, command: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run shell command with error handling"""
        cwd = cwd or self.root_dir
        print(f"🔄 Running: {' '.join(command)} (in {cwd})")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                print(f"✅ Output: {result.stdout.strip()}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running command: {' '.join(command)}")
            print(f"❌ Exit code: {e.returncode}")
            print(f"❌ Error output: {e.stderr}")
            if check:
                sys.exit(1)
            return e
    
    def clean_build_artifacts(self):
        """Clean all build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        # Clean directories
        for clean_dir in [self.build_dir, self.dist_dir]:
            if clean_dir.exists():
                shutil.rmtree(clean_dir)
                print(f"🗑️  Removed {clean_dir}")
        
        # Clean node_modules
        for node_modules in self.root_dir.glob("**/node_modules"):
            if node_modules.is_dir():
                shutil.rmtree(node_modules)
                print(f"🗑️  Removed {node_modules}")
        
        # Clean Python cache
        for pycache in self.root_dir.glob("**/__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
                print(f"🗑️  Removed {pycache}")
        
        # Clean build artifacts
        patterns = [".next", "dist", "build", "*.egg-info", ".pytest_cache", ".coverage"]
        for pattern in patterns:
            for artifact in self.root_dir.glob(f"**/{pattern}"):
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                elif artifact.is_file():
                    artifact.unlink()
                print(f"🗑️  Removed {artifact}")
        
        print("✅ Clean completed")
    
    def install_dependencies(self):
        """Install all project dependencies"""
        print("📦 Installing dependencies...")
        
        # Install root workspace dependencies
        print("📦 Installing root workspace dependencies...")
        self.run_command(["npm", "install"], self.root_dir)
        
        # Install backend dependencies
        backend_dir = self.apps_dir / "backend"
        if (backend_dir / "requirements.txt").exists():
            print("🐍 Installing backend Python dependencies...")
            self.run_command(["pip", "install", "-r", "requirements.txt"], backend_dir)
        
        # Install frontend dependencies
        frontend_dir = self.apps_dir / "frontend"
        if (frontend_dir / "package.json").exists():
            print("📦 Installing frontend dependencies...")
            self.run_command(["npm", "install"], frontend_dir)
        
        # Install shared packages dependencies
        for package_dir in self.packages_dir.glob("*/"):
            if (package_dir / "package.json").exists():
                print(f"📦 Installing {package_dir.name} dependencies...")
                self.run_command(["npm", "install"], package_dir)
        
        print("✅ Dependencies installed")
    
    def build_packages(self):
        """Build shared packages"""
        print("🔨 Building shared packages...")
        
        package_order = ["shared-constants", "shared-types", "shared-utils", "shared-components"]
        
        for package_name in package_order:
            package_dir = self.packages_dir / package_name
            if package_dir.exists() and (package_dir / "package.json").exists():
                print(f"🔨 Building {package_name}...")
                self.run_command(["npm", "run", "build"], package_dir)
        
        print("✅ Packages built")
    
    def build_backend(self):
        """Build backend application"""
        print("🔨 Building backend...")
        
        backend_dir = self.apps_dir / "backend"
        
        # Run backend tests
        print("🧪 Running backend tests...")
        self.run_command(["python", "-m", "pytest", "tests/", "-v"], backend_dir, check=False)
        
        # Create backend distribution
        print("📦 Creating backend distribution...")
        backend_dist = self.dist_dir / "backend"
        backend_dist.mkdir(parents=True, exist_ok=True)
        
        # Copy backend files (excluding tests and __pycache__)
        for item in backend_dir.iterdir():
            if item.name not in ["tests", "__pycache__", ".pytest_cache"]:
                if item.is_dir():
                    shutil.copytree(item, backend_dist / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, backend_dist / item.name)
        
        print("✅ Backend built")
    
    def build_frontend(self):
        """Build frontend application"""
        print("🔨 Building frontend...")
        
        frontend_dir = self.apps_dir / "frontend"
        
        # Build frontend
        print("🔨 Building Next.js application...")
        self.run_command(["npm", "run", "build"], frontend_dir)
        
        # Create frontend distribution
        frontend_dist = self.dist_dir / "frontend"
        frontend_dist.mkdir(parents=True, exist_ok=True)
        
        # Copy build artifacts
        if (frontend_dir / ".next").exists():
            shutil.copytree(frontend_dir / ".next", frontend_dist / ".next", dirs_exist_ok=True)
        
        if (frontend_dir / "public").exists():
            shutil.copytree(frontend_dir / "public", frontend_dist / "public", dirs_exist_ok=True)
        
        # Copy essential files
        essential_files = ["package.json", "next.config.mjs"]
        for file_name in essential_files:
            src_file = frontend_dir / file_name
            if src_file.exists():
                shutil.copy2(src_file, frontend_dist / file_name)
        
        print("✅ Frontend built")
    
    def build_agent(self):
        """Build Windows agent executable"""
        print("🔨 Building Windows agent...")
        
        agent_dir = self.apps_dir / "agent"
        
        # Build agent executable
        print("🔨 Building agent executable...")
        build_script = agent_dir / "modern_build_exe.py"
        if build_script.exists():
            self.run_command(["python", str(build_script)], agent_dir)
        
        # Copy agent distribution
        agent_dist = self.dist_dir / "agent"
        agent_dist.mkdir(parents=True, exist_ok=True)
        
        # Copy agent files
        if (agent_dir / "dist").exists():
            shutil.copytree(agent_dir / "dist", agent_dist / "dist", dirs_exist_ok=True)
        
        print("✅ Agent built")
    
    def run_linting(self):
        """Run code linting and formatting"""
        print("🔍 Running linting and formatting...")
        
        # Backend linting
        backend_dir = self.apps_dir / "backend"
        print("🐍 Linting Python code...")
        self.run_command(["python", "-m", "flake8", "."], backend_dir, check=False)
        
        # Frontend linting
        frontend_dir = self.apps_dir / "frontend"
        print("📦 Linting TypeScript/JavaScript code...")
        self.run_command(["npm", "run", "lint"], frontend_dir, check=False)
        
        print("✅ Linting completed")
    
    def run_tests(self):
        """Run all tests"""
        print("🧪 Running all tests...")
        
        # Backend tests
        backend_dir = self.apps_dir / "backend"
        print("🐍 Running backend tests...")
        self.run_command(["python", "-m", "pytest", "tests/", "-v", "--cov=app"], backend_dir, check=False)
        
        # Frontend tests
        frontend_dir = self.apps_dir / "frontend"
        print("📦 Running frontend tests...")
        self.run_command(["npm", "run", "test"], frontend_dir, check=False)
        
        print("✅ Tests completed")
    
    def create_docker_images(self):
        """Build Docker images"""
        print("🐳 Building Docker images...")
        
        # Build development images
        print("🐳 Building development images...")
        self.run_command(["docker-compose", "build"], self.root_dir)
        
        # Build production images
        print("🐳 Building production images...")
        self.run_command(["docker-compose", "-f", "docker-compose.prod.yml", "build"], self.root_dir)
        
        print("✅ Docker images built")
    
    def generate_build_info(self):
        """Generate build information"""
        print("📊 Generating build information...")
        
        build_info = {
            "build_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "version": "2.0.0",
            "commit": self._get_git_commit(),
            "branch": self._get_git_branch(),
            "packages": self._get_package_versions(),
            "environment": "production"
        }
        
        # Write build info
        build_info_file = self.dist_dir / "build-info.json"
        build_info_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(build_info_file, 'w') as f:
            json.dump(build_info, f, indent=2)
        
        print(f"📊 Build info written to {build_info_file}")
        print("✅ Build information generated")
    
    def _get_git_commit(self) -> str:
        """Get current Git commit hash"""
        try:
            result = self.run_command(["git", "rev-parse", "HEAD"], check=False)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_git_branch(self) -> str:
        """Get current Git branch"""
        try:
            result = self.run_command(["git", "branch", "--show-current"], check=False)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_package_versions(self) -> Dict[str, str]:
        """Get package versions"""
        versions = {}
        
        # Root package version
        root_package = self.root_dir / "package.json"
        if root_package.exists():
            with open(root_package) as f:
                data = json.load(f)
                versions["root"] = data.get("version", "unknown")
        
        # App versions
        for app_dir in self.apps_dir.glob("*/"):
            package_json = app_dir / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    versions[f"app-{app_dir.name}"] = data.get("version", "unknown")
        
        return versions
    
    def build_all(self, clean: bool = True, test: bool = True, docker: bool = False):
        """Run complete build process"""
        print("🚀 Starting complete build process...")
        start_time = time.time()
        
        try:
            if clean:
                self.clean_build_artifacts()
            
            self.install_dependencies()
            self.build_packages()
            self.build_backend()
            self.build_frontend()
            self.build_agent()
            
            if test:
                self.run_linting()
                self.run_tests()
            
            if docker:
                self.create_docker_images()
            
            self.generate_build_info()
            
            build_time = time.time() - start_time
            print(f"🎉 Build completed successfully in {build_time:.2f} seconds!")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DexAgent Build Script")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts before building")
    parser.add_argument("--no-test", action="store_true", help="Skip running tests")
    parser.add_argument("--docker", action="store_true", help="Build Docker images")
    parser.add_argument("--packages-only", action="store_true", help="Build packages only")
    parser.add_argument("--backend-only", action="store_true", help="Build backend only")
    parser.add_argument("--frontend-only", action="store_true", help="Build frontend only")
    parser.add_argument("--agent-only", action="store_true", help="Build agent only")
    
    args = parser.parse_args()
    
    builder = DexAgentBuilder()
    
    if args.packages_only:
        if args.clean:
            builder.clean_build_artifacts()
        builder.install_dependencies()
        builder.build_packages()
    elif args.backend_only:
        if args.clean:
            builder.clean_build_artifacts()
        builder.install_dependencies()
        builder.build_packages()
        builder.build_backend()
    elif args.frontend_only:
        if args.clean:
            builder.clean_build_artifacts()
        builder.install_dependencies()
        builder.build_packages()
        builder.build_frontend()
    elif args.agent_only:
        if args.clean:
            builder.clean_build_artifacts()
        builder.build_agent()
    else:
        # Full build
        builder.build_all(
            clean=args.clean,
            test=not args.no_test,
            docker=args.docker
        )

if __name__ == "__main__":
    main()