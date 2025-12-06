# New Landing Page System

## Implementation Complete ✅

This is a clean, optimized rewrite of the landing page system with reduced complexity and improved maintainability.

## File Structure

```
new-lp/
├── app.py                  # Flask app (11KB, ~300 lines)
├── config.py               # Configuration (1.4KB, ~50 lines)
├── image_service.py        # Image search service (21KB, ~650 lines)
├── utils.py                # Utility functions (3.4KB, ~130 lines)
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (copied from parent)
├── images/                 # Cached images (copied from parent)
│   ├── cache/              # Candidate images cache
│   └── *.webp              # Final optimized images
├── templates/
│   └── landing.html        # Main template (16KB, ~380 lines)
└── static/
    ├── logo.png            # EGuideSearches logo
    ├── chrome-icon.png     # Chrome browser icon
    ├── edge-icon.png       # Edge browser icon
    └── js/
        └── exit-intent.js  # Exit intent popup logic

Total: ~36KB of code (excluding images and templates)
```

## Comparison with Old System

| Metric | Old System | New System | Improvement |
|--------|-----------|-----------|-------------|
| Routes | 21 | 6 | 71% reduction |
| Main app.py | 1,017 lines | 300 lines | 70% reduction |
| Total code | 1,661+ lines | ~1,250 lines | 25% reduction |
| Files | Monolithic | Modular | Better organization |

## Essential Routes (6 Total)

1. **`/`** - Main landing page
   - Parameters: `kw` (keyword), `img` (true/false), `gclid`
   - Browser-specific personalization
   - Async image loading

2. **`/api/search`** - Image search API
   - Server-side proxy for Google API
   - Three-tier caching system
   - Returns JSON with images array

3. **`/image/<filename>`** - Image serving
   - Serves optimized images from cache
   - ~25KB per image

4. **`/api/track/click`** - CTA click tracking
   - Tracks button clicks with attribution
   - Logs GCLID for conversion tracking

5. **`/api/track/exit-popup`** - Exit popup tracking
   - Tracks popup impressions and clicks
   - Session-based display limiting

6. **`/post_install/`** - Post-install conversion page
   - Google Tag conversion tracking
   - Thank you page with conversion event

## Key Features Preserved

### ✅ Three-Tier Caching System
- **Tier 1:** Final images (100-day TTL)
- **Tier 2:** Candidate cache (temporary)
- **API calls:** 1 per keyword per 100 days

### ✅ Async Image Loading
- Page loads <0.1s (no server-side blocking)
- Images load via JavaScript AJAX
- Placeholders only for cached images

### ✅ Browser Detection
- Server-side User-Agent parsing
- Browser-specific CTA buttons and text
- Chrome/Edge store URL selection

### ✅ Exit Intent Popup
- Monitors Chrome Web Store tab
- Shows when user closes store tab
- Session-based limiting (once per session)

### ✅ GCLID Tracking
- localStorage persistence
- Attribution across sessions
- Conversion tracking via Google Tag

### ✅ Image Selection Algorithm
- Perceptual hashing (imagehash)
- Diversity selection (avoids duplicates)
- Binary search compression (~25KB target)

## Local Testing

### 1. Install Dependencies
```bash
cd new-lp
pip install -r requirements.txt
```

### 2. Verify Environment Variables
Ensure `.env` contains:
```
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CX=your_cx_id_here
```

### 3. Run Development Server
```bash
python app.py
```

### 4. Test URLs
- Main page: `http://localhost:5000/`
- With images: `http://localhost:5000/?kw=minecraft&img=true`
- With GCLID: `http://localhost:5000/?kw=gaming&img=true&gclid=test123`

### 5. Verify Features
- ✅ Page loads instantly (<0.1s)
- ✅ Images load from cache (check console logs)
- ✅ Browser detection works (check CTA button text)
- ✅ Exit popup appears when clicking CTA
- ✅ GCLID stored in localStorage

## Deployment to PythonAnywhere

### Option 1: Upload Entire Folder
1. Upload `new-lp/` folder to `/home/yanivbl/apps/eguidesearches/new_lp`
2. Update WSGI file: Change `steven-lp` → `new_lp`
3. Update Source Code path in dashboard
4. Update Working Directory path in dashboard
5. Reload web app

### Option 2: Use Git (Recommended)
```bash
# Commit new-lp to git
git add new-lp/
git commit -m "Add clean new landing page system"
git push

# On PythonAnywhere
cd /home/yanivbl/apps/eguidesearches
git pull

# Update paths and reload
# (same as Option 1, steps 2-5)
```

### WSGI File Changes
Edit `/var/www/www_eguidesearches_com_wsgi.py`:
```python
# OLD
sys.path.insert(0, '/home/yanivbl/apps/eguidesearches/steven-lp')
from app import app as application

# NEW
sys.path.insert(0, '/home/yanivbl/apps/eguidesearches/new_lp')
from app import app as application
```

### Rollback Plan
If issues occur, simply revert the WSGI file and dashboard paths back to `steven-lp`.

## Configuration

### Update Chrome/Edge Store URLs
Edit `config.py`:
```python
CHROME_STORE_URL = 'https://chromewebstore.google.com/detail/...'
EDGE_STORE_URL = 'https://microsoftedge.microsoft.com/addons/detail/...'
```

**IMPORTANT:** Always verify these URLs match the current product!

### Google Tag ID
Currently set to `AW-1006081641`. Update in `config.py` if needed.

## Code Quality

### Modular Design
- **app.py:** Flask routes only
- **config.py:** All configuration
- **utils.py:** Helper functions
- **image_service.py:** Image logic

### Clear Separation of Concerns
- Route handlers don't fetch images server-side
- JavaScript handles async image loading
- Config centralized (no hardcoded URLs)
- Logging comprehensive

### Battle-Tested Code
- ImageSearchService: Extracted unchanged from old system
- Browser detection: Proven order-sensitive logic
- Exit intent: Tested popup with tracking
- Compression: Binary search algorithm

## Performance Metrics

- **Page load:** <0.1s (cached or uncached)
- **Image size:** ~25KB each (~75KB total)
- **API calls:** 1 per keyword per 100 days
- **Total codebase:** ~1,250 lines (25% reduction)

## Success Criteria

### ✅ Functionality
- All stackfree features preserved
- Same layout and design
- Browser-specific personalization
- Exit intent popup working
- GCLID attribution tracking
- Google Tag conversion tracking

### ✅ Performance
- Page load <0.1s
- Image optimization working
- Caching system functional

### ✅ Code Quality
- Self-contained (no external dependencies)
- Clean separation of concerns
- Reused battle-tested code
- No template caching issues
- Comprehensive error handling

## Next Steps

1. ✅ Local testing completed
2. ⏳ Deploy to PythonAnywhere
3. ⏳ Test live site with real traffic
4. ⏳ Monitor logs for any issues
5. ⏳ Compare conversion rates with old system

## Documentation References

- **Implementation Guide:** `../documents/stackfree_complete_implementation_guide.md`
- **Deployment Guide:** `../documents/NEW_LP_DEPLOYMENT_GUIDE.md`
- **Old System:** `../app.py` (for reference)

---

**Implementation Date:** 2025-12-05
**Status:** Ready for Deployment ✅
**Confidence:** High (battle-tested code extracted from working system)
