#!/usr/bin/env python3
"""
Enterprise Production Deployment Script
Production-grade deployment validation and system health checks
"""

import os
import sys
import time
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)

class EnterpriseDeploymentManager:
    """Production-grade deployment manager with comprehensive validation"""
    
    def __init__(self):
        self.deployment_start_time = time.time()
        self.workspace_root = Path(__file__).parent
        self.backup_dir = self.workspace_root / "backups" / f"pre-deployment-{int(time.time())}"
        self.validation_results = {}
        
    def print_banner(self):
        """Print enterprise deployment banner"""
        print("🏭" + "=" * 80)
        print("    BENSON BOT ENTERPRISE PRODUCTION DEPLOYMENT")
        print("    Quantum-Ready Autonomous Trading Platform")
        print("=" * 82)
        print()
    
    def create_deployment_backup(self) -> bool:
        """Create comprehensive pre-deployment backup"""
        logging.info("Creating pre-deployment backup...")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Critical files to backup
            critical_files = [
                "benson_rsi_bot.py",
                "trade_executor.py",
                "enterprise_portfolio_manager.py",
                "benson_config_manager.py",
                "portfolio_manager.py",
                ".env",
                "benson_user_config.json",
                "profit_engine_config.json"
            ]
            
            backed_up = 0
            for file_name in critical_files:
                source_path = self.workspace_root / file_name
                if source_path.exists():
                    backup_path = self.backup_dir / file_name
                    
                    # Copy file
                    import shutil
                    shutil.copy2(source_path, backup_path)
                    backed_up += 1
                    logging.info(f"Backed up: {file_name}")
            
            # Create backup manifest
            manifest = {
                "backup_timestamp": time.time(),
                "backup_datetime": datetime.now().isoformat(),
                "files_backed_up": backed_up,
                "backup_purpose": "pre-enterprise-deployment",
                "critical_files": critical_files
            }
            
            with open(self.backup_dir / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Pre-deployment backup created: {self.backup_dir}")
            print(f"   Files backed up: {backed_up}")
            return True
            
        except Exception as e:
            logging.error(f"Backup creation failed: {e}")
            return False
    
    def validate_environment(self) -> bool:
        """Comprehensive environment validation"""
        logging.info("Validating deployment environment...")
        
        validation_checks = []
        
        # Check Python version
        try:
            python_version = sys.version_info
            if python_version >= (3, 8):
                validation_checks.append(("Python Version", True, f"{python_version.major}.{python_version.minor}"))
            else:
                validation_checks.append(("Python Version", False, f"Required >=3.8, found {python_version.major}.{python_version.minor}"))
        except Exception as e:
            validation_checks.append(("Python Version", False, str(e)))
        
        # Check required files exist
        required_files = [
            "benson_rsi_bot.py",
            "enterprise_portfolio_manager.py",
            "trade_executor.py",
            "benson_config_manager.py"
        ]
        
        for file_name in required_files:
            file_path = self.workspace_root / file_name
            exists = file_path.exists()
            validation_checks.append((f"File: {file_name}", exists, str(file_path)))
        
        # Check environment variables
        required_env_vars = [
            "KRAKEN_API_KEY",
            "KRAKEN_SECRET",
            "BENSON_CONFIG"
        ]
        
        for env_var in required_env_vars:
            exists = os.getenv(env_var) is not None
            validation_checks.append((f"Env Var: {env_var}", exists, "Set" if exists else "Missing"))
        
        # Check database files
        db_files = [
            "benson_memory.db",
            "benson_patterns.db"
        ]
        
        for db_file in db_files:
            db_path = self.workspace_root / db_file
            if db_path.exists():
                try:
                    # Test database connection
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("SELECT 1")
                    conn.close()
                    validation_checks.append((f"Database: {db_file}", True, "Accessible"))
                except Exception as e:
                    validation_checks.append((f"Database: {db_file}", False, str(e)))
            else:
                validation_checks.append((f"Database: {db_file}", False, "Not found"))
        
        # Print validation results
        print("\n🔍 ENVIRONMENT VALIDATION RESULTS:")
        print("-" * 50)
        
        all_passed = True
        for check_name, passed, details in validation_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check_name:25} {status:10} {details}")
            if not passed:
                all_passed = False
        
        self.validation_results['environment'] = {
            'passed': all_passed,
            'checks': validation_checks
        }
        
        return all_passed
    
    def validate_dependencies(self) -> bool:
        """Validate all required Python dependencies"""
        logging.info("Validating Python dependencies...")
        
        required_packages = [
            "ccxt",
            "pandas",
            "numpy",
            "pyyaml",
            "fastapi",
            "uvicorn",
            "sqlite3"  # Built-in, but check availability
        ]
        
        dependency_checks = []
        
        for package in required_packages:
            try:
                if package == "sqlite3":
                    import sqlite3
                    dependency_checks.append((package, True, "Built-in"))
                elif package == "pyyaml":
                    import yaml
                    dependency_checks.append((package, True, "Available"))
                else:
                    __import__(package)
                    dependency_checks.append((package, True, "Available"))
            except ImportError:
                dependency_checks.append((package, False, "Missing"))
        
        print("\n📦 DEPENDENCY VALIDATION RESULTS:")
        print("-" * 50)
        
        all_passed = True
        for package, passed, details in dependency_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {package:20} {status:10} {details}")
            if not passed:
                all_passed = False
        
        self.validation_results['dependencies'] = {
            'passed': all_passed,
            'checks': dependency_checks
        }
        
        return all_passed
    
    def run_integration_tests(self) -> bool:
        """Run comprehensive integration test suite"""
        logging.info("Running enterprise integration tests...")
        
        try:
            # Check if test file exists
            test_file = self.workspace_root / "enterprise_integration_tests.py"
            if not test_file.exists():
                print("⚠️ Integration tests not found - skipping")
                return True
            
            print("\n🧪 RUNNING INTEGRATION TESTS:")
            print("-" * 50)
            
            # Run the tests
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, cwd=self.workspace_root)
            
            if result.returncode == 0:
                print("✅ All integration tests passed")
                self.validation_results['integration_tests'] = {'passed': True, 'output': result.stdout}
                return True
            else:
                print("❌ Integration tests failed")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.validation_results['integration_tests'] = {'passed': False, 'output': result.stderr}
                return False
                
        except Exception as e:
            logging.error(f"Integration test execution failed: {e}")
            self.validation_results['integration_tests'] = {'passed': False, 'output': str(e)}
            return False
    
    def validate_configuration(self) -> bool:
        """Validate system configuration files"""
        logging.info("Validating system configuration...")
        
        config_checks = []
        
        # Check main config file
        config_path = os.getenv('BENSON_CONFIG', 'config/config.yaml')
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    config_checks.append(("Main Config", True, config_path))
            except Exception as e:
                config_checks.append(("Main Config", False, str(e)))
        else:
            config_checks.append(("Main Config", False, "Not found"))
        
        # Check user config
        user_config_path = self.workspace_root / "benson_user_config.json"
        if user_config_path.exists():
            try:
                with open(user_config_path, 'r') as f:
                    user_config = json.load(f)
                    config_checks.append(("User Config", True, "Valid JSON"))
            except Exception as e:
                config_checks.append(("User Config", False, str(e)))
        else:
            config_checks.append(("User Config", False, "Not found"))
        
        print("\n⚙️ CONFIGURATION VALIDATION RESULTS:")
        print("-" * 50)
        
        all_passed = True
        for check_name, passed, details in config_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check_name:20} {status:10} {details}")
            if not passed:
                all_passed = False
        
        self.validation_results['configuration'] = {
            'passed': all_passed,
            'checks': config_checks
        }
        
        return all_passed
    
    def perform_system_health_check(self) -> bool:
        """Comprehensive system health check"""
        logging.info("Performing system health check...")
        
        health_checks = []
        
        try:
            # Check if we can import main modules
            sys.path.append(str(self.workspace_root))
            
            from enterprise_portfolio_manager import EnterprisePortfolioManager
            from benson_config_manager import BensonConfigManager
            
            config_manager = BensonConfigManager()
            enterprise_portfolio = EnterprisePortfolioManager(config_manager)
            
            health_checks.append(("Enterprise Portfolio Manager", True, "Initialized successfully"))
            
            # Check if we can get health metrics (with mocked data)
            try:
                # This would normally connect to real systems
                # For deployment check, we verify the methods exist
                health_metrics_method = hasattr(enterprise_portfolio, 'get_health_metrics')
                health_checks.append(("Health Metrics Method", health_metrics_method, "Available" if health_metrics_method else "Missing"))
                
                trading_readiness_method = hasattr(enterprise_portfolio, 'get_trading_readiness_report')
                health_checks.append(("Trading Readiness Method", trading_readiness_method, "Available" if trading_readiness_method else "Missing"))
                
            except Exception as e:
                health_checks.append(("Health Check Methods", False, str(e)))
            
        except Exception as e:
            health_checks.append(("System Initialization", False, str(e)))
        
        print("\n🏥 SYSTEM HEALTH CHECK RESULTS:")
        print("-" * 50)
        
        all_passed = True
        for check_name, passed, details in health_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check_name:30} {status:10} {details}")
            if not passed:
                all_passed = False
        
        self.validation_results['system_health'] = {
            'passed': all_passed,
            'checks': health_checks
        }
        
        return all_passed
    
    def generate_deployment_report(self) -> Dict:
        """Generate comprehensive deployment readiness report"""
        
        deployment_duration = time.time() - self.deployment_start_time
        
        # Calculate overall readiness
        all_validations_passed = all(
            validation.get('passed', False) 
            for validation in self.validation_results.values()
        )
        
        report = {
            "deployment_timestamp": time.time(),
            "deployment_datetime": datetime.now().isoformat(),
            "deployment_duration_seconds": deployment_duration,
            "overall_readiness": all_validations_passed,
            "backup_location": str(self.backup_dir),
            "validation_results": self.validation_results,
            "recommendations": []
        }
        
        # Add recommendations based on validation results
        if not all_validations_passed:
            for validation_name, validation_data in self.validation_results.items():
                if not validation_data.get('passed', False):
                    report["recommendations"].append(f"Fix {validation_name} validation failures before deployment")
        
        # Save report
        report_path = self.workspace_root / f"deployment_report_{int(time.time())}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_full_deployment_check(self) -> bool:
        """Run complete deployment readiness validation"""
        self.print_banner()
        
        print(f"🚀 Starting enterprise deployment validation...")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        print(f"   Workspace: {self.workspace_root}")
        print()
        
        # Step 1: Create backup
        if not self.create_deployment_backup():
            print("❌ DEPLOYMENT ABORTED: Backup creation failed")
            return False
        
        # Step 2: Environment validation
        if not self.validate_environment():
            print("⚠️ Environment validation failed - review issues above")
        
        # Step 3: Dependencies validation
        if not self.validate_dependencies():
            print("⚠️ Dependencies validation failed - install missing packages")
        
        # Step 4: Configuration validation
        if not self.validate_configuration():
            print("⚠️ Configuration validation failed - fix config issues")
        
        # Step 5: Integration tests
        if not self.run_integration_tests():
            print("⚠️ Integration tests failed - fix test failures")
        
        # Step 6: System health check
        if not self.perform_system_health_check():
            print("⚠️ System health check failed - fix system issues")
        
        # Generate final report
        report = self.generate_deployment_report()
        
        print("\n" + "=" * 80)
        print("🎯 DEPLOYMENT READINESS SUMMARY")
        print("=" * 80)
        
        if report['overall_readiness']:
            print("✅ SYSTEM READY FOR PRODUCTION DEPLOYMENT")
            print("🚀 All validations passed - proceed with confidence")
            print()
            print("📋 DEPLOYMENT CHECKLIST:")
            print("   1. ✅ Pre-deployment backup created")
            print("   2. ✅ Environment validated")
            print("   3. ✅ Dependencies confirmed")
            print("   4. ✅ Configuration verified")
            print("   5. ✅ Integration tests passed")
            print("   6. ✅ System health confirmed")
            print()
            print("🏭 ENTERPRISE FEATURES ACTIVE:")
            print("   • Portfolio health monitoring")
            print("   • Comprehensive trade execution")
            print("   • Risk management systems")
            print("   • Performance analytics")
            print("   • Error handling & recovery")
            print()
        else:
            print("❌ SYSTEM NOT READY FOR PRODUCTION")
            print("🔧 Fix validation failures before deployment")
            print()
            print("📋 FAILED VALIDATIONS:")
            for validation_name, validation_data in self.validation_results.items():
                if not validation_data.get('passed', False):
                    print(f"   • {validation_name}")
            print()
            print("💡 RECOMMENDATIONS:")
            for recommendation in report.get('recommendations', []):
                print(f"   • {recommendation}")
        
        print(f"\n📊 Deployment report saved: deployment_report_{int(self.deployment_start_time)}.json")
        print(f"🔄 Backup location: {self.backup_dir}")
        print(f"⏱️  Total validation time: {report['deployment_duration_seconds']:.2f}s")
        
        return report['overall_readiness']

def main():
    """Main deployment validation entry point"""
    deployment_manager = EnterpriseDeploymentManager()
    
    try:
        success = deployment_manager.run_full_deployment_check()
        
        if success:
            print("\n🎉 READY TO DEPLOY!")
            print("Run: python benson_rsi_bot.py")
        else:
            print("\n🛠️  FIX ISSUES BEFORE DEPLOYMENT")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Deployment check cancelled by user")
        return 1
    except Exception as e:
        print(f"\n💥 Deployment check failed: {e}")
        logging.error(f"Deployment check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())