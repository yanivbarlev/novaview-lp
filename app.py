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
    GOOGLE_TAG_ID,
    AB_TEST_ENABLED,
    AB_TEST_NAME
)
from utils import detect_browser_type, sanitize_keyword_for_filename
from image_service import ImageSearchService

# Initialize Flask app with explicit absolute paths
_current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(_current_dir, 'templates'),
            static_folder=os.path.join(_current_dir, 'static'))

# Setup logging - write to both console and file
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configure root logger to write to file
log_file = os.path.join(_current_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Get logger for this app
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
    Main landing page for extension promotion with A/B testing support

    URL Parameters:
        kw (str): Keyword for image search (default: 'trending')
        img (str): 'true' to show images (default: false)
        gclid (str): Google Click ID for conversion attribution
        variant (str): A/B test variant ('a' or 'b')
    """
    # Extract and sanitize parameters
    keyword = request.args.get('kw', 'trending').strip()
    show_images = request.args.get('img', '').lower() == 'true'
    gclid = request.args.get('gclid', '')
    variant = request.args.get('variant', 'a').lower()  # NEW: Get variant from URL

    # Sanitize keyword (max 100 chars)
    if not keyword or len(keyword) > 100:
        keyword = 'trending'

    # NEW: Validate variant
    if variant not in ['a', 'b']:
        variant = 'a'

    # NEW: If A/B test disabled, force variant A
    if not AB_TEST_ENABLED:
        variant = 'a'

    # Conditional image display logic
    # Only show images if BOTH img=true AND kw parameter exist
    has_kw_param = request.args.get('kw') is not None
    show_images = show_images and has_kw_param

    # Browser detection from User-Agent
    user_agent = request.headers.get('User-Agent', 'Unknown')
    browser_type = detect_browser_type(user_agent)

    # Get client IP (respects proxy headers)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    # NEW: Log landing page visit with variant
    logger.info(
        f'LANDING_PAGE keyword="{keyword}" gclid="{gclid}" variant="{variant}" '
        f'show_images={show_images} has_kw_param={has_kw_param} '
        f'browser="{browser_type}" user_agent="{user_agent[:100]}" ip="{client_ip}"'
    )

    # NEW: Select template based on variant
    template_name = f'index_variant_{variant}.html'

    # Render template with NO server-side image fetching
    # Images will load via JavaScript AJAX after page renders
    return render_template(template_name,
                         keyword=keyword,
                         gclid=gclid,
                         show_images=show_images,
                         browser_type=browser_type,
                         variant=variant,              # NEW
                         ab_test_enabled=AB_TEST_ENABLED)  # NEW


# === ROUTE 2: StackFree Landing Page ===
@app.route('/stackfree')
def stackfree_landing():
    """
    StackFree landing page with A/B testing support (identical logic to main landing page)

    URL Parameters:
        kw (str): Keyword for image search (default: 'trending')
        img (str): 'true' to show images (default: false)
        gclid (str): Google Click ID for conversion attribution
        variant (str): A/B test variant ('a' or 'b')
    """
    # Extract and sanitize parameters
    keyword = request.args.get('kw', 'trending').strip()
    show_images = request.args.get('img', '').lower() == 'true'
    gclid = request.args.get('gclid', '')
    variant = request.args.get('variant', 'a').lower()  # NEW: Get variant from URL

    # Sanitize keyword (max 100 chars)
    if not keyword or len(keyword) > 100:
        keyword = 'trending'

    # NEW: Validate variant
    if variant not in ['a', 'b']:
        variant = 'a'

    # NEW: If A/B test disabled, force variant A
    if not AB_TEST_ENABLED:
        variant = 'a'

    # Conditional image display logic
    # Only show images if BOTH img=true AND kw parameter exist
    has_kw_param = request.args.get('kw') is not None
    show_images = show_images and has_kw_param

    # Browser detection from User-Agent
    user_agent = request.headers.get('User-Agent', 'Unknown')
    browser_type = detect_browser_type(user_agent)

    # Get client IP (respects proxy headers)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    # NEW: Log stackfree page visit with variant
    logger.info(
        f'STACKFREE_PAGE keyword="{keyword}" gclid="{gclid}" variant="{variant}" '
        f'show_images={show_images} has_kw_param={has_kw_param} '
        f'browser="{browser_type}" user_agent="{user_agent[:100]}" ip="{client_ip}"'
    )

    # NEW: Select template based on variant
    template_name = f'index_variant_{variant}.html'

    # Render template with NO server-side image fetching
    # Images will load via JavaScript AJAX after page renders
    return render_template(template_name,
                         keyword=keyword,
                         gclid=gclid,
                         show_images=show_images,
                         browser_type=browser_type,
                         variant=variant,              # NEW
                         ab_test_enabled=AB_TEST_ENABLED)  # NEW


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
    Track CTA button clicks with attribution data and A/B test variant

    Request Body (JSON):
        button_id (str): Button identifier
        keyword (str): Current keyword
        gclid (str): Google Click ID
        variant (str): A/B test variant
        timestamp (str): ISO timestamp

    Returns:
        JSON with success status
    """
    data = request.get_json() or {}

    button_id = data.get('button_id', 'unknown')
    keyword = data.get('keyword', 'unknown')
    gclid = data.get('gclid', '')
    variant = data.get('variant', '')  # NEW: Add variant

    user_agent = request.headers.get('User-Agent', 'Unknown')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    referer = request.headers.get('Referer', '')

    # NEW: Log click event with variant
    logger.info(
        f'CTA_CLICK button="{button_id}" keyword="{keyword}" '
        f'gclid="{gclid}" variant="{variant}" '
        f'user_agent="{user_agent[:100]}" ip="{client_ip}" referer="{referer}" '
        f'conversion_tracking={bool(gclid)}'
    )

    return jsonify({
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    })


# === ROUTE 6: Exit Popup Tracking ===
@app.route('/api/track/exit-popup', methods=['POST'])
def track_exit_popup():
    """
    Track exit popup events with A/B test variant

    Request Body (JSON):
        event (str): Event type (exit_popup_shown, exit_popup_dismissed, exit_popup_cta_clicked)
        keyword (str): Current keyword
        gclid (str): Google Click ID
        variant (str): A/B test variant
        timestamp (str): ISO timestamp

    Returns:
        JSON with success status
    """
    data = request.get_json() or {}

    event = data.get('event', 'unknown')
    keyword = data.get('keyword', 'unknown')
    gclid = data.get('gclid', '')
    variant = data.get('variant', '')  # NEW: Add variant
    timestamp = data.get('timestamp', '')

    user_agent = request.headers.get('User-Agent', 'Unknown')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    referer = request.headers.get('Referer', '')

    # NEW: Log exit popup event with variant
    logger.info(
        f'EXIT_POPUP_EVENT event="{event}" keyword="{keyword}" '
        f'gclid="{gclid}" variant="{variant}" '
        f'user_agent="{user_agent[:100]}" ip="{client_ip}" referer="{referer}" '
        f'conversion_tracking={bool(gclid)}'
    )

    return jsonify({'status': 'success', 'event': event, 'timestamp': timestamp})


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


# === ROUTE 7B: Thank You Page (TEST VERSION - NO REDIRECT) ===
@app.route('/thankyou-test')
def thankyou_test():
    """
    TEST VERSION of thank you page - NO YouTube redirect
    Use this to verify conversion tracking in DevTools

    URL Parameters:
        source (str): Source identifier (e.g., 'novaview')
        gclid (str): Google Click ID for conversion attribution

    Returns:
        HTML thank you page WITHOUT YouTube redirect
    """
    source = request.args.get('source', 'novaview')
    gclid = request.args.get('gclid', '')

    logger.info(
        f'THANKYOU_TEST_PAGE source="{source}" gclid="{gclid}" '
        f'ip="{request.remote_addr}" '
        f'user_agent="{request.headers.get("User-Agent", "Unknown")[:100]}"'
    )

    return render_template('thankyou-test.html', gclid=gclid, source=source)


# === ROUTE 8: Post-Install Redirect (Production) ===
@app.route('/post_install/')
def post_install():
    """
    Post-install redirect for production deployment with A/B test support
    Redirects to the main eguidesearches.com thank you page

    URL Parameters:
        gclid (str): Google Click ID for conversion attribution
        variant (str): A/B test variant

    Returns:
        Redirect to production thank you page
    """
    gclid = request.args.get('gclid', '')
    variant = request.args.get('variant', '')  # NEW: Get variant from URL

    # NEW: Log conversion with variant
    user_agent = request.headers.get('User-Agent', 'Unknown')[:100]
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    logger.info(
        f'CONVERSION gclid="{gclid}" variant="{variant}" '
        f'user_agent="{user_agent}" ip="{client_ip}"'
    )

    # Build redirect URL with gclid and variant if present
    thank_you_url = 'https://www.eguidesearches.com/thankyou-downloadmanager.html?source=novaview'
    if gclid:
        thank_you_url += f'&gclid={gclid}'
    if variant:
        thank_you_url += f'&variant={variant}'

    return redirect(thank_you_url)


# === ROUTE 9: A/B Test Dashboard ===
@app.route('/admin/ab-results')
def ab_dashboard():
    """A/B test results dashboard with statistical significance"""
    from ab_testing.ab_log_parser import ABLogParser
    from ab_testing.test_history import TestHistoryManager

    parser = ABLogParser()
    history_manager = TestHistoryManager()

    try:
        # Read last 5000 lines from log file for analysis
        log_lines = []
        log_file = os.path.join(_current_dir, 'app.log')  # Use absolute path

        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                # Read all lines and get last 5000
                all_lines = f.readlines()
                log_lines = all_lines[-5000:] if len(all_lines) > 5000 else all_lines

        metrics = parser.parse_logs(log_lines)
        results = parser.calculate_statistical_significance()
        winner, _ = parser.get_winner(min_impressions=50)

        # Get test history
        history = history_manager.get_history()

    except Exception as e:
        logger.error(f"Error reading logs for dashboard: {e}")
        # Return empty results on error
        results = {
            'a': {'impressions': 0, 'conversions': 0, 'clicks': 0,
                  'exit_popup_shows': 0, 'conversion_rate': 0.0, 'click_rate': 0.0,
                  'confidence_interval': (0, 0), 'margin_of_error': 0, 'confidence_pct': 0},
            'b': {'impressions': 0, 'conversions': 0, 'clicks': 0,
                  'exit_popup_shows': 0, 'conversion_rate': 0.0, 'click_rate': 0.0,
                  'confidence_interval': (0, 0), 'margin_of_error': 0, 'confidence_pct': 0},
            'p_value': 1.0,
            'is_significant': False
        }
        winner = 'error'
        history = []

    return render_template('ab_dashboard.html',
                         variant_a=results.get('a', {}),
                         variant_b=results.get('b', {}),
                         winner=winner,
                         test_enabled=AB_TEST_ENABLED,
                         test_name=AB_TEST_NAME,
                         p_value=results.get('p_value', 1.0),
                         is_significant=results.get('is_significant', False),
                         history=history)


@app.route('/admin/api/reset-test', methods=['POST'])
def reset_test():
    """Reset A/B test and archive results"""
    from ab_testing.ab_log_parser import ABLogParser
    from ab_testing.test_history import TestHistoryManager

    try:
        data = request.get_json()
        test_name = data.get('test_name', 'Unnamed Test')

        # Get current metrics before reset
        parser = ABLogParser()
        log_file = os.path.join(_current_dir, 'app.log')

        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()

            metrics = parser.parse_logs(log_lines)
            results = parser.calculate_statistical_significance()

            # Archive test results
            history_manager = TestHistoryManager()
            test_entry = {
                'name': test_name,
                'variant_a': results.get('a', {}),
                'variant_b': results.get('b', {}),
                'p_value': results.get('p_value', 1.0),
                'is_significant': results.get('is_significant', False)
            }
            history_manager.save_test_result(test_name, test_entry)

            # Clear the log file
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('')

            logger.info(f'A/B test "{test_name}" completed and archived')

            return jsonify({
                'success': True,
                'message': f'Test "{test_name}" archived successfully',
                'archived_results': test_entry
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No test data to archive'
            }), 400

    except Exception as e:
        logger.error(f"Error resetting test: {e}")
        return jsonify({
            'success': False,
            'message': f'Error resetting test: {str(e)}'
        }), 500


@app.route('/admin/api/test-history', methods=['GET'])
def get_test_history():
    """Get A/B test history"""
    from ab_testing.test_history import TestHistoryManager

    try:
        history_manager = TestHistoryManager()
        history = history_manager.get_history()
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f"Error retrieving test history: {e}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving history: {str(e)}'
        }), 500


@app.route('/admin/api/delete-test-history', methods=['POST'])
def delete_test_history():
    """Delete a test record from history"""
    from ab_testing.test_history import TestHistoryManager

    try:
        data = request.get_json()
        index = data.get('index', -1)

        if index < 0:
            return jsonify({'success': False, 'message': 'Invalid index'}), 400

        history_manager = TestHistoryManager()
        history = history_manager.get_history()

        if index >= len(history):
            return jsonify({'success': False, 'message': 'Index out of range'}), 400

        # Remove the item at the specified index
        deleted_item = history.pop(index)
        history_manager._save_history(history)

        logger.info(f'Deleted test history item: {deleted_item.get("name", "Unknown")}')

        return jsonify({
            'success': True,
            'message': 'Test record deleted successfully',
            'deleted_item': deleted_item
        })
    except Exception as e:
        logger.error(f"Error deleting test history: {e}")
        return jsonify({
            'success': False,
            'message': f'Error deleting test: {str(e)}'
        }), 500


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
