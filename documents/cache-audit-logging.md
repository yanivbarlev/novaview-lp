# Cache Audit Logging System

## Overview

The cache audit logging system tracks every image request, cache hit/miss, and Google API call in detail. This helps diagnose caching issues and monitor API usage.

## Log File Location

**Production (PythonAnywhere):**
```
/home/yanivbl/apps/eguidesearches-novaview/cache_audit.log
```

**Local Development:**
```
cache_audit.log (in project root)
```

## Log Format

Each log entry follows this format:
```
YYYY-MM-DD HH:MM:SS | ACTION | keyword=value | field=value | ...
```

## Log Entry Types

### 1. REQUEST_START
Logged when an image search request begins.
```
2025-12-08 11:34:34 | REQUEST_START | keyword=minecraft | keyword_base=minecraft | count=3
```
- `keyword`: Original search term
- `keyword_base`: Sanitized filename version
- `count`: Number of images requested

### 2. CACHE_CHECK
Logged when checking if images exist in final cache.
```
2025-12-08 11:34:34 | CACHE_CHECK | keyword=minecraft | count=3 | checking final images
```

### 3. CACHE_HIT
Logged for each image found in cache.
```
2025-12-08 11:34:34 | CACHE_HIT | keyword=minecraft | image=1 | path=images\minecraft_1.webp | size=23312
```
- `image`: Image number (1, 2, or 3)
- `path`: Full file path
- `size`: File size in bytes

### 4. CACHE_MISS
Logged for each image NOT found in cache.
```
2025-12-08 11:34:54 | CACHE_MISS | keyword=testword | image=1 | reason=file_not_found | path=images\testword_1
```
- `reason`: Why cache missed
  - `file_not_found`: File doesn't exist at expected path
  - `invalid_image`: File exists but is corrupted/invalid

### 5. CACHE_RESULT
Summary of cache check for all images.
```
2025-12-08 11:34:34 | CACHE_RESULT | keyword=minecraft | status=HIT | all_images_found=True
```
OR
```
2025-12-08 11:34:54 | CACHE_RESULT | keyword=testword | status=MISS | missing_images=[1, 2, 3]
```

### 6. PHASE_1_SUCCESS
Logged when all images found in final cache (best case - no API call).
```
2025-12-08 11:34:34 | PHASE_1_SUCCESS | keyword=minecraft | final_cache=HIT | returning cached images
```

### 7. PHASE_1_MISS
Logged when final cache check fails, proceeding to check candidates.
```
2025-12-08 11:34:54 | PHASE_1_MISS | keyword=testword | final_cache=MISS | checking candidates
```

### 8. PHASE_2_CHECK
Logged when checking candidate cache directory.
```
2025-12-08 11:34:54 | PHASE_2_CHECK | keyword=testword | candidates_found=0 | required=3
```
- `candidates_found`: Number of candidate images available
- `required`: Number of images needed

### 9. PHASE_2_SUCCESS
Logged when enough candidates found to avoid API call.
```
2025-12-08 11:35:00 | PHASE_2_SUCCESS | keyword=example | using_candidate_cache | count=5
```

### 10. PHASE_2_COMPLETE
Logged when candidates successfully promoted to final images.
```
2025-12-08 11:35:00 | PHASE_2_COMPLETE | keyword=example | promoted=3 | cleaned_candidates=True
```

### 11. PHASE_3_START
Logged when API download is required (cache completely missed).
```
2025-12-08 11:34:54 | PHASE_3_START | keyword=testword | reason=need_api_download | existing_candidates=0
```

### 12. API_CALL
**MOST IMPORTANT** - Logged for every Google Custom Search API call.
```
2025-12-08 11:34:54 | API_CALL | keyword=testword | api=primary | requested=10 | urls_received=0 | response_time=0.462s | status=200 | quota_used=1
```
- `api`: Which API key used (primary or backup)
- `requested`: Number of images requested from API
- `urls_received`: Number of image URLs returned
- `response_time`: API response time in seconds
- `status`: HTTP status code
- `quota_used`: API quota consumed (always 1 per call)

## Common Analysis Commands

### Count Total API Calls
```bash
ssh yanivbl@ssh.pythonanywhere.com
cd /home/yanivbl/apps/eguidesearches-novaview
grep "API_CALL" cache_audit.log | wc -l
```

### Find Keywords Making API Calls
```bash
grep "API_CALL" cache_audit.log | grep -oP 'keyword=\K[^ ]+' | sort | uniq -c | sort -rn | head -20
```
Shows keywords sorted by API call frequency.

### Count API Calls by Date
```bash
grep "API_CALL" cache_audit.log | grep "2025-12-08" | wc -l
```

### Find Cache Misses with Reasons
```bash
grep "CACHE_MISS" cache_audit.log | head -30
```

### See Cache Hit Rate
```bash
echo "Cache Hits:"
grep "CACHE_RESULT.*status=HIT" cache_audit.log | wc -l
echo "Cache Misses:"
grep "CACHE_RESULT.*status=MISS" cache_audit.log | wc -l
```

### Find Keywords with Repeated API Calls
This shows if same keyword is causing multiple API calls (indicates caching failure):
```bash
grep "API_CALL" cache_audit.log | grep -oP 'keyword=\K[^ ]+' | sort | uniq -c | grep -v "^ *1 "
```
If you see numbers > 1, that keyword is making multiple API calls (should only be 1).

### View Recent Activity
```bash
tail -50 cache_audit.log
```

### Search Specific Keyword
```bash
grep "keyword=minecraft" cache_audit.log
```

## Typical Flow Examples

### Perfect Cache Hit (No API Call)
```
REQUEST_START | keyword=minecraft | keyword_base=minecraft | count=3
CACHE_CHECK | keyword=minecraft | count=3 | checking final images
CACHE_HIT | keyword=minecraft | image=1 | path=images\minecraft_1.webp | size=23312
CACHE_HIT | keyword=minecraft | image=2 | path=images\minecraft_2.webp | size=20840
CACHE_HIT | keyword=minecraft | image=3 | path=images\minecraft_3.webp | size=20780
CACHE_RESULT | keyword=minecraft | status=HIT | all_images_found=True
PHASE_1_SUCCESS | keyword=minecraft | final_cache=HIT | returning cached images
```
✅ **Result**: Images served from cache, NO API call

### Complete Cache Miss (API Call Required)
```
REQUEST_START | keyword=newkeyword | keyword_base=newkeyword | count=3
CACHE_CHECK | keyword=newkeyword | count=3 | checking final images
CACHE_MISS | keyword=newkeyword | image=1 | reason=file_not_found | path=images\newkeyword_1
CACHE_MISS | keyword=newkeyword | image=2 | reason=file_not_found | path=images\newkeyword_2
CACHE_MISS | keyword=newkeyword | image=3 | reason=file_not_found | path=images\newkeyword_3
CACHE_RESULT | keyword=newkeyword | status=MISS | missing_images=[1, 2, 3]
PHASE_1_MISS | keyword=newkeyword | final_cache=MISS | checking candidates
PHASE_2_CHECK | keyword=newkeyword | candidates_found=0 | required=3
PHASE_3_START | keyword=newkeyword | reason=need_api_download | existing_candidates=0
API_CALL | keyword=newkeyword | api=primary | requested=10 | urls_received=3 | response_time=0.462s | status=200 | quota_used=1
```
⚠️ **Result**: No cache, API call made, images downloaded and cached

## Troubleshooting with Logs

### Problem: Thousands of API Calls

**Step 1**: Find which keywords are causing calls
```bash
grep "API_CALL" cache_audit.log | grep -oP 'keyword=\K[^ ]+' | sort | uniq -c | sort -rn | head -20
```

**Step 2**: Pick top keyword and investigate
```bash
grep "keyword=TOPKEYWORD" cache_audit.log | tail -100
```

**Step 3**: Check patterns
- **Same keyword multiple API calls?** → Caching is broken for that keyword
- **Many different keywords?** → Cache was cleared or new traffic
- **API calls then cache hits?** → Normal behavior, cache building

### Problem: Cache Files Exist But Not Found

Look for this pattern:
```
CACHE_MISS | keyword=example | image=1 | reason=file_not_found | path=images\example_1
```

Then manually check if file exists:
```bash
ls -la /home/yanivbl/apps/eguidesearches-novaview/images/example*
```

If files exist but logs say "not found":
- **Path issue**: Check working directory
- **Permission issue**: Check file permissions
- **Extension mismatch**: File might be .jpg but looking for .webp

### Problem: Files Exist But Invalid

Look for:
```
CACHE_MISS | keyword=example | image=1 | reason=invalid_image | path=images\example_1.webp
```

File is corrupted. Delete and let system re-download:
```bash
rm /home/yanivbl/apps/eguidesearches-novaview/images/example*
```

## Log Rotation

The cache_audit.log file will grow over time. To prevent disk space issues:

### Manual Rotation
```bash
cd /home/yanivbl/apps/eguidesearches-novaview
mv cache_audit.log cache_audit.log.$(date +%Y%m%d)
gzip cache_audit.log.*
# Log file will be recreated automatically on next request
```

### Keep Last 7 Days
```bash
cd /home/yanivbl/apps/eguidesearches-novaview
find . -name "cache_audit.log.*" -mtime +7 -delete
```

## Integration with Deployment

The cache audit log is:
- ✅ Automatically created when app starts
- ✅ Excluded from git (in .gitignore)
- ✅ Persists across deployments
- ✅ Separate from main app.log

**Note**: Log file persists on production between deployments - it won't be deleted by `git pull`.

## Performance Impact

- **Minimal**: Logging adds <1ms per request
- **Async**: Logs written asynchronously, doesn't block responses
- **Efficient**: Uses structured format, easy to parse

## Privacy & Security

- Log contains search keywords (user search terms)
- Does NOT log IP addresses, user IDs, or personal data
- Rotate/delete old logs if privacy is a concern
- Consider excluding sensitive keywords from logging if needed

## Example Production Workflow

### After Deployment
```bash
# SSH into production
ssh yanivbl@ssh.pythonanywhere.com

# Navigate to app directory
cd /home/yanivbl/apps/eguidesearches-novaview

# Check if logging is working
tail -f cache_audit.log

# In another terminal, make a test request
curl "https://www.eguidesearches.com/api/search?kw=test"

# You should see log entries appear in real-time
```

### Weekly Check
```bash
# Count API calls this week
grep "API_CALL" cache_audit.log | grep "2025-12-" | wc -l

# Find top 10 requested keywords
grep "REQUEST_START" cache_audit.log | grep -oP 'keyword=\K[^ ]+' | sort | uniq -c | sort -rn | head -10

# Check cache hit rate
echo "Hits: $(grep 'CACHE_RESULT.*HIT' cache_audit.log | wc -l)"
echo "Misses: $(grep 'CACHE_RESULT.*MISS' cache_audit.log | wc -l)"
```

### Monthly Cleanup
```bash
# Archive old log
cd /home/yanivbl/apps/eguidesearches-novaview
cp cache_audit.log cache_audit.log.$(date +%Y%m).backup
gzip cache_audit.log.*.backup

# Clear current log (start fresh)
> cache_audit.log

# Remove backups older than 3 months
find . -name "cache_audit.log.*.backup.gz" -mtime +90 -delete
```
