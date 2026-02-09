#!/usr/bin/env python3
"""
Automated Type Annotation Fixer
Fixes invalid type annotation syntax: `: type: type =` → `: type =`
"""

import re
import os
from pathlib import Path
from typing import List, Tuple

class TypeAnnotationFixer:
    """Fixes invalid type annotation syntax in Python files."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.fixed_files: List[str] = []
        self.total_fixes: int = 0
        
    def fix_file(self, file_path: Path) -> Tuple[int, bool]:
        """
        Fix type annotations in a single file.
        
        Returns:
            Tuple of (number of fixes, success)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            fixes = 0
            
            # Fix pattern: : type: type = → : type =
            patterns = [
                (r':\s*int\s*:\s*int\s*=', ': int ='),
                (r':\s*str\s*:\s*str\s*=', ': str ='),
                (r':\s*bool\s*:\s*bool\s*=', ': bool ='),
                (r':\s*float\s*:\s*float\s*=', ': float ='),
                (r':\s*list\s*:\s*list\s*=', ': list ='),
                (r':\s*dict\s*:\s*dict\s*=', ': dict ='),
                (r':\s*tuple\s*:\s*tuple\s*=', ': tuple ='),
                (r':\s*Any\s*:\s*Any\s*=', ': Any ='),
                (r':\s*Optional\s*:\s*Optional\s*=', ': Optional ='),
            ]
            
            for pattern, replacement in patterns:
                matches = len(re.findall(pattern, content))
                if matches > 0:
                    content = re.sub(pattern, replacement, content)
                    fixes += matches
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return fixes, True
            
            return 0, True
            
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return 0, False
    
    def scan_and_fix(self, max_files: int = 100) -> dict:
        """
        Scan directory and fix type annotations.
        
        Args:
            max_files: Maximum number of files to process
            
        Returns:
            Dictionary with statistics
        """
        count = 0
        total_fixes = 0
        
        # Focus on Python files in key directories
        key_dirs = [
            "agents/backend/onyx/server/features",
            "core",
            "utils",
        ]
        
        for dir_path in key_dirs:
            full_path = self.root_dir / dir_path
            if not full_path.exists():
                continue
                
            for file_path in full_path.rglob("*.py"):
                if count >= max_files:
                    break
                    
                # Skip common directories
                if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']):
                    continue
                
                fixes, success = self.fix_file(file_path)
                if fixes > 0:
                    self.fixed_files.append(str(file_path))
                    total_fixes += fixes
                    print(f"✅ Fixed {fixes} annotations in {file_path}")
                
                count += 1
                if count >= max_files:
                    break
        
        self.total_fixes = total_fixes
        
        return {
            "files_processed": count,
            "files_fixed": len(self.fixed_files),
            "total_fixes": total_fixes,
            "fixed_files": self.fixed_files
        }
    
    def generate_report(self) -> str:
        """Generate a report of fixes."""
        report = []
        report.append("=" * 80)
        report.append("TYPE ANNOTATION FIX REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Files Processed: {len(self.fixed_files)}")
        report.append(f"Total Fixes: {self.total_fixes}")
        report.append("")
        
        if self.fixed_files:
            report.append("Fixed Files:")
            report.append("-" * 80)
            for file_path in self.fixed_files[:20]:  # Limit to first 20
                report.append(f"  - {file_path}")
            if len(self.fixed_files) > 20:
                report.append(f"  ... and {len(self.fixed_files) - 20} more files")
        
        return "\n".join(report)


def main():
    """Main entry point."""
    print("🔧 Type Annotation Fixer")
    print("=" * 80)
    
    fixer = TypeAnnotationFixer()
    stats = fixer.scan_and_fix(max_files=50)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files Processed: {stats['files_processed']}")
    print(f"Files Fixed: {stats['files_fixed']}")
    print(f"Total Fixes: {stats['total_fixes']}")
    
    # Generate report
    report = fixer.generate_report()
    with open("TYPE_ANNOTATION_FIX_REPORT.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n✅ Report saved to TYPE_ANNOTATION_FIX_REPORT.txt")


if __name__ == "__main__":
    main()





