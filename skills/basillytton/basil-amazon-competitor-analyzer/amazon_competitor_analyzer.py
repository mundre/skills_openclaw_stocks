"""
Amazon Competitor Analyzer Skill
===============================
Scrapes Amazon product data from ASINs using SkillBoss API Hub
and performs surgical competitive analysis.

Author: OpenCode
Version: 1.0.0
"""

import os
import sys
import json
import re
import time
import csv
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env from same directory as script
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # If python-dotenv not available, check .env manually
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value.strip())


# Configuration
SKILLBOSS_API_KEY = os.getenv("SKILLBOSS_API_KEY", "")
API_BASE_URL = "https://api.skillboss.co/v1"


class AmazonCompetitorAnalyzer:
    """Main class for Amazon competitive analysis"""

    def __init__(self, api_key: str = None):
        """Initialize the analyzer with API credentials"""
        self.api_key = api_key or SKILLBOSS_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _pilot(self, body: dict) -> dict:
        """Call SkillBoss API Hub /v1/pilot endpoint"""
        response = requests.post(
            f"{API_BASE_URL}/pilot",
            headers=self.headers,
            json=body,
            timeout=60,
        )
        return response.json()

    def validate_asin(self, asin: str) -> bool:
        """Validate ASIN format"""
        return len(asin) == 10 and asin.isalnum()

    def extract_asins_from_text(self, text: str) -> List[str]:
        """Extract ASINs from user input text"""
        # Match 10-character alphanumeric strings starting with B0 or similar
        asin_pattern = r'\b[B0][A-Z0-9]{9}\b'
        asins = re.findall(asin_pattern, text.upper())
        return list(set(asins))  # Remove duplicates

    def scrape_product(self, asin: str, wait_timeout: int = 300) -> Optional[Dict]:
        """Scrape a single product using SkillBoss API Hub"""
        if not self.validate_asin(asin):
            print(f"Invalid ASIN: {asin}")
            return None

        amazon_url = f"https://www.amazon.com/dp/{asin}"
        try:
            # Step 1: Scrape the Amazon product page via SkillBoss API Hub
            scrape_result = self._pilot({
                "type": "scraper",
                "inputs": {"url": amazon_url}
            })
            raw_content = scrape_result["result"]["data"]["markdown"]

            # Step 2: Use SkillBoss LLM to extract structured product data
            extract_result = self._pilot({
                "type": "chat",
                "inputs": {
                    "messages": [{
                        "role": "user",
                        "content": (
                            "Extract structured product data from this Amazon page content "
                            "and return ONLY a JSON object with no extra text:\n\n"
                            f"{str(raw_content)[:3000]}\n\n"
                            "Return JSON with this exact structure:\n"
                            '{"results": {"products": [{"product_info": {"title": "", "brand": ""}, '
                            '"pricing": {"current_price": 0, "original_price": 0, "discount_percent": 0}, '
                            '"reviews": {"average_rating": 0, "total_count": 0}, '
                            '"specifications": {"weight": "", "features": []}}]}}'
                        )
                    }]
                },
                "prefer": "balanced"
            })

            response_text = extract_result["result"]["choices"][0]["message"]["content"]
            # Parse JSON from LLM response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None

        except Exception as e:
            print(f"Error scraping product {asin}: {e}")
            return None

    def scrape_multiple_products(self, asins: List[str], delay: int = 5) -> Dict[str, Any]:
        """Scrape multiple products"""
        results = {}

        for asin in asins:
            print(f"Processing: {asin}")

            data = self.scrape_product(asin)
            results[asin] = data

            if delay > 0 and asin != asins[-1]:
                time.sleep(delay)

        return results

    def analyze_competitive_position(self, products: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        analysis = {
            "price_analysis": {},
            "rating_analysis": {},
            "market_leaders": {},
            "opportunities": []
        }

        prices = []
        ratings = []

        for asin, data in products.items():
            if data:
                try:
                    product = data.get('results', {}).get('products', [{}])[0]
                    price = product.get('pricing', {}).get('current_price', 0)
                    rating = product.get('reviews', {}).get('average_rating', 0)
                    reviews = product.get('reviews', {}).get('total_count', 0)
                    brand = product.get('product_info', {}).get('brand', asin)

                    prices.append((asin, price, brand))
                    ratings.append((asin, rating, reviews, brand))

                except Exception:
                    pass

        # Sort by price
        prices.sort(key=lambda x: x[1])
        if prices:
            analysis["price_analysis"]["lowest"] = prices[0]
            analysis["price_analysis"]["highest"] = prices[-1]
            analysis["price_analysis"]["range"] = prices[-1][1] - prices[0][1]

        # Sort by rating
        ratings.sort(key=lambda x: x[1], reverse=True)
        if ratings:
            analysis["rating_analysis"]["top_rated"] = ratings[0]
            analysis["rating_analysis"]["by_volume"] = sorted(ratings, key=lambda x: x[2], reverse=True)

        return analysis

    def generate_csv_report(self, products: Dict[str, Any], output_path: str):
        """Generate CSV report"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ASIN', 'Product Title', 'Brand', 'Price ($)', 'Original Price ($)',
                'Discount (%)', 'Rating', 'Reviews Count', 'Weight', 'Features'
            ])

            for asin, data in products.items():
                if data:
                    try:
                        product = data.get('results', {}).get('products', [{}])[0]
                        writer.writerow([
                            asin,
                            product.get('product_info', {}).get('title', 'N/A')[:100],
                            product.get('product_info', {}).get('brand', 'N/A'),
                            product.get('pricing', {}).get('current_price', 'N/A'),
                            product.get('pricing', {}).get('original_price', 'N/A'),
                            product.get('pricing', {}).get('discount_percent', 'N/A'),
                            product.get('reviews', {}).get('average_rating', 'N/A'),
                            product.get('reviews', {}).get('total_count', 'N/A'),
                            product.get('specifications', {}).get('weight', 'N/A'),
                            ', '.join(product.get('specifications', {}).get('features', [])[:5])
                        ])
                    except:
                        writer.writerow([asin, 'Error', '', '', '', '', '', '', '', ''])
                else:
                    writer.writerow([asin, 'Failed', '', '', '', '', '', '', '', ''])

        print(f"CSV report saved: {output_path}")

    def generate_markdown_report(self, products: Dict[str, Any], output_path: str):
        """Generate comprehensive markdown report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Amazon Competitive Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Products Analyzed:** {len(products)}\n\n")

            # Summary table
            f.write("## Data Summary\n\n")
            f.write("| ASIN | Brand | Price | Rating | Reviews |\n")
            f.write("|------|-------|-------|--------|---------|\n")

            for asin, data in products.items():
                if data:
                    try:
                        product = data.get('results', {}).get('products', [{}])[0]
                        info = product.get('product_info', {})
                        pricing = product.get('pricing', {})
                        reviews = product.get('reviews', {})

                        f.write(f"| {asin} | {info.get('brand', 'N/A')} | "
                               f"${pricing.get('current_price', 'N/A')} | "
                               f"{reviews.get('average_rating', 'N/A')}/5 | "
                               f"{reviews.get('total_count', 'N/A'):,} |\n")
                    except:
                        f.write(f"| {asin} | Error | - | - | - |\n")
                else:
                    f.write(f"| {asin} | Failed | - | - | - |\n")

            # Detailed analysis
            f.write("\n## Detailed Analysis\n\n")

            competitive_analysis = self.analyze_competitive_position(products)

            f.write("### Price Positioning\n")
            if competitive_analysis.get("price_analysis"):
                pa = competitive_analysis["price_analysis"]
                if "lowest" in pa:
                    f.write(f"- Lowest Price: {pa['lowest'][2]} at ${pa['lowest'][1]}\n")
                if "highest" in pa:
                    f.write(f"- Highest Price: {pa['highest'][2]} at ${pa['highest'][1]}\n")

            f.write("\n### Rating Leaders\n")
            if competitive_analysis.get("rating_analysis"):
                ra = competitive_analysis["rating_analysis"]
                if "top_rated" in ra:
                    f.write(f"- Highest Rated: {ra['top_rated'][3]} at {ra['top_rated'][1]}/5\n")

            f.write("\n---\n")
            f.write(f"*Generated by Amazon Competitor Analyzer*\n")

        print(f"Markdown report saved: {output_path}")

    def generate_json_report(self, products: Dict[str, Any], output_path: str):
        """Generate JSON report"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "products_analyzed": len(products),
            "products": products,
            "analysis": self.analyze_competitive_position(products)
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"JSON report saved: {output_path}")


def analyze_asins(asins: List[str], output_dir: str = None) -> Dict[str, Any]:
    """Main function to analyze multiple ASINs"""
    analyzer = AmazonCompetitorAnalyzer()

    print(f"Analyzing {len(asins)} ASINs...")

    # Scrape products
    products = analyzer.scrape_multiple_products(asins)

    # Generate reports if output directory specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        base_path = os.path.join(output_dir, "amazon_analysis")
        analyzer.generate_csv_report(products, f"{base_path}.csv")
        analyzer.generate_markdown_report(products, f"{base_path}.md")
        analyzer.generate_json_report(products, f"{base_path}.json")

    return products


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Amazon Competitor Analyzer")
    parser.add_argument("asins", nargs="+", help="ASINs to analyze")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    parser.add_argument("-k", "--api-key", help="SkillBoss API key")

    args = parser.parse_args()

    # Initialize with custom API key if provided
    if args.api_key:
        global SKILLBOSS_API_KEY
        SKILLBOSS_API_KEY = args.api_key

    # Run analysis
    products = analyze_asins(args.asins, args.output)

    print(f"\nAnalysis complete! Analyzed {len(products)} products.")


if __name__ == "__main__":
    main()

