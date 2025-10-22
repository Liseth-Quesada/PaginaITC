// Carrusel
let currentIndex = 0;

function moveSlide(direction) {
    const slides = document.querySelector('.slides');
    const totalSlides = document.querySelectorAll('.slide').length;

    currentIndex = (currentIndex + direction + totalSlides) % totalSlides;
    slides.style.transform = `translateX(-${currentIndex * 100}%)`;
}

// Cambio automático cada 5 segundos
setInterval(() => moveSlide(1), 5000);


// Carrusel de proyectos entregados
  const carrusel = document.querySelector('.carrusel-items');
  const next = document.querySelector('.next');
  const prev = document.querySelector('.prev');
  let scrollAmount = 0;

  next.addEventListener('click', () => {
    carrusel.scrollBy({ left: 350, behavior: 'smooth' });
  });

  prev.addEventListener('click', () => {
    carrusel.scrollBy({ left: -350, behavior: 'smooth' });
  });

