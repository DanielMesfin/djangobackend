/* Mobile Navigation and Sidebar Toggle */
(function() {
    'use strict';

    function initMobileNavigation() {
        // Check if sidebar exists
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        // Create mobile toggle button if it doesn't exist
        if (!document.querySelector('.mobile-sidebar-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'mobile-sidebar-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            toggleBtn.setAttribute('aria-label', 'Toggle sidebar');
            toggleBtn.setAttribute('aria-expanded', 'false');
            
            // Add styles
            toggleBtn.style.cssText = `
                display: none;
                position: fixed;
                top: 1rem;
                left: 1rem;
                z-index: 1001;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 0.5rem;
                padding: 0.5rem 0.75rem;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            `;

            // Show on mobile
            const style = document.createElement('style');
            style.textContent = `
                @media (max-width: 768px) {
                    .mobile-sidebar-toggle {
                        display: flex !important;
                        align-items: center;
                        justify-content: center;
                    }
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(toggleBtn);

            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.style.cssText = `
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 999;
            `;
            document.body.appendChild(overlay);

            // Toggle sidebar
            function toggleSidebar() {
                const isOpen = sidebar.classList.contains('active');
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
                toggleBtn.setAttribute('aria-expanded', !isOpen);
                
                // Prevent body scroll when sidebar is open
                document.body.style.overflow = isOpen ? '' : 'hidden';
            }

            toggleBtn.addEventListener('click', toggleSidebar);
            overlay.addEventListener('click', toggleSidebar);

            // Close sidebar on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                    toggleSidebar();
                }
            });

            // Close sidebar on window resize if moving to desktop
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
                    toggleSidebar();
                }
            });
        }
    }

    // Responsive table handling
    function initResponsiveTables() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(function(table) {
            // Wrap table in responsive container if not already wrapped
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }

    // Mobile-friendly date inputs
    function initMobileDateInputs() {
        const dateInputs = document.querySelectorAll('input[type="date"], input[type="time"], input[type="datetime-local"]');
        dateInputs.forEach(function(input) {
            // Ensure mobile-friendly date pickers
            input.setAttribute('inputmode', 'none');
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initMobileNavigation();
            initResponsiveTables();
            initMobileDateInputs();
        });
    } else {
        initMobileNavigation();
        initResponsiveTables();
        initMobileDateInputs();
    }
})();