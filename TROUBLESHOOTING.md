# Troubleshooting Guide

Common issues and solutions for the NovaView Landing Page system.

---

## Table of Contents

1. [Deployment Issues](#deployment-issues)
2. [File Issues](#file-issues)
3. [Template Issues](#template-issues)
4. [Cache Issues](#cache-issues)
5. [Windows-Specific Issues](#windows-specific-issues)

---

## Deployment Issues

### Production Shows Old Version After Deployment

**Symptoms:**
- Files uploaded successfully (HTTP 200/201)
- Production still serves old content
- Incognito mode shows same old version

**Diagnosis:**
```bash
# Compare local vs production file sizes
wc -l app.py  # Local
curl -s -H "Authorization: Token YOUR_PAW_TOKEN" \
  "https://www.pythonanywhere.com/api/v0/user/yanivbl/files/path/home/yanivbl/apps/eguidesearches-novaview/app.py" \
  | jq -r '.content' | wc -l  # Production
```

**Solutions:**

1. **Manual Web App Reload (Most Effective)**
   - Go to: https://www.pythonanywhere.com/user/yanivbl/webapps/
   - Find: `www.eguidesearches.com`
   - Click: Green "Reload www.eguidesearches.com" button
   - Wait: 15 seconds
   - Test: Production URL in incognito mode

2. **If Still Not Working**
   - Reload 2-3 times (stubborn cache)
   - Wait 1 minute between reloads
   - Clear browser cache completely
   - Contact PythonAnywhere support

**Prevention:**
- Always do manual reload after deployment
- Verify served content matches uploaded files
- Follow deployment checklist in DEPLOYMENT_POSTMORTEM.md

---

### Production and Local Code Out of Sync

**Symptoms:**
- app.py line count differs significantly (>10 lines)
- Features work locally but not in production
- Production missing recent routes or functions

**Root Cause:**
- Production running old commit
- Only templates deployed, not core files
- Git pull not executed on production

**Solution:**
```bash
# Option 1: Deploy all files via API
python deploy.py  # Should deploy ALL files

# Option 2: Git pull on production (Recommended)
ssh yanivbl@ssh.pythonanywhere.com
cd /home/yanivbl/apps/eguidesearches-novaview
git status  # Check current state
git pull origin master  # Pull latest changes
touch /var/www/www_eguidesearches_com_wsgi.py  # Reload
```

**Prevention:**
- Always verify local vs production file sizes before deployment
- Deploy ALL files when app.py changes
- Use git-based deployment for consistency

---

## File Issues

### Accidental NUL File (788MB)

**Symptoms:**
- Git status shows `?? nul` or `?? images/NUL`
- Project directory size unexpectedly large (>500MB)
- Disk space warnings

**Diagnosis:**
```bash
# Check project size
du -sh .

# Find large files
find . -type f -size +100M 2>/dev/null

# Check for nul file
ls -lh nul 2>/dev/null || echo "No nul file"
```

**Root Cause:**
On Windows, using lowercase "nul" in output redirection creates a file instead of discarding output:
```bash
# WRONG - Creates massive file
command > nul 2>&1

# CORRECT - Discards output
command > NUL 2>&1
```

**Solution:**
```bash
# Remove the file
rm -f nul

# Verify it's gone
git status --short | grep -i nul  # Should return nothing
du -sh .  # Check new size
```

**Prevention:**
- Always use uppercase `NUL` on Windows
- Better: Use PowerShell `| Out-Null`
- Add `nul` to `.gitignore` (already done)
- Regularly check project size: `du -sh .`

---

### Large images/ Directory

**Symptoms:**
- `images/` folder over 500MB
- Slow git operations
- Deployment takes very long

**Diagnosis:**
```bash
# Check images folder size
du -sh images/

# Count cached images
ls images/*.webp 2>/dev/null | wc -l
du -sh images/cache/
```

**Solution:**
```bash
# Clean old cache (keeps recent keywords)
python -c "
from image_service import ImageSearchService
service = ImageSearchService()
service.clean_old_cache(days=30)  # Remove cache older than 30 days
"

# Or manually clean
rm -rf images/cache/old_keyword_*
```

**Prevention:**
- Cache is in `.gitignore` (shouldn't be committed)
- Run cache cleanup monthly
- Consider cloud storage for production cache

---

## Template Issues

### Templates Not Loading After Changes

**Symptoms:**
- Modified template locally
- Changes don't appear when testing
- Old template still renders

**Root Cause:**
- Multiple Flask processes running
- Flask serving from wrong directory
- Template cache not cleared

**Solution:**
```bash
# Kill all Python processes (Windows)
taskkill /IM python.exe /F

# Verify no processes
tasklist | findstr python

# Restart app
python app.py
```

**Prevention:**
- Only run one `python app.py` at a time
- Use absolute paths in Flask app initialization
- Check current directory before running: `pwd`

---

### Wrong Template Loaded in Production

**Symptoms:**
- Template uploaded successfully
- Production serves different template
- HTML source doesn't match uploaded file

**Diagnosis:**
```bash
# Check served HTML
curl -s "https://www.eguidesearches.com/?kw=test&variant=b" | wc -l

# Check uploaded template
curl -s -H "Authorization: Token YOUR_TOKEN" \
  "https://www.pythonanywhere.com/api/v0/user/yanivbl/files/path/home/yanivbl/apps/eguidesearches-novaview/templates/index_variant_b.html" \
  | jq -r '.content' | wc -l
```

**Solution:**
1. Manual web app reload (see Deployment Issues)
2. If still wrong: Check app.py has correct route logic
3. Verify template name matches route rendering call

---

## Cache Issues

### Image Cache Not Working

**Symptoms:**
- Every page load triggers Google API call
- Same keyword doesn't use cached images
- Cache status always 'MISS'

**Diagnosis:**
```bash
# Check if cache files exist
ls images/minecraft_*.webp 2>/dev/null

# Check cache directory
ls -la images/cache/minecraft/ 2>/dev/null

# Check file permissions
ls -la images/
```

**Solution:**
```bash
# Ensure images directory is writable
chmod 755 images/

# Clear and rebuild cache
rm -rf images/cache/
# Visit page with ?kw=test&img=true to rebuild
```

**Prevention:**
- Ensure images/ directory exists and is writable
- Monitor cache_audit.log for errors
- Check CACHE_TTL_HOURS in config.py

---

### Google API Quota Exceeded

**Symptoms:**
- Error: "Quota exceeded"
- Images not loading for new keywords
- API error in logs

**Diagnosis:**
```bash
# Check recent API calls in logs
grep "Google API" *.log | tail -20

# Count unique keywords cached
ls images/*.webp | grep -v "_[0-9]" | wc -l
```

**Solution:**
- Wait 24 hours (quota resets daily)
- Use backup API key (GOOGLE_API_KEY_BACKUP in .env)
- Reduce new keyword testing

**Prevention:**
- Cache is designed for ~1 API call per keyword per 100 days
- Don't clear cache unnecessarily
- Use existing cached keywords for testing

---

## Windows-Specific Issues

### Reserved Device Names

**Problem:**
Windows reserves certain names that cannot be used as filenames:
- `NUL`, `CON`, `PRN`, `AUX`
- `COM1` through `COM9`
- `LPT1` through `LPT9`

**Symptoms:**
- File creation fails with cryptic errors
- Output redirection creates unexpected files
- Git shows phantom files

**Solution:**
```bash
# Never use these names as filenames
# For output redirection, use uppercase:
command > NUL 2>&1  # CORRECT

# Or use PowerShell:
command | Out-Null  # BEST
```

---

### Path Length Issues

**Symptoms:**
- "Path too long" errors
- Cannot delete cache files
- Deployment fails on certain files

**Solution:**
```bash
# Enable long path support (Windows 10+)
# Run PowerShell as Administrator:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Or use shorter cache paths in config.py
```

---

### Line Ending Issues

**Symptoms:**
- Git shows files as modified when they're not
- Scripts fail with "command not found"
- Deployment uploads files with wrong line endings

**Solution:**
```bash
# Configure git to handle line endings
git config --global core.autocrlf true

# For specific files, add to .gitattributes:
*.py text eol=lf
*.sh text eol=lf
*.html text eol=lf
```

---

## Quick Diagnostic Commands

**Check everything at once:**
```bash
# Project health check
echo "=== Project Size ==="
du -sh .

echo "\n=== Git Status ==="
git status --short

echo "\n=== Local File Sizes ==="
wc -l app.py config.py image_service.py

echo "\n=== Python Processes ==="
tasklist | findstr python

echo "\n=== Recent Errors ==="
tail -20 *.log 2>/dev/null | grep -i error
```

**Production health check:**
```bash
# Compare local vs production
echo "Local app.py:" && wc -l app.py
echo "Production app.py:" && curl -s -H "Authorization: Token YOUR_TOKEN" \
  "https://www.pythonanywhere.com/api/v0/user/yanivbl/files/path/home/yanivbl/apps/eguidesearches-novaview/app.py" \
  | jq -r '.content' | wc -l
```

---

## Getting Help

If none of these solutions work:

1. **Check documentation:**
   - DEPLOYMENT_POSTMORTEM.md - Deployment issues
   - CLAUDE.md - Project overview and practices
   - README.md - General information

2. **Check logs:**
   - Local: `*.log` files in project directory
   - Production: https://www.pythonanywhere.com/user/yanivbl/files/var/log/

3. **Contact support:**
   - PythonAnywhere: support@pythonanywhere.com
   - GitHub Issues: https://github.com/yanivbarlev/novaview-lp/issues

4. **Emergency rollback:**
   ```bash
   # Revert to last known good commit
   git log -5  # Find last working commit hash
   git checkout <commit-hash>
   python deploy.py
   ```

---

## Preventive Maintenance

**Weekly:**
- Check project size: `du -sh .`
- Review git status for unexpected files
- Test key functionality locally

**Monthly:**
- Clean old cache: Remove keywords not used in 30+ days
- Review logs for errors
- Update dependencies: `pip list --outdated`

**Before Deployment:**
- Test locally: `python app.py`
- Compare file sizes: Local vs production
- Follow deployment checklist
- Commit changes to git

**After Deployment:**
- Manual web app reload
- Test production URL
- Verify specific features work
- Check served content matches uploaded files
