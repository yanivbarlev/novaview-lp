# Plan: Update Exit Popup for /trusted Landing Page

## Problem
The current exit popup on `/trusted` shows "Are you sure you want to leave?" after the user clicks the CTA and downloads the file. This messaging doesn't make sense for a download flow - the user already has the file, they need guidance on how to install it.

## Current Flow (Incorrect)
1. User clicks "Continue" → download URL opens
2. User returns to landing page
3. Popup shows: "Wait! Are you sure you want to leave?"
4. CTA: "Continue to Download" (redundant - they already downloaded)

## Desired Flow (For /trusted only)
1. User clicks "Continue" → download starts
2. User returns to landing page
3. Popup shows: "Your download has started!" with installation instructions
4. CTA: "Open Downloads" or guide them to run the installer

## Constraints
- Must NOT affect other landing pages (`/`, `/stackfree`)
- Other pages use `exit-intent.js` with "Are you sure you want to leave?" messaging
- Only `/trusted` should have the new "installation guide" popup

## Solution Approach

**Option A: Modify popup HTML in trusted.html only**
- Keep `exit-intent.js` unchanged (shared)
- Change the popup content in `trusted.html` template
- The JS just shows/hides - the content is already different per template

This is the simplest approach since:
- The popup HTML is already in each template
- We just need to change the text/content in `trusted.html`
- No changes to shared JavaScript

## Implementation Steps

### Step 1: Update Exit Popup Content in trusted.html

Change from:
```html
<div class="exit-popup-header">
    <h2>Wait!</h2>
    <button class="exit-popup-close">&times;</button>
</div>
<p class="exit-popup-subtitle">Are you sure you want to leave?</p>
<p class="exit-popup-description">
    Don't miss out on the free Trusted Stocks app to manage your portfolio.
</p>
<a href="#" class="exit-popup-cta" id="exitPopupCta">
    Continue to Download
</a>
```

Change to:
```html
<div class="exit-popup-header">
    <h2>Download Started!</h2>
    <button class="exit-popup-close">&times;</button>
</div>
<p class="exit-popup-subtitle">Here's how to install:</p>
<div class="exit-popup-description">
    <ol class="install-steps">
        <li>Open the downloaded file from your Downloads folder</li>
        <li>Run the installer and follow the prompts</li>
        <li>Launch Trusted Stocks from your desktop</li>
    </ol>
</div>
<a href="#" class="exit-popup-cta" id="exitPopupCta">
    Open Downloads Folder
</a>
```

### Step 2: Add CSS for Installation Steps

Add styling for the ordered list in trusted.html:
```css
.install-steps {
    text-align: left;
    padding-left: 20px;
    margin: 10px 0;
}

.install-steps li {
    margin-bottom: 10px;
    line-height: 1.4;
}
```

### Step 3: Update CTA Behavior for "Open Downloads"

Modify the `exitPopupCta` click handler in trusted.html to:
- Option A: Close popup only (user finds file themselves)
- Option B: Try to open downloads folder (limited browser support)
- Option C: Show a helpful message and close

Recommended: Change CTA to "Got it!" and just close the popup, since:
- Browsers can't reliably open the downloads folder
- The instructions are clear enough
- Less confusing for users

### Step 4: Test

1. Visit `http://localhost:5000/trusted?kw=test`
2. Click "Continue" button
3. Return to landing page
4. Verify popup shows installation instructions (not "Are you sure you want to leave?")
5. Verify other pages (`/`, `/stackfree`) still show original popup

## Files Modified

| File | Change |
|------|--------|
| `templates/trusted.html` | Update exit popup HTML content and add CSS |

## Files NOT Modified

| File | Reason |
|------|--------|
| `static/js/exit-intent.js` | Shared by all pages, no changes needed |
| `templates/index_variant_a.html` | Keep original popup behavior |
| `templates/index_variant_b.html` | Keep original popup behavior |
| `templates/landing.html` | Keep original popup behavior |
| `app.py` | No route changes needed |

## Verification Checklist

- [ ] `/trusted` popup shows "Download Started!" title
- [ ] `/trusted` popup shows installation steps (numbered list)
- [ ] `/trusted` popup CTA says "Got it!" and closes popup
- [ ] `/` landing page still shows "Are you sure you want to leave?"
- [ ] `/stackfree` still shows "Are you sure you want to leave?"
