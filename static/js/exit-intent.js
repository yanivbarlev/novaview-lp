/**
 * Exit Intent Popup System
 * Monitors Chrome Web Store tab behavior and triggers exit popup
 */

class ExitIntentPopup {
    constructor() {
        this.isActive = false;
        this.chromeStoreTabRef = null;
        this.checkInterval = null;
        this.hasShownPopup = false;
        this.sessionKey = 'exitPopupShown_' + new Date().toDateString();

        // Bind methods to maintain context
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.handleWindowFocus = this.handleWindowFocus.bind(this);
        this.checkTabStatus = this.checkTabStatus.bind(this);

        this.init();
    }

    init() {
        // Check if popup was already shown today
        if (sessionStorage.getItem(this.sessionKey)) {
            this.hasShownPopup = true;
            return;
        }

        // Listen for window focus events
        window.addEventListener('focus', this.handleWindowFocus);
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
    }

    startMonitoring(chromeStoreTabRef) {
        if (!chromeStoreTabRef || this.hasShownPopup) {
            console.log('Exit intent monitoring skipped - tab ref invalid or popup already shown');
            return;
        }

        this.isActive = true;
        this.chromeStoreTabRef = chromeStoreTabRef;

        console.log('Exit intent monitoring started for Chrome Web Store tab');

        // Start periodic checking of tab status
        this.checkInterval = setInterval(this.checkTabStatus, 1000);

        // Set timeout to stop monitoring after 5 minutes
        setTimeout(() => {
            this.stopMonitoring();
        }, 300000); // 5 minutes
    }

    checkTabStatus() {
        if (!this.chromeStoreTabRef || !this.isActive) {
            return;
        }

        try {
            // Check if tab is closed
            if (this.chromeStoreTabRef.closed) {
                console.log('Chrome Web Store tab was closed - showing exit intent popup');
                this.showExitPopup();
                this.stopMonitoring();
                return;
            }

            // Try to check if user navigated away from Chrome Web Store
            // This is limited due to cross-origin restrictions, but we can detect some cases
            try {
                if (this.chromeStoreTabRef.location &&
                    !this.chromeStoreTabRef.location.href.includes('chrome.google.com/webstore')) {
                    console.log('User navigated away from Chrome Web Store');
                    this.showExitPopup();
                    this.stopMonitoring();
                }
            } catch (e) {
                // Cross-origin access blocked - this is normal
            }
        } catch (error) {
            console.log('Error checking tab status:', error);
        }
    }

    handleWindowFocus() {
        // When user returns to our page, check if they came back without installing
        if (this.isActive && this.chromeStoreTabRef && !this.hasShownPopup) {
            // Small delay to let any installation messages process
            setTimeout(() => {
                // Check if extension was installed by looking for specific indicators
                // Since we can't directly detect extension installation, we'll show popup
                // after user returns from Chrome Web Store
                if (document.hasFocus() && this.isActive) {
                    console.log('User returned to landing page - showing exit intent popup');
                    this.showExitPopup();
                    this.stopMonitoring();
                }
            }, 500);
        }
    }

    handleVisibilityChange() {
        if (document.visibilityState === 'visible' && this.isActive && !this.hasShownPopup) {
            // User returned to our page
            setTimeout(() => {
                if (document.visibilityState === 'visible' && this.isActive) {
                    this.handleWindowFocus();
                }
            }, 300);
        }
    }

    showExitPopup() {
        if (this.hasShownPopup) {
            return;
        }

        console.log('Showing exit intent popup');

        const popup = document.getElementById('exit-intent-modal');
        if (popup) {
            popup.classList.add('show');
            this.hasShownPopup = true;

            // Store in session storage to prevent showing again
            sessionStorage.setItem(this.sessionKey, 'true');

            // Track popup impression
            this.trackEvent('exit_popup_shown');
        }
    }

    closePopup() {
        const popup = document.getElementById('exit-intent-modal');
        if (popup) {
            popup.classList.remove('show');
            this.trackEvent('exit_popup_dismissed');
        }
        this.stopMonitoring();
    }

    handlePopupCTA() {
        // Track CTA click from popup
        this.trackEvent('exit_popup_cta_clicked');

        // Get stored gclid and variant for tracking
        const gclid = localStorage.getItem('gclid') || '';
        const variant = window.abTestVariant || '';

        // Build Chrome Web Store URL with tracking parameters
        let storeUrl = window.chromeStoreUrl;
        if (gclid && variant) {
            storeUrl += `?gclid=${gclid}&variant=${variant}`;
        } else if (gclid) {
            storeUrl += `?gclid=${gclid}`;
        } else if (variant) {
            storeUrl += `?variant=${variant}`;
        }

        // Close popup and open Chrome Web Store
        this.closePopup();
        window.open(storeUrl, '_blank');
    }

    stopMonitoring() {
        this.isActive = false;
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
        console.log('Exit intent monitoring stopped');
    }

    trackEvent(eventName, additionalData = {}) {
        try {
            // Track with your existing analytics
            const gclid = localStorage.getItem('gclid') || '';
            const keyword = new URLSearchParams(window.location.search).get('kw') || 'trending';
            const variant = window.abTestVariant || '';  // NEW: Get variant

            fetch('/api/track/exit-popup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event: eventName,
                    keyword: keyword,
                    gclid: gclid,
                    variant: variant,  // NEW: Add variant
                    timestamp: new Date().toISOString(),
                    ...additionalData
                })
            }).catch(err => console.error('Exit popup tracking failed:', err));
        } catch (error) {
            console.error('Error tracking exit intent event:', error);
        }
    }

    // Public methods for popup controls
    static closePopup() {
        if (window.exitIntentPopup) {
            window.exitIntentPopup.closePopup();
        }
    }

    static handleCTA() {
        if (window.exitIntentPopup) {
            window.exitIntentPopup.handlePopupCTA();
        }
    }
}

// Initialize exit intent popup system when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.exitIntentPopup = new ExitIntentPopup();
});

// Global functions for popup interaction
window.closeExitPopup = ExitIntentPopup.closePopup;
window.handleExitPopupCTA = ExitIntentPopup.handleCTA;