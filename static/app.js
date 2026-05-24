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

  /* ---------- Clickable column-header sorting -------------- */
  // A <th> with data-sort-asc / data-sort-desc maps to the page's existing
  // server-side `sort_by` values. Clicking it sets the form's sort_by select
  // and submits — so the actual ordering still happens in SQL.
  function initHeaderSort() {
    const form = document.querySelector('form.filters');
    if (!form) return;
    const sortSelect = form.querySelector('select[name="sort_by"]');
    if (!sortSelect) return;

    const current = sortSelect.value;

    document.querySelectorAll('th[data-sort-asc], th[data-sort-desc]').forEach((th) => {
      const asc = th.getAttribute('data-sort-asc');
      const desc = th.getAttribute('data-sort-desc');
      th.classList.add('sortable');

      // Indicate current sort direction with an arrow.
      if (current && current === asc) th.classList.add('sorted-asc');
      else if (current && current === desc) th.classList.add('sorted-desc');

      th.addEventListener('click', () => {
        // Toggle: if already ascending, go descending, otherwise ascending.
        let next = asc || desc;
        if (asc && desc) {
          next = current === asc ? desc : asc;
        }
        if (!next) return;
        sortSelect.value = next;
        if (typeof form.requestSubmit === 'function') form.requestSubmit();
        else form.submit();
      });
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
      initHeaderSort();
      initSmoothAnchors();
    });
  } else {
    initScrollReveal();
    initFormLoading();
    initSmoothAnchors();
  }
})();
