from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
from collections import defaultdict
import anthropic
import gzip
import io

app = Flask(__name__, static_folder='static')
CORS(app)

# Anthropic API key from environment
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

def fetch_wayback_snapshots(domain):
    """Fetch all available snapshots from Wayback Machine"""
    url = "http://web.archive.org/cdx/search/cdx"

    # Try multiple variations of the domain
    domain_variations = [
        f'{domain}/',      # with trailing slash
        f'{domain}',       # without trailing slash
    ]

    # Also try with http:// prefix
    if not domain.startswith('http'):
        domain_variations.extend([
            f'http://{domain}',
            f'http://{domain}/',
            f'https://{domain}',
            f'https://{domain}/',
        ])

    all_snapshots = []

    for domain_var in domain_variations:
        params = {
            'url': domain_var,
            'matchType': 'exact',
            'output': 'json',
            'fl': 'timestamp,original,statuscode',
            'filter': 'statuscode:200'
        }

        try:
            print(f"Trying to fetch snapshots for: {domain_var}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Skip header row
            if data and len(data) > 1:
                snapshots = data[1:]
                print(f"Found {len(snapshots)} snapshots for {domain_var}")
                all_snapshots.extend(snapshots)
        except Exception as e:
            print(f"No snapshots for {domain_var}: {e}")
            continue

    # Remove duplicates based on timestamp
    seen_timestamps = set()
    unique_snapshots = []
    for snapshot in all_snapshots:
        timestamp = snapshot[0]
        if timestamp not in seen_timestamps:
            seen_timestamps.add(timestamp)
            unique_snapshots.append(snapshot)

    return unique_snapshots

def fetch_archived_page(url, timestamp):
    """Fetch the HTML content of an archived page"""
    wayback_url = f"https://web.archive.org/web/{timestamp}id_/{url}"

    try:
        response = requests.get(wayback_url, timeout=30)
        response.raise_for_status()

        # Check if content is gzipped
        content = response.content
        if content[:2] == b'\x1f\x8b':  # gzip magic number
            content = gzip.decompress(content)

        return content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching archived page {timestamp}: {e}")
        return None

def extract_text_content(html):
    """Extract meaningful text content from HTML"""
    if not html:
        return ""

    soup = BeautifulSoup(html, 'lxml')

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer"]):
        script.decompose()

    # Extract meta descriptions
    meta_desc = ""
    for meta in soup.find_all('meta'):
        if meta.get('name') == 'description' or meta.get('property') == 'og:description':
            meta_desc = meta.get('content', '')
            break

    # Get title
    title = soup.title.string if soup.title else ""

    # Get headings
    headings = []
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        text = heading.get_text().strip()
        if text and len(text) < 200:
            headings.append(text)

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading/trailing space
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # Combine everything
    full_text = f"Title: {title}\n"
    if meta_desc:
        full_text += f"Meta Description: {meta_desc}\n"
    if headings:
        full_text += f"Headings: {', '.join(headings[:10])}\n"
    full_text += f"\nContent:\n{text[:5000]}"

    return full_text

def analyze_with_claude(content, snapshot_date, quarter, is_first=False):
    """Use Claude to analyze the page content and project revenue"""
    if not ANTHROPIC_API_KEY:
        return {
            "error": "ANTHROPIC_API_KEY environment variable not set",
            "pricing": "API key not configured",
            "marketing_copy": "API key not configured",
            "value_proposition": "API key not configured",
            "revenue_projection": "API key not configured"
        }

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    if is_first:
        prompt = f"""Analyze this website snapshot from {snapshot_date} ({quarter}) and extract:

1. **Business Start Date**: Based on the snapshot date, when did this business likely start?
2. **Value Proposition**: What does this company/product do? What problem does it solve?
3. **Product Focus**: What are the main products or services being offered?
4. **Marketing Copy**: The main headline, tagline, and key marketing messages (keep it concise).
5. **Pricing Strategy**: What pricing model are they likely using? (subscription, one-time purchase, freemium, etc.) Even if not visible, infer from the business model.
6. **Distribution Channels**: How are they reaching customers? (direct website, marketplaces, retail, etc.)
7. **Revenue Projection**: Based on the business model, market, and positioning, estimate:
   - Likely pricing range (even if not shown on site)
   - Estimated monthly revenue range
   - Key revenue drivers

Website Content:
{content[:8000]}

Return your analysis in JSON format with keys: start_date, value_proposition, product_focus, marketing_copy, pricing_strategy, distribution_channels, revenue_projection"""
    else:
        prompt = f"""Analyze this website snapshot from {snapshot_date} ({quarter}) and extract:

1. **Marketing Copy**: Main headline, tagline, and key marketing messages (concise).
2. **Value Proposition**: What does this company/product do?
3. **Product Focus**: Main products or features being promoted.
4. **Pricing Strategy**: What pricing model or tiers are mentioned/implied?
5. **Changes**: What seems different from earlier versions? (positioning, messaging, product focus)
6. **Revenue Projection**: Estimate monthly revenue range based on business maturity and positioning at this stage.

Website Content:
{content[:8000]}

Return your analysis in JSON format with keys: marketing_copy, value_proposition, product_focus, pricing_strategy, changes, revenue_projection"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # Try to parse as JSON
        try:
            # Look for JSON in the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass

        # If JSON parsing fails, return structured text
        return {
            "raw_analysis": response_text
        }

    except Exception as e:
        print(f"Error analyzing with Claude: {e}")
        return {
            "error": str(e)
        }

def organize_by_quarter(snapshots):
    """Organize snapshots by quarter and get one per quarter"""
    quarters = defaultdict(list)

    for snapshot in snapshots:
        timestamp = snapshot[0]
        url = snapshot[1]

        # Parse timestamp (format: YYYYMMDDHHmmss)
        year = timestamp[:4]
        month = timestamp[4:6]

        # Calculate quarter
        quarter = (int(month) - 1) // 3 + 1
        quarter_key = f"{year}Q{quarter}"

        quarters[quarter_key].append({
            'timestamp': timestamp,
            'url': url,
            'date': f"{year}-{month}-{timestamp[6:8]}"
        })

    # Get first snapshot of each quarter
    quarterly_snapshots = {}
    for quarter_key in sorted(quarters.keys()):
        quarterly_snapshots[quarter_key] = quarters[quarter_key][0]

    return quarterly_snapshots

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(ANTHROPIC_API_KEY)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_website():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400

        domain = data.get('domain', '').strip()

        if not domain:
            return jsonify({'error': 'Domain is required'}), 400

        # Remove protocol if present
        domain = domain.replace('https://', '').replace('http://', '').rstrip('/')

        print(f"Analyzing domain: {domain}")

        # Fetch all snapshots
        snapshots = fetch_wayback_snapshots(domain)

        if not snapshots:
            return jsonify({
                'error': 'No snapshots found in Web Archive',
                'message': f'The domain "{domain}" has no archived snapshots. Try a different domain or check if it exists in https://web.archive.org',
                'suggestions': [
                    'Make sure the domain is spelled correctly',
                    'Try with or without "www" prefix',
                    'Check if the site exists in Web Archive manually',
                    'Some newer sites may not have been archived yet'
                ]
            }), 404

        print(f"Found {len(snapshots)} snapshots")

        # Organize by quarter
        quarterly = organize_by_quarter(snapshots)

        print(f"Organized into {len(quarterly)} quarters")

        # Get earliest snapshot info
        earliest_quarter = min(quarterly.keys())
        earliest = quarterly[earliest_quarter]
        earliest_date = earliest['date']

        # Analyze each quarter
        timeline_data = []
        first_analysis = None

        for i, quarter_key in enumerate(sorted(quarterly.keys())):
            snapshot = quarterly[quarter_key]

            print(f"Analyzing {quarter_key}: {snapshot['timestamp']}")

            # Fetch the page
            html = fetch_archived_page(snapshot['url'], snapshot['timestamp'])

            if html:
                text_content = extract_text_content(html)

                # Analyze with Claude
                is_first = (i == 0)
                analysis = analyze_with_claude(text_content, snapshot['date'], quarter_key, is_first)

                if is_first:
                    first_analysis = analysis

                timeline_data.append({
                    'quarter': quarter_key,
                    'timestamp': snapshot['timestamp'],
                    'date': snapshot['date'],
                    'url': snapshot['url'],
                    'analysis': analysis
                })
            else:
                print(f"Failed to fetch {quarter_key}")

        # Extract top-level info
        start_date = earliest_date
        distribution_channels = first_analysis.get('distribution_channels', 'Unknown') if first_analysis else 'Unknown'

        result = {
            'domain': domain,
            'start_date': start_date,
            'distribution_channels': distribution_channels,
            'total_quarters': len(quarterly),
            'timeline': timeline_data
        }

        return jsonify(result)

    except Exception as e:
        print(f"Error in analyze_website: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
