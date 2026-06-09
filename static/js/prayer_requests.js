// ============================================
// PRAYER REQUESTS - ANIMATED DESCRIPTIONS
// ============================================

class PrayerCardAnimator {
    constructor() {
        this.currentIndexes = {};
        this.intervals = {};
        this.isTransitioning = false;
    }

    /**
     * Initialize prayer cards and start animations
     */
    initializePrayerCards() {
        const prayerCards = document.querySelectorAll('.prayer-card');

        if (prayerCards.length === 0) {
            console.warn('No prayer cards found');
            return;
        }

        prayerCards.forEach((card, cardIndex) => {
            const descriptions = card.querySelectorAll('.prayer-description-item');

            // Store current index for this card
            this.currentIndexes[cardIndex] = 0;

            // Set initial active state
            this.setActiveDescription(card, 0);

            // Calculate interval based on description count (varies animation speed)
            const interval = 4000 + (descriptions.length * 300); // 4-6 seconds per rotation
            
            // Start the animation loop
            this.startCardAnimation(cardIndex, card, interval);
        });

        // Re-initialize on window resize (for responsive changes)
        window.addEventListener('resize', () => {
            this.resetAllAnimations();
        });
    }

    /**
     * Set the active description and handle transitions
     */
    setActiveDescription(card, index) {
        const descriptions = card.querySelectorAll('.prayer-description-item');
        
        if (descriptions.length === 0) return;

        descriptions.forEach((desc, i) => {
            if (i === index) {
                desc.classList.remove('exiting');
                desc.classList.add('active');
            } else {
                desc.classList.remove('active');
                desc.classList.add('exiting');
            }
        });
    }

    /**
     * Start animation loop for a specific card
     */
    startCardAnimation(cardIndex, card, interval) {
        // Clear any existing interval
        if (this.intervals[cardIndex]) {
            clearInterval(this.intervals[cardIndex]);
        }

        this.intervals[cardIndex] = setInterval(() => {
            const descriptions = card.querySelectorAll('.prayer-description-item');
            const totalDescriptions = descriptions.length;

            // Increment index and wrap around
            this.currentIndexes[cardIndex] = 
                (this.currentIndexes[cardIndex] + 1) % totalDescriptions;

            // Animate to next description
            this.setActiveDescription(card, this.currentIndexes[cardIndex]);
        }, interval);
    }

    /**
     * Reset all animations (useful for responsive changes)
     */
    resetAllAnimations() {
        // Clear all intervals
        Object.values(this.intervals).forEach(interval => {
            clearInterval(interval);
        });

        this.intervals = {};
        this.currentIndexes = {};

        // Reinitialize
        setTimeout(() => this.initializePrayerCards(), 100);
    }

    /**
     * Pause animations (optional)
     */
    pauseAnimations() {
        Object.values(this.intervals).forEach(interval => {
            clearInterval(interval);
        });
    }

    /**
     * Resume animations (optional)
     */
    resumeAnimations() {
        this.resetAllAnimations();
    }
}

// ============================================
// PRAYER PAGE INITIALIZATION
// ============================================

let prayerAnimator;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize prayer card animations
    prayerAnimator = new PrayerCardAnimator();
    prayerAnimator.initializePrayerCards();

    // Optional: Pause animations when user tabs away
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            prayerAnimator.pauseAnimations();
        } else {
            prayerAnimator.resumeAnimations();
        }
    });

    // Smooth scroll to prayer section
    const prayerSection = document.querySelector('.prayer-requests-section');
    if (prayerSection && prayerSection.dataset.scrollTo === 'true') {
        prayerSection.scrollIntoView({ behavior: 'smooth' });
    }

    console.log('✦ Prayer Requests initialized ✦');
});

// ============================================
// OPTIONAL: INTERACTIVE CARD FEATURES
// ============================================

// Pause/Resume on card hover
document.addEventListener('DOMContentLoaded', () => {
    const prayerCards = document.querySelectorAll('.prayer-card');

    prayerCards.forEach((card) => {
        card.addEventListener('mouseenter', () => {
            // Optional: Add a subtle visual indicator that animation is paused
            card.style.opacity = '1';
        });

        card.addEventListener('mouseleave', () => {
            card.style.opacity = '1';
        });
    });
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get current month and week number
 */
function getCurrentMonthAndWeek() {
    const now = new Date();
    const month = now.toLocaleString('default', { month: 'long' });
    
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const weekNumber = Math.ceil((now.getDate() + firstDay.getDay()) / 7);
    
    return { month, week: weekNumber };
}

/**
 * Format month and week for display (optional use in template)
 */
function formatPrayerPeriod(month, week) {
    return `${month} • Week ${week}`;
}

// Export utilities if needed in other scripts
if (typeof window !== 'undefined') {
    window.PrayerCardAnimator = PrayerCardAnimator;
    window.getCurrentMonthAndWeek = getCurrentMonthAndWeek;
    window.formatPrayerPeriod = formatPrayerPeriod;
}
