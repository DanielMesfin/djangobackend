(function () {
  function applyTheme(theme) {
    const root = document.documentElement;
    const body = document.body;
    const btn = document.getElementById('theme-toggle');
    const isDark = theme === 'dark';
    root.classList.toggle('dark-mode', isDark);
    body.classList.toggle('dark-mode', isDark);
    if (btn) {
      const icon = btn.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-moon', !isDark);
        icon.classList.toggle('fa-sun', isDark);
      }
      btn.setAttribute('aria-pressed', String(isDark));
      btn.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
    }
  }

  function getStoredTheme() {
    try {
      return localStorage.getItem('admin-theme');
    } catch (_) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      localStorage.setItem('admin-theme', theme);
    } catch (_) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    const stored = getStoredTheme();
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial = stored || (prefersDark ? 'dark' : 'light');
    applyTheme(initial);

    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        const next = (document.documentElement.classList.contains('dark-mode')) ? 'light' : 'dark';
        applyTheme(next);
        storeTheme(next);
      });
    }

    // Update if system preference changes and user has not stored preference yet
    if (!stored && window.matchMedia) {
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      mq.addEventListener('change', function (e) {
        applyTheme(e.matches ? 'dark' : 'light');
      });
    }
  });
})();
