#!/usr/bin/env python3
"""
Working Deployment Script for PythonAnywhere
Uses the Files API correctly to upload all application files
"""

import requests
import time
from pathlib import Path

# Configuration
PAW_TOKEN = "02cbe543901038d81a9bf86cddbf1288ed4c8c1b"
USERNAME = "yanivbl"
DOMAIN = "www.eguidesearches.com"
APP_PATH = f"/home/{USERNAME}/apps/eguidesearches-novaview"

# Project root
PROJECT_ROOT = Path(__file__).parent.absolute()

# Files to deploy (relative paths)
FILES_TO_DEPLOY = [
    # Core application files
    'app.py',
    'config.py',
    'image_service.py',
    'utils.py',
    # A/B testing module
    'ab_testing/__init__.py',
    'ab_testing/ab_log_parser.py',
    'ab_testing/test_history.py',
    # Templates
    'templates/ab_dashboard.html',
    'templates/index_variant_a.html',
    'templates/index_variant_b.html',
    'templates/landing.html',
    'templates/legal.html',
    'templates/legal_about.html',
    'templates/legal_contact.html',
    'templates/legal_copyright.html',
    'templates/legal_eula.html',
    'templates/legal_privacy.html',
    'templates/legal_terms.html',
    'templates/legal_uninstall.html',
    'templates/thankyou.html',
    'templates/thankyou-test.html',
]

def upload_file(local_path, remote_path):
    """Upload a single file to PythonAnywhere"""

    # Read file content
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # API endpoint
    url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path{remote_path}"

    headers = {
        'Authorization': f'Token {PAW_TOKEN}',
    }

    # Try POST first (create new file) with multipart form data
    response = requests.post(
        url,
        headers=headers,
        files={'content': content}
    )

    if response.status_code in [200, 201]:
        return True, f"Uploaded (POST)"

    # If POST fails, try PUT (update existing file) with raw data
    elif response.status_code in [400, 404]:
        response = requests.put(
            url,
            headers=headers,
            data=content.encode('utf-8')
        )

        if response.status_code in [200, 201, 204]:
            return True, f"Updated (PUT)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    else:
        return False, f"HTTP {response.status_code}: {response.text[:200]}"

def reload_webapp():
    """Reload the PythonAnywhere web app"""
    url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/webapps/{DOMAIN}/reload/"

    headers = {
        'Authorization': f'Token {PAW_TOKEN}',
    }

    response = requests.post(url, headers=headers)
    return response.status_code == 200

def verify_deployment():
    """Verify deployment by checking production"""
    time.sleep(10)  # Wait for server to fully reload

    try:
        response = requests.get(
            f"https://{DOMAIN}/?kw=test&img=true&variant=b",
            headers={'Cache-Control': 'no-cache'},
            timeout=15
        )

        # Check if variant B has no images (our recent change)
        has_images = '<div id="images-section"' in response.text

        return response.status_code == 200, has_images
    except Exception as e:
        return False, None

def main():
    print("=" * 70)
    print("DEPLOYING TO PYTHONANYWHERE")
    print("=" * 70)
    print(f"\nTarget: {DOMAIN}")
    print(f"Path: {APP_PATH}")
    print(f"Files: {len(FILES_TO_DEPLOY)}")
    print()

    uploaded = 0
    failed = 0
    errors = []

    # Upload all files
    for i, relative_path in enumerate(FILES_TO_DEPLOY, 1):
        local_path = PROJECT_ROOT / relative_path
        remote_path = f"{APP_PATH}/{relative_path}"

        print(f"[{i}/{len(FILES_TO_DEPLOY)}] {relative_path}...", end=" ")

        if not local_path.exists():
            print(f"SKIP (not found)")
            failed += 1
            errors.append(f"{relative_path}: File not found locally")
            continue

        success, message = upload_file(local_path, remote_path)

        if success:
            print(f"OK ({message})")
            uploaded += 1
        else:
            print(f"FAILED ({message})")
            failed += 1
            errors.append(f"{relative_path}: {message}")

    print()
    print("=" * 70)
    print(f"Upload Summary: {uploaded} succeeded, {failed} failed")
    print("=" * 70)

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        print()

    if uploaded == 0:
        print("\nDEPLOYMENT FAILED: No files uploaded")
        return 1

    # Reload web app
    print("\nReloading web app...", end=" ")
    if reload_webapp():
        print("OK")
    else:
        print("FAILED")
        print("Warning: Files uploaded but reload failed")
        print("Manually reload via PythonAnywhere web interface")
        return 1

    # Verify deployment
    print("\nVerifying deployment (waiting 10s for server restart)...", end=" ")
    success, has_images = verify_deployment()

    if success:
        print("OK")
        print(f"  Variant B has images: {has_images}")
        if has_images:
            print("  WARNING: Expected no images in variant B")
    else:
        print("FAILED")
        print("  Could not reach production URL")

    print()
    print("=" * 70)
    print("DEPLOYMENT COMPLETE")
    print("=" * 70)
    print(f"\nProduction URL: https://{DOMAIN}/?kw=test&img=true")
    print(f"Variant A: https://{DOMAIN}/?kw=test&img=true&variant=a")
    print(f"Variant B: https://{DOMAIN}/?kw=test&img=true&variant=b")
    print("\nNote: Use Ctrl+Shift+R to bypass browser cache when testing")

    return 0

if __name__ == '__main__':
    exit(main())
