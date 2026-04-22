# Southeast Asia Policy Query Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://clawhub.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://clawhub.ai/skills/southeast-asia-policy-query)

A comprehensive skill for querying and analyzing market policies in Southeast Asian countries including Singapore, Malaysia, Thailand, Vietnam, Philippines, and Indonesia.

## Features

- **Multi-country Support**: Query policies from 6+ Southeast Asian countries
- **Policy Categories**: Investment, technology, trade, tax, labor, environment
- **Market Analysis**: Industry-specific market environment analysis
- **Real-time Updates**: Policy change monitoring
- **Bilingual Support**: Chinese and English interfaces

## Installation

```bash
# Install via ClawHub
clawhub install southeast-asia-policy-query

# Or install manually
npm install southeast-asia-policy-query
```

## Quick Start

```javascript
const SoutheastAsiaPolicyQuery = require('southeast-asia-policy-query');

// Initialize the skill
const skill = new SoutheastAsiaPolicyQuery({
  countries: ['SG', 'MY', 'TH'],
  language: 'zh-CN'
});

// Query policies
async function example() {
  // Get Singapore technology policies
  const sgPolicies = await skill.queryPolicies('Singapore', {
    category: 'technology'
  });
  console.log(sgPolicies);

  // Analyze Malaysia investment market
  const myAnalysis = await skill.analyzeMarket('Malaysia', 'investment');
  console.log(myAnalysis);

  // Get supported countries
  const countries = skill.getSupportedCountries();
  console.log(countries);
}

example();
```

## Supported Countries

| Code | Country | 中文名称 |
|------|---------|----------|
| SG | Singapore | 新加坡 |
| MY | Malaysia | 马来西亚 |
| TH | Thailand | 泰国 |
| VN | Vietnam | 越南 |
| PH | Philippines | 菲律宾 |
| ID | Indonesia | 印度尼西亚 |

## API Reference

### `queryPolicies(country, options)`
Query policies for a specific country.

**Parameters:**
- `country` (string): Country name or code
- `options` (object): Query options
  - `category` (string): Policy category
  - `year` (number): Year filter

**Returns:** Policy data object

### `analyzeMarket(country, industry)`
Analyze market environment for specific industry.

**Parameters:**
- `country` (string): Country name
- `industry` (string): Industry name

**Returns:** Market analysis report

### `getSupportedCountries()`
Get list of supported countries.

**Returns:** Array of country objects

## Usage in OpenClaw

```
@agent 查询新加坡最新的科技政策
@agent 分析马来西亚的投资环境
@agent 获取支持的东南亚国家列表
```

## Configuration

Create `config/southeast-asia-policy.json`:

```json
{
  "countries": ["SG", "MY", "TH", "VN", "PH"],
  "language": "zh-CN",
  "updateInterval": 3600
}
```

## Development

```bash
# Clone repository
git clone https://github.com/your-org/southeast-asia-policy-query.git

# Install dependencies
npm install

# Run tests
npm test

# Build for production
npm run build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the [documentation](https://docs.clawhub.ai/skills/southeast-asia-policy-query)
2. Open an [issue](https://github.com/your-org/southeast-asia-policy-query/issues)
3. Contact the maintainers

## Changelog

### v1.0.0 (2026-04-22)
- Initial release
- Support for 6 Southeast Asian countries
- Basic policy query and market analysis
- Simplified version with no external dependencies

## Acknowledgments

- OpenClaw team for the amazing platform
- Contributors and testers
- Southeast Asian government data sources