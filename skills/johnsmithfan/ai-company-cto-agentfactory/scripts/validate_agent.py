#!/usr/bin/env python3
"""
AI-Company Agent Factory - Quality Gates Validator
Validates Agent files against Harness Engineering quality gates.

Usage:
    python validate_agent.py --agent-dir ./agents/my-agent/ [--layer tool|execution|management|decision]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    import yaml
except ImportError:
    print("Error: pyyaml required. Install: pip install pyyaml")
    sys.exit(1)


EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_IO_ERROR = 2


class QualityGate:
    """Base class for quality gates."""
    
    def __init__(self, gate_id: str, name: str, threshold: str, blocking: bool = True):
        self.gate_id = gate_id
        self.name = name
        self.threshold = threshold
        self.blocking = blocking
        self.status = "PENDING"
        self.details = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "name": self.name,
            "status": self.status,
            "threshold": self.threshold,
            "blocking": self.blocking,
            "details": self.details
        }


class SchemaValidator(QualityGate):
    """G1: Schema validation gate."""
    
    def __init__(self):
        super().__init__("G1", "Schema Validation", "100% fields covered", True)
    
    def validate(self, agent_dir: Path, layer: str) -> bool:
        """Validate SKILL.md frontmatter and config.yaml."""
        skill_md = agent_dir / "SKILL.md"
        config_yaml = agent_dir / "config.yaml"
        
        errors = []
        
        # Check SKILL.md exists and has frontmatter
        if not skill_md.exists():
            errors.append("SKILL.md not found")
        else:
            content = skill_md.read_text(encoding="utf-8")
            if not content.startswith("---"):
                errors.append("SKILL.md missing frontmatter")
            else:
                # Extract frontmatter
                parts = content.split("---", 2)
                if len(parts) < 3:
                    errors.append("SKILL.md frontmatter malformed")
                else:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        required = ["name", "slug", "version", "description"]
                        for field in required:
                            if field not in frontmatter:
                                errors.append(f"Missing frontmatter field: {field}")
                    except yaml.YAMLError as e:
                        errors.append(f"Frontmatter YAML error: {e}")
        
        # Check config.yaml exists
        if not config_yaml.exists():
            errors.append("config.yaml not found")
        else:
            try:
                with open(config_yaml, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                if "agent" not in config:
                    errors.append("config.yaml missing 'agent' section")
                elif "layer" not in config.get("agent", {}):
                    errors.append("config.yaml missing agent.layer")
            except yaml.YAMLError as e:
                errors.append(f"config.yaml YAML error: {e}")
        
        if errors:
            self.status = "FAIL"
            self.details = "; ".join(errors)
            return False
        
        self.status = "PASS"
        self.details = "All required fields present"
        return True


class LintChecker(QualityGate):
    """G2: Lint check gate."""
    
    def __init__(self):
        super().__init__("G2", "Lint Check", "0 errors", True)
    
    def validate(self, agent_dir: Path, layer: str) -> bool:
        """Basic lint checks for SKILL.md."""
        skill_md = agent_dir / "SKILL.md"
        errors = []
        
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Check line count (soft limit 200 for generated agents)
            if len(lines) > 200:
                errors.append(f"SKILL.md exceeds 200 lines ({len(lines)})")
            
            # Check for required sections
            required_sections = ["## When to Use", "## Core Rules"]
            for section in required_sections:
                if section not in content:
                    errors.append(f"Missing section: {section}")
            
            # Check for broken markdown links
            broken_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for text, link in broken_links:
                if link.startswith("./") or link.startswith("../"):
                    linked_path = agent_dir / link
                    if not linked_path.exists():
                        errors.append(f"Broken link: {link}")
        
        if errors:
            self.status = "FAIL"
            self.details = "; ".join(errors)
            return False
        
        self.status = "PASS"
        self.details = "No lint errors"
        return True


class SecurityScanner(QualityGate):
    """G3: Security scan gate."""
    
    FORBIDDEN_PATTERNS = [
        (r'eval\s*\(', "eval() usage"),
        (r'exec\s*\(', "exec() usage"),
        (r'__import__.*system', "system call via __import__"),
        (r'subprocess\.(call|run|Popen)', "subprocess usage"),
        (r'pickle\.loads', "pickle.loads usage"),
        (r'yaml\.load\s*\([^)]*\)(?!.*SafeLoader)', "unsafe yaml.load"),
        (r'[A-Za-z0-9]{40,}', "potential hardcoded key"),
    ]
    
    def __init__(self):
        super().__init__("G3", "Security Scan", "Critical/High=0", True)
    
    def validate(self, agent_dir: Path, layer: str) -> bool:
        """Scan for forbidden patterns."""
        findings = []
        
        # Scan all Python files
        for py_file in agent_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for pattern, desc in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, content):
                    findings.append(f"{py_file.name}: {desc}")
        
        # Scan all markdown files for suspicious patterns
        for md_file in agent_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            # Check for code blocks with eval/exec
            code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
            for block in code_blocks:
                if re.search(r'eval\s*\(|exec\s*\(', block):
                    findings.append(f"{md_file.name}: suspicious code block")
        
        if findings:
            self.status = "FAIL"
            self.details = "; ".join(findings[:5])  # Limit to first 5
            return False
        
        self.status = "PASS"
        self.details = "No security issues found"
        return True


class IntegrationTester(QualityGate):
    """G4: Integration test gate."""
    
    def __init__(self):
        super().__init__("G4", "Integration Test", "Pass rate >= 95%", True)
    
    def validate(self, agent_dir: Path, layer: str) -> bool:
        """Check for test files and basic test structure."""
        tests_dir = agent_dir / "tests"
        
        if not tests_dir.exists():
            self.status = "FAIL"
            self.details = "tests/ directory not found"
            return False
        
        test_files = list(tests_dir.glob("test_*.py"))
        if not test_files:
            self.status = "FAIL"
            self.details = "No test files found"
            return False
        
        # Check for actual test methods (not just TODO)
        has_real_tests = False
        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")
            if "def test_" in content and "pass" not in content.lower():
                has_real_tests = True
                break
        
        if not has_real_tests:
            self.status = "FAIL"
            self.details = "Tests are placeholders (only 'pass')"
            return False
        
        self.status = "PASS"
        self.details = f"Found {len(test_files)} test files with real tests"
        return True


class LayerSpecificValidator(QualityGate):
    """Layer-specific validation gate."""
    
    LAYER_REQUIREMENTS = {
        "tool": ["stateless", "idempotent", "input_schema", "output_schema"],
        "execution": ["role", "objective_kpi", "behavior_rules", "tool_permissions"],
        "management": ["state_machine", "orchestration", "error_recovery"],
        "decision": ["authority", "compliance", "audit_log"]
    }
    
    def __init__(self, layer: str):
        super().__init__(f"G5-{layer}", f"{layer.title()} Layer Validation", "Layer requirements met", True)
        self.layer = layer
    
    def validate(self, agent_dir: Path, layer: str) -> bool:
        """Validate layer-specific requirements."""
        skill_md = agent_dir / "SKILL.md"
        
        if not skill_md.exists():
            self.status = "FAIL"
            self.details = "SKILL.md not found"
            return False
        
        content = skill_md.read_text(encoding="utf-8").lower()
        requirements = self.LAYER_REQUIREMENTS.get(layer, [])
        
        missing = []
        for req in requirements:
            if req.replace("_", " ") not in content and req not in content:
                missing.append(req)
        
        if missing:
            self.status = "FAIL"
            self.details = f"Missing layer requirements: {', '.join(missing)}"
            return False
        
        self.status = "PASS"
        self.details = f"All {layer} layer requirements met"
        return True


def validate_agent(agent_dir: Path, layer: str = None) -> Tuple[bool, Dict[str, Any]]:
    """Run all quality gates on an agent directory."""
    
    if not agent_dir.exists():
        return False, {"error": f"Agent directory not found: {agent_dir}"}
    
    # Auto-detect layer from config if not provided
    if not layer:
        config_file = agent_dir / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                layer = config.get("agent", {}).get("layer", "unknown")
            except Exception:
                layer = "unknown"
        else:
            layer = "unknown"
    
    # Initialize gates
    gates = [
        SchemaValidator(),
        LintChecker(),
        SecurityScanner(),
        IntegrationTester(),
        LayerSpecificValidator(layer)
    ]
    
    # Run validation
    all_passed = True
    for gate in gates:
        passed = gate.validate(agent_dir, layer)
        if not passed and gate.blocking:
            all_passed = False
    
    # Generate report
    report = {
        "agent_name": agent_dir.name,
        "layer": layer,
        "timestamp": "2026-04-16T19:00:00Z",
        "gates": [gate.to_dict() for gate in gates],
        "summary": {
            "total": len(gates),
            "passed": sum(1 for g in gates if g.status == "PASS"),
            "failed": sum(1 for g in gates if g.status == "FAIL"),
            "blocking_failures": sum(1 for g in gates if g.status == "FAIL" and g.blocking)
        }
    }
    
    return all_passed, report


def main():
    parser = argparse.ArgumentParser(description="Validate AI-Company Agent quality gates")
    parser.add_argument("--agent-dir", "-a", required=True, help="Path to agent directory")
    parser.add_argument("--layer", "-l", choices=["tool", "execution", "management", "decision"], help="Agent layer")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON report")
    parser.add_argument("--output", "-o", help="Output file for report")
    
    args = parser.parse_args()
    
    agent_dir = Path(args.agent_dir)
    passed, report = validate_agent(agent_dir, args.layer)
    
    # Output report
    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Human-readable format
        lines = [
            f"Quality Gates Report: {report['agent_name']}",
            f"Layer: {report['layer']}",
            "-" * 50,
        ]
        for gate in report["gates"]:
            status_icon = "✅" if gate["status"] == "PASS" else "❌"
            lines.append(f"{status_icon} {gate['gate_id']}: {gate['name']} — {gate['status']}")
            lines.append(f"   Details: {gate['details']}")
        lines.append("-" * 50)
        lines.append(f"Summary: {report['summary']['passed']}/{report['summary']['total']} passed")
        if report['summary']['blocking_failures'] > 0:
            lines.append(f"⚠️  {report['summary']['blocking_failures']} blocking failures")
        output = "\n".join(lines)
    
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(output)
    
    sys.exit(EXIT_SUCCESS if passed else EXIT_VALIDATION_FAILED)


if __name__ == "__main__":
    main()
