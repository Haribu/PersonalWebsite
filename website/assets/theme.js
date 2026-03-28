// Micro-animation: Fade in content elegantly
document.addEventListener('DOMContentLoaded', () => {
    const content = document.querySelector('.content');
    if (content) {
        // Add a utility class that handles the transition
        content.classList.add('content-visible');
    }

    // Theme Toggle Logic
    const toggleButton = document.getElementById('theme-toggle');
    const moonIcon = document.getElementById('moon-icon');
    const sunIcon = document.getElementById('sun-icon');
    
    // Function to set theme
    function setTheme(isLight) {
        if (isLight) {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            if (moonIcon) {
                moonIcon.classList.remove('theme-icon-hidden');
                moonIcon.classList.add('theme-icon-visible');
            }
            if (sunIcon) {
                sunIcon.classList.remove('theme-icon-visible');
                sunIcon.classList.add('theme-icon-hidden');
            }
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
            if (moonIcon) {
                moonIcon.classList.remove('theme-icon-visible');
                moonIcon.classList.add('theme-icon-hidden');
            }
            if (sunIcon) {
                sunIcon.classList.remove('theme-icon-hidden');
                sunIcon.classList.add('theme-icon-visible');
            }
        }
    }
    
    // Check for saved theme (Apply initial state properly)
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        setTheme(true);
    } else {
        setTheme(false);
    }

    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            setTheme(currentTheme !== 'light');
        });
    }

    // Dynamic Copyright Year
    const yearSpan = document.getElementById('copyright-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // --- Mobile Nav Hamburger Toggle ---
    const navToggle = document.getElementById('nav-toggle');
    const navDrawer = document.getElementById('nav-drawer');

    function closeNav() {
        if (!navDrawer || !navToggle) return;
        navDrawer.classList.remove('open');
        navToggle.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
    }

    function openNav() {
        if (!navDrawer || !navToggle) return;
        navDrawer.classList.add('open');
        navToggle.classList.add('is-open');
        navToggle.setAttribute('aria-expanded', 'true');
    }

    if (navToggle && navDrawer) {
        navToggle.addEventListener('click', () => {
            const isOpen = navDrawer.classList.contains('open');
            if (isOpen) {
                closeNav();
            } else {
                openNav();
            }
        });

        // Close drawer when a nav link is tapped
        navDrawer.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeNav);
        });

        // Close drawer if viewport is resized to desktop width
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                closeNav();
            }
        });
    }

    // --- Back to Top Button ---
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        console.log("Back to top button initialized.");
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        }, { passive: true });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

