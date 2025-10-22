let currentIndex = 0;

function moveSlide(direction) {
    const slides = document.querySelector('.slides');
    const totalSlides = document.querySelectorAll('.slide').length;

    currentIndex = (currentIndex + direction + totalSlides) % totalSlides;
    slides.style.transform = `translateX(-${currentIndex * 100}%)`;
}

// Cambio automático cada 5 segundos
setInterval(() => moveSlide(1), 5000);
