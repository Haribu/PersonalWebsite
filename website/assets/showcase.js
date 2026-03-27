document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('showcase-search');
    const filterTabs = document.querySelectorAll('.filter-tab');
    const showcaseCards = document.querySelectorAll('.glass-card');
    const yearGroups = document.querySelectorAll('.year-group');
    const showcaseContent = document.getElementById('showcase-content');
    const noResults = document.getElementById('no-results');
    const backToTopBtn = document.getElementById('back-to-top');

    let activeFilter = 'all';
    let searchQuery = '';
    let debounceTimer;

    // Filter Tab Click Handling
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Update active state
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            activeFilter = tab.getAttribute('data-filter');
            applyFilters();
        });
    });

    // Search Input Handling with Debounce
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            searchQuery = e.target.value.toLowerCase().trim();
            applyFilters();
        }, 200);
    });

    function applyFilters() {
        let visibleCount = 0;
        
        // Update container classes for year-header color syncing
        showcaseContent.classList.remove('filter-speaking', 'filter-writing', 'filter-event');
        if (activeFilter !== 'all') {
            showcaseContent.classList.add(`filter-${activeFilter}`);
        }

        yearGroups.forEach(group => {
            const cards = group.querySelectorAll('.glass-card');
            let visibleInGroup = 0;

            cards.forEach(card => {
                const category = card.getAttribute('data-category');
                const title = card.getAttribute('data-title');
                const summary = card.getAttribute('data-summary');
                const content = card.getAttribute('data-content');

                const matchesFilter = activeFilter === 'all' || category === activeFilter;
                const matchesSearch = searchQuery === '' || 
                                    title.includes(searchQuery) || 
                                    summary.includes(searchQuery) || 
                                    content.includes(searchQuery);

                if (matchesFilter && matchesSearch) {
                    card.classList.remove('hidden');
                    visibleInGroup++;
                    visibleCount++;
                } else {
                    card.classList.add('hidden');
                }
            });

            // Hide the entire year group if no cards are visible within it
            if (visibleInGroup > 0) {
                group.classList.remove('hidden');
            } else {
                group.classList.add('hidden');
            }
        });

        // Show/Hide "No Results" message
        if (visibleCount === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
        }
    }

    // Back to Top Visibility & Scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});
