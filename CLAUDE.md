# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NovaView Landing Page System - A Flask-based landing page application for browser extension promotion with dynamic image search, conversion tracking, and exit intent functionality.

**Repository:** https://github.com/yanivbarlev/novaview-lp
**Primary Domain:** www.eguidesearches.com
**Product:** NovaView browser extension (Chrome/Edge)

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file (required)
cp .env.example .env
# Edit .env with GOOGLE_API_KEY and GOOGLE_CX
```

### Running the Application
```bash
# Development server (localhost:5000)
python app.py

# Deploy to production (PythonAnywhere)
python deploy.py
# See DEPLOYMENT.md for details
```

### Testing URLs
```bash
# Landing page without images
http://localhost:5000/?kw=minecraft

# Landing page with images (requires img=true AND kw parameter)
http://localhost:5000/?kw=minecraft&img=true

# Landing page with GCLID tracking
http://localhost:5000/?kw=minecraft&img=true&gclid=test123

# StackFree landing page (same logic as root)
http://localhost:5000/stackfree?kw=minecraft&img=true

# StackFree with GCLID
http://localhost:5000/stackfree?kw=minecraft&img=true&gclid=test123

# Thank you page
http://localhost:5000/thankyou-downloadmanager.html?source=novaview&gclid=test123

# Legal pages
http://localhost:5000/privacy
http://localhost:5000/terms
http://localhost:5000/eula
```

## Architecture

### Core Application Structure

**app.py** (~415 lines) - Main Flask application
- 15 routes total (8 main + 7 legal pages)
- NO server-side blocking on image fetching (async client-side loading)
- Uses absolute template/static paths to prevent loading conflicts
- Comprehensive logging for all requests

**config.py** (42 lines) - Centralized configuration
- Browser extension store URLs (CRITICAL: verify these match current product)
- Google Tag Manager ID (AW-1006081641)
- Image cache settings (TTL, target size, dimensions)
- Google API credentials (loaded from .env)

**image_service.py** (578 lines) - Image search and caching
- Three-tier caching system (final images, candidates, API fallback)
- Perceptual hashing for duplicate detection
- Binary search compression to ~25KB target
- 100-day cache TTL

**utils.py** (132 lines) - Helper functions
- Browser detection (CRITICAL: order-sensitive - Edge/Opera before Chrome)
- Keyword sanitization for filenames
- Image validation (PIL-based)

### Key Design Patterns

**Modular Separation:**
- Routes handle HTTP only (no business logic)
- ImageSearchService encapsulates all image operations
- Configuration centralized (no hardcoded URLs in routes/templates)
- Template globals expose config values

**Performance Optimization:**
- Landing page NEVER blocks on image fetching
- Page load <0.1s regardless of cache status
- Images load asynchronously via JavaScript
- Cache-aware UI (placeholders only when cache_status='HIT')

**Browser-Specific Behavior:**
- User-Agent detection determines browser type
- Different CTA text/URLs for Chrome vs Edge
- Order matters: check Edge/Opera BEFORE Chrome (they contain "Chrome" in UA)

## Critical Implementation Details

### Image Display Logic

Images are conditionally displayed based on TWO parameters:
```python
# Server-side check (app.py:87-89)
has_kw_param = request.args.get('kw') is not None
show_images = show_images and has_kw_param  # img=true AND kw exists
```

**Client-side behavior:**
- If `cache_status='HIT'`: Show placeholders immediately, load images after 300ms
- If `cache_status='MISS'`: Keep section hidden, fetch in background for next visit
- Never show placeholders for uncached images (prevents empty boxes)

### Three-Tier Caching System

**Tier 1: Final Images** (`images/{keyword}_1.webp`)
- Optimized, compressed images (~25KB each)
- 100-day TTL
- Direct serving via `/image/<filename>`

**Tier 2: Candidates Cache** (`images/cache/{keyword}/candidate_*.{ext}`)
- Raw downloaded images (up to 10 per keyword)
- Temporary storage for selection algorithm
- Used for perceptual hashing and diversity selection

**Tier 3: Google API**
- Only called when both Tier 1 and Tier 2 miss
- ~1 API call per keyword per 100 days
- Results stored in Tier 2, best 3 promoted to Tier 1

### Exit Intent Popup System

**Flow:**
1. User clicks CTA → Chrome store opens in new tab
2. `ExitIntentPopup` class monitors the store tab (checks every 1s)
3. When tab closes OR user returns → 500ms delay → popup shows
4. Session-based limiting (sessionStorage prevents spam)
5. All interactions tracked via `/api/track/exit-popup`

**Implementation:** `static/js/exit-intent.js` (214 lines)

### GCLID Tracking Flow

1. Landing page receives: `?gclid=abc123`
2. Stored in localStorage: `localStorage.setItem('gclid', 'abc123')`
3. Appended to ALL store URLs (main CTA, image clicks, exit popup)
4. Tracked in ALL analytics events
5. Passed to thank you page for conversion attribution
6. Used as `transaction_id` in Google Tag Manager events

### Template Configuration

Templates access configuration via template globals:
```python
# In templates: {{ chrome_store_url() }}
@app.template_global()
def chrome_store_url():
    return CHROME_STORE_URL
```

**Available globals:**
- `chrome_store_url()` - Chrome Web Store URL
- `edge_store_url()` - Edge Add-ons URL
- `google_tag_id()` - Google Tag Manager ID

## Routes Reference

### Main Application Routes

**`/`** - Landing page
- Parameters: `kw` (keyword), `img` (true/false), `gclid` (tracking)
- Browser detection and personalization
- NO server-side image fetching (async only)

**`/stackfree`** - StackFree landing page
- Identical logic to root landing page
- Same parameters: `kw` (keyword), `img` (true/false), `gclid` (tracking)
- Uses same template (landing.html)
- Separate logging prefix (STACKFREE_PAGE vs LANDING_PAGE)

**`/api/search`** - Image search API
- Parameter: `kw` (keyword)
- Returns: JSON with images array, count, cache_status
- Uses intelligent caching (checks Tier 1 → Tier 2 → API)

**`/image/<filename>`** - Image serving
- Serves optimized images from `images/` directory
- ~25KB WebP files

**`/api/track/click`** - CTA click tracking (POST)
- Logs button clicks with GCLID attribution

**`/api/track/exit-popup`** - Exit popup tracking (POST)
- Tracks popup impressions/dismissals/clicks

**`/thankyou-downloadmanager.html`** - Local thank you page
- Google Tag conversion tracking
- 3-second countdown → YouTube redirect
- URL: `https://www.youtube.com/@TechInsiderNextGen?sub_confirmation=1`

**`/post_install/`** - Production redirect
- Redirects to: `https://www.eguidesearches.com/thankyou-downloadmanager.html?source=novaview&gclid=...`

### Legal Pages

All use `legal.html` base template:
- `/privacy` - Privacy Policy
- `/terms` - Terms of Use
- `/eula` - End User License Agreement
- `/copyright` - Copyright Policy
- `/about` - About Us
- `/uninstall` - Uninstall Instructions
- `/contact` - Contact Us

## Configuration Management

### Critical URLs (config.py)

**ALWAYS verify these match the current product before deployment:**
```python
CHROME_STORE_URL = 'https://chromewebstore.google.com/detail/novaview/...'
EDGE_STORE_URL = 'https://microsoftedge.microsoft.com/addons/detail/novaview/...'
```

### Google Tag Manager

Current ID: `AW-1006081641`
Conversion label: `novaview_install`

### Environment Variables (.env)

Required:
```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CX=your_custom_search_engine_id_here
```

## Critical Development Practice

**ALWAYS VERIFY YOUR CHANGES BEFORE FINISHING:**

Before completing any task that modifies the landing page appearance or functionality:

1. **Start the development server** (if not already running):
   ```bash
   python app.py
   ```

2. **Check the actual rendered page** in your browser or with curl:
   ```bash
   curl -s "http://localhost:5000/?kw=test&img=true" | head -200
   ```

3. **Compare with the live production site**:
   - Production: https://www.eguidesearches.com/?kw=powerpoint&img=true
   - Local: http://localhost:5000/?kw=test&img=true

4. **Verify all visual elements render correctly**:
   - Logo displays properly
   - Images load (if img=true)
   - Chrome/Edge store badge is sharp and clear
   - CTA button appears correctly
   - Footer links work
   - No broken images or blank rectangles

5. **Never assume CSS/HTML changes work** - always test them visually

This prevents shipping broken changes like blank rectangles, blurry images, or layout issues.

## Common Development Tasks

### Adding a New Route

1. Add route handler in `app.py`
2. Create template in `templates/` (if needed)
3. Update this file with route documentation
4. Test locally with multiple browsers

### Updating Store URLs

1. Edit `config.py` - CHROME_STORE_URL and EDGE_STORE_URL
2. Verify URLs are correct (critical for conversions)
3. Test that URLs open correctly in browser
4. Deploy and verify in production

### Modifying Image Cache Behavior

- Cache TTL: `config.py` - CACHE_TTL_HOURS
- Image dimensions: `config.py` - THUMBNAIL_SIZE
- Target file size: `config.py` - TARGET_FILE_SIZE
- Selection algorithm: `image_service.py` - ImageSearchService class

### Deploying to Production

1. **Test locally first:**
   ```bash
   python app.py
   # Test at http://localhost:5000
   ```

2. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin master
   ```

3. **Deploy to PythonAnywhere:**
   ```bash
   python deploy.py
   ```

4. **Verify deployment:**
   - Check https://www.eguidesearches.com
   - Test key functionality
   - Monitor server logs

**See DEPLOYMENT.md for detailed deployment documentation.**

### Debugging Template Loading Issues

**Problem:** Flask loads templates from wrong directory

**Solution:**
1. Kill all Python processes: `taskkill /IM python.exe` (Windows)
2. Verify absolute paths in app.py:
   ```python
   _current_dir = os.path.dirname(os.path.abspath(__file__))
   app = Flask(__name__,
               template_folder=os.path.join(_current_dir, 'templates'),
               static_folder=os.path.join(_current_dir, 'static'))
   ```
3. Run app.py from the correct directory

## Browser Detection

**CRITICAL: Order matters!**

Edge and Opera contain "Chrome" in their User-Agent strings, so they MUST be checked first:

```python
# Correct order (utils.py:50-68)
if 'opr/' in user_agent or 'opera/' in user_agent:
    return 'opera'
if 'edg/' in user_agent or 'edge/' in user_agent:
    return 'edge'
if 'chrome/' in user_agent:  # MUST come after Edge/Opera
    return 'chrome'
```

## Production Deployment (PythonAnywhere)

### Quick Deploy

```bash
python deploy.py
```

**See DEPLOYMENT.md for complete deployment documentation.**

### Production Configuration

**Server:** PythonAnywhere
**User:** yanivbl
**App Directory:** `/home/yanivbl/apps/eguidesearches-novaview`
**WSGI File:** `/var/www/www_eguidesearches_com_wsgi.py`
**Production URL:** https://www.eguidesearches.com
**Python Version:** 3.10
**Virtualenv:** `/home/yanivbl/.virtualenvs/mysite-virtualen`

### Deployment Files

- `deploy.py` - Automated deployment script
- `DEPLOYMENT.md` - Complete deployment documentation
- `.deployment/` - Deployment logs and temporary files (NOT in git)
- `.deployment/deployment.log` - Activity log with timestamps

### Environment Variables

Add to web app settings or create `.env` file in working directory.

## A/B Testing Variant Assignment

### Overview

The application implements fair A/B testing with a three-tier variant assignment system:

1. **URL Parameter** (`?variant=a` or `?variant=b`) - Explicit override for testing
2. **Cookie** (`ab_variant`) - Maintains consistency for returning users
3. **Random 50/50** - Fair distribution for new users via `random.choice(['a', 'b'])`

### Implementation Details

**Location:** `app.py` lines 126-139 (landing page) and 213-238 (stackfree route)

**Code Flow:**
```python
variant_param = request.args.get('variant', '').lower()
variant_cookie = request.cookies.get('ab_variant', '')

if variant_param in ['a', 'b']:
    variant = variant_param  # URL parameter takes precedence
elif variant_cookie in ['a', 'b']:
    variant = variant_cookie  # Use existing cookie
else:
    variant = random.choice(['a', 'b'])  # Random for new users

# Cookie expires in 30 days
response.set_cookie('ab_variant', variant, max_age=30*24*60*60, samesite='Lax')
```

### Testing the Variant System

**Local Testing:**
```bash
# Start dev server
python app.py

# Test URL parameter override
curl http://localhost:5000/?kw=test&variant=b

# Test cookie persistence (in same session)
# First request: no parameter → random variant assigned
# Second request: same session → uses cookie from first request
```

**Production Testing:**
```bash
# Check current production logs
python << 'EOF'
import requests
resp = requests.get(
    'https://www.pythonanywhere.com/api/v0/user/yanivbl/files/path/home/yanivbl/apps/eguidesearches-novaview/app.log',
    headers={'Authorization': 'Token YOUR_API_TOKEN'}
)
lines = [l for l in resp.text.split('\n') if 'LANDING_PAGE' in l]
# Count variant distribution in last 50 lines
variants = {'a': 0, 'b': 0}
for line in lines[-50:]:
    if 'variant="a"' in line: variants['a'] += 1
    elif 'variant="b"' in line: variants['b'] += 1
print(f"Distribution: A={variants['a']}, B={variants['b']}")
EOF
```

### Key Features

- **Fair Distribution:** New users get random 50/50 split
- **User Persistence:** Returning users maintain their assigned variant via 30-day cookie
- **Testing Flexibility:** Can force specific variant with `?variant=a` parameter
- **Logging:** All assignments logged with `variant="a"` or `variant="b"` tags
- **Equal Paired Traffic:** Both variants get equal share of mysterious paired requests, making relative performance comparison valid

### Important Notes

- The random assignment fixes the previous bias where variant A was getting 3:1 more impressions
- Cookie expires after 30 days to accommodate delayed installations
- URL parameter always takes precedence (useful for direct testing/debugging)
- Both landing page (`/`) and stackfree (`/stackfree`) routes implement identical logic

## Known Issues

1. **Multiple Flask Servers:** If templates load incorrectly, kill all Python processes
2. **Cache Storage:** Images stored on disk (no database) - consider cloud storage for scale
3. **Google API Limits:** 100 queries/day on free tier (caching minimizes usage)
4. **Session Storage:** Exit popup uses sessionStorage (resets when browser closes)

## File Locations

**Application Code:**
- Main app: `app.py`
- Configuration: `config.py`
- Image service: `image_service.py`
- Utilities: `utils.py`

**Templates & Assets:**
- Templates: `templates/`
- Static assets: `static/`
- Cached images: `images/`
- Candidate cache: `images/cache/`

**Documentation:**
- Project overview: `README.md`
- Claude instructions: `CLAUDE.md`
- Deployment guide: `DEPLOYMENT.md`
- Build status: `documents/build-status.md`

**Deployment:**
- Deployment script: `deploy.py`
- Deployment logs: `.deployment/` (NOT in git)

**Configuration:**
- Dependencies: `requirements.txt`
- Environment: `.env` (NOT in git)

## Performance Expectations

- Page load: <0.1s (always, regardless of cache status)
- Image size: ~25KB each (~75KB total for 3 images)
- API calls: ~1 per keyword per 100 days
- Total codebase: ~1,250 lines (excluding templates)
