"""
Utility Functions for New Landing Page System
Contains browser detection, keyword sanitization, and image validation
"""

import os
import re
from typing import Optional
from PIL import Image
from config import SUPPORTED_EXTENSIONS


def sanitize_keyword_for_filename(keyword: str) -> str:
    """
    Convert keyword to safe filename format

    Args:
        keyword: User-provided keyword string

    Returns:
        Sanitized keyword safe for use in filenames

    Example:
        "Gaming Laptops!" -> "gaming_laptops"
    """
    keyword = keyword.strip().lower()
    keyword = keyword.replace(" ", "_")
    keyword = re.sub(r"[^a-z0-9_\-]", "", keyword)
    return keyword or "image"


def is_bot(user_agent: str) -> bool:
    """
    Detect if user agent is a bot/crawler

    Filters out common bots including:
    - Search engine crawlers (Google, Bing, etc.)
    - Monitoring/testing tools (curl, wget, Python, etc.)
    - Automated browsers (headless, Selenium, etc.)

    Args:
        user_agent: HTTP User-Agent header string

    Returns:
        True if bot detected, False if likely a real user
    """
    if not user_agent:
        return False

    user_agent_lower = user_agent.lower()

    # Bot patterns to detect
    bot_patterns = [
        'bot', 'crawler', 'spider', 'scraper',
        'curl', 'wget', 'python', 'java',
        'http', 'axios', 'fetch', 'go-http',
        'headless', 'phantom', 'selenium', 'playwright', 'puppeteer',
        'preview', 'validator', 'checker', 'monitor', 'uptime',
        'gtmetrix', 'pingdom', 'statuscake', 'newrelic'
    ]

    # Check for bot patterns
    for pattern in bot_patterns:
        if pattern in user_agent_lower:
            return True

    # Specific check for Google's mobile crawler (Nexus 5X)
    # This is used by PageSpeed Insights and Mobile-Friendly Test
    if 'nexus 5x build/mmb29p' in user_agent_lower:
        return True

    # Check for suspicious patterns (valid browsers always have Mozilla/5.0)
    if 'mozilla/5.0' not in user_agent_lower:
        return True

    return False


def detect_browser_type(user_agent: str) -> str:
    """
    Detect browser type from User-Agent string

    CRITICAL: Order matters! Edge and Opera contain "Chrome" in their
    User-Agent strings, so they must be checked first.

    Args:
        user_agent: HTTP User-Agent header string

    Returns:
        Browser type: 'chrome', 'edge', 'firefox', 'safari', 'opera', or 'other'
    """
    if not user_agent:
        return 'unknown'

    user_agent = user_agent.lower()

    # Opera detection (must come before Chrome since Opera contains "Chrome" in UA)
    if 'opr/' in user_agent or 'opera/' in user_agent:
        return 'opera'

    # Edge detection (must come before Chrome since Edge contains "Chrome" in UA)
    if 'edg/' in user_agent or 'edge/' in user_agent:
        return 'edge'

    # Chrome detection
    if 'chrome/' in user_agent and 'chromium/' not in user_agent:
        return 'chrome'

    # Firefox detection
    if 'firefox/' in user_agent:
        return 'firefox'

    # Safari detection
    if 'safari/' in user_agent and 'chrome/' not in user_agent:
        return 'safari'

    return 'other'


def is_file_an_image(file_path: str) -> bool:
    """
    Validate if file is a valid image

    Performs comprehensive validation:
    1. File exists
    2. File size > 0
    3. PIL can verify the image
    4. PIL can load the image data

    Args:
        file_path: Path to image file

    Returns:
        True if valid image, False otherwise
    """
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False

        # Verify image integrity
        with Image.open(file_path) as im:
            im.verify()

        # Actually load image data
        with Image.open(file_path) as im:
            im.load()

        return True
    except Exception:
        return False


def resolve_actual_saved_path(base_without_ext: str) -> Optional[str]:
    """
    Find actual file path with any supported extension

    Given a base filename without extension, try all supported extensions
    to find the actual file.

    Args:
        base_without_ext: Base filename without extension (e.g., "images/keyword_1")

    Returns:
        Full path with extension if found, None otherwise

    Example:
        resolve_actual_saved_path("images/gaming_laptop_1")
        -> "images/gaming_laptop_1.jpg" (if exists)
    """
    if os.path.exists(base_without_ext):
        return base_without_ext

    for ext in SUPPORTED_EXTENSIONS:
        candidate = base_without_ext + ext
        if os.path.exists(candidate):
            return candidate

    return None
