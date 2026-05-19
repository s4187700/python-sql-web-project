/* =========================================================
   UI behaviours — scroll reveal + form loading
   ========================================================= */
(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Scroll reveal -------------------------------- */
  function initScrollReveal() {
    // Auto-tag every .panel and .cards as reveal targets, unless author
    // already added the class.
    const targets = document.querySelectorAll('.panel, .cards');
    targets.forEach((el) => {
      if (!el.classList.contains('reveal')) el.classList.add('reveal');
    });

    if (prefersReducedMotion) {
      targets.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    if (!('IntersectionObserver' in window)) {
      targets.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );

    targets.forEach((el) => io.observe(el));
  }

  /* ---------- Form loading state --------------------------- */
  function initFormLoading() {
    const forms = document.querySelectorAll('form.filters');
    forms.forEach((form) => {
      form.addEventListener('submit', () => {
        document.body.classList.add('is-loading');
        // Replace table cell contents with skeleton placeholders for a quick
        // feedback flash before the navigation completes.
        document.querySelectorAll('.panel:not(:first-of-type) tbody td').forEach((td) => {
          const w = ['w-60', 'w-80', 'w-40'][Math.floor(Math.random() * 3)];
          td.innerHTML = `<span class="skeleton skeleton-row ${w}"></span>`;
        });
      });
    });

    // Clear loading state when navigating back via bfcache
    window.addEventListener('pageshow', () => {
      document.body.classList.remove('is-loading');
    });
  }

  /* ---------- Smooth-scroll anchors (defensive) ------------ */
  function initSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener('click', (e) => {
        const id = a.getAttribute('href').slice(1);
        const target = id && document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth', block: 'start' });
        }
      });
    });
  }

  /* ---------- Boot ----------------------------------------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initScrollReveal();
      initFormLoading();
      initSmoothAnchors();
    });
  } else {
    initScrollReveal();
    initFormLoading();
    initSmoothAnchors();
  }
})();
