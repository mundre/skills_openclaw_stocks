# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-16

### Added
- Initial release of AI-Company Agent Factory
- Four-layer architecture: Tool, Execution, Management, Decision
- Harness Engineering principles: Standardization, Modularity, Generalization
- Layer-specific templates with complete examples
- Agent generation script with YAML configuration
- Quality gates validation system (4 gates + layer-specific)
- Security compliance documentation (VirusTotal, ClawHub, layer security)
- Quality gates documentation with thresholds and tools
- Harness Engineering principles reference

### Features
- `generate_agent.py`: Generate standardized Agent from YAML config
- `validate_agent.py`: Run quality gates validation on generated Agents
- Four layer templates with 5-step generation process each
- Five Elements framework: Role, Objective/KPI, Behavior Rules, Tool Permissions, Error Handling
- Quality gates: Schema Validation, Lint Check, Security Scan, Integration Test

### Security
- VirusTotal compliance: No eval/exec/hardcoded keys patterns
- ClawHub compliance: Frontmatter schema, permissions, dependencies
- Layer-specific security gates for all four layers
- SandboxedEnvironment for Jinja2 template rendering

### Documentation
- SKILL.md: Main trigger file with usage guide
- templates/: Layer-specific templates with examples
- references/: Harness Engineering, Quality Gates, Security Compliance
- DESIGN-SPEC.md: Design specification summary
