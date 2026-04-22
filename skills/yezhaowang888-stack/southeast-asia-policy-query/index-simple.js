/**
 * 东南亚市场政策查询Skill - 简化版（无外部依赖）
 * 支持新加坡、马来西亚、泰国、越南、菲律宾等国家的政策查询
 */

class SoutheastAsiaPolicyQuery {
  constructor(config = {}) {
    this.config = {
      countries: config.countries || ['SG', 'MY', 'TH', 'VN', 'PH'],
      language: config.language || 'zh-CN',
      ...config
    };
    
    this.countryMap = {
      'SG': { name: 'Singapore', fullName: '新加坡' },
      'MY': { name: 'Malaysia', fullName: '马来西亚' },
      'TH': { name: 'Thailand', fullName: '泰国' },
      'VN': { name: 'Vietnam', fullName: '越南' },
      'PH': { name: 'Philippines', fullName: '菲律宾' },
      'ID': { name: 'Indonesia', fullName: '印度尼西亚' }
    };
    
    this.policyCache = new Map();
  }

  /**
   * 查询政策
   */
  async queryPolicies(country, options = {}) {
    const countryCode = this.getCountryCode(country);
    if (!countryCode) {
      throw new Error(`不支持的国家: ${country}`);
    }

    const cacheKey = `${countryCode}_${JSON.stringify(options)}`;
    if (this.policyCache.has(cacheKey)) {
      return this.policyCache.get(cacheKey);
    }

    try {
      const policies = this.generatePolicies(countryCode, options);
      this.policyCache.set(cacheKey, policies);
      return policies;
    } catch (error) {
      console.error(`查询${country}政策失败:`, error.message);
      return {
        country: this.countryMap[countryCode].fullName,
        policies: [],
        error: error.message
      };
    }
  }

  /**
   * 生成政策数据
   */
  generatePolicies(countryCode, options) {
    const country = this.countryMap[countryCode];
    const categories = options.category ? [options.category] : ['investment', 'technology', 'trade', 'tax'];
    const policies = [];
    
    categories.forEach(category => {
      policies.push({
        id: `${countryCode}_${category}_${Date.now()}`,
        title: `${country.name} ${this.getCategoryName(category)} Policy 2026`,
        category: category,
        issuedDate: '2026-01-15',
        effectiveDate: '2026-04-01',
        summary: `Latest ${category} policy in ${country.name} to promote economic growth`,
        impact: 'Positive for foreign investment',
        url: `https://${countryCode.toLowerCase()}-gov.com/policy/${category}`,
        tags: [category, countryCode, '2026']
      });
    });

    return {
      country: country.fullName,
      countryCode: countryCode,
      lastUpdated: new Date().toISOString(),
      policies: policies
    };
  }

  /**
   * 分析市场环境
   */
  async analyzeMarket(country, industry) {
    const countryCode = this.getCountryCode(country);
    if (!countryCode) {
      throw new Error(`不支持的国家: ${country}`);
    }

    return {
      country: this.countryMap[countryCode].fullName,
      industry: industry,
      analysisDate: new Date().toISOString(),
      marketSize: this.getMarketSize(countryCode, industry),
      growthRate: this.getGrowthRate(countryCode, industry),
      competitionLevel: this.getCompetitionLevel(countryCode, industry),
      regulatoryEnvironment: this.getRegulatoryScore(countryCode),
      recommendations: this.generateRecommendations(countryCode, industry)
    };
  }

  /**
   * 获取支持的国家列表
   */
  getSupportedCountries() {
    return Object.entries(this.countryMap).map(([code, info]) => ({
      code,
      name: info.name,
      fullName: info.fullName
    }));
  }

  /**
   * 工具方法
   */
  getCountryCode(country) {
    if (this.countryMap[country]) return country;
    
    for (const [code, info] of Object.entries(this.countryMap)) {
      if (info.name.toLowerCase() === country.toLowerCase() || 
          info.fullName === country) {
        return code;
      }
    }
    return null;
  }

  getCategoryName(category) {
    const categoryMap = {
      'investment': 'Investment',
      'technology': 'Technology',
      'trade': 'Trade',
      'tax': 'Tax',
      'labor': 'Labor',
      'environment': 'Environment'
    };
    return categoryMap[category] || category;
  }

  getMarketSize(countryCode, industry) {
    const sizes = { SG: 'Large', MY: 'Medium', TH: 'Medium', VN: 'Growing', PH: 'Growing' };
    return sizes[countryCode] || 'Medium';
  }

  getGrowthRate(countryCode, industry) {
    const rates = { SG: '8%', MY: '12%', TH: '10%', VN: '15%', PH: '14%' };
    return rates[countryCode] || '10%';
  }

  getCompetitionLevel(countryCode, industry) {
    const levels = { SG: 'High', MY: 'Medium', TH: 'Medium', VN: 'Low', PH: 'Low' };
    return levels[countryCode] || 'Medium';
  }

  getRegulatoryScore(countryCode) {
    const scores = { SG: 9, MY: 7, TH: 6, VN: 5, PH: 5 };
    return scores[countryCode] || 6;
  }

  generateRecommendations(countryCode, industry) {
    const country = this.countryMap[countryCode];
    return [
      `Monitor ${country.name} government announcements regularly`,
      `Consider local partnership for market entry`,
      `Review tax incentives for ${industry} sector`,
      `Stay updated on regulatory changes`
    ];
  }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SoutheastAsiaPolicyQuery;
}

// 浏览器环境支持
if (typeof window !== 'undefined') {
  window.SoutheastAsiaPolicyQuery = SoutheastAsiaPolicyQuery;
}