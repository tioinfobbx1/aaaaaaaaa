if ('ontouchstart' in window) {
  document.body.classList.add('touch');
}

if (!document.querySelector('body > footer')) {
  document.body.classList.add('modo-foco');
}
