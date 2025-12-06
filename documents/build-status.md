# NovaView Landing Page System - Build Status

**Project:** New Landing Page System (new-lp)
**Repository:** https://github.com/yanivbarlev/novaview-lp
**Last Updated:** 2025-12-06
**Status:** ✅ Ready for Testing (Not yet deployed to PythonAnywhere)

## Overview

Complete Flask application for NovaView extension landing pages with:
- Minimal architecture (7 main routes + 7 legal pages)
- Async image loading with intelligent caching
- Browser-specific CTAs (Chrome/Edge)
- Exit intent popup system
- GCLID tracking and conversion attribution
- Thank you page with YouTube redirect
- Legal pages (Privacy, Terms, EULA, etc.)
- Teal gradient background matching brand
- Google Tag Manager integration (AW-1006081641)

## Architecture Summary

### Core Files Created

**Configuration & Services:**
- `config.py` - Centralized configuration (store URLs, Google Tag ID, image settings)
- `utils.py` - Helper functions (browser detection, keyword sanitization, image validation)
- `image_service.py` - Image caching and selection logic (578 lines)
- `app.py` - Flask application with 14 routes (337 lines)
- `requirements.txt` - Dependencies (Flask, Pillow, imagehash, python-dotenv, requests)
- `.gitignore` - Excludes __pycache__, .env, venv

**Templates:**
- `templates/landing.html` - Main landing page (633 lines)
- `templates/thankyou.html` - Conversion tracking page (249 lines)
- `templates/legal.html` - Legal pages base template (143 lines)
- `templates/legal_privacy.html` - Privacy policy
- `templates/legal_terms.html` - Terms of use
- `templates/legal_eula.html` - End user license agreement
- `templates/legal_copyright.html` - Copyright policy
- `templates/legal_about.html` - About us
- `templates/legal_uninstall.html` - Uninstall instructions
- `templates/legal_contact.html` - Contact information

**Static Assets:**
- `static/js/exit-intent.js` - Exit popup monitoring (214 lines)
- `static/logo.png` - NovaView logo
- `static/chrome-icon.png` - Chrome Web Store badge
- `static/edge-icon.png` - Edge Add-ons badge

**Images:**
- 75+ pre-cached images in `images/` directory
- Various keywords: chrome, minecraft, roblox, robux, gta_5, pokemon, etc.
- Optimized WebP format (~25KB each)

## Features Implemented

### 1. Landing Page (`/`)
**URL Structure:** `/?kw=<keyword>&img=true&gclid=<gclid>`

**Features:**
- Teal gradient background with SVG decorative polygons
- White card container with rounded corners
- Logo, title, subtitle, images, CTA button
- Browser detection (Chrome/Edge/Firefox/Safari)
- Async image loading via JavaScript
- Cache-aware UI (shows placeholders only if images cached)
- Clickable images (same behavior as CTA button)
- Exit intent popup on Chrome store tab close/return
- GCLID tracking via localStorage
- Google Tag Manager integration
- Responsive design (mobile/desktop)

**Key Implementation Details:**
- Server-side: NO blocking on API calls (<0.1s response time)
- Client-side: Async image fetch via `/api/search`
- Images only display if `img=true` AND `kw` parameter present
- Images only show placeholders if `cache_status='HIT'`
- Images load in background if `cache_status='MISS'` (cached for next visit)

**Background & Styling:**
```css
background-color: #eff5f4;
background-image: url("data:image/svg+xml,<SVG with teal gradient>");
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
```

**Footer:**
- Transparent background (shows gradient)
- White text with underlined links
- Copyright + 6 legal page links
- Hover effect removes underline

### 2. Image Search API (`/api/search`)
**URL Structure:** `/api/search?kw=<keyword>`

**Response:**
```json
{
  "keyword": "minecraft",
  "images": [
    {"url": "/image/minecraft_1.webp", "title": "...", "thumbnail": "..."},
    {"url": "/image/minecraft_2.webp", "title": "...", "thumbnail": "..."},
    {"url": "/image/minecraft_3.webp", "title": "...", "thumbnail": "..."}
  ],
  "count": 3,
  "cached": true,
  "cache_status": "HIT",
  "api_call_made": false
}
```

**Three-Tier Caching:**
1. **Final Images Cache:** `images/{keyword}_{1-3}.{ext}` (100-day TTL)
2. **Candidates Cache:** `images/cache/{keyword}/candidate_{1-10}.{ext}` (temporary)
3. **Google API:** Fallback when no cache exists

**Image Selection Algorithm:**
- Downloads 10 candidate images from Google Custom Search API
- Uses perceptual hashing (dhash) to group similar images
- Selects largest (best quality) image from each similarity group
- Compresses to ~25KB target size (480x270px, 16:9 aspect ratio)
- Promotes selected images to final cache

### 3. Image Serving (`/image/<filename>`)
Serves optimized images from `images/` directory.

### 4. CTA Click Tracking (`/api/track/click`)
**Request Body:**
```json
{
  "button_id": "main-cta" | "image-1" | "image-2" | "image-3",
  "keyword": "minecraft",
  "gclid": "test123",
  "timestamp": "2025-12-06T17:00:00.000Z"
}
```

Logs all CTA clicks for analytics.

### 5. Exit Popup Tracking (`/api/track/exit-popup`)
**Request Body:**
```json
{
  "event": "exit_popup_shown" | "exit_popup_dismissed" | "exit_popup_cta_clicked",
  "keyword": "minecraft",
  "gclid": "test123",
  "timestamp": "2025-12-06T17:00:00.000Z"
}
```

Tracks exit popup interactions.

### 6. Thank You Page (Local) (`/thankyou-downloadmanager.html`)
**URL Structure:** `/thankyou-downloadmanager.html?source=novaview&gclid=<gclid>`

**Features:**
- Same teal gradient background as landing page
- Animated checkmark with smooth CSS animations
- Google Tag Manager conversion tracking
- GCLID parameter handling (transaction_id)
- "What's Next" info box with 4 action items
- 3-second countdown spinner
- Auto-redirect to YouTube channel with subscription prompt

**Conversion Tracking:**
```javascript
gtag('event', 'conversion', {
  'send_to': 'AW-1006081641/novaview_install',
  'value': 1.0,
  'currency': 'USD',
  'transaction_id': gclid  // If gclid present
});
```

**Redirect After 3 Seconds:**
```
https://www.youtube.com/@TechInsiderNextGen?sub_confirmation=1
```

The `sub_confirmation=1` parameter triggers YouTube's subscription prompt automatically.

### 7. Post-Install Redirect (`/post_install/`)
**URL Structure:** `/post_install/?gclid=<gclid>`

**Behavior:**
Returns 302 redirect to production thank you page:
```
https://www.eguidesearches.com/thankyou-downloadmanager.html?source=novaview&gclid=<gclid>
```

This route is used in production to redirect to the main eguidesearches.com domain.

### 8. Legal Pages
All legal pages use the `legal.html` base template with teal header and footer:

- `/privacy` - Privacy Policy
- `/terms` - Terms of Use
- `/eula` - End User License Agreement
- `/copyright` - Copyright Policy (DMCA compliance)
- `/about` - About Us (mission, features)
- `/uninstall` - Uninstall Instructions (Chrome/Edge)
- `/contact` - Contact Us (email addresses for support, business, legal, security)

## Exit Intent Popup System

### How It Works
1. User clicks "Add to Chrome" → Chrome Web Store opens in new tab
2. System monitors the Chrome store tab (checks every 1 second)
3. When user closes tab OR returns to landing page → 500ms delay → Exit popup shows
4. Popup shows once per session (sessionStorage prevents spam)
5. All interactions tracked via `/api/track/exit-popup`

### Features
- Session-based display limiting (`sessionStorage`)
- Comprehensive tracking (impressions, clicks, dismissals)
- Mobile responsive design
- Matches site branding (teal accent, white background)
- Animated slide-in effect
- Pulsing CTA button

### Implementation Files
- `static/js/exit-intent.js` - Core logic (214 lines)
- `templates/landing.html` - Popup HTML and event listeners
- CSS in landing.html - Popup styling and animations

## GCLID Tracking Flow

### 1. Landing Page Receives GCLID
```
/?kw=minecraft&img=true&gclid=abc123
```

### 2. Stored in localStorage
```javascript
localStorage.setItem('gclid', 'abc123');
```

### 3. Appended to All Store URLs
**Main CTA Button:**
```html
<a href="https://chromewebstore.google.com/detail/novaview/...?gclid=abc123">
```

**Image Clicks:**
```javascript
const finalStoreUrl = trackedGclid ? `${storeUrl}?gclid=${trackedGclid}` : storeUrl;
window.open(finalStoreUrl, '_blank');
```

**Exit Popup CTA:**
```javascript
let storeUrl = window.chromeStoreUrl;
if (gclid) {
  storeUrl += `?gclid=${gclid}`;
}
window.open(storeUrl, '_blank');
```

### 4. Tracked in All Analytics Events
```javascript
fetch('/api/track/click', {
  body: JSON.stringify({
    button_id: 'main-cta',
    keyword: keyword,
    gclid: trackedGclid,  // Included in all events
    timestamp: new Date().toISOString()
  })
});
```

### 5. Conversion Tracking
```javascript
gtag('event', 'conversion', {
  'send_to': 'AW-1006081641/novaview_install',
  'transaction_id': gclid  // Links conversion to original click
});
```

## Configuration Management

### Centralized Configuration (`config.py`)
```python
# Chrome/Edge Store URLs
CHROME_STORE_URL = 'https://chromewebstore.google.com/detail/novaview/...'
EDGE_STORE_URL = 'https://microsoftedge.microsoft.com/addons/detail/novaview/...'

# Google Tag Manager
GOOGLE_TAG_ID = 'AW-1006081641'

# Image Settings
FINAL_IMAGES_DIR = './images'
CANDIDATES_CACHE_DIR = './images/cache'
IMAGE_TARGET_SIZE_KB = 25
IMAGE_DIMENSIONS = (480, 270)  # 16:9 aspect ratio
CACHE_TTL_DAYS = 100
```

### Template Global Functions
```python
@app.template_global()
def chrome_store_url():
    return CHROME_STORE_URL

@app.template_global()
def edge_store_url():
    return EDGE_STORE_URL

@app.template_global()
def google_tag_id():
    return GOOGLE_TAG_ID
```

Usage in templates:
```html
{{ chrome_store_url() }}
{{ edge_store_url() }}
{{ google_tag_id() }}
```

## Key Fixes & Improvements

### Issue 1: Images Showing When img=false
**Problem:** Images displayed even when `img=false`
**Fix:** Added `style="display: none;"` to images-section, only show when `img=true` AND `kw` parameter exists

### Issue 2: Placeholders for Uncached Images
**Problem:** Showed placeholders even when images not cached
**Fix:** Check `cache_status` from API - only show placeholders if `'HIT'`, keep hidden if `'MISS'`

### Issue 3: Template Loading Issues
**Problem:** Multiple Flask servers using parent templates/ directory
**Fix:**
- Killed all Python processes
- Added absolute template paths:
```python
_current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(_current_dir, 'templates'),
            static_folder=os.path.join(_current_dir, 'static'))
```

### Issue 4: Exit Popup Not Clickable
**Problem:** Event listeners not connected
**Fix:** Added DOMContentLoaded listeners for close button, CTA, and backdrop click

### Issue 5: CTA Button Redirecting Original Tab
**Problem:** Both original tab and new tab redirected to store
**Fix:** Added `e.preventDefault()` to CTA click handler

### Issue 6: GCLID Not Passed Correctly
**Problem:** Image click handler checked wrong variable
**Fix:** Changed `gclid` to `trackedGclid` in conditional check

### Issue 7: Store URL Not Available to Exit Popup
**Problem:** Exit popup couldn't access store URL
**Fix:** Added `window.chromeStoreUrl = storeUrl;` to make it globally available

### Issue 8: Logo Alignment
**Problem:** Logo appeared on right side
**Fix:** Added `flex-direction: column` to .container CSS

### Issue 9: Footer Not Visible
**Problem:** White text on light background
**Fix:** Removed dark background, kept white text (shows gradient through transparent background)

### Issue 10: Thank You Page Redirect
**Problem:** Needed to redirect to YouTube channel, not Google
**Fix:** Changed redirect URL to:
```javascript
window.location.href = 'https://www.youtube.com/@TechInsiderNextGen?sub_confirmation=1';
```

## Testing

### Local Testing URLs

**Landing Page (no images):**
```
http://localhost:5000/?kw=minecraft
```

**Landing Page (with images):**
```
http://localhost:5000/?kw=minecraft&img=true
```

**Landing Page (with tracking):**
```
http://localhost:5000/?kw=minecraft&img=true&gclid=test123
```

**Thank You Page:**
```
http://localhost:5000/thankyou-downloadmanager.html?source=novaview&gclid=test123
```

**Legal Pages:**
```
http://localhost:5000/privacy
http://localhost:5000/terms
http://localhost:5000/eula
http://localhost:5000/copyright
http://localhost:5000/about
http://localhost:5000/uninstall
http://localhost:5000/contact
```

### Testing Checklist

**Landing Page:**
- [ ] Page loads in <0.1s (no server-side blocking)
- [ ] Logo displays correctly
- [ ] Title shows "Get {Keyword} Free"
- [ ] Subtitle shows correct text
- [ ] CTA button is centered and clickable
- [ ] Store badge appears below card
- [ ] Footer links work
- [ ] Background gradient displays correctly

**Images (img=true):**
- [ ] No placeholders show when cache_status='MISS'
- [ ] Placeholders show when cache_status='HIT'
- [ ] Images load after 300ms delay
- [ ] Images are clickable
- [ ] Image clicks open Chrome store in new tab
- [ ] Image clicks preserve gclid
- [ ] Image section hidden when img=false

**Exit Popup:**
- [ ] Popup shows when Chrome store tab closes
- [ ] Popup shows when user returns from Chrome store
- [ ] Popup only shows once per session
- [ ] Close button works
- [ ] CTA button opens Chrome store
- [ ] Backdrop click closes popup
- [ ] All interactions tracked

**GCLID Tracking:**
- [ ] GCLID stored in localStorage
- [ ] GCLID appended to main CTA URL
- [ ] GCLID appended to image click URLs
- [ ] GCLID appended to exit popup CTA URL
- [ ] GCLID included in all tracking events
- [ ] GCLID passed to thank you page

**Thank You Page:**
- [ ] Checkmark animates correctly
- [ ] "What's Next" info displays
- [ ] Conversion pixel fires
- [ ] GCLID included in conversion event
- [ ] Redirects to YouTube after 3 seconds
- [ ] YouTube subscription prompt appears

**Browser Compatibility:**
- [ ] Chrome - Shows "Add to Chrome" button
- [ ] Edge - Shows "Add to Edge" button
- [ ] Firefox - Shows "Get Chrome Extension" button
- [ ] Safari - Shows "Get Chrome Extension" button

**Mobile Responsiveness:**
- [ ] Layout adapts to mobile screens
- [ ] Images stack vertically on mobile
- [ ] CTA button remains accessible
- [ ] Text sizes adjust appropriately

## Git Repository

**Repository:** https://github.com/yanivbarlev/novaview-lp
**Commit ID:** 38deb02
**Files:** 90 files, 2,941 lines of code
**Branch:** master

### Repository Structure
```
novaview-lp/
├── .gitignore
├── README.md
├── requirements.txt
├── config.py
├── utils.py
├── image_service.py
├── app.py
├── .env (not in repo)
├── templates/
│   ├── landing.html
│   ├── thankyou.html
│   ├── legal.html
│   ├── legal_privacy.html
│   ├── legal_terms.html
│   ├── legal_eula.html
│   ├── legal_copyright.html
│   ├── legal_about.html
│   ├── legal_uninstall.html
│   └── legal_contact.html
├── static/
│   ├── js/
│   │   └── exit-intent.js
│   ├── logo.png
│   ├── chrome-icon.png
│   └── edge-icon.png
├── images/
│   ├── {keyword}_1.webp
│   ├── {keyword}_2.webp
│   ├── {keyword}_3.webp
│   └── cache/
│       └── {keyword}/
│           ├── candidate_1.{ext}
│           └── candidate_10.{ext}
└── documents/
    └── build-status.md
```

## Environment Variables

Create `.env` file with:
```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CX=your_custom_search_engine_id_here
```

## Dependencies

```
Flask==3.1.0
Pillow==11.0.0
imagehash==4.3.1
python-dotenv==1.0.1
requests==2.32.3
```

Install with:
```bash
pip install -r requirements.txt
```

## Running Locally

```bash
cd new-lp
pip install -r requirements.txt
cp .env.example .env  # Edit with your Google API credentials
python app.py
```

Server starts on http://localhost:5000

## Deployment to PythonAnywhere

### Prerequisites
- PythonAnywhere account
- API token
- Google API credentials

### Deployment Steps

**1. Clone Repository:**
```bash
cd ~/
git clone https://github.com/yanivbarlev/novaview-lp.git
```

**2. Install Dependencies:**
```bash
cd ~/novaview-lp
pip3 install --user -r requirements.txt
```

**3. Create .env File:**
```bash
nano .env
# Add:
# GOOGLE_API_KEY=your_key
# GOOGLE_CX=your_cx_id
```

**4. Configure WSGI File:**
Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
```python
import sys
path = '/home/yourusername/novaview-lp'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

**5. Set Working Directory:**
In PythonAnywhere web app settings:
- Working directory: `/home/yourusername/novaview-lp`
- Static files: `/static/` → `/home/yourusername/novaview-lp/static/`

**6. Reload Web App:**
Click "Reload" button in PythonAnywhere web tab

### Post-Deployment Testing
- Test landing page: `https://yourdomain.com/?kw=test&img=true`
- Test thank you page: `https://yourdomain.com/thankyou-downloadmanager.html?source=novaview`
- Test legal pages
- Verify GCLID tracking
- Check server logs for errors

## Next Steps (Not Yet Implemented)

1. **Deploy to PythonAnywhere**
   - Upload repository
   - Configure WSGI
   - Test live URLs
   - Verify conversion tracking

2. **Performance Optimization**
   - Implement CDN for static assets
   - Add response compression
   - Optimize image loading

3. **Analytics Integration**
   - Set up Google Analytics 4
   - Configure conversion funnels
   - Track user behavior

4. **A/B Testing (Optional)**
   - Test different CTA copy
   - Test different background colors
   - Test image layout variations

5. **Additional Features (Optional)**
   - Add more legal pages if needed
   - Implement rate limiting
   - Add CAPTCHA for API endpoints

## Known Issues / Limitations

1. **Multiple Flask Servers:** If multiple instances run, use `taskkill /IM python.exe` to clean up
2. **Cache Storage:** Images stored on disk (no database) - consider cloud storage for production
3. **Google API Limits:** 100 queries/day on free tier - caching helps minimize usage
4. **Session Storage:** Exit popup uses sessionStorage - resets when browser closes
5. **YouTube Redirect:** Hardcoded URL - consider making configurable

## Support & Maintenance

**Repository Issues:** https://github.com/yanivbarlev/novaview-lp/issues
**Documentation:** This file + CLAUDE.md in parent directory
**Contact:** See `/contact` page for support emails

## Change Log

**2025-12-06 - Initial Build**
- Created complete Flask application
- Implemented all 14 routes
- Created all templates (10 total)
- Added exit intent popup
- Configured GCLID tracking
- Set up image caching system
- Created legal pages
- Implemented YouTube redirect
- Added comprehensive documentation
- Pushed to GitHub repository

---

**Status:** ✅ Build Complete - Ready for Testing
**Next Milestone:** Deploy to PythonAnywhere
**Estimated Deployment Time:** 30-60 minutes
