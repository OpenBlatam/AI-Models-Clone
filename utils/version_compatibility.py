"""
Version Compatibility Checker

This module checks version compatibility between installed packages
and their documentation requirements.
"""

import pkg_resources
import requests
import json
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

@dataclass
class VersionInfo:
    """Version information for a package."""
    package_name: str
    installed_version: str
    latest_version: str
    min_required: str
    compatible: bool
    issues: List[str]

class VersionCompatibilityChecker:
    """Check version compatibility for ML/AI libraries."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Version requirements from documentation
        self.version_requirements = {
            "torch": {
                "min_version": "2.0.0",
                "recommended": "2.1.0",
                "documentation_url": "https://pytorch.org/docs/stable/"
            },
            "transformers": {
                "min_version": "4.30.0",
                "recommended": "4.35.0",
                "documentation_url": "https://huggingface.co/docs/transformers/"
            },
            "diffusers": {
                "min_version": "0.20.0",
                "recommended": "0.24.0",
                "documentation_url": "https://huggingface.co/docs/diffusers/"
            },
            "gradio": {
                "min_version": "3.40.0",
                "recommended": "4.0.0",
                "documentation_url": "https://gradio.app/docs/"
            },
            "numpy": {
                "min_version": "1.24.0",
                "recommended": "1.25.0",
                "documentation_url": "https://numpy.org/doc/"
            },
            "scikit-learn": {
                "min_version": "1.3.0",
                "recommended": "1.3.0",
                "documentation_url": "https://scikit-learn.org/stable/"
            }
        }
    
    def get_installed_versions(self) -> Dict[str, str]:
        """Get currently installed package versions."""
        installed_versions = {}
        
        for package_name in self.version_requirements.keys():
            try:
                version = pkg_resources.get_distribution(package_name).version
                installed_versions[package_name] = version
            except pkg_resources.DistributionNotFound:
                installed_versions[package_name] = "not_installed"
        
        return installed_versions
    
    def get_latest_versions(self) -> Dict[str, str]:
        """Get latest available versions from PyPI."""
        latest_versions = {}
        
        for package_name in self.version_requirements.keys():
            try:
                response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
                if response.status_code == 200:
                    data = response.json()
                    latest_versions[package_name] = data['info']['version']
                else:
                    latest_versions[package_name] = "unknown"
            except Exception as e:
                self.logger.warning(f"Could not fetch latest version for {package_name}: {e}")
                latest_versions[package_name] = "unknown"
        
        return latest_versions
    
    def check_compatibility(self) -> Dict[str, VersionInfo]:
        """Check compatibility for all packages."""
        installed_versions = self.get_installed_versions()
        latest_versions = self.get_latest_versions()
        
        compatibility_info = {}
        
        for package_name, requirements in self.version_requirements.items():
            installed_version = installed_versions.get(package_name, "not_installed")
            latest_version = latest_versions.get(package_name, "unknown")
            min_required = requirements["min_version"]
            
            issues = []
            compatible = True
            
            if installed_version == "not_installed":
                issues.append("Package not installed")
                compatible = False
            else:
                # Compare versions
                if not self._version_greater_equal(installed_version, min_required):
                    issues.append(f"Version {installed_version} is below minimum required {min_required}")
                    compatible = False
                
                if latest_version != "unknown" and installed_version != latest_version:
                    issues.append(f"Not using latest version (latest: {latest_version})")
            
            compatibility_info[package_name] = VersionInfo(
                package_name=package_name,
                installed_version=installed_version,
                latest_version=latest_version,
                min_required=min_required,
                compatible=compatible,
                issues=issues
            )
        
        return compatibility_info
    
    def _version_greater_equal(self, version1: str, version2: str) -> bool:
        """Compare two version strings."""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad with zeros if needed
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            return v1_parts >= v2_parts
        except Exception:
            return False
    
    def generate_compatibility_report(self) -> str:
        """Generate a human-readable compatibility report."""
        compatibility_info = self.check_compatibility()
        
        report = "📦 Version Compatibility Report\n"
        report += "=" * 50 + "\n\n"
        
        all_compatible = True
        
        for package_name, info in compatibility_info.items():
            status_icon = "✅" if info.compatible else "❌"
            report += f"{status_icon} {package_name}\n"
            report += f"   Installed: {info.installed_version}\n"
            report += f"   Latest: {info.latest_version}\n"
            report += f"   Min Required: {info.min_required}\n"
            
            if info.issues:
                report += f"   Issues:\n"
                for issue in info.issues:
                    report += f"     - {issue}\n"
                all_compatible = False
            
            report += "\n"
        
        # Summary
        report += "📊 Summary\n"
        report += "-" * 20 + "\n"
        compatible_count = sum(1 for info in compatibility_info.values() if info.compatible)
        total_count = len(compatibility_info)
        
        report += f"Compatible: {compatible_count}/{total_count}\n"
        
        if all_compatible:
            report += "🎉 All packages are compatible with documentation requirements!\n"
        else:
            report += "⚠️  Some packages need updates for full compatibility.\n"
        
        return report
    
    def get_upgrade_commands(self) -> List[str]:
        """Get pip upgrade commands for outdated packages."""
        compatibility_info = self.check_compatibility()
        upgrade_commands = []
        
        for package_name, info in compatibility_info.items():
            if not info.compatible and info.installed_version != "not_installed":
                if info.latest_version != "unknown":
                    upgrade_commands.append(f"pip install --upgrade {package_name}")
                else:
                    upgrade_commands.append(f"pip install --upgrade {package_name}")
            elif info.installed_version == "not_installed":
                upgrade_commands.append(f"pip install {package_name}")
        
        return upgrade_commands
    
    def check_documentation_compatibility(self, library: str) -> Dict[str, Any]:
        """Check if current version is compatible with documentation."""
        compatibility_info = self.check_compatibility()
        
        if library not in compatibility_info:
            return {"compatible": False, "message": f"Unknown library: {library}"}
        
        info = compatibility_info[library]
        
        return {
            "compatible": info.compatible,
            "installed_version": info.installed_version,
            "min_required": info.min_required,
            "latest_version": info.latest_version,
            "issues": info.issues,
            "documentation_url": self.version_requirements[library]["documentation_url"]
        }

def main():
    """Main function to run compatibility check."""
    checker = VersionCompatibilityChecker()
    
    print(checker.generate_compatibility_report())
    
    upgrade_commands = checker.get_upgrade_commands()
    if upgrade_commands:
        print("\n🔧 Upgrade Commands:")
        print("-" * 20)
        for command in upgrade_commands:
            print(command)

if __name__ == "__main__":
    main()
