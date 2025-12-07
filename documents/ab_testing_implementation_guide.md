# A/B Testing Implementation Guide
*Complete guide for implementing 50-50 A/B testing on Steven LP landing pages*

## Overview
This guide implements a simple A/B testing system to compare two different landing page versions and determine which has the best conversion rate. The solution is easy to implement, uses 50-50 random split testing, and provides a web dashboard for viewing results.

## Requirements Met
- ✅ Different LP versions that compete with each other
- ✅ 50-50 random A/B testing
- ✅ Conversion tracked on thank you page (`/post_install/`)
- ✅ Works at URL: `https://www.eguidesearches.com/stackfree`
- ✅ Supports image/text mechanism (`?kw={keyword}&img=true`)
- ✅ Easy to implement and find results
- ✅ Config file toggle to enable/disable test

---

## Architecture

### How It Works
1. **User visits landing page** → Client-side JavaScript checks sessionStorage
2. **No variant assigned?** → Randomly assigns 'a' or 'b' (50-50 split)
3. **Stores variant** in sessionStorage (session persistence) + localStorage (for conversion tracking)
4. **Adds to URL** → `?variant=a` parameter and reloads page
5. **Flask route** reads variant parameter and serves appropriate template
6. **All interactions tracked** with variant information (clicks, conversions, etc.)
7. **Dashboard** parses logs and displays metrics per variant

### Data Flow
```
Landing Page → Variant Assignment → sessionStorage + URL param
     ↓
Flask Route → Select Template (variant_a.html or variant_b.html)
     ↓
User Clicks CTA → Track with variant → Opens Chrome Store
     ↓
User Installs Extension → Redirects to /post_install/?variant=a&gclid=xxx
     ↓
Conversion Event → Google tag fires + Server logs with variant
     ↓
Dashboard (/admin/ab-results) → Parses logs → Shows metrics
```

---

## Implementation Steps

## PHASE 1: Configuration Setup (5 minutes)

### File: `config.py`
Add at the end of the file:

```python
# =============================================================================
# A/B Testing Configuration
# =============================================================================

# Master toggle to enable/disable A/B test
# Set to False to disable test and serve variant A to all users
AB_TEST_ENABLED = True

# Test metadata
AB_TEST_NAME = 'landing_page_design_v1'
AB_VARIANT_A_NAME = 'control'      # Current design
AB_VARIANT_B_NAME = 'treatment'    # Alternative design
AB_VARIANT_SPLIT = 0.5             # 50-50 split
```

---

## PHASE 2: Flask Route Modifications (30 minutes)

### File: `app.py`

#### 2.1 Update Landing Page Route
**Location**: Find the `@app.route('/')` function (around line 549-580)

**Replace** the existing function with:

```python
@app.route('/')
def landing_page():
    """Main landing page with A/B testing support"""
    keyword = request.args.get('kw', 'trending').strip()
    show_images = request.args.get('img', '').lower() == 'true'
    variant = request.args.get('variant', 'a').lower()  # NEW: Get variant from URL

    # Sanitize keyword
    if not keyword or len(keyword) > 100:
        keyword = 'trending'

    # NEW: Validate variant
    if variant not in ['a', 'b']:
        variant = 'a'

    # NEW: If A/B test disabled, force variant A
    if not AB_TEST_ENABLED:
        variant = 'a'

    # Don't show images on default page (no kw parameter) or if img=true not specified
    has_kw_param = request.args.get('kw') is not None
    show_images = show_images and has_kw_param

    # Get gclid for tracking
    gclid = request.args.get('gclid', '')

    # Detect browser type
    user_agent = request.headers.get('User-Agent', 'Unknown')
    browser_type = detect_browser_type(user_agent)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    # NEW: Log landing page visit with variant
    logger.info(f'LANDING_PAGE keyword="{keyword}" gclid="{gclid}" variant="{variant}" '
               f'show_images={show_images} has_kw_param={has_kw_param} '
               f'browser="{browser_type}" user_agent="{user_agent[:100]}" ip="{client_ip}"')

    # NEW: Select template based on variant
    template_name = f'index_variant_{variant}.html'

    return render_template(template_name,
                         keyword=keyword,
                         gclid=gclid,
                         show_images=show_images,
                         browser_type=browser_type,
                         variant=variant,              # NEW
                         ab_test_enabled=AB_TEST_ENABLED)  # NEW
```

#### 2.2 Update Post Install Route
**Location**: Find the `@app.route('/post_install/')` function (around line 927-931)

**Replace** with:

```python
@app.route('/post_install/')
def post_install():
    """Post-install conversion tracking page with A/B test support"""
    gclid = request.args.get('gclid', '')
    variant = request.args.get('variant', '')  # NEW: Get variant from URL

    # NEW: Log conversion with variant
    user_agent = request.headers.get('User-Agent', 'Unknown')[:100]
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    logger.info(f'CONVERSION gclid="{gclid}" variant="{variant}" '
               f'user_agent="{user_agent}" ip="{client_ip}"')

    return render_template('post_install.html', gclid=gclid, variant=variant)
```

#### 2.3 Update CTA Click Tracking
**Location**: Find the `@app.route('/api/track/click', methods=['POST'])` function (around line 695-719)

**Modify** the function to add variant tracking:

```python
@app.route('/api/track/click', methods=['POST'])
def track_click():
    """Track button clicks with A/B test variant"""
    try:
        data = request.get_json() or {}
        button_id = data.get('button_id', '')
        gclid = data.get('gclid', '')
        keyword = data.get('keyword', '')
        variant = data.get('variant', '')  # NEW: Add variant
        timestamp = datetime.now().isoformat()

        # Get additional tracking data
        user_agent = request.headers.get('User-Agent', 'Unknown')[:100]
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        referer = request.headers.get('Referer', '')

        # NEW: Log click event with variant
        logger.info(f'CTA_CLICK button="{button_id}" keyword="{keyword}" '
                   f'gclid="{gclid}" variant="{variant}" '
                   f'user_agent="{user_agent}" ip="{client_ip}" referer="{referer}" '
                   f'conversion_tracking={bool(gclid)}')

        return jsonify({'status': 'success', 'timestamp': timestamp})
    except Exception as e:
        logger.error(f'CTA_CLICK_ERROR exception="{str(e)}"')
        return jsonify({'error': 'Tracking failed'}), 500
```

#### 2.4 Update Exit Popup Tracking
**Location**: Find the `@app.route('/api/track/exit-popup', methods=['POST'])` function (around line 721-745)

**Modify** to add variant:

```python
@app.route('/api/track/exit-popup', methods=['POST'])
def track_exit_popup():
    """Track exit popup events with A/B test variant"""
    try:
        data = request.get_json() or {}
        event = data.get('event', '')
        gclid = data.get('gclid', '')
        keyword = data.get('keyword', '')
        variant = data.get('variant', '')  # NEW: Add variant
        timestamp = data.get('timestamp', datetime.now().isoformat())

        # Get additional tracking data
        user_agent = request.headers.get('User-Agent', 'Unknown')[:100]
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        referer = request.headers.get('Referer', '')

        # NEW: Log exit popup event with variant
        logger.info(f'EXIT_POPUP_EVENT event="{event}" keyword="{keyword}" '
                   f'gclid="{gclid}" variant="{variant}" '
                   f'user_agent="{user_agent}" ip="{client_ip}" referer="{referer}" '
                   f'conversion_tracking={bool(gclid)}')

        return jsonify({'status': 'success', 'event': event, 'timestamp': timestamp})
    except Exception as e:
        logger.error(f'EXIT_POPUP_ERROR exception="{str(e)}"')
        return jsonify({'error': 'Tracking failed'}), 500
```

#### 2.5 Add Dashboard Route
**Location**: Add at the end of the routes section in `app.py` (before `if __name__ == '__main__':`)

```python
@app.route('/admin/ab-results')
def ab_dashboard():
    """A/B test results dashboard - Windows compatible"""
    from utils.ab_log_parser import ABLogParser

    parser = ABLogParser()

    try:
        # Read last 5000 lines from log file for analysis
        log_lines = []
        log_file = 'app.log'  # Adjust path if logs are stored elsewhere

        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                # Read all lines and get last 5000
                all_lines = f.readlines()
                log_lines = all_lines[-5000:] if len(all_lines) > 5000 else all_lines

        metrics = parser.parse_logs(log_lines)
        results = parser.calculate_conversion_rates()
        winner, _ = parser.get_winner(min_impressions=50)

    except Exception as e:
        logger.error(f"Error reading logs for dashboard: {e}")
        # Return empty results on error
        results = {
            'a': {'impressions': 0, 'conversions': 0, 'clicks': 0,
                  'exit_popup_shows': 0, 'conversion_rate': 0.0, 'click_rate': 0.0},
            'b': {'impressions': 0, 'conversions': 0, 'clicks': 0,
                  'exit_popup_shows': 0, 'conversion_rate': 0.0, 'click_rate': 0.0}
        }
        winner = 'error'

    return render_template('ab_dashboard.html',
                         variant_a=results.get('a', {}),
                         variant_b=results.get('b', {}),
                         winner=winner,
                         test_enabled=AB_TEST_ENABLED,
                         test_name=AB_TEST_NAME)
```

---

## PHASE 3: Template Setup (30 minutes)

### Step 1: Rename Current Template
```bash
# In templates/ directory
# Rename index.html to index_variant_a.html
# Windows: ren templates\index.html templates\index_variant_a.html
```

### Step 2: Create Variant B Template
```bash
# Copy variant A to variant B
# Windows: copy templates\index_variant_a.html templates\index_variant_b.html
```

### Step 3: Add Variant Tracking Script
**Files**: Both `templates/index_variant_a.html` AND `templates/index_variant_b.html`

**Location**: Add just before the closing `</body>` tag in BOTH files

```html
    <!-- A/B Test Variant Tracking -->
    <script>
        // Make variant available to all scripts
        window.abTestVariant = '{{ variant }}';
        window.abTestEnabled = {{ 'true' if ab_test_enabled else 'false' }};
    </script>
</body>
</html>
```

### Step 4: Update CTA Click Tracking
**Files**: Both `templates/index_variant_a.html` AND `templates/index_variant_b.html`

**Location**: Find the `proceedWithInstallation()` function (around line 648-680)

**Find** this section:
```javascript
fetch('/api/track/click', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        button_id: 'main-cta',
        keyword: keyword,
        gclid: gclid
    })
})
```

**Replace** with:
```javascript
fetch('/api/track/click', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        button_id: 'main-cta',
        keyword: keyword,
        gclid: gclid,
        variant: window.abTestVariant  // NEW: Add variant
    })
})
```

### Step 5: Update Exit Popup Tracking
**Files**: Both `templates/index_variant_a.html` AND `templates/index_variant_b.html`

**Location**: Find where exit popup events are tracked (search for `trackEvent` or `/api/track/exit-popup`)

**Add** `variant: window.abTestVariant` to the request body

OR if using `static/js/exit-intent.js`:

**File**: `static/js/exit-intent.js`

**Find** the `trackEvent()` method (around line 176-198)

**Modify** to include variant:
```javascript
trackEvent(eventName, additionalData = {}) {
    try {
        const gclid = localStorage.getItem('gclid') || '';
        const keyword = new URLSearchParams(window.location.search).get('kw') || 'trending';
        const variant = window.abTestVariant || '';  // NEW: Get variant

        fetch('/api/track/exit-popup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event: eventName,
                keyword: keyword,
                gclid: gclid,
                variant: variant,  // NEW: Add variant
                timestamp: new Date().toISOString(),
                ...additionalData
            })
        }).catch(err => console.error('Exit popup tracking failed:', err));
    } catch (error) {
        console.error('Error tracking exit intent event:', error);
    }
}
```

---

## PHASE 4: Post Install Template Update (10 minutes)

### File: `templates/post_install.html`

**Location**: Find the JavaScript section (around lines 22-37)

**Replace** the existing script with:

```html
<script>
    // Get variant from URL, localStorage, or template
    const urlParams = new URLSearchParams(window.location.search);
    const variant = urlParams.get('variant') ||
                   localStorage.getItem('ab_variant') ||
                   '{{ variant }}' ||
                   '';

    // Get gclid from URL or localStorage
    const gclid = urlParams.get('gclid') ||
                 localStorage.getItem('gclid') ||
                 '{{ gclid }}';

    // Fire conversion event
    if (gclid) {
        gtag('event', 'conversion', {
            'send_to': 'AW-936222252/conversion',
            'transaction_id': '',
            'gclid': gclid
        });
    }

    // Log for debugging (includes variant now)
    console.log('Conversion fired - gclid:', gclid, 'variant:', variant);
</script>
```

---

## PHASE 5: Client-Side Variant Assignment (20 minutes)

### Step 1: Create A/B Test JavaScript
**File**: `static/js/ab-test.js` (NEW FILE)

**Create** this file with the following content:

```javascript
/**
 * A/B Test Variant Assignment
 * Assigns user to variant A or B on first visit within session
 * Stores assignment in sessionStorage for session persistence
 */

(function() {
    const STORAGE_KEY = 'ab_variant';
    const SPLIT_RATIO = 0.5;  // 50-50 split

    function getOrAssignVariant() {
        // Check for existing assignment in sessionStorage
        let variant = sessionStorage.getItem(STORAGE_KEY);

        if (!variant) {
            // New visitor within session - assign random variant
            variant = Math.random() < SPLIT_RATIO ? 'a' : 'b';
            sessionStorage.setItem(STORAGE_KEY, variant);
        }

        return variant;
    }

    function addVariantToUrl() {
        const variant = getOrAssignVariant();
        const urlParams = new URLSearchParams(window.location.search);

        // Only add if not already present
        if (!urlParams.has('variant')) {
            urlParams.set('variant', variant);

            // Reload with variant parameter (use replace to avoid back button issues)
            const newUrl = window.location.pathname + '?' + urlParams.toString();
            window.location.replace(newUrl);
        }

        // Store in localStorage for post_install tracking
        localStorage.setItem('ab_variant', variant);
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addVariantToUrl);
    } else {
        addVariantToUrl();
    }

    // Make variant available globally
    window.abVariant = getOrAssignVariant();
})();
```

### Step 2: Include Script in Templates
**Files**: Both `templates/index_variant_a.html` AND `templates/index_variant_b.html`

**Location**: Add in the `<head>` section, BEFORE other JavaScript files

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- A/B Test Script (must load first) -->
    <script src="{{ url_for('static', filename='js/ab-test.js') }}"></script>

    <!-- Rest of head content... -->
</head>
```

---

## PHASE 6: Log Parser & Dashboard (45 minutes)

### Step 1: Create Utils Directory
```bash
# Create utils directory if it doesn't exist
# Windows: mkdir utils
```

### Step 2: Create Log Parser
**File**: `utils/ab_log_parser.py` (NEW FILE)

```python
"""
A/B Test Log Parser
Parses Flask application logs to extract A/B test metrics
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class ABLogParser:
    def __init__(self, log_file_path: str = None):
        self.log_file_path = log_file_path
        self.metrics = {
            'a': {'impressions': 0, 'conversions': 0, 'clicks': 0, 'exit_popup_shows': 0},
            'b': {'impressions': 0, 'conversions': 0, 'clicks': 0, 'exit_popup_shows': 0}
        }

    def parse_logs(self, lines: List[str] = None) -> Dict:
        """Parse log lines and extract A/B test metrics"""
        if lines is None:
            if self.log_file_path:
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                return self.metrics

        for line in lines:
            # Parse LANDING_PAGE events (impressions)
            if 'LANDING_PAGE' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['impressions'] += 1

            # Parse CONVERSION events
            elif 'CONVERSION' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['conversions'] += 1

            # Parse CTA_CLICK events
            elif 'CTA_CLICK' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['clicks'] += 1

            # Parse EXIT_POPUP_EVENT (show events only)
            elif 'EXIT_POPUP_EVENT' in line and 'event="exit_popup_shown"' in line:
                variant = self._extract_field(line, 'variant')
                if variant in ['a', 'b']:
                    self.metrics[variant]['exit_popup_shows'] += 1

        return self.metrics

    def _extract_field(self, log_line: str, field_name: str) -> str:
        """Extract field value from log line"""
        pattern = f'{field_name}="([^"]*)"'
        match = re.search(pattern, log_line)
        return match.group(1) if match else ''

    def calculate_conversion_rates(self) -> Dict:
        """Calculate conversion rates for each variant"""
        results = {}

        for variant in ['a', 'b']:
            impressions = self.metrics[variant]['impressions']
            conversions = self.metrics[variant]['conversions']
            clicks = self.metrics[variant]['clicks']

            conv_rate = (conversions / impressions * 100) if impressions > 0 else 0.0
            click_rate = (clicks / impressions * 100) if impressions > 0 else 0.0

            results[variant] = {
                'impressions': impressions,
                'conversions': conversions,
                'clicks': clicks,
                'exit_popup_shows': self.metrics[variant]['exit_popup_shows'],
                'conversion_rate': round(conv_rate, 2),
                'click_rate': round(click_rate, 2)
            }

        return results

    def get_winner(self, min_impressions: int = 100) -> Tuple[str, Dict]:
        """Determine winning variant based on conversion rate"""
        results = self.calculate_conversion_rates()

        # Check if we have enough data
        if results['a']['impressions'] < min_impressions or results['b']['impressions'] < min_impressions:
            return 'insufficient_data', results

        # Compare conversion rates
        if results['a']['conversion_rate'] > results['b']['conversion_rate']:
            winner = 'a'
        elif results['b']['conversion_rate'] > results['a']['conversion_rate']:
            winner = 'b'
        else:
            winner = 'tie'

        return winner, results
```

### Step 3: Create Dashboard Template
**File**: `templates/ab_dashboard.html` (NEW FILE)

Create this file - see the full HTML in the next section or use this simplified version:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Test Results - {{ test_name }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Roboto', sans-serif; background-color: #f5f5f5; padding: 40px 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { color: #333; margin-bottom: 10px; }
        .status { display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: 500; }
        .status.active { background: #4caf50; color: white; }
        .status.inactive { background: #f44336; color: white; }
        .variants-container { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .variant-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: relative; }
        .variant-card.winner { border: 3px solid #4caf50; }
        .variant-card.winner::after { content: '🏆 WINNER'; position: absolute; top: 15px; right: 15px; background: #4caf50; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: 700; }
        .variant-card h2 { color: #333; margin-bottom: 20px; font-size: 24px; }
        .metric { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #eee; }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #666; font-weight: 500; }
        .metric-value { color: #333; font-weight: 700; font-size: 18px; }
        .metric-value.highlight { color: #1b68d2; font-size: 28px; }
        .refresh-button { background: #1b68d2; color: white; border: none; padding: 15px 30px; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 20px; }
        .refresh-button:hover { background: #1557b8; }
        .winner-announcement { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .winner-announcement h2 { font-size: 32px; margin-bottom: 15px; }
        .winner-announcement p { font-size: 18px; opacity: 0.9; }
        .insufficient-data { background: #ff9800; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }
        @media (max-width: 768px) { .variants-container { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>A/B Test Results: {{ test_name }}</h1>
            <span class="status {{ 'active' if test_enabled else 'inactive' }}">
                {{ 'ACTIVE' if test_enabled else 'INACTIVE' }}
            </span>
            <button class="refresh-button" onclick="location.reload()">Refresh Results</button>
        </div>

        {% if winner == 'insufficient_data' %}
        <div class="insufficient-data">
            <h3>⚠️ Insufficient Data</h3>
            <p>Need at least 50 impressions per variant for reliable results</p>
        </div>
        {% endif %}

        <div class="variants-container">
            <!-- Variant A -->
            <div class="variant-card {{ 'winner' if winner == 'a' else '' }}">
                <h2>Variant A (Control)</h2>
                <div class="metric">
                    <span class="metric-label">Impressions</span>
                    <span class="metric-value">{{ variant_a.impressions }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Clicks</span>
                    <span class="metric-value">{{ variant_a.clicks }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Click Rate</span>
                    <span class="metric-value">{{ variant_a.click_rate }}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Conversions</span>
                    <span class="metric-value">{{ variant_a.conversions }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Conversion Rate</span>
                    <span class="metric-value highlight">{{ variant_a.conversion_rate }}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Exit Popup Shows</span>
                    <span class="metric-value">{{ variant_a.exit_popup_shows }}</span>
                </div>
            </div>

            <!-- Variant B -->
            <div class="variant-card {{ 'winner' if winner == 'b' else '' }}">
                <h2>Variant B (Treatment)</h2>
                <div class="metric">
                    <span class="metric-label">Impressions</span>
                    <span class="metric-value">{{ variant_b.impressions }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Clicks</span>
                    <span class="metric-value">{{ variant_b.clicks }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Click Rate</span>
                    <span class="metric-value">{{ variant_b.click_rate }}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Conversions</span>
                    <span class="metric-value">{{ variant_b.conversions }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Conversion Rate</span>
                    <span class="metric-value highlight">{{ variant_b.conversion_rate }}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Exit Popup Shows</span>
                    <span class="metric-value">{{ variant_b.exit_popup_shows }}</span>
                </div>
            </div>
        </div>

        {% if winner == 'a' %}
        <div class="winner-announcement">
            <h2>🎉 Variant A Wins!</h2>
            <p>Variant A (Control) has a higher conversion rate</p>
            <p style="margin-top: 10px; font-size: 14px;">
                To deploy the winner: Set AB_TEST_ENABLED = False in config.py
            </p>
        </div>
        {% elif winner == 'b' %}
        <div class="winner-announcement">
            <h2>🎉 Variant B Wins!</h2>
            <p>Variant B (Treatment) has a higher conversion rate</p>
            <p style="margin-top: 10px; font-size: 14px;">
                To deploy: Set AB_TEST_ENABLED = False and update default template
            </p>
        </div>
        {% elif winner == 'tie' %}
        <div class="winner-announcement" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h2>🤝 It's a Tie!</h2>
            <p>Both variants have identical conversion rates</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
```

---

## Testing Your Implementation

### 1. Test Variant Assignment
1. Clear browser cache and cookies
2. Visit `http://localhost:5000/`
3. You should be redirected to `http://localhost:5000/?variant=a` or `?variant=b`
4. Refresh page - variant should stay the same (sessionStorage)
5. Open new browser/incognito - should get random variant

### 2. Test Template Rendering
- Visit `http://localhost:5000/?variant=a` - should load variant A
- Visit `http://localhost:5000/?variant=b` - should load variant B
- Both should support: `?variant=a&kw=gaming_laptop&img=true`

### 3. Test Tracking
- Click CTA button - check logs for `CTA_CLICK` with variant
- Check console logs in browser DevTools
- Verify `localStorage.ab_variant` is set

### 4. Test Conversion
- Complete install flow
- Visit `/post_install/` page
- Check logs for `CONVERSION` event with variant

### 5. Test Dashboard
- Visit `http://localhost:5000/admin/ab-results`
- Should show metrics for both variants
- Refresh to see updated numbers

---

## Viewing Results

### Access Dashboard
```
http://localhost:5000/admin/ab-results
```

Or in production:
```
https://www.eguidesearches.com/admin/ab-results
```

### Dashboard Shows:
- **Test Status**: Active or Inactive
- **Variant A Metrics**: Impressions, clicks, click rate, conversions, conversion rate, exit popup shows
- **Variant B Metrics**: Same metrics as variant A
- **Winner Declaration**: When sufficient data (50+ impressions per variant)

### Manual Log Analysis
You can also grep logs directly:

```bash
# Count impressions per variant
grep "LANDING_PAGE" app.log | grep 'variant="a"' | wc -l
grep "LANDING_PAGE" app.log | grep 'variant="b"' | wc -l

# Count conversions per variant
grep "CONVERSION" app.log | grep 'variant="a"' | wc -l
grep "CONVERSION" app.log | grep 'variant="b"' | wc -l
```

---

## Declaring a Winner

### Option 1: Variant A Wins (Keep Current Design)
Simply disable the test in `config.py`:

```python
AB_TEST_ENABLED = False
```

All users will now see variant A.

### Option 2: Variant B Wins (Deploy New Design)

**Step 1**: Backup current variant A
```bash
copy templates\index_variant_a.html templates\index_variant_a_backup.html
```

**Step 2**: Promote variant B to default
```bash
copy templates\index_variant_b.html templates\index_variant_a.html
```

**Step 3**: Disable test
```python
# config.py
AB_TEST_ENABLED = False
```

---

## Customizing Variant B

After implementing the system, edit `templates/index_variant_b.html` to test different:
- Headlines and copy
- CTA button text/color/size
- Images and layout
- Color scheme
- Trust badges
- Exit popup messaging
- Any other design elements

**Important**: Keep all functionality intact:
- Image loading mechanism
- Exit intent popup
- Tracking calls
- Browser detection

---

## Troubleshooting

### Issue: Variant not appearing in logs
**Solution**: Check that `window.abTestVariant` is defined in browser console

### Issue: Always getting same variant
**Solution**: Clear sessionStorage in browser DevTools → Application → Session Storage

### Issue: Dashboard shows no data
**Solution**:
1. Check log file path in `ab_dashboard()` route
2. Verify logs contain `variant="a"` or `variant="b"`
3. Check file permissions on log file

### Issue: Post install not tracking variant
**Solution**: Check that localStorage contains `ab_variant` key before extension install

### Issue: 404 on static files
**Solution**: Verify `static/js/ab-test.js` exists and Flask is serving static files

---

## File Checklist

After implementation, you should have:

- ✅ `config.py` - Added A/B test config section
- ✅ `app.py` - Updated 4 routes + added dashboard route
- ✅ `templates/index_variant_a.html` - Variant A template with tracking
- ✅ `templates/index_variant_b.html` - Variant B template with tracking
- ✅ `templates/post_install.html` - Updated conversion tracking
- ✅ `templates/ab_dashboard.html` - New dashboard template
- ✅ `static/js/ab-test.js` - New variant assignment script
- ✅ `utils/ab_log_parser.py` - New log parser utility
- ✅ `static/js/exit-intent.js` - Updated with variant tracking (optional)

---

## Key Benefits

1. **No Database Required** - Uses existing logging infrastructure
2. **Session Consistent** - Users see same variant within session
3. **Easy Toggle** - Single config flag to enable/disable
4. **Conversion Attribution** - Tracks variant through entire funnel
5. **Real-Time Results** - Dashboard updates on refresh
6. **Maintainable** - Clear separation of variant templates
7. **Backwards Compatible** - Existing URLs work (default to variant A)
8. **Simple to Extend** - Can add more variants (C, D, etc.)

---

## Next Steps

1. ✅ Implement all phases above
2. ✅ Test locally with both variants
3. ✅ Deploy to production
4. ✅ Monitor dashboard for results
5. ✅ Wait for statistical significance (minimum 50 impressions per variant)
6. ✅ Declare winner and disable test

---

## Support

If you encounter issues:
1. Check browser console for JavaScript errors
2. Check Flask logs for Python errors
3. Verify all files are in correct locations
4. Test with `AB_TEST_ENABLED = False` first
5. Gradually enable features

---

**Implementation Time**: ~2-3 hours total
**Testing Time**: ~30 minutes
**Data Collection**: ~1-2 weeks (depending on traffic)

Good luck with your A/B test! 🚀
