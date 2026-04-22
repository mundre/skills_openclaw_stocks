# OpenClaw Volcengine Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Volcano Engine](https://img.shields.io/badge/Provider-Volcano%20Engine-orange)](https://www.volcengine.com/product/ark)

Official Volcano Engine (Volcengine) integration skill for OpenClaw. This skill enables seamless integration with Volcengine's AI models including Doubao, GLM, Kimi, and DeepSeek through OpenAI-compatible API endpoints.

## Features

- **Multi-Model Support**: Doubao Seed 2.0, GLM-4, Kimi K2.5, DeepSeek V3
- **Dual Endpoints**: General conversation and specialized coding endpoints
- **Full API Coverage**: Complete OpenAI-compatible API implementation
- **Security Best Practices**: API key quotas, permission controls, project isolation
- **Comprehensive Documentation**: Based on official Volcengine API reference

## Quick Start

### 1. Install via ClawHub
```bash
clawhub install volcengine
```

### 2. Configure API Key
```bash
openclaw onboard --auth-choice volcengine-api-key
```

### 3. Test Connection
```bash
pwsh ./scripts/run-tests.ps1
```

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation and usage guide
- **[Configuration Guide](references/configuration.md)** - Detailed configuration options
- **[Models Reference](references/models.md)** - Complete model specifications
- **[API Parameters](references/api-parameters.md)** - Full API parameter reference
- **[Roadmap](ROADMAP.md)** - Development roadmap and future plans

## Supported Models

### General Models
- `doubao-seed-2-0-pro-260215` - Doubao Seed 2.0 Pro (256K context)
- `glm-4-7-251222` - GLM-4 7B (200K context)
- `kimi-k2-5-260127` - Kimi K2.5 (256K context)
- `deepseek-v3-2-251201` - DeepSeek V3.2 (128K context)

### Coding Models
- `ark-code-latest` - Ark Coding Plan (256K context)
- `doubao-seed-code` - Doubao Seed Code (256K context)
- `kimi-k2-thinking` - Kimi K2 Thinking (256K context, reasoning)

## Scripts

- `scripts/run-tests.ps1` - Comprehensive test suite
- `scripts/test-connection.ps1` - Basic connection test
- `scripts/quick-start.ps1` - Quick setup and configuration
- `scripts/generate-config.ps1` - Generate OpenClaw configuration

## Development

```bash
# Clone repository
git clone https://github.com/openclaw/skills.git
cd skills/volcengine

# Run tests
npm test
# or
./scripts/run-tests.ps1 -ApiKey YOUR_API_KEY
```

## License

This skill is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Support

- **Documentation**: [OpenClaw Docs](https://docs.openclaw.ai)
- **Community**: [Discord](https://discord.com/invite/clawd)
- **Issues**: [GitHub Issues](https://github.com/openclaw/skills/issues)

## Acknowledgments

- Volcano Engine for providing excellent AI services
- OpenClaw community for feedback and testing
- All contributors who helped improve this skill

---

**Skill Version**: 1.0.0  
**Last Updated**: 2026-04-19  
**OpenClaw Compatibility**: >=2026.4.0