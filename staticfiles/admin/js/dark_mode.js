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

  // Create theme toggle button if it doesn't exist in Jazzmin
  function createThemeToggle() {
    if (document.getElementById('theme-toggle')) return;

    const navbar = document.querySelector('.navbar') || document.querySelector('.main-header');
    if (!navbar) return;

    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'theme-toggle';
    toggleBtn.className = 'btn btn-outline-secondary';
    toggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
    toggleBtn.setAttribute('aria-label', 'Toggle dark mode');
    toggleBtn.setAttribute('aria-pressed', 'false');
    toggleBtn.style.cssText = `
      margin-left: 12px;
      border: none;
      background: transparent;
      color: var(--gray-600);
      padding: 0.5rem;
      border-radius: 0.375rem;
      cursor: pointer;
      transition: all 0.2s ease;
    `;

    toggleBtn.addEventListener('mouseenter', function() {
      this.style.background = 'var(--gray-100)';
    });

    toggleBtn.addEventListener('mouseleave', function() {
      this.style.background = 'transparent';
    });

    // Find the right place to insert the button
    const userMenu = navbar.querySelector('.user-menu') || navbar.querySelector('.dropdown');
    if (userMenu) {
      userMenu.parentNode.insertBefore(toggleBtn, userMenu);
    } else {
      navbar.appendChild(toggleBtn);
    }

    // Apply current theme to button
    const currentTheme = document.documentElement.classList.contains('dark-mode') ? 'dark' : 'light';
    const icon = toggleBtn.querySelector('i');
    if (icon) {
      icon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  // Initialize theme toggle
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createThemeToggle);
  } else {
    createThemeToggle();
  }
})();
