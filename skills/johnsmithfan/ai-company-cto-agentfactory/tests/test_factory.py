"""Tests for ai-company-agent-factory"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestSchemaValidation(unittest.TestCase):
    """Test schema validation in generate_agent.py"""
    
    def test_validate_schema_valid_config(self):
        """Test validation with valid config"""
        from generate_agent import validate_schema
        
        config = {
            "agent": {
                "layer": "execution",
                "name": "test-agent",
                "role": "Test role"
            }
        }
        
        is_valid, errors = validate_schema(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_schema_missing_agent(self):
        """Test validation with missing agent section"""
        from generate_agent import validate_schema
        
        config = {}
        
        is_valid, errors = validate_schema(config)
        self.assertFalse(is_valid)
        self.assertIn("Missing required field: agent", errors)
    
    def test_validate_schema_invalid_layer(self):
        """Test validation with invalid layer"""
        from generate_agent import validate_schema
        
        config = {
            "agent": {
                "layer": "invalid",
                "name": "test-agent",
                "role": "Test role"
            }
        }
        
        is_valid, errors = validate_schema(config)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid layer" in e for e in errors))
    
    def test_validate_schema_invalid_name(self):
        """Test validation with invalid agent name"""
        from generate_agent import validate_schema
        
        config = {
            "agent": {
                "layer": "execution",
                "name": "Test_Agent",  # Invalid: uppercase and underscore
                "role": "Test role"
            }
        }
        
        is_valid, errors = validate_schema(config)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid agent name" in e for e in errors))


class TestTemplateRendering(unittest.TestCase):
    """Test template rendering"""
    
    def test_render_skill_md(self):
        """Test SKILL.md rendering"""
        from generate_agent import render_skill_md
        
        config = {
            "agent": {
                "name": "test-agent",
                "role": "Test agent role",
                "layer": "execution"
            },
            "objective_kpi": {"metric": "test", "target": ">=90%"},
            "behavior_rules": {"must_do": ["rule1"], "must_not_do": ["rule2"]},
            "tool_permissions": [{"skill": "test", "access": "read"}],
            "error_handling": {"retry_policy": "3x"}
        }
        
        template = "# {{ name }}\nRole: {{ role }}\nLayer: {{ layer }}"
        result = render_skill_md(config, template)
        
        self.assertIn("test-agent", result)
        self.assertIn("Test agent role", result)
        self.assertIn("execution", result)


class TestQualityGates(unittest.TestCase):
    """Test quality gates validation"""
    
    def test_schema_validator(self):
        """Test SchemaValidator gate"""
        from validate_agent import SchemaValidator
        
        validator = SchemaValidator()
        # Test with non-existent directory
        result = validator.validate(Path("/nonexistent"), "execution")
        self.assertFalse(result)
        self.assertEqual(validator.status, "FAIL")
    
    def test_security_scanner_clean_code(self):
        """Test SecurityScanner with clean code"""
        from validate_agent import SecurityScanner
        
        scanner = SecurityScanner()
        # Create temp directory with clean file
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# Clean code\ndef hello():\n    return 'hello'")
            result = scanner.validate(Path(tmpdir), "execution")
            self.assertTrue(result)
            self.assertEqual(scanner.status, "PASS")
    
    def test_security_scanner_forbidden_pattern(self):
        """Test SecurityScanner detects forbidden patterns"""
        from validate_agent import SecurityScanner
        
        scanner = SecurityScanner()
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("eval('dangerous_code')")
            result = scanner.validate(Path(tmpdir), "execution")
            self.assertFalse(result)
            self.assertEqual(scanner.status, "FAIL")


class TestLayerRequirements(unittest.TestCase):
    """Test layer-specific requirements"""
    
    def test_tool_layer_requirements(self):
        """Test Tool layer requirements"""
        from validate_agent import LayerSpecificValidator
        
        validator = LayerSpecificValidator("tool")
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / "SKILL.md"
            skill_md.write_text("---\nname: test\n---\n# Test\nstateless idempotent input_schema output_schema")
            result = validator.validate(Path(tmpdir), "tool")
            self.assertTrue(result)
    
    def test_execution_layer_requirements(self):
        """Test Execution layer requirements"""
        from validate_agent import LayerSpecificValidator
        
        validator = LayerSpecificValidator("execution")
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / "SKILL.md"
            skill_md.write_text("---\nname: test\n---\n# Test\nrole objective_kpi behavior_rules tool_permissions")
            result = validator.validate(Path(tmpdir), "execution")
            self.assertTrue(result)


class TestDependencies(unittest.TestCase):
    """Test dependencies are correctly specified"""
    
    def test_requirements_txt_exists(self):
        """Test requirements.txt exists"""
        factory_dir = Path(__file__).parent.parent
        req_file = factory_dir / "requirements.txt"
        self.assertTrue(req_file.exists())
    
    def test_requirements_content(self):
        """Test requirements.txt has required packages"""
        factory_dir = Path(__file__).parent.parent
        req_file = factory_dir / "requirements.txt"
        content = req_file.read_text()
        self.assertIn("pyyaml", content)
        self.assertIn("jinja2", content)


if __name__ == "__main__":
    unittest.main()
