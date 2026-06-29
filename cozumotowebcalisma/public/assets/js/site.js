(function () {
  'use strict';

  // Mobil menü.
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('is-open'); });
    });
  }

  // Flash mesajı kapatma + otomatik gizleme.
  document.querySelectorAll('.flash').forEach(function (el) {
    var close = el.querySelector('.flash__close');
    if (close) close.addEventListener('click', function () { el.remove(); });
    setTimeout(function () { el.style.transition = 'opacity .4s'; el.style.opacity = '0'; setTimeout(function () { el.remove(); }, 400); }, 6000);
  });

  // Header gölgesi (scroll).
  var header = document.getElementById('site-header');
  if (header) {
    window.addEventListener('scroll', function () {
      header.style.boxShadow = window.scrollY > 10 ? '0 6px 24px rgba(0,0,0,.25)' : 'none';
    });
  }
})();
