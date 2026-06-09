// ============================================
// THEME TOGGLE & PERSISTENCE
// ============================================

const toggleButton = document.getElementById('theme-toggle');
const html = document.documentElement;

if (toggleButton) {
    toggleButton.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
}

// ============================================
// HAMBURGER MENU TOGGLE
// ============================================

const hamburgerToggle = document.getElementById('hamburger-toggle');
const navMenu = document.querySelector('.nav-menu');

if (hamburgerToggle) {
    hamburgerToggle.addEventListener('click', () => {
        hamburgerToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close menu when a nav link is clicked
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            hamburgerToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.navbar')) {
            hamburgerToggle.classList.remove('active');
            navMenu.classList.remove('active');
        }
    });
}

// ============================================
// CANDLE GLOW CURSOR EFFECT
// ============================================

const glow = document.querySelector('.cursor-glow');

if (glow) {
    let mouseX = 0;
    let mouseY = 0;
    let glowX = 0;
    let glowY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Smooth trailing effect
    function animateGlow() {
        glowX += (mouseX - glowX) * 0.1;
        glowY += (mouseY - glowY) * 0.1;

        glow.style.left = `${glowX}px`;
        glow.style.top = `${glowY}px`;

        requestAnimationFrame(animateGlow);
    }

    animateGlow();
}

// ============================================
// SMOOTH MODAL TRANSITIONS
// ============================================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        // Trigger animation
        setTimeout(() => {
            modal.style.animation = 'fadeIn 0.3s ease-out';
        }, 10);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function openSignupModal() {
    openModal('signup-modal');
}

function closeSignupModal() {
    closeModal('signup-modal');
}

function openLoginModal() {
    openModal('login-modal');
}

function closeLoginModal() {
    closeModal('login-modal');
}

function openProfileModal() {
    openModal('profile-modal');
}

function closeProfileModal() {
    closeModal('profile-modal');
}

// ============================================
// CLOSE MODALS ON BACKGROUND CLICK
// ============================================

const modals = {
    signup: document.getElementById('signup-modal'),
    login: document.getElementById('login-modal'),
    profile: document.getElementById('profile-modal')
};

Object.entries(modals).forEach(([key, modal]) => {
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    }
});

// ============================================
// CLOSE MODALS ON ESCAPE KEY
// ============================================

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        Object.values(modals).forEach(modal => {
            if (modal && modal.classList.contains('active')) {
                closeModal(modal.id);
            }
        });
    }
});

// ============================================
// PARISHIONER CARD HOVER EFFECTS
// ============================================

const parishionerCards = document.querySelectorAll('.parishioner-card');

parishionerCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transition = 'all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    });

    card.addEventListener('mouseleave', () => {
        card.style.transition = 'all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    });
});

// ============================================
// FORM INPUT FOCUS EFFECTS
// ============================================

const formInputs = document.querySelectorAll('.form-row input, .form-row textarea, .form-row select');

formInputs.forEach(input => {
    input.addEventListener('focus', () => {
        const formRow = input.closest('.form-row');
        if (formRow) {
            formRow.style.transform = 'translateY(-2px)';
            formRow.style.transition = 'all 0.3s ease';
        }
    });

    input.addEventListener('blur', () => {
        const formRow = input.closest('.form-row');
        if (formRow) {
            formRow.style.transform = 'translateY(0)';
        }
    });
});

// ============================================
// CLOSE BUTTON EVENT LISTENERS
// ============================================

const closeButtons = document.querySelectorAll('.modal-close');

closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const modal = btn.closest('.auth-modal');
        if (modal) {
            closeModal(modal.id);
        }
    });
});

// ============================================
// SMOOTH REVEAL ANIMATION ON SCROLL
// ============================================

const observerOptions = {
    threshold: 0.2,
    rootMargin: '0px 0px -50px 0px'
};

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'slideUp 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            revealObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('[data-reveal]').forEach(el => {
    revealObserver.observe(el);
});

// ============================================
// BUTTON CLICK FEEDBACK
// ============================================

const buttons = document.querySelectorAll('.btn-primary, .nav-link');

buttons.forEach(btn => {
    btn.addEventListener('click', function() {
        this.style.transform = 'scale(0.98)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
    });
});

// ============================================
// PRESERVE SCROLL POSITION ON PAGE RELOAD
// ============================================

if (sessionStorage.getItem('scrollPosition')) {
    window.scrollTo(0, parseInt(sessionStorage.getItem('scrollPosition')));
    sessionStorage.removeItem('scrollPosition');
}

window.addEventListener('beforeunload', () => {
    sessionStorage.setItem('scrollPosition', window.scrollY);
});

document.addEventListener('DOMContentLoaded', () => {

    const dashboardSection =
        document.querySelector('.dashboard-section');

    if (!dashboardSection) return;

    const shouldShowProfileModal =
        dashboardSection.dataset.showProfileModal === 'true';

    if (shouldShowProfileModal) {
        openProfileModal();
    }
});

console.log('✦ MinistryHub initialized ✦');