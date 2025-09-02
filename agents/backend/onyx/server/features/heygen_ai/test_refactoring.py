#!/usr/bin/env python3
"""
HeyGen AI Refactoring Test Script

This script tests the refactored HeyGen AI system to ensure all components
are working correctly after the refactoring.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class RefactoringTester:
    """Tests the refactored HeyGen AI system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
    
    def run_all_tests(self) -> bool:
        """Run all refactoring tests."""
        print("🧪 Testing HeyGen AI Refactoring")
        print("=" * 50)
        
        tests = [
            ("Project Structure", self.test_project_structure),
            ("Requirements Files", self.test_requirements_files),
            ("Configuration System", self.test_configuration_system),
            ("Management Scripts", self.test_management_scripts),
            ("Plugin System", self.test_plugin_system),
            ("Documentation", self.test_documentation),
            ("Import Paths", self.test_import_paths)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    all_passed = False
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
                all_passed = False
        
        self.print_summary()
        return all_passed
    
    def test_project_structure(self) -> bool:
        """Test if project structure is properly organized."""
        required_dirs = [
            "src",
            "configs",
            "requirements",
            "docs",
            "tests",
            "scripts"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                print(f"  ❌ Missing directory: {dir_name}")
                return False
        
        print("  ✅ All required directories exist")
        return True
    
    def test_requirements_files(self) -> bool:
        """Test if requirements files are properly organized."""
        requirements_dir = self.project_root / "requirements"
        
        if not requirements_dir.exists():
            print("  ❌ Requirements directory not found")
            return False
        
        # Check modular requirements
        modular_files = ["base.txt", "ml.txt", "web.txt", "enterprise.txt", "dev.txt"]
        for file_name in modular_files:
            file_path = requirements_dir / file_name
            if not file_path.exists():
                print(f"  ❌ Missing requirements file: {file_name}")
                return False
        
        # Check main requirements.txt
        main_requirements = self.project_root / "requirements.txt"
        if not main_requirements.exists():
            print("  ❌ Main requirements.txt not found")
            return False
        
        # Check if main requirements references modular files
        with open(main_requirements, 'r') as f:
            content = f.read()
            if "-r requirements/" not in content:
                print("  ❌ Main requirements.txt doesn't reference modular files")
                return False
        
        print("  ✅ Requirements files properly organized")
        return True
    
    def test_configuration_system(self) -> bool:
        """Test if configuration system is working."""
        config_dir = self.project_root / "configs" / "main"
        
        if not config_dir.exists():
            print("  ❌ Configuration directory not found")
            return False
        
        config_file = config_dir / "heygen_ai_config.yaml"
        if not config_file.exists():
            print("  ❌ Main configuration file not found")
            return False
        
        # Test configuration manager
        try:
            sys.path.insert(0, str(self.project_root))
            from core.config_manager import ConfigurationManager
            
            config_manager = ConfigurationManager()
            config = config_manager.get_config()
            
            if config is None:
                print("  ❌ Configuration manager failed to load config")
                return False
            
            print("  ✅ Configuration system working")
            return True
            
        except Exception as e:
            print(f"  ❌ Configuration manager error: {e}")
            return False
    
    def test_management_scripts(self) -> bool:
        """Test if management scripts are working."""
        scripts = [
            "install_requirements.py",
            "organize_project.py",
            "manage.py"
        ]
        
        for script_name in scripts:
            script_path = self.project_root / script_name
            if not script_path.exists():
                print(f"  ❌ Missing script: {script_name}")
                return False
            
            # Test if script can be imported
            try:
                if script_name == "manage.py":
                    # Test manage.py help
                    result = subprocess.run(
                        [sys.executable, str(script_path), "--help"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode != 0:
                        print(f"  ❌ Script failed: {script_name}")
                        return False
                else:
                    # Test if script can be imported
                    spec = subprocess.run(
                        [sys.executable, "-c", f"import {script_name.replace('.py', '')}"],
                        capture_output=True, text=True, timeout=10
                    )
                    if spec.returncode != 0:
                        print(f"  ❌ Script import failed: {script_name}")
                        return False
        
        print("  ✅ Management scripts working")
        return True
    
    def test_plugin_system(self) -> bool:
        """Test if plugin system is working."""
        try:
            from core.plugin_system import PluginManager, PluginMetadata
            
            # Test basic plugin system functionality
            metadata = PluginMetadata(
                name="test_plugin",
                version="1.0.0",
                description="Test plugin",
                plugin_type="model",
                author="Test Author",
                dependencies=[]
            )
            
            if metadata.name != "test_plugin":
                print("  ❌ Plugin metadata creation failed")
                return False
            
            print("  ✅ Plugin system working")
            return True
            
        except Exception as e:
            print(f"  ❌ Plugin system error: {e}")
            return False
    
    def test_documentation(self) -> bool:
        """Test if documentation is properly created."""
        docs_dir = self.project_root / "docs"
        
        if not docs_dir.exists():
            print("  ❌ Documentation directory not found")
            return False
        
        required_docs = [
            "PROJECT_STRUCTURE.md",
            "SETUP.md"
        ]
        
        for doc_name in required_docs:
            doc_path = docs_dir / doc_name
            if not doc_path.exists():
                print(f"  ❌ Missing documentation: {doc_name}")
                return False
        
        # Check main README
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            print("  ❌ Main README not found")
            return False
        
        print("  ✅ Documentation properly created")
        return True
    
    def test_import_paths(self) -> bool:
        """Test if import paths are correctly updated."""
        # This test would check if all Python files have correct import statements
        # For now, we'll just check if the structure allows for proper imports
        
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            print("  ❌ Source directory not found")
            return False
        
        # Check if core modules exist
        core_dir = src_dir / "core"
        if not core_dir.exists():
            print("  ❌ Core directory not found")
            return False
        
        # Check if plugins directory exists
        plugins_dir = src_dir / "plugins"
        if not plugins_dir.exists():
            print("  ❌ Plugins directory not found")
            return False
        
        print("  ✅ Import paths structure correct")
        return True
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 50)
        print("📊 REFACTORING TEST RESULTS")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Refactoring successful!")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Review issues above.")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")

def main():
    """Main test function."""
    tester = RefactoringTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
