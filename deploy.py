#!/usr/bin/env python3
"""
Clean Deployment Script for NovaView Landing Page
Automatically deploys code to PythonAnywhere and verifies deployment
No clutter files created - everything stays in .deployment/ folder
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, level="INFO"):
    """Log message with timestamp and color"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if level == "INFO":
        color = Color.BLUE
        prefix = "INFO   "
    elif level == "SUCCESS":
        color = Color.GREEN
        prefix = "SUCCESS"
    elif level == "WARNING":
        color = Color.YELLOW
        prefix = "WARNING"
    elif level == "ERROR":
        color = Color.RED
        prefix = "ERROR  "
    elif level == "HEADER":
        color = Color.HEADER
        prefix = "---"
    else:
        color = Color.ENDC
        prefix = level

    print(f"{color}[{timestamp}] {prefix}: {message}{Color.ENDC}")

    # Also log to file
    log_file = Path(".deployment/deployment.log")
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {prefix}: {message}\n")

def run_command(cmd, description="", timeout=120):
    """Execute shell command and return success status"""
    try:
        log(description or f"Executing: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            if description:
                log(f"{description} completed successfully", "SUCCESS")
            return True, result.stdout.strip()
        else:
            log(f"Command failed: {result.stderr}", "ERROR")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        log(f"Command timed out after {timeout} seconds", "ERROR")
        return False, ""
    except Exception as e:
        log(f"Error executing command: {e}", "ERROR")
        return False, str(e)

def check_git_status():
    """Check if there are uncommitted changes"""
    success, output = run_command("git status --short", "Checking git status")
    if success and output:
        log("Uncommitted changes detected:", "WARNING")
        for line in output.split("\n"):
            if line.strip():
                log(f"  {line}", "WARNING")
        response = input(f"{Color.YELLOW}Continue with deployment anyway? (y/n): {Color.ENDC}")
        return response.lower() == "y"
    return True

def deploy():
    """Main deployment process"""
    log("=" * 60, "HEADER")
    log("NovaView Landing Page - Automated Deployment", "HEADER")
    log("=" * 60, "HEADER")

    # Step 1: Pre-deployment checks
    log("Step 1: Pre-deployment checks", "HEADER")
    if not check_git_status():
        log("Deployment cancelled by user", "WARNING")
        return False

    # Step 2: Local updates
    log("Step 2: Pulling latest changes locally", "HEADER")
    success, output = run_command("git pull origin master", "Pulling latest changes from git")
    if not success:
        log("Failed to pull latest changes", "ERROR")
        return False
    log(f"Git output: {output}", "INFO")

    # Step 3: Remote deployment
    log("Step 3: Deploying to PythonAnywhere", "HEADER")

    ssh_commands = (
        "cd /home/yanivbl/apps/eguidesearches-novaview && "
        "git pull origin master && "
        "echo 'Remote deployment completed' && "
        "head -1 .git/logs/HEAD"
    )

    success, output = run_command(
        f'ssh yanivbl@ssh.pythonanywhere.com "{ssh_commands}"',
        "Executing remote deployment commands",
        timeout=60
    )

    if not success:
        log("Remote deployment failed", "ERROR")
        return False

    log("Remote git pull successful", "SUCCESS")

    # Step 4: WSGI reload
    log("Step 4: Reloading WSGI application", "HEADER")
    success, output = run_command(
        'ssh yanivbl@ssh.pythonanywhere.com "touch /var/www/www_eguidesearches_com_wsgi.py"',
        "Touching WSGI file to trigger reload",
        timeout=30
    )

    if not success:
        log("Failed to reload WSGI application", "ERROR")
        return False

    log("WSGI application reloaded successfully", "SUCCESS")

    # Step 5: Verification
    log("Step 5: Verifying deployment", "HEADER")
    success, output = run_command(
        'ssh yanivbl@ssh.pythonanywhere.com "cd /home/yanivbl/apps/eguidesearches-novaview && git log -1 --oneline"',
        "Checking remote git log",
        timeout=30
    )

    if success:
        log(f"Latest remote commit: {output}", "SUCCESS")
    else:
        log("Could not verify deployment (SSH might not be fully configured)", "WARNING")

    # Step 6: Summary
    log("=" * 60, "HEADER")
    log("Deployment completed successfully!", "SUCCESS")
    log("=" * 60, "HEADER")
    log("Production URL: https://www.eguidesearches.com", "INFO")
    log("Deployment log: .deployment/deployment.log", "INFO")

    return True

def main():
    """Main entry point"""
    try:
        # Ensure .deployment directory exists
        Path(".deployment").mkdir(exist_ok=True)

        # Run deployment
        success = deploy()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        log("Deployment cancelled by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
