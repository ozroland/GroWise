window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    const scrollY = window.scrollY;
  
    if (scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  function toggleSelection(card) {
    const checkbox = card.querySelector('.image-checkbox');
    checkbox.checked = !checkbox.checked;
    card.classList.toggle('selected', checkbox.checked);
}

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('year').textContent = new Date().getFullYear();
});
