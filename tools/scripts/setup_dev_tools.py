#!/usr/bin/env python3
"""
Setup Development Tools
Install and configure all development tools and pre-commit hooks
"""

import subprocess
import sys
from pathlib import Path

class DevToolsSetup:
    """Setup development tools and environment"""
    
    def __init__(self):
        """Initialize setup"""
        self.root_dir = Path(__file__).parent.parent.parent
        
    def run_command(self, command: list, cwd: Path = None, check: bool = True):
        """Run shell command"""
        cwd = cwd or self.root_dir
        print(f"🔄 Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)
            if result.stdout:
                print(f"✅ {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stderr:
                print(f"❌ Error output: {e.stderr}")
            if check:
                sys.exit(1)
            return e
    
    def install_python_tools(self):
        """Install Python development tools"""
        print("🐍 Installing Python development tools...")
        
        tools = [
            "black",
            "isort", 
            "flake8",
            "bandit",
            "pytest",
            "pytest-cov",
            "safety",
            "pre-commit"
        ]
        
        for tool in tools:
            self.run_command(["pip", "install", tool], check=False)
        
        print("✅ Python tools installed")
    
    def install_node_tools(self):
        """Install Node.js development tools"""
        print("📦 Installing Node.js development tools...")
        
        frontend_dir = self.root_dir / "apps" / "frontend"
        if not frontend_dir.exists():
            print("⚠️  Frontend directory not found, skipping Node.js tools")
            return
        
        # Install frontend dependencies (includes dev tools)
        self.run_command(["npm", "install"], frontend_dir)
        
        # Global tools
        global_tools = [
            "prettier",
            "eslint",
            "typescript",
            "@typescript-eslint/parser",
            "@typescript-eslint/eslint-plugin"
        ]
        
        for tool in global_tools:
            self.run_command(["npm", "install", "-g", tool], check=False)
        
        print("✅ Node.js tools installed")
    
    def setup_pre_commit(self):
        """Setup pre-commit hooks"""
        print("🔗 Setting up pre-commit hooks...")
        
        # Install pre-commit
        self.run_command(["pip", "install", "pre-commit"], check=False)
        
        # Install hooks
        self.run_command(["pre-commit", "install"])
        self.run_command(["pre-commit", "install", "--hook-type", "commit-msg"])
        
        # Run hooks on all files (optional)
        print("🔄 Running pre-commit on all files (this may take a while)...")
        self.run_command(["pre-commit", "run", "--all-files"], check=False)
        
        print("✅ Pre-commit hooks setup complete")
    
    def setup_git_hooks(self):
        """Setup custom Git hooks"""
        print("🔗 Setting up custom Git hooks...")
        
        # Install Jira integration hooks
        jira_hooks_script = self.root_dir / "tools" / "scripts" / "git_jira_hooks.py"
        if jira_hooks_script.exists():
            self.run_command(["python", str(jira_hooks_script), "install-hooks"])
        
        print("✅ Custom Git hooks setup complete")
    
    def create_vscode_settings(self):
        """Create VS Code settings for the project"""
        print("⚙️  Creating VS Code settings...")
        
        vscode_dir = self.root_dir / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "python.defaultInterpreterPath": "./apps/backend/venv/bin/python",
            "python.formatting.provider": "black",
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.banditEnabled": True,
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["apps/backend/tests"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "typescript.preferences.includePackageJsonAutoImports": "auto",
            "eslint.workingDirectories": ["apps/frontend"],
            "files.exclude": {
                "**/node_modules": True,
                "**/.next": True,
                "**/dist": True,
                "**/__pycache__": True,
                "**/.pytest_cache": True
            },
            "search.exclude": {
                "**/node_modules": True,
                "**/.next": True,
                "**/dist": True,
                "**/__pycache__": True
            }
        }
        
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.flake8",
                "ms-python.black-formatter",
                "bradlc.vscode-tailwindcss",
                "esbenp.prettier-vscode",
                "ms-vscode.vscode-eslint",
                "ms-vscode.vscode-typescript-next",
                "ms-vscode.docker",
                "redhat.vscode-yaml",
                "davidanson.vscode-markdownlint"
            ]
        }
        
        # Write settings
        import json
        with open(vscode_dir / "settings.json", 'w') as f:
            json.dump(settings, f, indent=2)
        
        with open(vscode_dir / "extensions.json", 'w') as f:
            json.dump(extensions, f, indent=2)
        
        print("✅ VS Code settings created")
    
    def setup_env_files(self):
        """Setup environment files"""
        print("🔧 Setting up environment files...")
        
        env_example = self.root_dir / ".env.example"
        env_file = self.root_dir / ".env"
        
        if env_example.exists() and not env_file.exists():
            import shutil
            shutil.copy2(env_example, env_file)
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file with your configuration")
        
        # Setup environment files for different stages
        env_files = [".env.dev", ".env.staging", ".env.prod"]
        for env_file_name in env_files:
            env_path = self.root_dir / env_file_name
            if not env_path.exists():
                with open(env_path, 'w') as f:
                    f.write(f"# {env_file_name} - Environment specific configuration\n")
                    f.write("# Copy from .env.example and modify as needed\n\n")
                print(f"✅ Created {env_file_name}")
    
    def validate_setup(self):
        """Validate development tools setup"""
        print("🔍 Validating development tools setup...")
        
        validations = [
            (["black", "--version"], "Black formatter"),
            (["isort", "--version"], "isort"),
            (["flake8", "--version"], "Flake8"),
            (["pytest", "--version"], "pytest"),
            (["pre-commit", "--version"], "pre-commit"),
            (["docker", "--version"], "Docker"),
            (["docker-compose", "--version"], "Docker Compose")
        ]
        
        results = []
        for command, tool_name in validations:
            result = self.run_command(command, check=False)
            if result.returncode == 0:
                results.append(f"✅ {tool_name}")
            else:
                results.append(f"❌ {tool_name}")
        
        print("\n📋 Validation Results:")
        for result in results:
            print(f"  {result}")
    
    def setup_all(self):
        """Setup all development tools"""
        print("🚀 Setting up DexAgent development environment...")
        
        try:
            self.install_python_tools()
            self.install_node_tools()
            self.setup_pre_commit()
            self.setup_git_hooks()
            self.create_vscode_settings()
            self.setup_env_files()
            self.validate_setup()
            
            print("\n🎉 Development environment setup complete!")
            print("\n📋 Next steps:")
            print("  1. Edit .env file with your configuration")
            print("  2. Run 'make dev' to start the development environment")
            print("  3. Install recommended VS Code extensions")
            print("  4. Configure your IDE settings")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup DexAgent development tools")
    parser.add_argument("--python-only", action="store_true", help="Install Python tools only")
    parser.add_argument("--node-only", action="store_true", help="Install Node.js tools only")
    parser.add_argument("--hooks-only", action="store_true", help="Setup hooks only")
    parser.add_argument("--validate", action="store_true", help="Validate setup only")
    
    args = parser.parse_args()
    
    setup = DevToolsSetup()
    
    if args.python_only:
        setup.install_python_tools()
    elif args.node_only:
        setup.install_node_tools()
    elif args.hooks_only:
        setup.setup_pre_commit()
        setup.setup_git_hooks()
    elif args.validate:
        setup.validate_setup()
    else:
        setup.setup_all()

if __name__ == "__main__":
    main()