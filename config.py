"""
Global Configuration for New Landing Page System
Contains centralized settings and URLs used across the application
"""

import os

# Browser Extension Store URLs
# CRITICAL: These are the single source of truth for extension store URLs
# ALWAYS verify these URLs match the current product being promoted

# Chrome Web Store URL - NovaView Extension
CHROME_STORE_URL = 'https://chromewebstore.google.com/detail/novaview/gkpnedgnhkkloibfigmamhgbikfbmojf'

# Edge Add-ons Store URL - NovaView Extension
EDGE_STORE_URL = 'https://microsoftedge.microsoft.com/addons/detail/novaview/lfdlalahkanbjcdchhhlobccgppbfnnd'

# Cache Configuration
CACHE_TTL_HOURS = 2400  # 100 days
TARGET_FILE_SIZE = 25 * 1024  # 25KB target for optimized images
THUMBNAIL_SIZE = (480, 270)  # 16:9 aspect ratio

# Directory Configuration
FINAL_IMAGES_DIR = 'images'
CANDIDATES_CACHE_DIR = 'images/cache'

# Supported image extensions
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')

# Google API Configuration (loaded from environment)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')

# Backup Google API Configuration (for rate limit fallback)
GOOGLE_API_KEY_BACKUP = os.getenv('GOOGLE_API_KEY_BACKUP')
GOOGLE_CX_BACKUP = os.getenv('GOOGLE_CX_BACKUP')

# Application metadata
APP_NAME = 'EGuideSearches'
APP_DESCRIPTION = 'Easily find manuals online'
COPYRIGHT_YEAR = '2025'
COPYRIGHT_HOLDER = 'EGuideSearches'

# Google Tag ID for conversion tracking
GOOGLE_TAG_ID = 'AW-1006081641'
