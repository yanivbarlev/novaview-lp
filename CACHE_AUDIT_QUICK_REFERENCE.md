# Cache Audit Logging - Quick Reference

## ✅ Deployment Complete

Cache audit logging is now active on production:
- **Log file**: `/home/yanivbl/apps/eguidesearches-novaview/cache_audit.log`
- **Auto-created**: Log file created automatically when app starts
- **No maintenance needed**: Logging happens automatically for all image requests

## Quick Commands (SSH Required)

### View Live Logging
```bash
ssh yanivbl@ssh.pythonanywhere.com
cd /home/yanivbl/apps/eguidesearches-novaview
tail -f cache_audit.log
```
(Press Ctrl+C to stop)

### Count Total API Calls
```bash
ssh yanivbl@ssh.pythonanywhere.com "grep 'API_CALL' /home/yanivbl/apps/eguidesearches-novaview/cache_audit.log | wc -l"
```

### Find Keywords Making API Calls
```bash
ssh yanivbl@ssh.pythonanywhere.com "grep 'API_CALL' /home/yanivbl/apps/eguidesearches-novaview/cache_audit.log | grep -oP 'keyword=\K[^ ]+' | sort | uniq -c | sort -rn | head -20"
```

### Check Today's API Calls
```bash
ssh yanivbl@ssh.pythonanywhere.com "grep 'API_CALL' /home/yanivbl/apps/eguidesearches-novaview/cache_audit.log | grep '$(date +%Y-%m-%d)' | wc -l"
```

### View Last 30 Log Entries
```bash
ssh yanivbl@ssh.pythonanywhere.com "tail -30 /home/yanivbl/apps/eguidesearches-novaview/cache_audit.log"
```

### Check Cache Hit/Miss Ratio
```bash
ssh yanivbl@ssh.pythonanywhere.com "
cd /home/yanivbl/apps/eguidesearches-novaview
echo 'Cache Hits:' && grep 'CACHE_RESULT.*HIT' cache_audit.log | wc -l
echo 'Cache Misses:' && grep 'CACHE_RESULT.*MISS' cache_audit.log | wc -l
"
```

## What to Look For

### ✅ Good Pattern (Cache Working)
```
REQUEST_START | keyword=minecraft
CACHE_HIT | keyword=minecraft | image=1 | size=23312
CACHE_HIT | keyword=minecraft | image=2 | size=20840
CACHE_HIT | keyword=minecraft | image=3 | size=20780
PHASE_1_SUCCESS | keyword=minecraft | final_cache=HIT
```
**No API call** - images served from cache

### ⚠️ Bad Pattern (Repeated API Calls)
If you see the SAME keyword with multiple API_CALL entries:
```
API_CALL | keyword=example | ... | quota_used=1
... (later) ...
API_CALL | keyword=example | ... | quota_used=1
```
**Problem**: Same keyword making multiple API calls = cache not working for that keyword

### 🔍 Diagnosis Pattern (New Keyword)
```
REQUEST_START | keyword=newword
CACHE_MISS | keyword=newword | image=1 | reason=file_not_found
CACHE_MISS | keyword=newword | image=2 | reason=file_not_found
CACHE_MISS | keyword=newword | image=3 | reason=file_not_found
PHASE_1_MISS | keyword=newword | final_cache=MISS
PHASE_2_CHECK | keyword=newword | candidates_found=0
PHASE_3_START | keyword=newword | reason=need_api_download
API_CALL | keyword=newword | ... | quota_used=1
```
**Normal**: First time seeing keyword, API call expected

## Troubleshooting Steps

### If You See Thousands of API Calls:

**Step 1**: Find the culprit keywords
```bash
ssh yanivbl@ssh.pythonanywhere.com "grep 'API_CALL' /home/yanivbl/apps/eguidesearches-novaview/cache_audit.log | grep -oP 'keyword=\K[^ ]+' | sort | uniq -c | sort -rn | head -10"
```

**Step 2**: Investigate the top keyword
```bash
ssh yanivbl@ssh.pythonanywhere.com "grep 'keyword=REPLACE_WITH_TOP_KEYWORD' /home/yanivbl/apps/eguidesearches-novaview/cache_audit.log | tail -50"
```

**Step 3**: Check if files exist
```bash
ssh yanivbl@ssh.pythonanywhere.com "ls -la /home/yanivbl/apps/eguidesearches-novaview/images/KEYWORD*"
```

**Step 4**: Compare log vs reality
- If logs say "file_not_found" but `ls` shows files exist → path issue
- If logs say "file_not_found" and `ls` shows no files → cache was deleted
- If same keyword has multiple API_CALL entries → cache isn't working

## Log Rotation (Optional)

If log file gets too large (> 100MB), rotate it:
```bash
ssh yanivbl@ssh.pythonanywhere.com
cd /home/yanivbl/apps/eguidesearches-novaview
mv cache_audit.log cache_audit.log.$(date +%Y%m%d)
gzip cache_audit.log.*
# New log will be created automatically
```

## Full Documentation

See `documents/cache-audit-logging.md` for complete documentation including:
- All log entry types explained
- Advanced analysis commands
- Integration with deployment
- Performance impact details
