"""
Image Search Service for New Landing Page System
Contains all image downloading, caching, selection, and compression logic
"""

import os
import shutil
import time
import logging
from io import BytesIO
from typing import List, Tuple, Dict, Optional
import requests
import imagehash
from PIL import Image

from config import (
    GOOGLE_API_KEY,
    GOOGLE_CX,
    GOOGLE_API_KEY_BACKUP,
    GOOGLE_CX_BACKUP,
    FINAL_IMAGES_DIR,
    CANDIDATES_CACHE_DIR,
    TARGET_FILE_SIZE,
    THUMBNAIL_SIZE,
    SUPPORTED_EXTENSIONS
)
from utils import (
    sanitize_keyword_for_filename,
    is_file_an_image,
    resolve_actual_saved_path
)

# Setup logging
logger = logging.getLogger(__name__)


def check_all_images_cached(keyword_base: str, count: int = 3) -> bool:
    """
    Check if all final images exist for a keyword

    Args:
        keyword_base: Sanitized keyword
        count: Number of images required

    Returns:
        True if all images exist and are valid, False otherwise
    """
    for i in range(1, count + 1):
        base_path = os.path.join(FINAL_IMAGES_DIR, f"{keyword_base}_{i}")
        actual_path = resolve_actual_saved_path(base_path)
        if not actual_path or not is_file_an_image(actual_path):
            return False
    return True


def get_candidates_dir(keyword_base: str) -> str:
    """
    Get candidate cache directory for keyword

    Args:
        keyword_base: Sanitized keyword

    Returns:
        Path to candidates cache directory
    """
    return os.path.join(CANDIDATES_CACHE_DIR, keyword_base)


def list_valid_cached_candidates(keyword_base: str) -> List[Tuple[str, int]]:
    """
    List all valid candidate images with their file sizes

    Args:
        keyword_base: Sanitized keyword

    Returns:
        List of tuples (file_path, file_size)
    """
    candidates_dir = get_candidates_dir(keyword_base)
    if not os.path.isdir(candidates_dir):
        return []

    valid = []
    try:
        for name in os.listdir(candidates_dir):
            path = os.path.join(candidates_dir, name)
            if not os.path.isfile(path):
                continue
            _, ext = os.path.splitext(path)
            if ext.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if is_file_an_image(path):
                try:
                    size = os.path.getsize(path)
                except OSError:
                    size = 0
                valid.append((path, size))
    except FileNotFoundError:
        return []
    return valid


def delete_candidates_cache(keyword_base: str) -> None:
    """
    Delete candidate cache directory for keyword

    Args:
        keyword_base: Sanitized keyword
    """
    candidates_dir = get_candidates_dir(keyword_base)
    try:
        if os.path.isdir(candidates_dir):
            # Count files before deletion for logging
            files_count = len([f for f in os.listdir(candidates_dir)
                             if os.path.isfile(os.path.join(candidates_dir, f))])
            shutil.rmtree(candidates_dir, ignore_errors=True)
            logger.info(f'CACHE_CLEANUP keyword_base="{keyword_base}" '
                       f'candidates_deleted={files_count} action="delete_candidates"')
    except Exception as e:
        logger.warning(f'CACHE_CLEANUP_ERROR keyword_base="{keyword_base}" error="{str(e)}"')


def compute_image_hash(image_path: str) -> Optional[str]:
    """
    Compute perceptual hash for image similarity detection

    Uses dhash (difference hash) for good similarity detection

    Args:
        image_path: Path to image file

    Returns:
        ImageHash object or None if computation fails
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed for consistent hashing
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Use dhash (difference hash) for good similarity detection
            return imagehash.dhash(img)
    except Exception as e:
        logger.warning(f"Failed to compute hash for {image_path}: {e}")
        return None


def select_diverse_images(candidates: List[Tuple[str, int]], count: int = 3,
                          similarity_threshold: int = 10) -> List[str]:
    """
    Select diverse images from candidates using perceptual hashing

    Groups similar images together and selects the largest (best quality)
    image from each group to ensure visual diversity.

    Args:
        candidates: List of tuples (file_path, file_size)
        count: Number of images to select
        similarity_threshold: Hash distance threshold for similarity (default: 10)

    Returns:
        List of selected image paths
    """
    if len(candidates) <= count:
        return [path for path, _ in candidates]

    # Compute hashes for all candidates
    candidates_with_hash = []
    for path, size in candidates:
        img_hash = compute_image_hash(path)
        if img_hash is not None:
            candidates_with_hash.append((path, size, img_hash))

    if len(candidates_with_hash) <= count:
        return [path for path, _, _ in candidates_with_hash]

    # Group similar images
    groups = []

    for path, size, img_hash in candidates_with_hash:
        # Find if this image is similar to any existing group
        added_to_group = False
        for group in groups:
            # Check similarity with first image in group (group representative)
            group_hash = group[0][2]
            if abs(img_hash - group_hash) <= similarity_threshold:
                group.append((path, size, img_hash))
                added_to_group = True
                break

        # If not similar to any group, create new group
        if not added_to_group:
            groups.append([(path, size, img_hash)])

    # Sort groups by the size of their largest image (descending)
    groups.sort(key=lambda g: max(item[1] for item in g), reverse=True)

    # Select one image from each group, prioritizing larger images within groups
    selected = []
    for group in groups:
        if len(selected) >= count:
            break
        # Sort group by size (descending) and take the largest
        group.sort(key=lambda item: item[1], reverse=True)
        selected.append(group[0][0])  # Take the path of the largest image

    # If we still need more images, take from remaining groups
    if len(selected) < count:
        remaining_candidates = []
        for group in groups[len(selected):]:
            remaining_candidates.extend(group)

        # Sort remaining by size and take what we need
        remaining_candidates.sort(key=lambda item: item[1], reverse=True)
        for path, _, _ in remaining_candidates:
            if len(selected) >= count:
                break
            selected.append(path)

    logger.info(f"Selected {len(selected)} diverse images from {len(groups)} similarity groups")
    return selected[:count]


def compress_image_to_target(image: Image.Image, target_bytes: int = TARGET_FILE_SIZE) -> Tuple[bytes, str]:
    """
    Compress image to target size using binary search

    Tries JPEG and WebP formats to find the best compression while
    maintaining quality. Uses binary search for optimal quality setting.

    Args:
        image: PIL Image object
        target_bytes: Target file size in bytes

    Returns:
        Tuple of (compressed_data, extension)
    """
    # Try different formats and qualities
    best_result = None
    best_size = float('inf')

    # Convert image for compression
    if image.mode in ('RGBA', 'LA'):
        # Create white background for transparency
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    elif image.mode == 'P':
        image = image.convert('RGB')

    # Binary search for optimal JPEG quality
    low, high = 30, 95
    while low <= high:
        quality = (low + high) // 2
        buf = BytesIO()
        try:
            image.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
            size = buf.tell()

            if size <= target_bytes:
                best_result = (buf.getvalue(), '.jpg')
                best_size = size
                low = quality + 1
            else:
                high = quality - 1
        except Exception:
            break

    # Try WebP if JPEG didn't work well
    try:
        for quality in [80, 70, 60, 50]:
            buf = BytesIO()
            image.save(buf, format='WEBP', quality=quality, method=6)
            size = buf.tell()
            if size <= target_bytes and size < best_size:
                best_result = (buf.getvalue(), '.webp')
                best_size = size
                break
    except Exception:
        pass

    if best_result:
        return best_result

    # Fallback: save as JPEG with quality 75
    buf = BytesIO()
    image.save(buf, format='JPEG', quality=75, optimize=True)
    return buf.getvalue(), '.jpg'


def promote_candidates_to_outputs(keyword_base: str, selected_paths: List[str]) -> List[str]:
    """
    Promote selected candidates to final output locations

    Resizes, compresses, and saves images to final cache locations.

    Args:
        keyword_base: Sanitized keyword
        selected_paths: List of candidate image paths

    Returns:
        List of successfully saved file paths
    """
    saved_files = []

    for idx, src_path in enumerate(selected_paths, start=1):
        try:
            # Load and resize image
            with Image.open(src_path) as img:
                # Resize to target dimensions maintaining aspect ratio
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                # Create final image with exact dimensions (center if needed)
                final_img = Image.new('RGB', THUMBNAIL_SIZE, (255, 255, 255))
                x = (THUMBNAIL_SIZE[0] - img.width) // 2
                y = (THUMBNAIL_SIZE[1] - img.height) // 2
                if img.mode == 'RGBA':
                    final_img.paste(img, (x, y), img)
                else:
                    final_img.paste(img, (x, y))

                # Compress to target size
                compressed_data, ext = compress_image_to_target(final_img)

                # Save to final location
                base_path = os.path.join(FINAL_IMAGES_DIR, f"{keyword_base}_{idx}")

                # Remove any existing files with different extensions
                for old_ext in SUPPORTED_EXTENSIONS:
                    old_path = base_path + old_ext
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception:
                            pass

                final_path = base_path + ext
                with open(final_path, 'wb') as f:
                    f.write(compressed_data)

                if is_file_an_image(final_path):
                    saved_files.append(final_path)
                    size_kb = len(compressed_data) // 1024
                    logger.info(f"Saved optimized image: {os.path.basename(final_path)} (~{size_kb}KB)")

        except Exception as e:
            logger.error(f"Error processing candidate {src_path}: {e}")
            continue

    return saved_files


class ImageSearchService:
    """
    Main service for image search, caching, and optimization

    Implements three-phase intelligent caching:
    1. Check final images cache (100-day TTL)
    2. Reuse candidates cache (if available)
    3. Download new candidates from Google API
    """

    def __init__(self):
        """Initialize service with headers for API requests"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

    def search_images(self, keyword: str, count: int = 3) -> List[Dict]:
        """
        Enhanced image search with candidate selection

        Args:
            keyword: Search keyword
            count: Number of images to return (default: 3)

        Returns:
            List of image dictionaries with url, thumbnail, title, source
        """
        keyword_base = sanitize_keyword_for_filename(keyword)

        # Phase 1: Check if all final images already exist (works without API credentials)
        if check_all_images_cached(keyword_base, count):
            logger.info(f"Cache hit: All images exist for '{keyword}'")
            return self._get_final_images(keyword_base, count)

        # Only check API credentials if we need to fetch new images
        if not GOOGLE_API_KEY or not GOOGLE_CX:
            logger.error("Google API credentials not configured - cannot fetch new images")
            return []

        # Phase 2: Try to reuse existing candidates
        existing_candidates = list_valid_cached_candidates(keyword_base)
        if len(existing_candidates) >= count:
            logger.info(f"Candidate reuse: Found {len(existing_candidates)} candidates for '{keyword}'")
            # Select diverse images from existing candidates
            selected_paths = select_diverse_images(existing_candidates, count)

            # Promote to final outputs
            saved_files = promote_candidates_to_outputs(keyword_base, selected_paths)
            if len(saved_files) == count:
                # Clean up candidates after successful promotion
                delete_candidates_cache(keyword_base)
                return self._get_final_images(keyword_base, count)

        # Phase 3: Download new candidates from API
        logger.info(f"API call needed for '{keyword}' - downloading candidates")
        return self._download_and_select_candidates(keyword, keyword_base, count)

    def _get_final_images(self, keyword_base: str, count: int) -> List[Dict]:
        """
        Get final images for display

        Args:
            keyword_base: Sanitized keyword
            count: Number of images to get

        Returns:
            List of image dictionaries
        """
        images = []
        for i in range(1, count + 1):
            base_path = os.path.join(FINAL_IMAGES_DIR, f"{keyword_base}_{i}")
            actual_path = resolve_actual_saved_path(base_path)
            if actual_path:
                filename = os.path.basename(actual_path)
                images.append({
                    'url': f'/image/{filename}',
                    'thumbnail': f'/image/{filename}',
                    'title': f'Image {i}',
                    'source': 'Cached'
                })
        return images

    def _download_and_select_candidates(self, keyword: str, keyword_base: str, count: int) -> List[Dict]:
        """
        Download candidates and select best ones

        Args:
            keyword: Original search keyword
            keyword_base: Sanitized keyword
            count: Number of images needed

        Returns:
            List of image dictionaries
        """
        try:
            # Request 10 images for selection (always request more than needed)
            request_num = max(count, 10)

            # Try primary API first, then fallback to backup if rate limited
            urls = []
            api_used = 'primary'

            # Primary API attempt
            params_primary = {
                'key': GOOGLE_API_KEY,
                'cx': GOOGLE_CX,
                'q': keyword,
                'searchType': 'image',
                'num': request_num,
                'safe': 'active'
            }

            api_start_time = time.time()
            try:
                response = requests.get('https://www.googleapis.com/customsearch/v1',
                                       params=params_primary, timeout=20)
                api_response_time = round(time.time() - api_start_time, 3)
                response.raise_for_status()

                data = response.json()
                urls = [item.get('link') for item in data.get('items', []) if item.get('link')]

                # Log successful primary API call
                logger.info(f'GOOGLE_API_CALL keyword="{keyword}" requested={request_num} '
                           f'urls_received={len(urls)} response_time={api_response_time}s '
                           f'quota_usage=1 status_code={response.status_code} api=primary')

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limit hit on primary - try backup
                    logger.warning(f'PRIMARY_API_RATE_LIMIT keyword="{keyword}" - trying backup API')

                    if GOOGLE_API_KEY_BACKUP and GOOGLE_CX_BACKUP:
                        params_backup = {
                            'key': GOOGLE_API_KEY_BACKUP,
                            'cx': GOOGLE_CX_BACKUP,
                            'q': keyword,
                            'searchType': 'image',
                            'num': request_num,
                            'safe': 'active'
                        }

                        backup_start_time = time.time()
                        response = requests.get('https://www.googleapis.com/customsearch/v1',
                                               params=params_backup, timeout=20)
                        api_response_time = round(time.time() - backup_start_time, 3)
                        response.raise_for_status()

                        data = response.json()
                        urls = [item.get('link') for item in data.get('items', []) if item.get('link')]
                        api_used = 'backup'

                        # Log successful backup API call
                        logger.info(f'GOOGLE_API_CALL keyword="{keyword}" requested={request_num} '
                                   f'urls_received={len(urls)} response_time={api_response_time}s '
                                   f'quota_usage=1 status_code={response.status_code} api=backup')
                    else:
                        logger.error(f'BACKUP_API_NOT_CONFIGURED keyword="{keyword}"')
                        raise
                else:
                    raise

            if not urls:
                logger.warning(f'GOOGLE_API_NO_RESULTS keyword="{keyword}" requested={request_num}')
                return []

            # Download all candidates
            candidates_dir = get_candidates_dir(keyword_base)
            os.makedirs(candidates_dir, exist_ok=True)

            downloaded_candidates = []
            for idx, url in enumerate(urls, start=1):
                try:
                    candidate_path = os.path.join(candidates_dir, f"candidate_{idx}")
                    downloaded_path = self._download_candidate(url, candidate_path)
                    if downloaded_path and is_file_an_image(downloaded_path):
                        size = os.path.getsize(downloaded_path)
                        downloaded_candidates.append((downloaded_path, size))
                except Exception as e:
                    logger.warning(f"Failed to download candidate {idx}: {e}")
                    continue

            # Combine with any existing candidates
            existing_candidates = list_valid_cached_candidates(keyword_base)
            all_candidates = existing_candidates + downloaded_candidates

            # Log candidate processing metrics
            logger.info(f'CANDIDATE_PROCESSING keyword="{keyword}" '
                       f'downloaded_new={len(downloaded_candidates)} '
                       f'existing_candidates={len(existing_candidates)} '
                       f'total_candidates={len(all_candidates)} '
                       f'download_failures={len(urls) - len(downloaded_candidates)}')

            if len(all_candidates) < count:
                logger.error(f'INSUFFICIENT_CANDIDATES keyword="{keyword}" '
                            f'available={len(all_candidates)} required={count}')
                return []

            # Select diverse images using perceptual hashing to avoid duplicates
            selection_start = time.time()
            selected_paths = select_diverse_images(all_candidates, count)
            selection_time = round(time.time() - selection_start, 3)

            # Promote selected candidates to final outputs
            compression_start = time.time()
            saved_files = promote_candidates_to_outputs(keyword_base, selected_paths)
            compression_time = round(time.time() - compression_start, 3)

            # Log image processing metrics
            logger.info(f'IMAGE_PROCESSING keyword="{keyword}" '
                       f'selection_time={selection_time}s '
                       f'compression_time={compression_time}s '
                       f'final_images={len(saved_files)}')

            if len(saved_files) < count:
                logger.error(f"Failed to save enough images: got {len(saved_files)}, needed {count}")
                return []

            # Clean up candidates cache
            delete_candidates_cache(keyword_base)

            logger.info(f"Successfully selected {len(saved_files)} images from {len(all_candidates)} candidates")
            return self._get_final_images(keyword_base, count)

        except Exception as e:
            logger.error(f"Error in candidate download/selection for '{keyword}': {str(e)}")
            return []

    def _download_candidate(self, url: str, destination_path: str) -> Optional[str]:
        """
        Download a single candidate image

        Args:
            url: Image URL
            destination_path: Base path without extension

        Returns:
            Full path with extension if successful, None otherwise
        """
        try:
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if not content_type.startswith('image/'):
                return None

            # Determine file extension
            ext = '.jpg'  # Default
            if 'jpeg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            elif 'gif' in content_type:
                ext = '.gif'

            final_path = destination_path + ext

            # Download and save
            with open(final_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return final_path if is_file_an_image(final_path) else None

        except Exception as e:
            logger.warning(f"Download failed for {url}: {e}")
            return None
