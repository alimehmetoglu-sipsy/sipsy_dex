#!/usr/bin/env python3
"""
DexAgent Code Analyzer
Analyze codebase for quality, security, and performance issues
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from collections import defaultdict
import ast

class CodeAnalyzer:
    """Analyze DexAgent codebase"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.root_dir = Path(__file__).parent.parent.parent
        self.apps_dir = self.root_dir / "apps"
        self.packages_dir = self.root_dir / "packages"
        self.reports_dir = self.root_dir / "tools" / "reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def run_command(self, command: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
        """Run shell command"""
        cwd = cwd or self.root_dir
        try:
            return subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False
            )
        except Exception as e:
            print(f"Error running command {' '.join(command)}: {e}")
            return None
    
    def analyze_python_code(self) -> Dict[str, Any]:
        """Analyze Python code quality"""
        print("🐍 Analyzing Python code...")
        
        results = {
            "flake8": {},
            "complexity": {},
            "security": {},
            "imports": {},
            "documentation": {}
        }
        
        # Find Python files
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(self.root_dir.glob(pattern))
        
        python_files = [f for f in python_files if "node_modules" not in str(f) and ".git" not in str(f)]
        
        # Flake8 analysis
        backend_dir = self.apps_dir / "backend"
        if backend_dir.exists():
            flake8_result = self.run_command(["python", "-m", "flake8", ".", "--format=json"], backend_dir)
            if flake8_result and flake8_result.stdout:
                try:
                    results["flake8"] = json.loads(flake8_result.stdout)
                except:
                    results["flake8"] = {"error": "Failed to parse flake8 output"}
        
        # Complexity analysis
        results["complexity"] = self._analyze_complexity(python_files)
        
        # Security analysis with bandit
        security_result = self.run_command(["python", "-m", "bandit", "-r", ".", "-f", "json"], backend_dir)
        if security_result and security_result.stdout:
            try:
                results["security"] = json.loads(security_result.stdout)
            except:
                results["security"] = {"error": "Failed to parse bandit output"}
        
        # Import analysis
        results["imports"] = self._analyze_imports(python_files)
        
        # Documentation analysis
        results["documentation"] = self._analyze_python_docs(python_files)
        
        return results
    
    def analyze_typescript_code(self) -> Dict[str, Any]:
        """Analyze TypeScript/JavaScript code"""
        print("📦 Analyzing TypeScript/JavaScript code...")
        
        results = {
            "eslint": {},
            "typescript": {},
            "complexity": {},
            "imports": {},
            "components": {}
        }
        
        frontend_dir = self.apps_dir / "frontend"
        
        if not frontend_dir.exists():
            return results
        
        # ESLint analysis
        eslint_result = self.run_command(["npm", "run", "lint", "--", "--format=json"], frontend_dir)
        if eslint_result and eslint_result.stdout:
            try:
                results["eslint"] = json.loads(eslint_result.stdout)
            except:
                results["eslint"] = {"error": "Failed to parse ESLint output"}
        
        # TypeScript analysis
        tsc_result = self.run_command(["npx", "tsc", "--noEmit", "--listFiles"], frontend_dir)
        if tsc_result:
            results["typescript"] = {
                "status": "success" if tsc_result.returncode == 0 else "error",
                "files_checked": len(tsc_result.stdout.split('\n')) if tsc_result.stdout else 0,
                "errors": tsc_result.stderr if tsc_result.stderr else None
            }
        
        # Find TypeScript/JavaScript files
        ts_files = []
        for pattern in ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]:
            ts_files.extend(frontend_dir.glob(pattern))
        
        ts_files = [f for f in ts_files if "node_modules" not in str(f)]
        
        # Component analysis
        results["components"] = self._analyze_react_components(ts_files)
        
        # Import analysis
        results["imports"] = self._analyze_ts_imports(ts_files)
        
        return results
    
    def analyze_docker_files(self) -> Dict[str, Any]:
        """Analyze Docker configuration"""
        print("🐳 Analyzing Docker configuration...")
        
        results = {
            "dockerfiles": [],
            "compose_files": [],
            "security_issues": [],
            "optimization_suggestions": []
        }
        
        # Find Dockerfiles
        dockerfiles = list(self.root_dir.glob("**/Dockerfile*"))
        for dockerfile in dockerfiles:
            analysis = self._analyze_dockerfile(dockerfile)
            results["dockerfiles"].append(analysis)
        
        # Find docker-compose files
        compose_files = list(self.root_dir.glob("**/docker-compose*.yml"))
        for compose_file in compose_files:
            analysis = self._analyze_compose_file(compose_file)
            results["compose_files"].append(analysis)
        
        return results
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        print("📋 Analyzing dependencies...")
        
        results = {
            "python": {},
            "node": {},
            "vulnerabilities": {},
            "outdated": {}
        }
        
        # Python dependencies
        backend_dir = self.apps_dir / "backend"
        requirements_file = backend_dir / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file) as f:
                requirements = f.read().splitlines()
            
            results["python"] = {
                "file": str(requirements_file),
                "dependencies": [line for line in requirements if line and not line.startswith("#")],
                "count": len([line for line in requirements if line and not line.startswith("#")])
            }
            
            # Check for outdated packages
            pip_outdated = self.run_command(["pip", "list", "--outdated", "--format=json"], backend_dir)
            if pip_outdated and pip_outdated.stdout:
                try:
                    results["outdated"]["python"] = json.loads(pip_outdated.stdout)
                except:
                    pass
        
        # Node.js dependencies
        frontend_dir = self.apps_dir / "frontend"
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package_data = json.load(f)
            
            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})
            
            results["node"] = {
                "file": str(package_json),
                "dependencies": deps,
                "devDependencies": dev_deps,
                "total_count": len(deps) + len(dev_deps)
            }
            
            # Check for outdated packages
            npm_outdated = self.run_command(["npm", "outdated", "--json"], frontend_dir)
            if npm_outdated and npm_outdated.stdout:
                try:
                    results["outdated"]["node"] = json.loads(npm_outdated.stdout)
                except:
                    pass
        
        # Security audit
        npm_audit = self.run_command(["npm", "audit", "--json"], frontend_dir)
        if npm_audit and npm_audit.stdout:
            try:
                results["vulnerabilities"]["node"] = json.loads(npm_audit.stdout)
            except:
                pass
        
        return results
    
    def analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage"""
        print("🧪 Analyzing test coverage...")
        
        results = {
            "python": {},
            "javascript": {},
            "summary": {}
        }
        
        # Python coverage
        backend_dir = self.apps_dir / "backend"
        coverage_result = self.run_command(["python", "-m", "pytest", "--cov=app", "--cov-report=json"], backend_dir)
        coverage_file = backend_dir / "coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                results["python"] = json.load(f)
        
        # JavaScript coverage (if available)
        frontend_dir = self.apps_dir / "frontend"
        jest_coverage = frontend_dir / "coverage" / "coverage-summary.json"
        if jest_coverage.exists():
            with open(jest_coverage) as f:
                results["javascript"] = json.load(f)
        
        return results
    
    def _analyze_complexity(self, python_files: List[Path]) -> Dict[str, Any]:
        """Analyze code complexity"""
        complexity_data = {
            "files": {},
            "summary": {
                "total_files": len(python_files),
                "high_complexity": 0,
                "avg_complexity": 0
            }
        }
        
        total_complexity = 0
        
        for file_path in python_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                
                tree = ast.parse(content)
                visitor = ComplexityVisitor()
                visitor.visit(tree)
                
                file_complexity = visitor.complexity
                complexity_data["files"][str(file_path)] = {
                    "complexity": file_complexity,
                    "functions": visitor.functions
                }
                
                total_complexity += file_complexity
                if file_complexity > 10:
                    complexity_data["summary"]["high_complexity"] += 1
                    
            except Exception as e:
                complexity_data["files"][str(file_path)] = {"error": str(e)}
        
        if python_files:
            complexity_data["summary"]["avg_complexity"] = total_complexity / len(python_files)
        
        return complexity_data
    
    def _analyze_imports(self, python_files: List[Path]) -> Dict[str, Any]:
        """Analyze Python imports"""
        imports_data = {
            "external_packages": set(),
            "internal_imports": set(),
            "unused_imports": [],
            "circular_imports": []
        }
        
        for file_path in python_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                
                # Find imports
                import_pattern = r'^(?:from\s+(\S+)\s+import\s+.*|import\s+(\S+)).*$'
                for line in content.split('\n'):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        module = match.group(1) or match.group(2)
                        if module.startswith('app.'):
                            imports_data["internal_imports"].add(module)
                        else:
                            imports_data["external_packages"].add(module)
                            
            except Exception:
                continue
        
        # Convert sets to lists for JSON serialization
        imports_data["external_packages"] = list(imports_data["external_packages"])
        imports_data["internal_imports"] = list(imports_data["internal_imports"])
        
        return imports_data
    
    def _analyze_python_docs(self, python_files: List[Path]) -> Dict[str, Any]:
        """Analyze Python documentation"""
        docs_data = {
            "total_functions": 0,
            "documented_functions": 0,
            "total_classes": 0,
            "documented_classes": 0,
            "coverage_percentage": 0
        }
        
        for file_path in python_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        docs_data["total_functions"] += 1
                        if ast.get_docstring(node):
                            docs_data["documented_functions"] += 1
                    
                    elif isinstance(node, ast.ClassDef):
                        docs_data["total_classes"] += 1
                        if ast.get_docstring(node):
                            docs_data["documented_classes"] += 1
                            
            except Exception:
                continue
        
        total_items = docs_data["total_functions"] + docs_data["total_classes"]
        documented_items = docs_data["documented_functions"] + docs_data["documented_classes"]
        
        if total_items > 0:
            docs_data["coverage_percentage"] = (documented_items / total_items) * 100
        
        return docs_data
    
    def _analyze_react_components(self, ts_files: List[Path]) -> Dict[str, Any]:
        """Analyze React components"""
        components_data = {
            "total_components": 0,
            "functional_components": 0,
            "class_components": 0,
            "components_with_props": 0,
            "components_with_state": 0
        }
        
        for file_path in ts_files:
            if not file_path.name.endswith(('.tsx', '.jsx')):
                continue
                
            try:
                with open(file_path) as f:
                    content = f.read()
                
                # Detect components
                if re.search(r'const\s+\w+\s*:\s*React\.FC', content):
                    components_data["functional_components"] += 1
                elif re.search(r'function\s+\w+\s*\(.*\)\s*{', content) and 'return' in content:
                    components_data["functional_components"] += 1
                elif re.search(r'class\s+\w+\s+extends\s+.*Component', content):
                    components_data["class_components"] += 1
                
                if re.search(r'interface\s+\w+Props', content):
                    components_data["components_with_props"] += 1
                
                if re.search(r'useState\s*\(', content) or re.search(r'this\.state', content):
                    components_data["components_with_state"] += 1
                    
            except Exception:
                continue
        
        components_data["total_components"] = (
            components_data["functional_components"] + 
            components_data["class_components"]
        )
        
        return components_data
    
    def _analyze_ts_imports(self, ts_files: List[Path]) -> Dict[str, Any]:
        """Analyze TypeScript imports"""
        imports_data = {
            "external_packages": set(),
            "internal_imports": set(),
            "relative_imports": set()
        }
        
        for file_path in ts_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                
                # Find imports
                import_pattern = r'^import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]'
                for line in content.split('\n'):
                    match = re.search(import_pattern, line.strip())
                    if match:
                        module = match.group(1)
                        if module.startswith('./') or module.startswith('../'):
                            imports_data["relative_imports"].add(module)
                        elif module.startswith('@/') or module.startswith('~/'):
                            imports_data["internal_imports"].add(module)
                        else:
                            imports_data["external_packages"].add(module)
                            
            except Exception:
                continue
        
        # Convert sets to lists for JSON serialization
        imports_data["external_packages"] = list(imports_data["external_packages"])
        imports_data["internal_imports"] = list(imports_data["internal_imports"])
        imports_data["relative_imports"] = list(imports_data["relative_imports"])
        
        return imports_data
    
    def _analyze_dockerfile(self, dockerfile_path: Path) -> Dict[str, Any]:
        """Analyze individual Dockerfile"""
        analysis = {
            "file": str(dockerfile_path),
            "issues": [],
            "suggestions": [],
            "security_score": 100
        }
        
        try:
            with open(dockerfile_path) as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for security issues
                if line.startswith('USER root'):
                    analysis["issues"].append(f"Line {i}: Running as root user")
                    analysis["security_score"] -= 20
                
                if 'sudo' in line:
                    analysis["issues"].append(f"Line {i}: Using sudo in container")
                    analysis["security_score"] -= 15
                
                if '--no-check-certificate' in line:
                    analysis["issues"].append(f"Line {i}: Disabling certificate checks")
                    analysis["security_score"] -= 25
                
                # Check for optimization opportunities
                if line.startswith('RUN apt-get update') and 'apt-get install' not in line:
                    analysis["suggestions"].append(f"Line {i}: Consider combining apt-get update and install")
                
                if line.startswith('COPY . .'):
                    analysis["suggestions"].append(f"Line {i}: Consider using .dockerignore to exclude unnecessary files")
        
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_compose_file(self, compose_path: Path) -> Dict[str, Any]:
        """Analyze docker-compose file"""
        analysis = {
            "file": str(compose_path),
            "services": [],
            "issues": [],
            "suggestions": []
        }
        
        try:
            import yaml
            
            with open(compose_path) as f:
                compose_data = yaml.safe_load(f)
            
            services = compose_data.get('services', {})
            analysis["services"] = list(services.keys())
            
            for service_name, service_config in services.items():
                # Check for security issues
                if service_config.get('privileged'):
                    analysis["issues"].append(f"Service {service_name}: Running in privileged mode")
                
                if 'secrets' not in service_config and 'environment' in service_config:
                    env_vars = service_config['environment']
                    if isinstance(env_vars, list):
                        for env_var in env_vars:
                            if any(sensitive in env_var.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY']):
                                analysis["suggestions"].append(f"Service {service_name}: Consider using secrets for sensitive environment variables")
                                break
        
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def generate_report(self, output_format: str = "json") -> str:
        """Generate comprehensive analysis report"""
        print("📊 Generating comprehensive analysis report...")
        
        report = {
            "analysis_time": os.popen("date").read().strip(),
            "project": "DexAgent",
            "python_analysis": self.analyze_python_code(),
            "typescript_analysis": self.analyze_typescript_code(),
            "docker_analysis": self.analyze_docker_files(),
            "dependencies_analysis": self.analyze_dependencies(),
            "test_coverage": self.analyze_test_coverage()
        }
        
        # Generate summary
        report["summary"] = self._generate_summary(report)
        
        # Save report
        timestamp = str(int(time.time()))
        if output_format == "json":
            report_file = self.reports_dir / f"code_analysis_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        else:
            report_file = self.reports_dir / f"code_analysis_{timestamp}.md"
            with open(report_file, 'w') as f:
                f.write(self._format_markdown_report(report))
        
        print(f"📊 Report saved: {report_file}")
        return str(report_file)
    
    def _generate_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary"""
        summary = {
            "overall_score": 85,  # Default score
            "issues_found": 0,
            "suggestions": 0,
            "critical_issues": [],
            "recommendations": []
        }
        
        # Count issues from different analyses
        python_analysis = report.get("python_analysis", {})
        if "flake8" in python_analysis and isinstance(python_analysis["flake8"], list):
            summary["issues_found"] += len(python_analysis["flake8"])
        
        # Add recommendations based on analysis
        if report.get("test_coverage", {}).get("python", {}).get("totals", {}).get("percent_covered", 0) < 80:
            summary["recommendations"].append("Increase test coverage to at least 80%")
        
        if report.get("dependencies_analysis", {}).get("vulnerabilities", {}).get("node", {}).get("metadata", {}).get("vulnerabilities", 0) > 0:
            summary["critical_issues"].append("Security vulnerabilities found in dependencies")
        
        return summary
    
    def _format_markdown_report(self, report: Dict[str, Any]) -> str:
        """Format report as Markdown"""
        md = f"""# DexAgent Code Analysis Report

**Generated**: {report['analysis_time']}

## Summary

- **Overall Score**: {report['summary']['overall_score']}/100
- **Issues Found**: {report['summary']['issues_found']}
- **Critical Issues**: {len(report['summary']['critical_issues'])}

## Python Analysis

### Code Quality
- **Flake8 Issues**: {len(report['python_analysis'].get('flake8', [])) if isinstance(report['python_analysis'].get('flake8', []), list) else 'N/A'}
- **Documentation Coverage**: {report['python_analysis'].get('documentation', {}).get('coverage_percentage', 0):.1f}%

## TypeScript Analysis

### Code Quality  
- **ESLint Issues**: {len(report['typescript_analysis'].get('eslint', [])) if isinstance(report['typescript_analysis'].get('eslint', []), list) else 'N/A'}
- **Components**: {report['typescript_analysis'].get('components', {}).get('total_components', 0)}

## Recommendations

"""
        
        for rec in report['summary']['recommendations']:
            md += f"- {rec}\n"
        
        return md

class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity"""
    
    def __init__(self):
        self.complexity = 1
        self.functions = {}
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        old_complexity = self.complexity
        self.complexity = 1
        self.generic_visit(node)
        self.functions[node.name] = self.complexity
        self.complexity = old_complexity
        self.current_function = None
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DexAgent Code Analyzer")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                       help="Output format")
    parser.add_argument("--python", action="store_true", help="Analyze Python code only")
    parser.add_argument("--typescript", action="store_true", help="Analyze TypeScript code only")
    parser.add_argument("--docker", action="store_true", help="Analyze Docker configuration only")
    parser.add_argument("--dependencies", action="store_true", help="Analyze dependencies only")
    
    args = parser.parse_args()
    
    analyzer = CodeAnalyzer()
    
    if args.python:
        result = analyzer.analyze_python_code()
        print(json.dumps(result, indent=2, default=str))
    elif args.typescript:
        result = analyzer.analyze_typescript_code()
        print(json.dumps(result, indent=2, default=str))
    elif args.docker:
        result = analyzer.analyze_docker_files()
        print(json.dumps(result, indent=2, default=str))
    elif args.dependencies:
        result = analyzer.analyze_dependencies()
        print(json.dumps(result, indent=2, default=str))
    else:
        # Full analysis
        report_file = analyzer.generate_report(args.format)
        print(f"✅ Analysis complete. Report saved to: {report_file}")

if __name__ == "__main__":
    import time
    main()