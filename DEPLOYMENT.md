# NovaView Landing Page - Deployment Guide

## Quick Deploy

```bash
python deploy.py
```

That's it! The script handles everything automatically.

## What It Does

The deployment script performs the following steps:

1. **Pre-deployment checks**
   - Verifies git status (warns if uncommitted changes)
   - Ensures local repository is ready

2. **Local updates**
   - Pulls latest changes from git origin/master
   - Confirms local repo is up to date

3. **Remote deployment**
   - Connects to PythonAnywhere via SSH
   - Pulls latest changes on remote server
   - Touches WSGI file to reload application

4. **Verification**
   - Checks remote git log to confirm deployment
   - Reports latest commit on server

5. **Cleanup**
   - Removes any temporary files created
   - Logs deployment activity

## Requirements

### Local Environment

- Python 3.7+
- Git installed and configured
- SSH access to PythonAnywhere (ssh keys configured)

### SSH Setup

Before first deployment, ensure SSH access is configured:

```bash
# Test SSH connection
ssh yanivbl@ssh.pythonanywhere.com

# If this works, you're ready to deploy
```

If SSH authentication fails, you need to:
1. Generate SSH key: `ssh-keygen -t rsa -b 4096`
2. Copy public key to PythonAnywhere dashboard
3. Test connection again

## Configuration

All configuration is in `deploy.py`:

```python
REMOTE_USER = "yanivbl"
REMOTE_HOST = "ssh.pythonanywhere.com"
REMOTE_APP_DIR = "/home/yanivbl/apps/eguidesearches-novaview"
WSGI_FILE = "/var/www/www_eguidesearches_com_wsgi.py"
```

## Deployment Logs

All deployment activity is logged to:
```
.deployment/deployment.log
```

The log includes:
- Timestamps for all operations
- Git pull results
- SSH command outputs
- Verification results
- Any errors encountered

## File Structure

```
novaview-lp/
├── deploy.py              # Main deployment script
├── DEPLOYMENT.md          # This file
├── .deployment/           # Deployment artifacts (NOT in git)
│   ├── README.md         # Deployment directory documentation
│   └── deployment.log    # Activity log with timestamps
└── .gitignore            # Excludes .deployment/ from git
```

## Production Environment

**Server:** PythonAnywhere
**User:** yanivbl
**App Directory:** /home/yanivbl/apps/eguidesearches-novaview
**WSGI File:** /var/www/www_eguidesearches_com_wsgi.py
**Production URL:** https://www.eguidesearches.com
**Python Version:** 3.10
**Virtualenv:** /home/yanivbl/.virtualenvs/mysite-virtualen

## Troubleshooting

### SSH Authentication Fails

```bash
# Check SSH connection
ssh yanivbl@ssh.pythonanywhere.com

# If fails, check SSH key configuration in PythonAnywhere dashboard
```

### Git Pull Fails on Remote

```bash
# SSH into server and check manually
ssh yanivbl@ssh.pythonanywhere.com
cd /home/yanivbl/apps/eguidesearches-novaview
git status
git pull origin master
```

### WSGI Not Reloading

```bash
# Manually touch WSGI file via SSH
ssh yanivbl@ssh.pythonanywhere.com "touch /var/www/www_eguidesearches_com_wsgi.py"

# Or use PythonAnywhere web interface to reload
```

### Uncommitted Local Changes

The script will warn you if there are uncommitted changes:
- Press 'y' to continue deployment anyway
- Press 'n' to cancel and commit changes first

### Check Deployment Logs

```bash
# View recent deployment activity
cat .deployment/deployment.log | tail -50

# View all deployment history
cat .deployment/deployment.log
```

## Manual Deployment Steps

If the automated script fails, you can deploy manually:

```bash
# 1. Pull latest changes locally
git pull origin master

# 2. SSH into PythonAnywhere
ssh yanivbl@ssh.pythonanywhere.com

# 3. Navigate to app directory
cd /home/yanivbl/apps/eguidesearches-novaview

# 4. Pull latest changes
git pull origin master

# 5. Reload WSGI application
touch /var/www/www_eguidesearches_com_wsgi.py

# 6. Exit SSH
exit
```

## Clean Deployment Practices

### What Gets Deployed

- Application code (app.py, config.py, utils.py, image_service.py)
- Templates (templates/*.html)
- Static assets (static/*)
- Configuration files (requirements.txt)
- Documentation (README.md, CLAUDE.md)

### What Doesn't Get Deployed

- Environment variables (.env) - configured separately on server
- Python cache (__pycache__/)
- Logs (*.log)
- Image cache (images/cache/, images/*.webp)
- Deployment artifacts (.deployment/)
- IDE files (.vscode/, .idea/)

### No Clutter Policy

The deployment system is designed to be clean:
- NO deployment documentation in main project folder
- NO diagnostic scripts in main project folder
- NO temporary files left after deployment
- ALL deployment artifacts in .deployment/ folder
- .deployment/ folder excluded from git

## Post-Deployment Verification

After deployment, verify the site is working:

1. **Check production URL:**
   ```
   https://www.eguidesearches.com/?kw=pokemon&img=true
   ```

2. **Test key functionality:**
   - Landing page loads
   - Images display correctly
   - CTA button works
   - Exit popup triggers
   - Thank you page loads

3. **Check logs on server:**
   ```bash
   ssh yanivbl@ssh.pythonanywhere.com
   tail -f /home/yanivbl/apps/eguidesearches-novaview/app.log
   ```

## Rollback Procedure

If deployment causes issues:

```bash
# SSH into server
ssh yanivbl@ssh.pythonanywhere.com

# Navigate to app directory
cd /home/yanivbl/apps/eguidesearches-novaview

# Check recent commits
git log --oneline -5

# Rollback to previous commit (replace COMMIT_HASH)
git reset --hard COMMIT_HASH

# Reload WSGI
touch /var/www/www_eguidesearches_com_wsgi.py
```

## Best Practices

1. **Always test locally first**
   ```bash
   python app.py
   # Test at http://localhost:5000
   ```

2. **Commit changes before deploying**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin master
   ```

3. **Deploy during low-traffic periods**
   - Minimizes impact if issues occur
   - Easier to monitor and rollback

4. **Monitor after deployment**
   - Check production URL immediately
   - Watch server logs for errors
   - Test key user flows

5. **Keep deployment logs**
   - Review .deployment/deployment.log periodically
   - Helps diagnose issues
   - Provides deployment history

## Support

- **Repository:** https://github.com/yanivbarlev/novaview-lp
- **Issues:** https://github.com/yanivbarlev/novaview-lp/issues
- **Documentation:** CLAUDE.md, README.md
- **Contact:** See /contact page on production site
