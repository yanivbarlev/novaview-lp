"""
New Landing Page Application
Clean, minimal Flask app with only essential routes
"""

import os
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and services
from config import (
    CHROME_STORE_URL,
    EDGE_STORE_URL,
    FINAL_IMAGES_DIR,
    CANDIDATES_CACHE_DIR,
    GOOGLE_TAG_ID
)
from utils import detect_browser_type, sanitize_keyword_for_filename
from image_service import ImageSearchService

# Initialize Flask app with explicit absolute paths
_current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(_current_dir, 'templates'),
            static_folder=os.path.join(_current_dir, 'static'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs(FINAL_IMAGES_DIR, exist_ok=True)
os.makedirs(CANDIDATES_CACHE_DIR, exist_ok=True)

# Initialize image service
image_service = ImageSearchService()


# URL Normalization - Remove trailing slashes for consistency
# This ensures browsers don't cache /path/ and /path separately
@app.before_request
def normalize_trailing_slash():
    """
    Remove trailing slashes from non-root URLs
    Prevents browser from caching .com/? and .com? as different pages
    """
    # Only process non-root paths with trailing slashes
    if request.path != '/' and request.path.endswith('/'):
        # Build new URL without trailing slash
        new_path = request.path.rstrip('/')
        query_string = request.query_string.decode('utf-8')

        if query_string:
            redirect_url = f"{new_path}?{query_string}"
        else:
            redirect_url = new_path

        # 301 permanent redirect
        return redirect(redirect_url, code=301)


# Template global functions
@app.template_global()
def chrome_store_url():
    """Get Chrome store URL for templates"""
    return CHROME_STORE_URL


@app.template_global()
def edge_store_url():
    """Get Edge store URL for templates"""
    return EDGE_STORE_URL


@app.template_global()
def google_tag_id():
    """Get Google Tag ID for templates"""
    return GOOGLE_TAG_ID


# === ROUTE 1: Main Landing Page ===
@app.route('/')
def landing_page():
    """
    Main landing page for extension promotion

    URL Parameters:
        kw (str): Keyword for image search (default: 'trending')
        img (str): 'true' to show images (default: false)
        gclid (str): Google Click ID for conversion attribution
    """
    # Extract and sanitize parameters
    keyword = request.args.get('kw', 'trending').strip()
    show_images = request.args.get('img', '').lower() == 'true'
    gclid = request.args.get('gclid', '')

    # Sanitize keyword (max 100 chars)
    if not keyword or len(keyword) > 100:
        keyword = 'trending'

    # Conditional image display logic
    # Only show images if BOTH img=true AND kw parameter exist
    has_kw_param = request.args.get('kw') is not None
    show_images = show_images and has_kw_param

    # Browser detection from User-Agent
    user_agent = request.headers.get('User-Agent', 'Unknown')
    browser_type = detect_browser_type(user_agent)

    # Get client IP (respects proxy headers)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    # Logging (critical for debugging)
    logger.info(
        f'LANDING_PAGE keyword="{keyword}" gclid="{gclid}" '
        f'show_images={show_images} browser="{browser_type}" '
        f'user_agent="{user_agent[:100]}" ip="{client_ip}"'
    )

    # Render template with NO server-side image fetching
    # Images will load via JavaScript AJAX after page renders
    return render_template('landing.html',
                         keyword=keyword,
                         gclid=gclid,
                         show_images=show_images,
                         browser_type=browser_type)


# === ROUTE 2: StackFree Landing Page ===
@app.route('/stackfree')
def stackfree_landing():
    """
    StackFree landing page (identical logic to main landing page)

    URL Parameters:
        kw (str): Keyword for image search (default: 'trending')
        img (str): 'true' to show images (default: false)
        gclid (str): Google Click ID for conversion attribution
    """
    # Extract and sanitize parameters
    keyword = request.args.get('kw', 'trending').strip()
    show_images = request.args.get('img', '').lower() == 'true'
    gclid = request.args.get('gclid', '')

    # Sanitize keyword (max 100 chars)
    if not keyword or len(keyword) > 100:
        keyword = 'trending'

    # Conditional image display logic
    # Only show images if BOTH img=true AND kw parameter exist
    has_kw_param = request.args.get('kw') is not None
    show_images = show_images and has_kw_param

    # Browser detection from User-Agent
    user_agent = request.headers.get('User-Agent', 'Unknown')
    browser_type = detect_browser_type(user_agent)

    # Get client IP (respects proxy headers)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    # Logging (critical for debugging)
    logger.info(
        f'STACKFREE_PAGE keyword="{keyword}" gclid="{gclid}" '
        f'show_images={show_images} browser="{browser_type}" '
        f'user_agent="{user_agent[:100]}" ip="{client_ip}"'
    )

    # Render template with NO server-side image fetching
    # Images will load via JavaScript AJAX after page renders
    return render_template('landing.html',
                         keyword=keyword,
                         gclid=gclid,
                         show_images=show_images,
                         browser_type=browser_type)


# === ROUTE 3: Image Search API ===
@app.route('/api/search')
def api_search():
    """
    Image search API endpoint (server-side proxy for Google API)

    URL Parameters:
        kw (str): Keyword for image search

    Returns:
        JSON with images array and cache status
    """
    keyword = request.args.get('kw', '').strip()

    if not keyword:
        return jsonify({
            'error': 'Missing keyword parameter',
            'images': [],
            'count': 0
        }), 400

    # Sanitize keyword
    if len(keyword) > 100:
        keyword = keyword[:100]

    # Log API request
    logger.info(f'API_SEARCH keyword="{keyword}" '
               f'ip="{request.remote_addr}" '
               f'user_agent="{request.headers.get("User-Agent", "Unknown")[:100]}"')

    try:
        # Check if images are already cached
        keyword_base = sanitize_keyword_for_filename(keyword)
        from image_service import check_all_images_cached
        cache_hit = check_all_images_cached(keyword_base, 3)

        if cache_hit:
            # Images are cached - return them immediately
            images = image_service.search_images(keyword, count=3)
            return jsonify({
                'keyword': keyword,
                'images': images,
                'count': len(images),
                'cached': True,
                'cache_status': 'HIT',
                'api_call_made': False
            })
        else:
            # Images not cached - trigger background download and return empty
            def background_download():
                try:
                    logger.info(f'BACKGROUND_DOWNLOAD_START keyword="{keyword}"')
                    image_service.search_images(keyword, count=3)
                    logger.info(f'BACKGROUND_DOWNLOAD_COMPLETE keyword="{keyword}"')
                except Exception as e:
                    logger.error(f'BACKGROUND_DOWNLOAD_ERROR keyword="{keyword}" error="{str(e)}"')

            # Start background thread
            thread = threading.Thread(target=background_download, daemon=True)
            thread.start()

            # Return empty response immediately
            return jsonify({
                'keyword': keyword,
                'images': [],
                'count': 0,
                'cached': False,
                'cache_status': 'DOWNLOADING',
                'api_call_made': True
            })

    except Exception as e:
        logger.error(f'API_SEARCH_ERROR keyword="{keyword}" error="{str(e)}"')
        return jsonify({
            'error': 'Failed to fetch images',
            'images': [],
            'count': 0
        }), 500


# === ROUTE 4: Image Serving ===
@app.route('/image/<filename>')
def serve_image(filename):
    """
    Serve optimized images from cache

    Args:
        filename (str): Image filename

    Returns:
        Image file
    """
    try:
        return send_from_directory(FINAL_IMAGES_DIR, filename)
    except Exception as e:
        logger.error(f'IMAGE_SERVE_ERROR filename="{filename}" error="{str(e)}"')
        return 'Image not found', 404


# === ROUTE 5: CTA Click Tracking ===
@app.route('/api/track/click', methods=['POST'])
def track_click():
    """
    Track CTA button clicks with attribution data

    Request Body (JSON):
        button_id (str): Button identifier
        keyword (str): Current keyword
        gclid (str): Google Click ID
        timestamp (str): ISO timestamp

    Returns:
        JSON with success status
    """
    data = request.get_json() or {}

    button_id = data.get('button_id', 'unknown')
    keyword = data.get('keyword', 'unknown')
    gclid = data.get('gclid', '')

    user_agent = request.headers.get('User-Agent', 'Unknown')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    referer = request.headers.get('Referer', '')

    logger.info(
        f'CTA_CLICK button_id="{button_id}" keyword="{keyword}" '
        f'gclid="{gclid}" user_agent="{user_agent[:100]}" '
        f'ip="{client_ip}" referer="{referer}"'
    )

    return jsonify({
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    })


# === ROUTE 6: Exit Popup Tracking ===
@app.route('/api/track/exit-popup', methods=['POST'])
def track_exit_popup():
    """
    Track exit popup events

    Request Body (JSON):
        event (str): Event type (exit_popup_shown, exit_popup_dismissed, exit_popup_cta_clicked)
        keyword (str): Current keyword
        gclid (str): Google Click ID
        timestamp (str): ISO timestamp

    Returns:
        JSON with success status
    """
    data = request.get_json() or {}

    event = data.get('event', 'unknown')
    keyword = data.get('keyword', 'unknown')
    gclid = data.get('gclid', '')
    timestamp = data.get('timestamp', '')

    user_agent = request.headers.get('User-Agent', 'Unknown')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    logger.info(
        f'EXIT_POPUP event="{event}" keyword="{keyword}" '
        f'gclid="{gclid}" timestamp="{timestamp}" '
        f'user_agent="{user_agent[:100]}" ip="{client_ip}"'
    )

    return jsonify({'status': 'success'})


# === ROUTE 7: Thank You Page (Local) ===
@app.route('/thankyou-downloadmanager.html')
def thankyou_downloadmanager():
    """
    Local thank you page for testing
    Matches production URL structure

    URL Parameters:
        source (str): Source identifier (e.g., 'novaview')
        gclid (str): Google Click ID for conversion attribution

    Returns:
        HTML thank you page with conversion tracking
    """
    source = request.args.get('source', 'novaview')
    gclid = request.args.get('gclid', '')

    logger.info(
        f'THANKYOU_PAGE source="{source}" gclid="{gclid}" '
        f'ip="{request.remote_addr}" '
        f'user_agent="{request.headers.get("User-Agent", "Unknown")[:100]}"'
    )

    return render_template('thankyou.html', gclid=gclid, source=source)


# === ROUTE 8: Post-Install Redirect (Production) ===
@app.route('/post_install/')
def post_install():
    """
    Post-install redirect for production deployment
    Redirects to the main eguidesearches.com thank you page

    URL Parameters:
        gclid (str): Google Click ID for conversion attribution

    Returns:
        Redirect to production thank you page
    """
    gclid = request.args.get('gclid', '')

    logger.info(
        f'POST_INSTALL_REDIRECT gclid="{gclid}" '
        f'ip="{request.remote_addr}" '
        f'user_agent="{request.headers.get("User-Agent", "Unknown")[:100]}"'
    )

    # Build redirect URL with gclid if present
    thank_you_url = 'https://www.eguidesearches.com/thankyou-downloadmanager.html?source=novaview'
    if gclid:
        thank_you_url += f'&gclid={gclid}'

    return redirect(thank_you_url)


# === Legal Pages ===
@app.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('legal.html',
                         page_title='Privacy Policy',
                         page='privacy')

@app.route('/terms')
def terms():
    """Terms of Use page"""
    return render_template('legal.html',
                         page_title='Terms of Use',
                         page='terms')

@app.route('/eula')
def eula():
    """End User License Agreement page"""
    return render_template('legal.html',
                         page_title='End User License Agreement',
                         page='eula')

@app.route('/copyright')
def copyright_policy():
    """Copyright Policy page"""
    return render_template('legal.html',
                         page_title='Copyright Policy',
                         page='copyright')

@app.route('/about')
def about():
    """About Us page"""
    return render_template('legal.html',
                         page_title='About Us',
                         page='about')

@app.route('/uninstall')
def uninstall():
    """Uninstall Instructions page"""
    return render_template('legal.html',
                         page_title='Uninstall Instructions',
                         page='uninstall')

@app.route('/contact')
def contact():
    """Contact Us page"""
    return render_template('legal.html',
                         page_title='Contact Us',
                         page='contact')


if __name__ == '__main__':
    # Run Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
