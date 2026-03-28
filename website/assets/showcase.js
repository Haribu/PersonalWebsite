document.addEventListener('DOMContentLoaded', () => {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const yearGroups = document.querySelectorAll('.year-group');
    const showcaseContent = document.getElementById('showcase-content');
    const noResults = document.getElementById('no-results');

    let activeFilter = 'all';

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
                const matchesFilter = activeFilter === 'all' || category === activeFilter;

                if (matchesFilter) {
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
});
