/**
 * A/B Test Variant Assignment
 * DISABLED - A/B test is off, all users get variant A
 * This script is kept for potential future use
 */

(function() {
    // A/B testing is disabled - no client-side assignment or redirection
    // The server always assigns variant 'a' when AB_TEST_ENABLED = False

    // Make variant 'a' available globally for any scripts that reference it
    window.abVariant = 'a';

    // Store in localStorage for consistency (though server controls assignment)
    localStorage.setItem('ab_variant', 'a');
    sessionStorage.setItem('ab_variant', 'a');
})();
