window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    const scrollY = window.scrollY;
  
    if (scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });


  document.addEventListener("DOMContentLoaded", function() {
    const navLinks = document.querySelectorAll('.nav-item a');

    navLinks.forEach(function(link, index) {
        if (index > 0 && index < navLinks.length - 1) { // Ellenőrizze, hogy az aktuális index nagyobb-e, mint 0
          link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').slice(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
              const yOffset = -50; // A szükséges korrekció mértéke
              const y = targetElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
              window.scrollTo({top: y, behavior: 'smooth'});
            }
          });
        }
      });
    });

   