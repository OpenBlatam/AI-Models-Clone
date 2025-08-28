"""
Best Practices Checker for ML/AI Projects

This module checks code against official best practices from PyTorch,
Transformers, Diffusers, and Gradio documentation.
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging

@dataclass
class PracticeViolation:
    """Represents a best practice violation."""
    rule_id: str
    rule_name: str
    severity: str  # "error", "warning", "info"
    message: str
    line_number: int
    code_snippet: str
    suggestion: str
    documentation_url: str

class BestPracticesChecker:
    """Checker for best practices from official documentation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.violations = []
        
        # Load best practices rules
        self.rules = self._load_best_practices_rules()
    
    def _load_best_practices_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load best practices rules from configuration."""
        return {
            "pytorch": {
                "PY001": {
                    "name": "Use torch.no_grad() for inference",
                    "severity": "warning",
                    "pattern": r"model\(.*\)",
                    "context": "inference",
                    "suggestion": "Wrap model calls with torch.no_grad() for inference",
                    "doc_url": "https://pytorch.org/docs/stable/generated/torch.no_grad.html"
                },
                "PY002": {
                    "name": "Use device placement consistently",
                    "severity": "warning",
                    "pattern": r"\.to\(device\)",
                    "context": "model_creation",
                    "suggestion": "Ensure consistent device placement across model and data",
                    "doc_url": "https://pytorch.org/docs/stable/tensor_attributes.html#torch.device"
                },
                "PY003": {
                    "name": "Use proper loss function",
                    "severity": "error",
                    "pattern": r"nn\.(CrossEntropyLoss|MSELoss|BCELoss)",
                    "context": "training",
                    "suggestion": "Choose appropriate loss function for your task",
                    "doc_url": "https://pytorch.org/docs/stable/nn.html#loss-functions"
                },
                "PY004": {
                    "name": "Use DataLoader for batching",
                    "severity": "warning",
                    "pattern": r"for.*in.*data",
                    "context": "data_loading",
                    "suggestion": "Use torch.utils.data.DataLoader for efficient batching",
                    "doc_url": "https://pytorch.org/docs/stable/data.html"
                },
                "PY005": {
                    "name": "Use model.eval() for evaluation",
                    "severity": "warning",
                    "pattern": r"model\(.*\)",
                    "context": "evaluation",
                    "suggestion": "Call model.eval() before evaluation",
                    "doc_url": "https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval"
                }
            },
            "transformers": {
                "TF001": {
                    "name": "Use AutoTokenizer for tokenization",
                    "severity": "warning",
                    "pattern": r"tokenizer\s*=",
                    "context": "tokenization",
                    "suggestion": "Use AutoTokenizer.from_pretrained() for consistency",
                    "doc_url": "https://huggingface.co/docs/transformers/main_classes/tokenizer"
                },
                "TF002": {
                    "name": "Use pipeline for simple tasks",
                    "severity": "info",
                    "pattern": r"pipeline\(",
                    "context": "inference",
                    "suggestion": "Consider using pipeline() for simple inference tasks",
                    "doc_url": "https://huggingface.co/docs/transformers/main_classes/pipelines"
                },
                "TF003": {
                    "name": "Handle attention masks properly",
                    "severity": "warning",
                    "pattern": r"attention_mask",
                    "context": "model_input",
                    "suggestion": "Ensure attention masks are properly handled",
                    "doc_url": "https://huggingface.co/docs/transformers/glossary#attention-mask"
                },
                "TF004": {
                    "name": "Use proper model loading",
                    "severity": "error",
                    "pattern": r"from_pretrained\(",
                    "context": "model_loading",
                    "suggestion": "Use AutoModel.from_pretrained() with proper error handling",
                    "doc_url": "https://huggingface.co/docs/transformers/main_classes/model"
                }
            },
            "diffusers": {
                "DF001": {
                    "name": "Use proper scheduler",
                    "severity": "warning",
                    "pattern": r"scheduler\s*=",
                    "context": "pipeline_setup",
                    "suggestion": "Choose appropriate scheduler for your use case",
                    "doc_url": "https://huggingface.co/docs/diffusers/api/schedulers/overview"
                },
                "DF002": {
                    "name": "Set proper inference steps",
                    "severity": "info",
                    "pattern": r"num_inference_steps",
                    "context": "inference",
                    "suggestion": "Adjust num_inference_steps for quality vs speed trade-off",
                    "doc_url": "https://huggingface.co/docs/diffusers/using-diffusers/pipeline_overview"
                },
                "DF003": {
                    "name": "Use guidance scale for better control",
                    "severity": "info",
                    "pattern": r"guidance_scale",
                    "context": "generation",
                    "suggestion": "Use guidance_scale parameter for better generation control",
                    "doc_url": "https://huggingface.co/docs/diffusers/using-diffusers/pipeline_overview"
                }
            },
            "gradio": {
                "GR001": {
                    "name": "Use proper input validation",
                    "severity": "warning",
                    "pattern": r"gr\.(Textbox|Number|Slider)",
                    "context": "interface_creation",
                    "suggestion": "Add proper validation to input components",
                    "doc_url": "https://gradio.app/docs/components"
                },
                "GR002": {
                    "name": "Handle errors gracefully",
                    "severity": "error",
                    "pattern": r"try:",
                    "context": "error_handling",
                    "suggestion": "Implement proper error handling in Gradio functions",
                    "doc_url": "https://gradio.app/docs/troubleshooting"
                },
                "GR003": {
                    "name": "Use appropriate output components",
                    "severity": "info",
                    "pattern": r"gr\.(Text|Image|Plot)",
                    "context": "output_components",
                    "suggestion": "Choose appropriate output components for your data type",
                    "doc_url": "https://gradio.app/docs/components"
                },
                "GR004": {
                    "name": "Add proper descriptions",
                    "severity": "info",
                    "pattern": r"description\s*=",
                    "context": "interface_creation",
                    "suggestion": "Add descriptions to help users understand the interface",
                    "doc_url": "https://gradio.app/docs/interface"
                }
            }
        }
    
    def check_file(self, file_path: Path, library: str = None) -> List[PracticeViolation]:
        """Check a Python file for best practice violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            violations = []
            
            # Check based on library
            if library and library.lower() in self.rules:
                violations.extend(self._check_library_rules(content, library.lower(), file_path))
            else:
                # Check all libraries
                for lib in self.rules:
                    violations.extend(self._check_library_rules(content, lib, file_path))
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error checking file {file_path}: {e}")
            return []
    
    def _check_library_rules(self, content: str, library: str, file_path: Path) -> List[PracticeViolation]:
        """Check content against library-specific rules."""
        violations = []
        
        lines = content.split('\n')
        
        for rule_id, rule in self.rules[library].items():
            pattern = rule['pattern']
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Check context if specified
                    if 'context' in rule:
                        context_lines = self._get_context_lines(lines, line_num, 5)
                        if not self._check_context(context_lines, rule['context']):
                            continue
                    
                    violation = PracticeViolation(
                        rule_id=rule_id,
                        rule_name=rule['name'],
                        severity=rule['severity'],
                        message=f"{rule['name']} violation detected",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=rule['suggestion'],
                        documentation_url=rule['doc_url']
                    )
                    
                    violations.append(violation)
        
        return violations
    
    def _get_context_lines(self, lines: List[str], line_num: int, context_size: int) -> List[str]:
        """Get context lines around a specific line."""
        start = max(0, line_num - context_size - 1)
        end = min(len(lines), line_num + context_size)
        return lines[start:end]
    
    def _check_context(self, context_lines: List[str], context_type: str) -> bool:
        """Check if context lines match the expected context."""
        context_text = '\n'.join(context_lines).lower()
        
        context_patterns = {
            "inference": ["inference", "predict", "forward", "eval"],
            "training": ["train", "loss", "optimizer", "backward"],
            "model_creation": ["model", "nn", "module", "class"],
            "data_loading": ["data", "dataset", "loader", "batch"],
            "evaluation": ["eval", "test", "validate", "accuracy"],
            "tokenization": ["token", "encode", "decode", "text"],
            "model_input": ["input", "attention", "mask", "padding"],
            "model_loading": ["load", "pretrained", "from_pretrained"],
            "pipeline_setup": ["pipeline", "scheduler", "diffusion"],
            "generation": ["generate", "sample", "guidance"],
            "interface_creation": ["interface", "gradio", "gr"],
            "error_handling": ["try", "except", "error", "exception"],
            "output_components": ["output", "display", "show"]
        }
        
        if context_type in context_patterns:
            patterns = context_patterns[context_type]
            return any(pattern in context_text for pattern in patterns)
        
        return True
    
    def check_project(self, project_path: Path) -> Dict[str, List[PracticeViolation]]:
        """Check entire project for best practice violations."""
        results = {}
        
        # Find all Python files
        python_files = list(project_path.rglob("*.py"))
        
        for file_path in python_files:
            # Skip __pycache__ and virtual environments
            if "__pycache__" in str(file_path) or "venv" in str(file_path):
                continue
            
            violations = self.check_file(file_path)
            if violations:
                results[str(file_path)] = violations
        
        return results
    
    def generate_report(self, violations: Dict[str, List[PracticeViolation]]) -> str:
        """Generate a human-readable report of violations."""
        if not violations:
            return "✅ No best practice violations found!"
        
        report = "📋 Best Practices Violation Report\n"
        report += "=" * 50 + "\n\n"
        
        # Group by severity
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        
        for file_path, file_violations in violations.items():
            report += f"📁 {file_path}\n"
            report += "-" * 30 + "\n"
            
            for violation in file_violations:
                severity_counts[violation.severity] += 1
                
                severity_icon = {
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(violation.severity, "❓")
                
                report += f"{severity_icon} {violation.rule_name} (Line {violation.line_number})\n"
                report += f"   Message: {violation.message}\n"
                report += f"   Code: {violation.code_snippet}\n"
                report += f"   Suggestion: {violation.suggestion}\n"
                report += f"   Documentation: {violation.documentation_url}\n\n"
        
        # Summary
        report += "📊 Summary\n"
        report += "-" * 20 + "\n"
        report += f"Total files checked: {len(violations)}\n"
        report += f"Total violations: {sum(severity_counts.values())}\n"
        report += f"Errors: {severity_counts['error']}\n"
        report += f"Warnings: {severity_counts['warning']}\n"
        report += f"Info: {severity_counts['info']}\n"
        
        return report
    
    def suggest_improvements(self, violations: List[PracticeViolation]) -> List[str]:
        """Generate improvement suggestions based on violations."""
        suggestions = []
        
        for violation in violations:
            if violation.severity == "error":
                suggestions.append(f"🔧 Fix {violation.rule_name}: {violation.suggestion}")
            elif violation.severity == "warning":
                suggestions.append(f"⚡ Improve {violation.rule_name}: {violation.suggestion}")
            else:
                suggestions.append(f"💡 Consider {violation.rule_name}: {violation.suggestion}")
        
        return suggestions

def main():
    """Main function to run best practices check."""
    checker = BestPracticesChecker()
    
    # Check current directory
    project_path = Path.cwd()
    violations = checker.check_project(project_path)
    
    # Generate report
    report = checker.generate_report(violations)
    print(report)
    
    # Print suggestions
    all_violations = []
    for file_violations in violations.values():
        all_violations.extend(file_violations)
    
    if all_violations:
        print("\n💡 Improvement Suggestions:")
        print("-" * 30)
        suggestions = checker.suggest_improvements(all_violations)
        for suggestion in suggestions:
            print(f"  {suggestion}")

if __name__ == "__main__":
    main()
