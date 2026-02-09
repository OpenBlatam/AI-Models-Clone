#!/usr/bin/env python3
"""
📚 LIBRARY MIGRATION MANAGER
============================

Comprehensive library migration and management system for upgrading
to the latest and greatest libraries in the Python ecosystem.
"""

import os
import sys
import subprocess
import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import requests
import pkg_resources
from loguru import logger

# Configure logging
logger.add("library_migration.log", rotation="10 MB", level="INFO")

class MigrationStatus(Enum):
    """Migration status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class LibraryCategory(Enum):
    """Library category enumeration."""
    CORE = "core"
    PERFORMANCE = "performance"
    DEVELOPMENT = "development"
    SPECIALIZED = "specialized"
    SECURITY = "security"
    MONITORING = "monitoring"

@dataclass
class LibraryInfo:
    """Information about a library."""
    name: str
    current_version: str
    target_version: str
    category: LibraryCategory
    description: str
    migration_notes: str = ""
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    performance_impact: str = "medium"
    security_impact: str = "medium"

@dataclass
class MigrationResult:
    """Result of a migration operation."""
    library_name: str
    status: MigrationStatus
    old_version: str
    new_version: str
    duration: float
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class LibraryMigrationManager:
    """Comprehensive library migration manager."""
    
    def __init__(self, requirements_dir: str = "."):
        self.requirements_dir = Path(requirements_dir)
        self.migration_results: List[MigrationResult] = []
        self.library_info: Dict[str, LibraryInfo] = {}
        self.conflicts: List[Tuple[str, str]] = []
        self._load_library_info()
    
    def _load_library_info(self):
        """Load library information from configuration."""
        # Core Framework Libraries
        self.library_info.update({
            "fastapi": LibraryInfo(
                name="fastapi",
                current_version="0.104.1",
                target_version="0.115.0",
                category=LibraryCategory.CORE,
                description="Modern web framework with latest async improvements",
                performance_impact="high",
                dependencies=["uvicorn", "pydantic"]
            ),
            "uvicorn": LibraryInfo(
                name="uvicorn",
                current_version="0.24.0",
                target_version="0.27.0",
                category=LibraryCategory.CORE,
                description="Lightning-fast ASGI server with enhanced WebSocket support",
                performance_impact="high"
            ),
            "pydantic": LibraryInfo(
                name="pydantic",
                current_version="2.5.0",
                target_version="2.8.0",
                category=LibraryCategory.CORE,
                description="Data validation with latest type hints and validation features",
                performance_impact="medium"
            ),
            "torch": LibraryInfo(
                name="torch",
                current_version="2.1.1",
                target_version="2.2.0",
                category=LibraryCategory.PERFORMANCE,
                description="Latest PyTorch with enhanced CUDA support and optimizations",
                performance_impact="high",
                dependencies=["torchvision", "torchaudio"]
            ),
            "transformers": LibraryInfo(
                name="transformers",
                current_version="4.36.2",
                target_version="4.40.0",
                category=LibraryCategory.SPECIALIZED,
                description="Latest transformer models and architectures",
                performance_impact="high"
            ),
            "pandas": LibraryInfo(
                name="pandas",
                current_version="2.1.4",
                target_version="2.2.0",
                category=LibraryCategory.PERFORMANCE,
                description="Enhanced DataFrame operations with better performance",
                performance_impact="high"
            ),
            "numpy": LibraryInfo(
                name="numpy",
                current_version="1.24.4",
                target_version="1.26.0",
                category=LibraryCategory.PERFORMANCE,
                description="Latest NumPy with enhanced array operations",
                performance_impact="high"
            ),
            "sqlalchemy": LibraryInfo(
                name="sqlalchemy",
                current_version="2.0.23",
                target_version="2.0.25",
                category=LibraryCategory.CORE,
                description="Latest SQLAlchemy with improved async support",
                performance_impact="medium"
            ),
            "redis": LibraryInfo(
                name="redis",
                current_version="5.0.1",
                target_version="5.0.8",
                category=LibraryCategory.CORE,
                description="Enhanced Redis with better clustering and memory management",
                performance_impact="medium"
            ),
            "pytest": LibraryInfo(
                name="pytest",
                current_version="7.4.3",
                target_version="8.0.0",
                category=LibraryCategory.DEVELOPMENT,
                description="Latest pytest with enhanced testing features",
                performance_impact="low"
            ),
            "black": LibraryInfo(
                name="black",
                current_version="23.11.0",
                target_version="24.0.0",
                category=LibraryCategory.DEVELOPMENT,
                description="Latest Black with improved code formatting",
                performance_impact="low"
            ),
            "mypy": LibraryInfo(
                name="mypy",
                current_version="1.7.1",
                target_version="1.8.0",
                category=LibraryCategory.DEVELOPMENT,
                description="Enhanced type checking with better error detection",
                performance_impact="low"
            ),
            "spacy": LibraryInfo(
                name="spacy",
                current_version="3.7.2",
                target_version="3.8.0",
                category=LibraryCategory.SPECIALIZED,
                description="Latest spaCy with enhanced NLP models",
                performance_impact="medium"
            ),
            "opencv-python": LibraryInfo(
                name="opencv-python",
                current_version="4.8.1",
                target_version="4.9.0",
                category=LibraryCategory.SPECIALIZED,
                description="Latest OpenCV with enhanced computer vision capabilities",
                performance_impact="medium"
            ),
            "prometheus-client": LibraryInfo(
                name="prometheus-client",
                current_version="0.19.0",
                target_version="0.21.0",
                category=LibraryCategory.MONITORING,
                description="Enhanced Prometheus client with better metrics collection",
                performance_impact="low"
            ),
            "cryptography": LibraryInfo(
                name="cryptography",
                current_version="41.0.0",
                target_version="42.0.0",
                category=LibraryCategory.SECURITY,
                description="Latest cryptography with enhanced security features",
                security_impact="high"
            )
        })
    
    async def analyze_current_environment(self) -> Dict[str, Any]:
        """Analyze current library environment."""
        logger.info("🔍 Analyzing current library environment...")
        
        analysis = {
            "installed_libraries": {},
            "outdated_libraries": [],
            "security_vulnerabilities": [],
            "performance_issues": [],
            "conflicts": []
        }
        
        # Get installed packages
        try:
            installed_packages = pkg_resources.working_set
            for package in installed_packages:
                analysis["installed_libraries"][package.key] = package.version
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
        
        # Check for outdated libraries
        for lib_name, lib_info in self.library_info.items():
            if lib_name in analysis["installed_libraries"]:
                current_version = analysis["installed_libraries"][lib_name]
                if current_version != lib_info.target_version:
                    analysis["outdated_libraries"].append({
                        "name": lib_name,
                        "current": current_version,
                        "target": lib_info.target_version,
                        "category": lib_info.category.value
                    })
        
        logger.info(f"📊 Found {len(analysis['outdated_libraries'])} outdated libraries")
        return analysis
    
    async def check_security_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities in current libraries."""
        logger.info("🔒 Checking for security vulnerabilities...")
        
        vulnerabilities = []
        
        # Check using safety
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                vuln_data = json.loads(result.stdout)
                for vuln in vuln_data:
                    vulnerabilities.append({
                        "package": vuln.get("package"),
                        "vulnerability": vuln.get("vulnerability"),
                        "severity": vuln.get("severity"),
                        "description": vuln.get("description")
                    })
        except Exception as e:
            logger.warning(f"Could not run safety check: {e}")
        
        logger.info(f"🔒 Found {len(vulnerabilities)} security vulnerabilities")
        return vulnerabilities
    
    async def generate_migration_plan(self, categories: List[LibraryCategory] = None) -> Dict[str, Any]:
        """Generate a comprehensive migration plan."""
        logger.info("📋 Generating migration plan...")
        
        if categories is None:
            categories = list(LibraryCategory)
        
        plan = {
            "phases": [],
            "estimated_duration": 0,
            "risk_assessment": {},
            "rollback_plan": {},
            "testing_strategy": {}
        }
        
        # Phase 1: Core Framework (Low Risk)
        core_phase = {
            "name": "Core Framework Upgrade",
            "duration": "2-3 hours",
            "libraries": [],
            "risk_level": "low",
            "dependencies": []
        }
        
        for lib_name, lib_info in self.library_info.items():
            if lib_info.category == LibraryCategory.CORE and lib_info.category in categories:
                core_phase["libraries"].append(lib_name)
        
        plan["phases"].append(core_phase)
        
        # Phase 2: Performance Libraries (Medium Risk)
        perf_phase = {
            "name": "Performance Libraries Upgrade",
            "duration": "3-4 hours",
            "libraries": [],
            "risk_level": "medium",
            "dependencies": []
        }
        
        for lib_name, lib_info in self.library_info.items():
            if lib_info.category == LibraryCategory.PERFORMANCE and lib_info.category in categories:
                perf_phase["libraries"].append(lib_name)
        
        plan["phases"].append(perf_phase)
        
        # Phase 3: Development Tools (Low Risk)
        dev_phase = {
            "name": "Development Tools Upgrade",
            "duration": "1-2 hours",
            "libraries": [],
            "risk_level": "low",
            "dependencies": []
        }
        
        for lib_name, lib_info in self.library_info.items():
            if lib_info.category == LibraryCategory.DEVELOPMENT and lib_info.category in categories:
                dev_phase["libraries"].append(lib_name)
        
        plan["phases"].append(dev_phase)
        
        # Phase 4: Specialized Libraries (High Risk)
        spec_phase = {
            "name": "Specialized Libraries Upgrade",
            "duration": "4-6 hours",
            "libraries": [],
            "risk_level": "high",
            "dependencies": []
        }
        
        for lib_name, lib_info in self.library_info.items():
            if lib_info.category == LibraryCategory.SPECIALIZED and lib_info.category in categories:
                spec_phase["libraries"].append(lib_name)
        
        plan["phases"].append(spec_phase)
        
        logger.info(f"📋 Generated migration plan with {len(plan['phases'])} phases")
        return plan
    
    async def migrate_library(self, library_name: str, dry_run: bool = False) -> MigrationResult:
        """Migrate a single library to its target version."""
        logger.info(f"🔄 Migrating {library_name}...")
        
        if library_name not in self.library_info:
            return MigrationResult(
                library_name=library_name,
                status=MigrationStatus.FAILED,
                old_version="unknown",
                new_version="unknown",
                duration=0,
                error_message="Library not found in migration info"
            )
        
        lib_info = self.library_info[library_name]
        start_time = time.time()
        
        try:
            # Get current version
            current_version = "unknown"
            try:
                result = subprocess.run(
                    ["pip", "show", library_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            current_version = line.split(':')[1].strip()
                            break
            except Exception as e:
                logger.warning(f"Could not get current version for {library_name}: {e}")
            
            if dry_run:
                logger.info(f"🔍 DRY RUN: Would upgrade {library_name} from {current_version} to {lib_info.target_version}")
                return MigrationResult(
                    library_name=library_name,
                    status=MigrationStatus.SKIPPED,
                    old_version=current_version,
                    new_version=lib_info.target_version,
                    duration=time.time() - start_time
                )
            
            # Perform upgrade
            upgrade_command = [
                "pip", "install", "--upgrade",
                f"{library_name}>={lib_info.target_version}"
            ]
            
            result = subprocess.run(
                upgrade_command,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully upgraded {library_name} to {lib_info.target_version}")
                return MigrationResult(
                    library_name=library_name,
                    status=MigrationStatus.COMPLETED,
                    old_version=current_version,
                    new_version=lib_info.target_version,
                    duration=time.time() - start_time
                )
            else:
                logger.error(f"❌ Failed to upgrade {library_name}: {result.stderr}")
                return MigrationResult(
                    library_name=library_name,
                    status=MigrationStatus.FAILED,
                    old_version=current_version,
                    new_version=lib_info.target_version,
                    duration=time.time() - start_time,
                    error_message=result.stderr
                )
                
        except Exception as e:
            logger.error(f"❌ Error migrating {library_name}: {e}")
            return MigrationResult(
                library_name=library_name,
                status=MigrationStatus.FAILED,
                old_version="unknown",
                new_version=lib_info.target_version,
                duration=time.time() - start_time,
                error_message=str(e)
            )
    
    async def migrate_category(self, category: LibraryCategory, dry_run: bool = False) -> List[MigrationResult]:
        """Migrate all libraries in a specific category."""
        logger.info(f"🔄 Migrating {category.value} libraries...")
        
        results = []
        category_libraries = [
            lib_name for lib_name, lib_info in self.library_info.items()
            if lib_info.category == category
        ]
        
        for library_name in category_libraries:
            result = await self.migrate_library(library_name, dry_run)
            results.append(result)
            self.migration_results.append(result)
            
            # Add delay between migrations to avoid overwhelming the system
            if not dry_run:
                await asyncio.sleep(1)
        
        logger.info(f"✅ Completed {category.value} migration: {len([r for r in results if r.status == MigrationStatus.COMPLETED])} successful")
        return results
    
    async def run_comprehensive_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run comprehensive migration across all categories."""
        logger.info("🚀 Starting comprehensive library migration...")
        
        start_time = time.time()
        migration_summary = {
            "total_libraries": len(self.library_info),
            "migrated": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0,
            "results": []
        }
        
        # Run migrations by category in order of risk
        categories_order = [
            LibraryCategory.CORE,      # Lowest risk
            LibraryCategory.DEVELOPMENT,
            LibraryCategory.MONITORING,
            LibraryCategory.SECURITY,
            LibraryCategory.PERFORMANCE,
            LibraryCategory.SPECIALIZED  # Highest risk
        ]
        
        for category in categories_order:
            logger.info(f"🔄 Processing {category.value} category...")
            results = await self.migrate_category(category, dry_run)
            migration_summary["results"].extend(results)
        
        migration_summary["duration"] = time.time() - start_time
        migration_summary["migrated"] = len([r for r in migration_summary["results"] if r.status == MigrationStatus.COMPLETED])
        migration_summary["failed"] = len([r for r in migration_summary["results"] if r.status == MigrationStatus.FAILED])
        migration_summary["skipped"] = len([r for r in migration_summary["results"] if r.status == MigrationStatus.SKIPPED])
        
        logger.info(f"✅ Migration completed: {migration_summary['migrated']} successful, {migration_summary['failed']} failed")
        return migration_summary
    
    def generate_migration_report(self) -> str:
        """Generate a comprehensive migration report."""
        logger.info("📊 Generating migration report...")
        
        report = []
        report.append("# 📚 LIBRARY MIGRATION REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        total = len(self.migration_results)
        completed = len([r for r in self.migration_results if r.status == MigrationStatus.COMPLETED])
        failed = len([r for r in self.migration_results if r.status == MigrationStatus.FAILED])
        skipped = len([r for r in self.migration_results if r.status == MigrationStatus.SKIPPED])
        
        report.append(f"## 📊 Summary")
        report.append(f"- **Total Libraries**: {total}")
        report.append(f"- **Successfully Migrated**: {completed}")
        report.append(f"- **Failed**: {failed}")
        report.append(f"- **Skipped**: {skipped}")
        report.append(f"- **Success Rate**: {(completed/total*100):.1f}%")
        report.append("")
        
        # Detailed Results
        report.append("## 📋 Detailed Results")
        report.append("")
        
        for result in self.migration_results:
            status_emoji = {
                MigrationStatus.COMPLETED: "✅",
                MigrationStatus.FAILED: "❌",
                MigrationStatus.SKIPPED: "⏭️",
                MigrationStatus.IN_PROGRESS: "🔄",
                MigrationStatus.PENDING: "⏳"
            }
            
            report.append(f"### {status_emoji[result.status]} {result.library_name}")
            report.append(f"- **Status**: {result.status.value}")
            report.append(f"- **Version**: {result.old_version} → {result.new_version}")
            report.append(f"- **Duration**: {result.duration:.2f}s")
            
            if result.error_message:
                report.append(f"- **Error**: {result.error_message}")
            
            if result.warnings:
                report.append(f"- **Warnings**: {', '.join(result.warnings)}")
            
            report.append("")
        
        # Recommendations
        report.append("## 🎯 Recommendations")
        report.append("")
        
        if failed > 0:
            report.append("### ⚠️ Failed Migrations")
            failed_libs = [r for r in self.migration_results if r.status == MigrationStatus.FAILED]
            for lib in failed_libs:
                report.append(f"- **{lib.library_name}**: {lib.error_message}")
            report.append("")
        
        if completed > 0:
            report.append("### ✅ Successful Migrations")
            completed_libs = [r for r in self.migration_results if r.status == MigrationStatus.COMPLETED]
            for lib in completed_libs:
                lib_info = self.library_info.get(lib.library_name)
                if lib_info:
                    report.append(f"- **{lib.library_name}**: {lib_info.description}")
            report.append("")
        
        report.append("### 🚀 Next Steps")
        report.append("1. **Test the application** thoroughly after migration")
        report.append("2. **Update documentation** to reflect new library versions")
        report.append("3. **Monitor performance** to ensure improvements")
        report.append("4. **Update CI/CD pipelines** with new requirements")
        report.append("5. **Train team** on new library features")
        
        return "\n".join(report)

# Main execution
async def main():
    """Main execution function."""
    logger.info("🚀 Starting Library Migration Manager...")
    
    # Initialize manager
    manager = LibraryMigrationManager()
    
    # Analyze current environment
    analysis = await manager.analyze_current_environment()
    logger.info(f"📊 Found {len(analysis['outdated_libraries'])} outdated libraries")
    
    # Check security vulnerabilities
    vulnerabilities = await manager.check_security_vulnerabilities()
    if vulnerabilities:
        logger.warning(f"🔒 Found {len(vulnerabilities)} security vulnerabilities")
    
    # Generate migration plan
    plan = await manager.generate_migration_plan()
    logger.info(f"📋 Generated migration plan with {len(plan['phases'])} phases")
    
    # Run comprehensive migration (dry run first)
    logger.info("🔍 Running dry run migration...")
    dry_run_results = await manager.run_comprehensive_migration(dry_run=True)
    
    # Generate report
    report = manager.generate_migration_report()
    
    # Save report
    with open("library_migration_report.md", "w") as f:
        f.write(report)
    
    logger.info("✅ Migration analysis completed. Check library_migration_report.md for details.")
    
    # Ask user if they want to proceed with actual migration
    print("\n" + "="*60)
    print("📚 LIBRARY MIGRATION ANALYSIS COMPLETED")
    print("="*60)
    print(f"📊 Found {len(analysis['outdated_libraries'])} outdated libraries")
    print(f"🔒 Found {len(vulnerabilities)} security vulnerabilities")
    print(f"✅ Dry run completed: {dry_run_results['migrated']} would be migrated")
    print(f"❌ {dry_run_results['failed']} would fail")
    print("\n📄 Full report saved to: library_migration_report.md")
    print("\n🚀 To proceed with actual migration, run:")
    print("   python library_migration_manager.py --migrate")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Library Migration Manager")
    parser.add_argument("--migrate", action="store_true", help="Perform actual migration")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--category", choices=[cat.value for cat in LibraryCategory], help="Migrate specific category")
    
    args = parser.parse_args()
    
    if args.migrate:
        # Run actual migration
        async def run_migration():
            manager = LibraryMigrationManager()
            if args.category:
                category = LibraryCategory(args.category)
                await manager.migrate_category(category, dry_run=args.dry_run)
            else:
                await manager.run_comprehensive_migration(dry_run=args.dry_run)
            
            report = manager.generate_migration_report()
            with open("library_migration_report.md", "w") as f:
                f.write(report)
            print("✅ Migration completed. Check library_migration_report.md for details.")
        
        asyncio.run(run_migration())
    else:
        # Run analysis
        asyncio.run(main()) 