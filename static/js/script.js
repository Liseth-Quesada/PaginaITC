// Carrusel
let currentIndex = 0;

function showSlide(index) {
  const slides = document.querySelector('.slides');
  const totalSlides = document.querySelectorAll('.slide').length;
  if (!slides) return;

  // Reiniciar si llega al final
  if (index >= totalSlides) currentIndex = 0;
  else if (index < 0) currentIndex = totalSlides - 1;
  else currentIndex = index;

  slides.style.transform = `translateX(-${currentIndex * 100}%)`;
}

setInterval(() => {
  showSlide(currentIndex + 1);
}, 4000);

setInterval(() => moveSlide(1), 5000); 

// Carrusel de proyectos entregados
function moveSlide(direction) {
  const container = document.getElementById('slides');
  const scrollAmount = 360; // desplazamiento por clic (ajústalo a tu gusto)
  container.scrollBy({
    left: direction * scrollAmount,
    behavior: 'smooth'
  });
}

const cards = document.querySelector('.cards');
const card = document.querySelector('.card');
const prevBtn = document.querySelector('.btn-prev');
const nextBtn = document.querySelector('.btn-next');

let index = 0;
const cardWidth = card.offsetWidth + 15; // ancho + gap

nextBtn.addEventListener('click', () => {
  if (index < cards.children.length - 3) {
    index++;
  } else {
    index = 0;
  }
  cards.style.transform = `translateX(-${index * cardWidth}px)`;
});

prevBtn.addEventListener('click', () => {
  if (index > 0) {
    index--;
  } else {
    index = cards.children.length - 3;
  }
  cards.style.transform = `translateX(-${index * cardWidth}px)`;
});


