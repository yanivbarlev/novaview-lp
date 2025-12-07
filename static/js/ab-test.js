/**
 * A/B Test Variant Assignment
 * Assigns user to variant A or B on first visit within session
 * Stores assignment in sessionStorage for session persistence
 */

(function() {
    const STORAGE_KEY = 'ab_variant';
    const SPLIT_RATIO = 0.5;  // 50-50 split

    function getOrAssignVariant() {
        // Check for existing assignment in sessionStorage
        let variant = sessionStorage.getItem(STORAGE_KEY);

        if (!variant) {
            // New visitor within session - assign random variant
            variant = Math.random() < SPLIT_RATIO ? 'a' : 'b';
            sessionStorage.setItem(STORAGE_KEY, variant);
        }

        return variant;
    }

    function addVariantToUrl() {
        const variant = getOrAssignVariant();
        const urlParams = new URLSearchParams(window.location.search);

        // Only add if not already present
        if (!urlParams.has('variant')) {
            urlParams.set('variant', variant);

            // Reload with variant parameter (use replace to avoid back button issues)
            const newUrl = window.location.pathname + '?' + urlParams.toString();
            window.location.replace(newUrl);
        }

        // Store in localStorage for post_install tracking
        localStorage.setItem('ab_variant', variant);
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addVariantToUrl);
    } else {
        addVariantToUrl();
    }

    // Make variant available globally
    window.abVariant = getOrAssignVariant();
})();
