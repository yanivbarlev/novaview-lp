# Deployment Directory

This directory contains deployment-related files and logs. It is NOT tracked in git.

## Purpose

Keeps deployment artifacts separate from the main codebase to maintain a clean project structure.

## Contents

### `deployment.log`
Activity log with timestamps for all deployment operations including:
- Git pull results
- SSH command outputs
- Verification results
- Error messages
- Deployment summaries

### Temporary Files
Any temporary files created during deployment are stored here and automatically cleaned up after completion.

## File Management

- **Created by:** `deploy.py` script
- **Updated on:** Every deployment
- **Cleaned up:** Automatically after each deployment
- **Git tracking:** Excluded (only README.md is tracked)

## Log Format

```
[YYYY-MM-DD HH:MM:SS] LEVEL: Message
```

**Levels:**
- `INFO` - General information
- `SUCCESS` - Successful operations
- `WARNING` - Non-critical issues
- `ERROR` - Critical failures

## Viewing Logs

```bash
# View recent activity (last 50 lines)
tail -50 .deployment/deployment.log

# View all deployment history
cat .deployment/deployment.log

# Watch logs in real-time (during deployment)
tail -f .deployment/deployment.log
```

## Cleaning Up

The deployment directory can be safely deleted if needed:

```bash
# Remove deployment logs and temporary files
rm -rf .deployment/

# The directory will be recreated on next deployment
```

## Privacy Note

Deployment logs may contain:
- Git commit messages
- SSH command outputs
- Server paths
- Timestamps

Do NOT commit deployment logs to git or share publicly as they may reveal sensitive deployment details.
