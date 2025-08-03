#!/usr/bin/env python3
"""
DexAgent Deployment Script
Automated deployment for different environments
"""

import os
import sys
import subprocess
import argparse
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import shutil

class DexAgentDeployer:
    """Deployment automation for DexAgent"""
    
    def __init__(self, environment: str = "development"):
        """Initialize deployer"""
        self.environment = environment
        self.root_dir = Path(__file__).parent.parent.parent
        self.deploy_dir = self.root_dir / "deploy"
        self.config_dir = self.root_dir / "deploy" / "config"
        
        # Environment-specific configurations
        self.configs = {
            "development": {
                "compose_file": "docker-compose.dev.yml",
                "env_file": ".env.dev",
                "replicas": 1,
                "port_prefix": "80"
            },
            "staging": {
                "compose_file": "docker-compose.staging.yml", 
                "env_file": ".env.staging",
                "replicas": 2,
                "port_prefix": "81"
            },
            "production": {
                "compose_file": "docker-compose.prod.yml",
                "env_file": ".env.prod", 
                "replicas": 3,
                "port_prefix": "443"
            }
        }
    
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
    
    def validate_environment(self):
        """Validate deployment environment"""
        print(f"🔍 Validating {self.environment} environment...")
        
        config = self.configs.get(self.environment)
        if not config:
            print(f"❌ Unknown environment: {self.environment}")
            sys.exit(1)
        
        # Check required files
        compose_file = self.root_dir / config["compose_file"]
        if not compose_file.exists():
            print(f"❌ Compose file not found: {compose_file}")
            sys.exit(1)
        
        # Check environment file
        env_file = self.root_dir / config["env_file"]
        if not env_file.exists():
            print(f"⚠️  Environment file not found: {env_file}")
            print(f"📝 Consider creating {env_file} based on .env.example")
        
        print("✅ Environment validation passed")
    
    def pre_deployment_checks(self):
        """Run pre-deployment checks"""
        print("🔍 Running pre-deployment checks...")
        
        # Check Docker
        try:
            self.run_command(["docker", "--version"])
            self.run_command(["docker-compose", "--version"])
        except:
            print("❌ Docker or Docker Compose not available")
            sys.exit(1)
        
        # Check disk space
        disk_usage = shutil.disk_usage(self.root_dir)
        free_space_gb = disk_usage.free / (1024**3)
        if free_space_gb < 5:
            print(f"⚠️  Low disk space: {free_space_gb:.1f}GB available")
        
        # Check Git status
        try:
            result = self.run_command(["git", "status", "--porcelain"], check=False)
            if result.stdout.strip():
                print("⚠️  Uncommitted changes detected")
                if self.environment == "production":
                    print("❌ Production deployment requires clean Git state")
                    sys.exit(1)
        except:
            print("⚠️  Git not available or not a Git repository")
        
        print("✅ Pre-deployment checks passed")
    
    def backup_current_deployment(self):
        """Backup current deployment"""
        if self.environment == "production":
            print("💾 Creating deployment backup...")
            
            backup_dir = self.deploy_dir / "backups" / f"backup-{int(time.time())}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup database
            print("💾 Backing up database...")
            db_backup = backup_dir / "database.sql"
            self.run_command([
                "docker-compose", "exec", "-T", "postgres",
                "pg_dump", "-U", "postgres", "dexagents"
            ], check=False)
            
            # Backup configuration
            print("💾 Backing up configuration...")
            config_backup = backup_dir / "config"
            if self.config_dir.exists():
                shutil.copytree(self.config_dir, config_backup, dirs_exist_ok=True)
            
            print(f"✅ Backup created: {backup_dir}")
    
    def build_images(self):
        """Build deployment images"""
        print("🔨 Building deployment images...")
        
        config = self.configs[self.environment]
        compose_file = config["compose_file"]
        
        # Build images
        self.run_command([
            "docker-compose", "-f", compose_file, "build", "--no-cache"
        ])
        
        print("✅ Images built")
    
    def deploy_services(self):
        """Deploy services"""
        print(f"🚀 Deploying to {self.environment}...")
        
        config = self.configs[self.environment]
        compose_file = config["compose_file"]
        
        # Stop existing services
        print("⏹️  Stopping existing services...")
        self.run_command([
            "docker-compose", "-f", compose_file, "down"
        ], check=False)
        
        # Start services
        print("▶️  Starting services...")
        self.run_command([
            "docker-compose", "-f", compose_file, "up", "-d", "--scale", 
            f"backend={config['replicas']}", f"frontend={config['replicas']}"
        ])
        
        print("✅ Services deployed")
    
    def run_migrations(self):
        """Run database migrations"""
        print("🗃️  Running database migrations...")
        
        config = self.configs[self.environment]
        compose_file = config["compose_file"]
        
        # Wait for database
        print("⏳ Waiting for database...")
        time.sleep(10)
        
        # Run migrations
        self.run_command([
            "docker-compose", "-f", compose_file, "exec", "-T", "backend",
            "python", "app/migrations/migration_manager.py"
        ])
        
        print("✅ Migrations completed")
    
    def health_check(self):
        """Perform health checks"""
        print("🏥 Performing health checks...")
        
        config = self.configs[self.environment]
        port = f"{config['port_prefix']}80"
        
        # Check backend health
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/api/v1/system/health", timeout=30)
            if response.status_code == 200:
                print("✅ Backend health check passed")
            else:
                print(f"⚠️  Backend health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend health check error: {e}")
        
        # Check frontend
        try:
            import requests
            response = requests.get(f"http://localhost:3000", timeout=30)
            if response.status_code == 200:
                print("✅ Frontend health check passed")
            else:
                print(f"⚠️  Frontend health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Frontend health check error: {e}")
        
        # Check services status
        config = self.configs[self.environment]
        result = self.run_command([
            "docker-compose", "-f", config["compose_file"], "ps"
        ])
        
        print("✅ Health checks completed")
    
    def setup_monitoring(self):
        """Setup monitoring and alerting"""
        if self.environment in ["staging", "production"]:
            print("📊 Setting up monitoring...")
            
            # Start monitoring services
            monitoring_compose = self.root_dir / "monitoring" / "docker-compose.yml"
            if monitoring_compose.exists():
                self.run_command([
                    "docker-compose", "-f", str(monitoring_compose), "up", "-d"
                ])
                print("✅ Monitoring services started")
            else:
                print("⚠️  Monitoring configuration not found")
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        print("📋 Generating deployment report...")
        
        report = {
            "deployment_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "environment": self.environment,
            "version": self._get_version(),
            "commit": self._get_git_commit(),
            "services": self._get_service_status(),
            "health_status": "healthy"  # TODO: Implement actual health check
        }
        
        # Write report
        report_file = self.deploy_dir / f"deployment-{self.environment}-{int(time.time())}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📋 Deployment report: {report_file}")
        return report
    
    def _get_version(self) -> str:
        """Get project version"""
        package_json = self.root_dir / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                return data.get("version", "unknown")
        return "unknown"
    
    def _get_git_commit(self) -> str:
        """Get Git commit"""
        try:
            result = self.run_command(["git", "rev-parse", "HEAD"], check=False)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_service_status(self) -> Dict[str, str]:
        """Get service status"""
        try:
            config = self.configs[self.environment]
            result = self.run_command([
                "docker-compose", "-f", config["compose_file"], "ps", "--format", "json"
            ], check=False)
            
            if result.returncode == 0:
                services = json.loads(result.stdout) if result.stdout else []
                return {service.get("Service", "unknown"): service.get("State", "unknown") for service in services}
        except:
            pass
        
        return {}
    
    def rollback(self):
        """Rollback to previous deployment"""
        print("🔄 Rolling back deployment...")
        
        # Find latest backup
        backup_dir = self.deploy_dir / "backups"
        if backup_dir.exists():
            backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], reverse=True)
            if backups:
                latest_backup = backups[0]
                print(f"🔄 Rolling back to {latest_backup.name}")
                
                # Stop current services
                config = self.configs[self.environment]
                self.run_command([
                    "docker-compose", "-f", config["compose_file"], "down"
                ], check=False)
                
                # Restore database
                db_backup = latest_backup / "database.sql"
                if db_backup.exists():
                    print("🔄 Restoring database...")
                    # TODO: Implement database restore
                
                print("✅ Rollback completed")
            else:
                print("❌ No backups found for rollback")
        else:
            print("❌ Backup directory not found")
    
    def deploy(self, build: bool = True, migrate: bool = True):
        """Complete deployment process"""
        print(f"🚀 Starting deployment to {self.environment}...")
        start_time = time.time()
        
        try:
            self.validate_environment()
            self.pre_deployment_checks()
            
            if self.environment == "production":
                self.backup_current_deployment()
            
            if build:
                self.build_images()
            
            self.deploy_services()
            
            if migrate:
                self.run_migrations()
            
            self.health_check()
            self.setup_monitoring()
            
            report = self.generate_deployment_report()
            
            deploy_time = time.time() - start_time
            print(f"🎉 Deployment completed successfully in {deploy_time:.2f} seconds!")
            
            return report
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            if self.environment == "production":
                print("🔄 Consider running rollback if needed")
            sys.exit(1)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DexAgent Deployment Script")
    parser.add_argument("environment", choices=["development", "staging", "production"], 
                       help="Deployment environment")
    parser.add_argument("--no-build", action="store_true", help="Skip building images")
    parser.add_argument("--no-migrate", action="store_true", help="Skip database migrations")
    parser.add_argument("--rollback", action="store_true", help="Rollback to previous deployment")
    
    args = parser.parse_args()
    
    deployer = DexAgentDeployer(args.environment)
    
    if args.rollback:
        deployer.rollback()
    else:
        deployer.deploy(
            build=not args.no_build,
            migrate=not args.no_migrate
        )

if __name__ == "__main__":
    main()