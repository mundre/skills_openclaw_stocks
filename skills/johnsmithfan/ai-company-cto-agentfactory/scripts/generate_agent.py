#!/usr/bin/env python3
"""
AI-Company Agent Factory - Agent Generator Script
Generates standardized Agent files following Harness Engineering principles.

Usage:
    python generate_agent.py --config ./agent-config.yaml --output ./agents/
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    from jinja2.sandbox import SandboxedEnvironment
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    print("Install: pip install pyyaml jinja2")
    sys.exit(1)


# Exit codes
EXIT_SUCCESS = 0
EXIT_SCHEMA_ERROR = 1
EXIT_VALIDATION_ERROR = 2
EXIT_TEMPLATE_ERROR = 3
EXIT_IO_ERROR = 4


# Schema definitions
AGENT_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["agent"],
    "properties": {
        "agent": {
            "type": "object",
            "required": ["layer", "name", "role"],
            "properties": {
                "layer": {
                    "type": "string",
                    "enum": ["tool", "execution", "management", "decision"]
                },
                "name": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                "role": {"type": "string"},
                "description": {"type": "string"}
            }
        },
        "objective_kpi": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "target": {"type": "string"},
                "measurement": {"type": "string"}
            }
        },
        "behavior_rules": {
            "type": "object",
            "properties": {
                "must_do": {"type": "array", "items": {"type": "string"}},
                "must_not_do": {"type": "array", "items": {"type": "string"}}
            }
        },
        "tool_permissions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "access": {"type": "string", "enum": ["read", "write", "read_write"]}
                }
            }
        },
        "error_handling": {
            "type": "object",
            "properties": {
                "retry_policy": {"type": "string"},
                "fallback_skill": {"type": "string"},
                "escalation_target": {"type": "string"}
            }
        }
    }
}


def validate_schema(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate config against schema."""
    errors = []
    
    # Check required fields
    if "agent" not in config:
        errors.append("Missing required field: agent")
        return False, errors
    
    agent = config["agent"]
    required_agent_fields = ["layer", "name", "role"]
    for field in required_agent_fields:
        if field not in agent:
            errors.append(f"Missing required field: agent.{field}")
    
    # Validate layer enum
    if "layer" in agent:
        valid_layers = ["tool", "execution", "management", "decision"]
        if agent["layer"] not in valid_layers:
            errors.append(f"Invalid layer: {agent['layer']}. Must be one of {valid_layers}")
    
    # Validate name pattern
    if "name" in agent:
        import re
        if not re.match(r'^[a-z0-9-]+$', agent["name"]):
            errors.append(f"Invalid agent name: {agent['name']}. Must match ^[a-z0-9-]+$")
    
    return len(errors) == 0, errors


def load_template(layer: str, template_dir: Path) -> str:
    """Load template for specified layer."""
    template_files = {
        "tool": "tool-layer.md",
        "execution": "execution-layer.md",
        "management": "management-layer.md",
        "decision": "decision-layer.md"
    }
    
    template_file = template_files.get(layer)
    if not template_file:
        raise ValueError(f"Unknown layer: {layer}")
    
    template_path = template_dir / template_file
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    return template_path.read_text(encoding="utf-8")


def render_skill_md(config: Dict[str, Any], template: str) -> str:
    """Render SKILL.md from template and config."""
    agent = config.get("agent", {})
    
    # Build template variables
    vars_dict = {
        "name": agent.get("name", ""),
        "slug": agent.get("name", "").replace("_", "-"),
        "version": "1.0.0",
        "description": agent.get("description", agent.get("role", "")),
        "role": agent.get("role", ""),
        "layer": agent.get("layer", ""),
        "kpi": config.get("objective_kpi", {}),
        "rules": config.get("behavior_rules", {}),
        "permissions": config.get("tool_permissions", []),
        "error_handling": config.get("error_handling", {})
    }
    
    # Use SandboxedEnvironment for secure template rendering
    env = SandboxedEnvironment()
    jinja_template = env.from_string(template)
    return jinja_template.render(**vars_dict)


def generate_agent(config_path: Path, output_dir: Path, layer: Optional[str] = None, 
                   dry_run: bool = False, skip_validation: bool = False) -> int:
    """Generate agent files from config."""
    
    # Load config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return EXIT_SCHEMA_ERROR
    
    # Validate schema
    if not skip_validation:
        is_valid, errors = validate_schema(config)
        if not is_valid:
            print("Schema validation failed:")
            for error in errors:
                print(f"  - {error}")
            return EXIT_SCHEMA_ERROR
        print("✅ Schema validation passed")
    
    if dry_run:
        print("Dry run mode - skipping file generation")
        return EXIT_SUCCESS
    
    # Determine layer
    agent_layer = layer or config.get("agent", {}).get("layer")
    if not agent_layer:
        print("Error: Layer not specified in config or command line")
        return EXIT_SCHEMA_ERROR
    
    # Load template
    script_dir = Path(__file__).parent.parent
    template_dir = script_dir / "templates"
    
    try:
        template = load_template(agent_layer, template_dir)
    except Exception as e:
        print(f"Error loading template: {e}")
        return EXIT_TEMPLATE_ERROR
    
    # Render SKILL.md
    try:
        skill_md = render_skill_md(config, template)
    except Exception as e:
        print(f"Error rendering template: {e}")
        return EXIT_TEMPLATE_ERROR
    
    # Create output directory
    agent_name = config["agent"]["name"]
    agent_dir = output_dir / agent_name
    
    try:
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md
        skill_path = agent_dir / "SKILL.md"
        skill_path.write_text(skill_md, encoding="utf-8")
        print(f"✅ Generated: {skill_path}")
        
        # Write config.yaml
        config_output_path = agent_dir / "config.yaml"
        with open(config_output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"✅ Generated: {config_output_path}")
        
        # Create tests directory
        tests_dir = agent_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Write test template based on layer
        layer_tests = {
            "tool": '''
    def test_schema_compliance(self):
        """Test input/output schema compliance"""
        # Verify SKILL.md has input_schema and output_schema
        skill_content = (Path(__file__).parent.parent / "SKILL.md").read_text()
        self.assertIn("input_schema", skill_content.lower())
        self.assertIn("output_schema", skill_content.lower())
    
    def test_stateless_idempotent(self):
        """Test stateless and idempotent properties"""
        # Same input should produce same output
        # Implementation: call skill twice with same input, compare outputs
        pass  # Replace with actual implementation
''',
            "execution": '''
    def test_role_definition(self):
        """Test role is clearly defined"""
        skill_content = (Path(__file__).parent.parent / "SKILL.md").read_text()
        self.assertIn("## Role", skill_content)
        self.assertIn("## Objective & KPI", skill_content)
    
    def test_tool_permissions(self):
        """Test tool permissions are declared"""
        skill_content = (Path(__file__).parent.parent / "SKILL.md").read_text()
        self.assertIn("## Tool Permissions", skill_content)
''',
            "management": '''
    def test_state_machine_defined(self):
        """Test state machine is defined"""
        skill_content = (Path(__file__).parent.parent / "SKILL.md").read_text()
        self.assertIn("## State Machine", skill_content)
    
    def test_error_recovery(self):
        """Test error recovery paths"""
        skill_content = (Path(__file__).parent.parent / "SKILL.md").read_text()
        self.assertIn("## Error Handling", skill_content)
''',
            "decision": '''
    def test_authority_compliance(self):
        """Test authority and compliance section"""
        skill_content = (Path(__file__).parent.parent / "SKILL.md").read_text()
        self.assertIn("## Authority & Compliance", skill_content)
    
    def test_audit_logging(self):
        """Test audit logging requirements"""
        config = (Path(__file__).parent.parent / "config.yaml")
        self.assertTrue(config.exists())
'''
        }
        
        test_path = tests_dir / "test_agent.py"
        layer_specific_tests = layer_tests.get(agent_layer, layer_tests["execution"])
        
        test_content = f'''"""Tests for {agent_name}

Generated by AI-Company Agent Factory v1.0.0
Layer: {agent_layer.title()}
"""

import unittest
from pathlib import Path


class Test{agent_name.replace("-", "_").title().replace("-", "")}(unittest.TestCase):
    """Test cases for {agent_name}"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent_dir = Path(__file__).parent.parent
        self.skill_md = self.agent_dir / "SKILL.md"
        self.config_yaml = self.agent_dir / "config.yaml"
    
    def test_skill_md_exists(self):
        """Test SKILL.md exists"""
        self.assertTrue(self.skill_md.exists(), "SKILL.md not found")
    
    def test_config_yaml_exists(self):
        """Test config.yaml exists"""
        self.assertTrue(self.config_yaml.exists(), "config.yaml not found")
    
    def test_frontmatter_complete(self):
        """Test frontmatter has required fields"""
        import yaml
        content = self.skill_md.read_text()
        # Extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                required = ["name", "slug", "version", "description"]
                for field in required:
                    self.assertIn(field, frontmatter, f"Missing frontmatter field: {{field}}")
{layer_specific_tests}


if __name__ == "__main__":
    unittest.main()
'''
        test_path.write_text(test_content, encoding="utf-8")
        print(f"✅ Generated: {test_path}")
        
        # Write README.md
        readme_path = agent_dir / "README.md"
        readme_content = f'''# {agent_name.title().replace("-", " ")}

## Overview

{config["agent"].get("role", "AI Agent")}

## Layer

{agent_layer.title()} Layer

## Usage

See [SKILL.md](./SKILL.md) for detailed usage instructions.

## Testing

```bash
python -m pytest tests/
```
'''
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"✅ Generated: {readme_path}")
        
    except Exception as e:
        print(f"Error writing files: {e}")
        return EXIT_IO_ERROR
    
    print(f"\n🎉 Agent '{agent_name}' generated successfully!")
    print(f"   Location: {agent_dir}")
    
    return EXIT_SUCCESS


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI-Company Agent from configuration"
    )
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--output", "-o",
        default="./agents/",
        help="Output directory (default: ./agents/)"
    )
    parser.add_argument(
        "--layer", "-l",
        choices=["tool", "execution", "management", "decision"],
        help="Override layer from config"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config only, do not generate files"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation gates"
    )
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    output_dir = Path(args.output)
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(EXIT_SCHEMA_ERROR)
    
    exit_code = generate_agent(
        config_path=config_path,
        output_dir=output_dir,
        layer=args.layer,
        dry_run=args.dry_run,
        skip_validation=args.skip_validation
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
