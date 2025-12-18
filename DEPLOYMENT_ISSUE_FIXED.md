# Deployment Issue - Fixed 2025-12-18

## Problem

The deployment scripts (`deploy_production.py`, `deploy_files_to_paw.py`) were **NOT actually uploading files** to PythonAnywhere, even though they reported success.

### What Went Wrong

**`deploy_production.py`:**
- Only READ files locally into memory
- NEVER uploaded them to the server
- Only reloaded the web app (which restarted with old files)
- Result: "Deployment successful" but no files changed

**`deploy_files_to_paw.py`:**
- Tried to upload using `Content-Type: application/octet-stream`
- PythonAnywhere API rejected with HTTP 415 "Unsupported media type"
- All 21 files failed to upload

## Root Cause

PythonAnywhere Files API requires:
1. **POST** with `files={'content': file_content}` for new files
2. **PUT** with raw data for updating existing files
3. Correct authentication headers

The broken scripts used wrong HTTP methods or content types.

## Solution

Created `deploy.py` (working deployment script) that:
1. ✓ Uses POST with multipart form data (`files={'content': ...}`)
2. ✓ Falls back to PUT with raw data if file exists
3. ✓ Properly encodes UTF-8 content
4. ✓ Reloads web app after successful upload
5. ✓ Verifies deployment by checking production URL

## How to Deploy (Correct Method)

```bash
# One command to deploy everything:
python deploy.py
```

This will:
1. Upload all 21 application files to `/home/yanivbl/apps/eguidesearches-novaview`
2. Reload the web app at www.eguidesearches.com
3. Wait 10 seconds for server restart
4. Verify deployment by checking production URL

## Verification

After deployment, verify changes are live:

```bash
# Check variant B has no images
curl -s "https://www.eguidesearches.com/?kw=test&img=true&variant=b" | grep "images-section"
# Should return nothing (no div)

# Check card width is updated
curl -s "https://www.eguidesearches.com/?kw=test&img=true&variant=b" | grep "max-width"
# Should show max-width: 750px (or your latest value)
```

## Files to Use

- ✓ **USE:** `deploy.py` (working script)
- ✗ **DON'T USE:** `deploy_production.py` (doesn't upload)
- ✗ **DON'T USE:** `deploy_files_to_paw.py` (wrong content type)
- ✗ **DON'T USE:** `deploy_*.py` (old broken scripts)

## Key Learnings

1. Always verify deployment by checking production URL
2. Don't trust "success" messages - verify actual file content
3. PythonAnywhere API is picky about content types
4. Template changes require actual file upload, not just reload
5. Use hard refresh (Ctrl+Shift+R) to bypass browser cache when testing

## Test Checklist

After every deployment:
- [ ] Wait 10-15 seconds for server reload
- [ ] Visit production URL with cache-busting parameter
- [ ] Use browser dev tools to verify HTML source
- [ ] Check specific changes (e.g., no images-section div)
- [ ] Test both variants (A and B)
- [ ] Verify button text matches expected values
