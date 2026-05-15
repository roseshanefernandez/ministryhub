let currentIndex = 0;
let autoSlide;

function getCardsPerView() {
    if (window.innerWidth <= 768) return 1;
    if (window.innerWidth <= 1024) return 2;
    return 3;
}

function updateCarousel() {
    const track = document.getElementById('carouselTrack');
    if (!track) return;

    const cards = document.querySelectorAll('.carousel-card');
    if (cards.length === 0) return;

    const cardsPerView = getCardsPerView();
    const maxIndex = Math.max(0, cards.length - cardsPerView);

    if (currentIndex > maxIndex) {
        currentIndex = 0;
    }

    // 1. Target the first actual card element from the list safely
    const firstCard = cards[0];
    const cardWidth = firstCard.getBoundingClientRect().width;

    // 2. Read the actual layout gap value directly from the browser window
    const trackComputedStyle = window.getComputedStyle(track);
    const gap = parseFloat(trackComputedStyle.gap) || 0;

    // 3. Calculate step size (one card dimension plus the single track gap)
    const amountToMove = (cardWidth + gap) * currentIndex;

    // 4. Translate track coordinates smoothly
    track.style.transform = `translateX(-${amountToMove}px)`;
}

function carouselNext() {
    const cards = document.querySelectorAll('.carousel-card');
    const cardsPerView = getCardsPerView();
    const maxIndex = Math.max(0, cards.length - cardsPerView);

    currentIndex = currentIndex >= maxIndex ? 0 : currentIndex + 1;
    updateCarousel();
    resetAutoSlide();
}

function carouselPrev() {
    const cards = document.querySelectorAll('.carousel-card');
    const cardsPerView = getCardsPerView();
    const maxIndex = Math.max(0, cards.length - cardsPerView);

    currentIndex = currentIndex <= 0 ? maxIndex : currentIndex - 1;
    updateCarousel();
    resetAutoSlide();
}

function startAutoSlide() {
    autoSlide = setInterval(carouselNext, 5000);
}

function resetAutoSlide() {
    clearInterval(autoSlide);
    startAutoSlide();
}

window.addEventListener('resize', updateCarousel);

window.addEventListener('DOMContentLoaded', () => {
    updateCarousel();
    startAutoSlide();

    window.addEventListener('scroll', () => {
        const hero = document.querySelector('.dashboard-section');
        if (!hero) return;
        const scrollY = window.scrollY;
        hero.style.backgroundPositionY = `${scrollY * 0.4}px`;
    });
});
