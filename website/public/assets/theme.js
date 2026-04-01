// Micro-animation: Fade in content elegantly
document.addEventListener('DOMContentLoaded', () => {
    const content = document.querySelector('.content');
    if (content) {
        // Add a utility class that handles the transition
        content.classList.add('content-visible');
    }

    // Appearance Dropdown Logic
    const appearanceToggle = document.getElementById('appearance-toggle');
    const appearanceDropdown = document.getElementById('appearance-dropdown');
    
    if (appearanceToggle && appearanceDropdown) {
        appearanceToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            const isExpanded = appearanceToggle.getAttribute('aria-expanded') === 'true';
            appearanceToggle.setAttribute('aria-expanded', !isExpanded);
            appearanceDropdown.classList.toggle('hidden');
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!appearanceDropdown.contains(e.target) && e.target !== appearanceToggle) {
                appearanceDropdown.classList.add('hidden');
                appearanceToggle.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Prevent closing when clicking inside dropdown
        appearanceDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Theme Toggle Logic
    const themeLightBtn = document.getElementById('theme-light-btn');
    const themeDarkBtn = document.getElementById('theme-dark-btn');
    
    function setTheme(isLight) {
        if (isLight) {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            if (themeLightBtn) themeLightBtn.classList.add('active');
            if (themeDarkBtn) themeDarkBtn.classList.remove('active');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
            if (themeDarkBtn) themeDarkBtn.classList.add('active');
            if (themeLightBtn) themeLightBtn.classList.remove('active');
        }
    }
    
    // UI Hydration for Theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        if (themeLightBtn) themeLightBtn.classList.add('active');
        if (themeDarkBtn) themeDarkBtn.classList.remove('active');
    } else {
        if (themeDarkBtn) themeDarkBtn.classList.add('active');
        if (themeLightBtn) themeLightBtn.classList.remove('active');
    }

    if (themeLightBtn) themeLightBtn.addEventListener('click', () => setTheme(true));
    if (themeDarkBtn) themeDarkBtn.addEventListener('click', () => setTheme(false));

    // Font Toggle Logic
    const fontToggleButton = document.getElementById('font-toggle');
    
    function setFont(isDyslexic) {
        if (isDyslexic) {
            document.documentElement.setAttribute('data-font', 'dyslexic');
            localStorage.setItem('fontPreference', 'dyslexic');
            if(fontToggleButton) fontToggleButton.setAttribute('aria-pressed', 'true');
        } else {
            document.documentElement.removeAttribute('data-font');
            localStorage.setItem('fontPreference', 'default');
            if(fontToggleButton) fontToggleButton.setAttribute('aria-pressed', 'false');
        }
    }
    
    // UI Hydration for Font
    const savedFont = localStorage.getItem('fontPreference');
    if (savedFont === 'dyslexic') {
        if(fontToggleButton) fontToggleButton.setAttribute('aria-pressed', 'true');
    } else {
        if(fontToggleButton) fontToggleButton.setAttribute('aria-pressed', 'false');
    }
    
    if (fontToggleButton) {
        fontToggleButton.addEventListener('click', () => {
            const currentFont = document.documentElement.getAttribute('data-font') || savedFont;
            setFont(currentFont !== 'dyslexic');
        });
    }

    // Text Size Logic
    const btnDecrease = document.getElementById('text-decrease');
    const btnIncrease = document.getElementById('text-increase');
    const sizeDisplay = document.getElementById('text-size-display');
    
    let currentTextSize = parseInt(localStorage.getItem('textSize')) || 100;
    
    function setTextSize(size) {
        // Clamp between 90% and 140%
        size = Math.max(90, Math.min(140, size));
        currentTextSize = size;
        
        document.documentElement.setAttribute('data-text-size', size.toString());
        localStorage.setItem('textSize', size.toString());
        
        if (sizeDisplay) {
            sizeDisplay.textContent = `${size}%`;
        }
    }
    
    // UI Hydration for Text Size
    if (sizeDisplay) {
        sizeDisplay.textContent = `${currentTextSize}%`;
    }
    
    if (btnDecrease) btnDecrease.addEventListener('click', () => setTextSize(currentTextSize - 10));
    if (btnIncrease) btnIncrease.addEventListener('click', () => setTextSize(currentTextSize + 10));

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

