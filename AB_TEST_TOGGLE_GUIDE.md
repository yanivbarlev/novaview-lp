# A/B Test Toggle Guide

Complete guide for enabling/disabling A/B tests without bugs.

**Last Updated:** 2025-12-24
**Current Status:** A/B Testing DISABLED (Variant A at 100%)

---

## Table of Contents

1. [Current Configuration](#current-configuration)
2. [How A/B Testing Works](#how-ab-testing-works)
3. [Disabling A/B Tests](#disabling-ab-tests)
4. [Re-enabling A/B Tests](#re-enabling-ab-tests)
5. [Common Pitfalls](#common-pitfalls)
6. [Testing Checklist](#testing-checklist)

---

## Current Configuration

**Status:** DISABLED (as of 2025-12-24)

**Files Modified:**
- `config.py` - Set `AB_TEST_ENABLED = False`
- `static/js/ab-test.js` - Disabled client-side variant assignment and redirection

**Reason:** Variant A (original design with images) outperformed Variant B (no images)

**Git Commits:**
```bash
ff9bfed - Disable A/B test - variant A (original) wins
ca8f2ff - Fix: Disable client-side A/B test redirection
fabf900 - Add static JS files to deployment script
```

---

## How A/B Testing Works

The A/B testing system has **TWO layers** that must work together:

### 1. Server-Side Assignment (app.py)

**Location:** `app.py` lines 126-151 and 213-238

**Logic:**
```python
# Variant assignment with proper precedence:
# 1. URL parameter (explicit override)
# 2. Cookie (returning user)
# 3. Random 50/50 split (new user)
variant_param = request.args.get('variant', '').lower()
variant_cookie = request.cookies.get('ab_variant', '')

if variant_param in ['a', 'b']:
    variant = variant_param  # URL parameter takes precedence
elif variant_cookie in ['a', 'b']:
    variant = variant_cookie  # Use existing cookie
else:
    # Random assignment for new users (50/50 split)
    variant = random.choice(['a', 'b'])

# If A/B test disabled, force variant A
if not AB_TEST_ENABLED:
    variant = 'a'
```

**What it does:**
- Assigns user to variant A or B
- Renders appropriate template (`index_variant_a.html` or `index_variant_b.html`)
- Sets cookie to persist variant for 30 days
- Forces variant A when `AB_TEST_ENABLED = False`

### 2. Client-Side Behavior (static/js/ab-test.js)

**Location:** `static/js/ab-test.js`

**What it does (when enabled):**
- Assigns random variant if none exists
- Adds `?variant=a` or `?variant=b` to URL
- Redirects browser to URL with variant parameter
- Stores variant in sessionStorage and localStorage

**CRITICAL:** Both server and client must be disabled together, or you get bugs!

---

## Disabling A/B Tests

### Step 1: Disable Server-Side Testing

**File:** `config.py`

```python
# Change this line from True to False
AB_TEST_ENABLED = False
```

**What this does:**
- Forces all users to variant A
- Prevents random assignment on server

### Step 2: Disable Client-Side Redirection

**File:** `static/js/ab-test.js`

Replace the entire file with:

```javascript
/**
 * A/B Test Variant Assignment
 * DISABLED - A/B test is off, all users get variant A
 * This script is kept for potential future use
 */

(function() {
    // A/B testing is disabled - no client-side assignment or redirection
    // The server always assigns variant 'a' when AB_TEST_ENABLED = False

    // Make variant 'a' available globally for any scripts that reference it
    window.abVariant = 'a';

    // Store in localStorage for consistency (though server controls assignment)
    localStorage.setItem('ab_variant', 'a');
    sessionStorage.setItem('ab_variant', 'a');
})();
```

**Why this is necessary:**
- Without this, users get redirected to `?variant=b` even though server forces variant A
- Creates confusing UX where URL says variant B but they see variant A
- The old script did random assignment independent of server setting

### Step 3: Deploy

```bash
# Commit changes
git add config.py static/js/ab-test.js
git commit -m "Disable A/B test - variant A at 100%"
git push origin master

# Deploy to production
python deploy.py
```

### Step 4: Verify

```bash
# Check production JavaScript
curl -s "https://www.eguidesearches.com/static/js/ab-test.js" | head -10

# Should show: "DISABLED - A/B test is off"

# Test clean URL (no redirect should happen)
# Visit in incognito: https://www.eguidesearches.com/?kw=test&img=true
# URL should stay clean, no ?variant=b added
```

---

## Re-enabling A/B Tests

**When to use:** Testing new design variants, feature experiments, etc.

### Step 1: Restore Server-Side Testing

**File:** `config.py`

```python
# Change from False to True
AB_TEST_ENABLED = True
```

### Step 2: Restore Client-Side Assignment

**File:** `static/js/ab-test.js`

**Option A: Full restoration (recommended)**

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

**Option B: Server-only assignment (no client-side redirection)**

Keep the disabled version but change 'a' to use server-passed variant:

```javascript
(function() {
    // Use server-assigned variant (passed via template)
    const serverVariant = document.body.dataset.variant || 'a';

    window.abVariant = serverVariant;
    localStorage.setItem('ab_variant', serverVariant);
    sessionStorage.setItem('ab_variant', serverVariant);
})();
```

Then add to templates:
```html
<body data-variant="{{ variant }}">
```

**Recommendation:** Use Option B to avoid URL redirection bugs

### Step 3: Update Variant Templates (if needed)

If creating a new test:

1. **Edit variant files:**
   - `templates/index_variant_a.html` - Control version
   - `templates/index_variant_b.html` - Test version

2. **Make your changes** to variant B (test version)

3. **Test locally first:**
   ```bash
   python app.py

   # Test variant A
   http://localhost:5000/?kw=test&img=true&variant=a

   # Test variant B
   http://localhost:5000/?kw=test&img=true&variant=b
   ```

### Step 4: Update Config Metadata

**File:** `config.py`

```python
# Update test name for tracking
AB_TEST_NAME = 'landing_page_design_v2'  # Increment version
AB_VARIANT_A_NAME = 'control'             # Describe variant A
AB_VARIANT_B_NAME = 'new_treatment'       # Describe variant B
AB_VARIANT_SPLIT = 0.5                    # 50-50 split
```

### Step 5: Deploy and Monitor

```bash
# Commit all changes
git add config.py static/js/ab-test.js templates/
git commit -m "Enable A/B test: [describe test]"
git push origin master

# Deploy
python deploy.py

# Verify both variants work
curl "https://www.eguidesearches.com/?kw=test&img=true&variant=a" | grep "window.abTestVariant"
curl "https://www.eguidesearches.com/?kw=test&img=true&variant=b" | grep "window.abTestVariant"
```

### Step 6: Monitor A/B Dashboard

```bash
# View results
https://www.eguidesearches.com/ab/dashboard
```

---

## Common Pitfalls

### ❌ Pitfall 1: Only Disabling Server-Side

**Symptom:** Users get redirected to `?variant=b` but see variant A content

**Problem:** `ab-test.js` still does client-side assignment and redirection

**Fix:** Must disable BOTH config.py AND ab-test.js

### ❌ Pitfall 2: Forgetting to Deploy JavaScript

**Symptom:** Changes to `ab-test.js` don't appear in production

**Problem:** `deploy.py` didn't include static/js files (fixed in commit fabf900)

**Fix:** Ensure `deploy.py` includes:
```python
'static/js/ab-test.js',
'static/js/exit-intent.js',
```

### ❌ Pitfall 3: Browser Cache

**Symptom:** Old JavaScript still running after deployment

**Problem:** Browser cached the old `ab-test.js` file

**Fix:** Hard refresh with Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### ❌ Pitfall 4: Cookie Persistence

**Symptom:** User stuck on variant B even after disabling test

**Problem:** 30-day cookie from previous test still active

**Fix:** Clear cookies or wait for expiration (server will override with variant A)

### ❌ Pitfall 5: URL Redirection Loop

**Symptom:** Page keeps reloading, URL keeps changing

**Problem:** Client-side script adds variant parameter, then runs again

**Fix:** Check that `addVariantToUrl()` has the guard:
```javascript
if (!urlParams.has('variant')) {
    // Only add if not already present
}
```

### ❌ Pitfall 6: Different Variants on Different Routes

**Symptom:** User sees variant A on `/` but variant B on `/stackfree`

**Problem:** Both routes must use same variant assignment logic

**Fix:** Verify both routes (lines 126-151 and 213-238 in app.py) have identical logic

---

## Testing Checklist

### Before Disabling A/B Test

- [ ] Verify which variant won (check dashboard)
- [ ] Document reason for disabling
- [ ] Backup current variant templates

### After Disabling A/B Test

- [ ] Verify `AB_TEST_ENABLED = False` in config.py
- [ ] Verify `ab-test.js` shows "DISABLED" comment
- [ ] Deploy to production
- [ ] Test clean URLs (no redirection)
- [ ] Test with incognito/private browsing
- [ ] Verify `window.abTestVariant = 'a'` in browser console
- [ ] Verify `window.abTestEnabled = false` in browser console
- [ ] Check both routes: `/` and `/stackfree`

### Before Re-enabling A/B Test

- [ ] Define clear hypothesis for test
- [ ] Update variant B template with changes
- [ ] Test both variants locally
- [ ] Update `AB_TEST_NAME` in config.py
- [ ] Document expected outcome

### After Re-enabling A/B Test

- [ ] Verify `AB_TEST_ENABLED = True` in config.py
- [ ] Verify `ab-test.js` has assignment logic
- [ ] Deploy to production
- [ ] Test variant A URL explicitly
- [ ] Test variant B URL explicitly
- [ ] Test clean URL (gets random assignment)
- [ ] Clear cookies and test multiple times
- [ ] Verify dashboard shows both variants
- [ ] Monitor for 24-48 hours before making decisions

---

## File Reference

### Files Modified When Toggling A/B Tests

| File | Purpose | Change When Disabling | Change When Enabling |
|------|---------|----------------------|---------------------|
| `config.py` | Server config | `AB_TEST_ENABLED = False` | `AB_TEST_ENABLED = True` |
| `static/js/ab-test.js` | Client-side logic | Remove assignment/redirect | Restore assignment/redirect |
| `deploy.py` | Deployment script | No change needed | No change needed |

### Files Used By A/B Testing (Don't Modify When Toggling)

| File | Purpose | Notes |
|------|---------|-------|
| `app.py` | Server routing | Contains variant assignment logic |
| `templates/index_variant_a.html` | Variant A template | Only modify when changing variant A design |
| `templates/index_variant_b.html` | Variant B template | Only modify when changing variant B design |
| `static/js/exit-intent.js` | Exit popup | Uses variant for tracking |
| `ab_testing/ab_log_parser.py` | Dashboard parser | Analyzes logs for metrics |

---

## Quick Reference Commands

### Disable A/B Test
```bash
# 1. Edit config.py: AB_TEST_ENABLED = False
# 2. Edit static/js/ab-test.js: Use disabled version (see above)
git add config.py static/js/ab-test.js
git commit -m "Disable A/B test - variant A at 100%"
git push origin master
python deploy.py
```

### Re-enable A/B Test
```bash
# 1. Edit config.py: AB_TEST_ENABLED = True
# 2. Edit static/js/ab-test.js: Restore assignment logic (see above)
# 3. Update AB_TEST_NAME in config.py
git add config.py static/js/ab-test.js
git commit -m "Enable A/B test: [test description]"
git push origin master
python deploy.py
```

### Verify Production Status
```bash
# Check config
curl -s "https://www.eguidesearches.com/?kw=test" | grep "abTestEnabled"

# Check JavaScript
curl -s "https://www.eguidesearches.com/static/js/ab-test.js" | head -5

# Test both variants
curl "https://www.eguidesearches.com/?kw=test&variant=a" | grep "window.abTestVariant"
curl "https://www.eguidesearches.com/?kw=test&variant=b" | grep "window.abTestVariant"
```

---

## Version History

### 2025-12-24: A/B Test Disabled
- **Reason:** Variant A (with images) outperformed Variant B (no images)
- **Changes:**
  - Set `AB_TEST_ENABLED = False`
  - Disabled client-side assignment in `ab-test.js`
  - Fixed deployment script to include JavaScript files
- **Commits:** ff9bfed, ca8f2ff, fabf900

### 2025-12-11: Random Assignment Implemented
- **Reason:** Fix 3:1 bias toward variant A
- **Changes:** Implemented `random.choice(['a', 'b'])` for fair distribution
- **Commit:** ea3d5ae

### 2025-12-07: A/B Test System Created
- **Reason:** Test image vs no-image landing page designs
- **Changes:** Created variant A/B templates and assignment logic
- **Commit:** 8688f12

---

## Support

If you encounter issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for deployment issues
2. Check [AB_TESTING_IMPLEMENTATION_GUIDE.md](documents/ab_testing_implementation_guide.md) for detailed A/B test architecture
3. Review git history: `git log --oneline --grep="A/B\|variant"`
4. Check production logs for variant assignment: Look for `LANDING_PAGE` and `variant=` in logs

---

**Last Modified:** 2025-12-24
**Next Review:** When planning next A/B test
