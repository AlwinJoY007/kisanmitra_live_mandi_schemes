// Kisan Mitra - Government Schemes JavaScript

// DOM Elements
const searchInput = document.getElementById('searchInput');
const schemesGrid = document.getElementById('schemesGrid');
const noResults = document.getElementById('noResults');
const schemeCards = document.querySelectorAll('.scheme-card');

// Scheme data for enhanced search
const schemeData = [
    {
        id: 'pm-kisan',
        name: 'PM-Kisan Samman Nidhi',
        keywords: ['pm kisan', 'samman nidhi', 'income support', '6000', 'direct transfer', 'financial'],
        description: 'Direct income support of ₹6,000 per year to small and marginal farmer families'
    },
    {
        id: 'kcc',
        name: 'Kisan Credit Card (KCC)',
        keywords: ['kisan credit card', 'kcc', 'credit facility', 'loan', 'agricultural finance', 'banking'],
        description: 'Flexible credit facility for farmers with simplified procedures and lower interest rates'
    },
    {
        id: 'pmfb',
        name: 'PM Fasal Bima Yojana',
        keywords: ['pm fasal bima', 'crop insurance', 'insurance', 'crop failure', 'natural calamities', 'protection'],
        description: 'Comprehensive crop insurance scheme protecting farmers against crop failure'
    },
    {
        id: 'soil-health',
        name: 'Soil Health Card Scheme',
        keywords: ['soil health', 'soil testing', 'fertilizer', 'soil quality', 'agriculture testing', 'health card'],
        description: 'Free soil testing and health cards for farmers to optimize fertilizer use'
    },
    {
        id: 'e-nam',
        name: 'e-NAM (National Agriculture Market)',
        keywords: ['e nam', 'enam', 'online trading', 'agriculture market', 'price discovery', 'digital market'],
        description: 'Online trading platform connecting agricultural markets across India'
    },
    {
        id: 'pmksy',
        name: 'PM Krishi Sinchayee Yojana',
        keywords: ['pm krishi sinchayee', 'irrigation', 'water management', 'krishi sinchayee', 'water scheme', 'irrigation scheme'],
        description: 'Comprehensive irrigation scheme for end-to-end water management solutions'
    }
];

/**
 * Initialize the page
 */
function initializePage() {
    // Add event listeners
    setupEventListeners();
    
    // Show all schemes initially
    showAllSchemes();
    
    console.log('Kisan Mitra Schemes page initialized successfully');
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search input event listener
    searchInput.addEventListener('input', handleSearch);
    
    // Search button click
    document.querySelector('.search-btn').addEventListener('click', () => {
        handleSearch();
    });
    
    // Enter key in search input
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSearch();
        }
    });
    
    // Clear search when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            // Optional: Auto-clear search after delay
        }
    });
}

/**
 * Handle search functionality
 */
function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        showAllSchemes();
        return;
    }
    
    const filteredSchemes = filterSchemes(searchTerm);
    displayFilteredSchemes(filteredSchemes, searchTerm);
}

/**
 * Filter schemes based on search term
 * @param {string} searchTerm - The search term
 * @returns {Array} Filtered schemes
 */
function filterSchemes(searchTerm) {
    return schemeData.filter(scheme => {
        // Search in scheme name
        if (scheme.name.toLowerCase().includes(searchTerm)) {
            return true;
        }
        
        // Search in description
        if (scheme.description.toLowerCase().includes(searchTerm)) {
            return true;
        }
        
        // Search in keywords
        if (scheme.keywords.some(keyword => keyword.includes(searchTerm))) {
            return true;
        }
        
        return false;
    });
}

/**
 * Display filtered schemes
 * @param {Array} filteredSchemes - Array of filtered schemes
 * @param {string} searchTerm - The search term used
 */
function displayFilteredSchemes(filteredSchemes, searchTerm) {
    // Hide all cards first
    schemeCards.forEach(card => {
        card.style.display = 'none';
        card.classList.remove('visible');
        card.classList.add('hidden');
    });
    
    // Show matching cards
    filteredSchemes.forEach(scheme => {
        const card = document.querySelector(`[data-scheme="${scheme.id}"]`);
        if (card) {
            card.style.display = 'block';
            card.classList.remove('hidden');
            card.classList.add('visible');
            
            // Add search highlight effect
            highlightSearchTerm(card, searchTerm);
        }
    });
    
    // Show/hide no results message
    if (filteredSchemes.length === 0) {
        showNoResults(searchTerm);
    } else {
        hideNoResults();
        showSearchResults(filteredSchemes.length, searchTerm);
    }
}

/**
 * Show all schemes
 */
function showAllSchemes() {
    schemeCards.forEach(card => {
        card.style.display = 'block';
        card.classList.remove('hidden');
        card.classList.add('visible');
        removeHighlight(card);
    });
    
    hideNoResults();
    
    // Clear search input
    searchInput.value = '';
}

/**
 * Highlight search term in card content
 * @param {HTMLElement} card - The scheme card element
 * @param {string} searchTerm - The search term to highlight
 */
function highlightSearchTerm(card, searchTerm) {
    const title = card.querySelector('.scheme-title');
    const description = card.querySelector('.scheme-description');
    
    // Remove existing highlights
    removeHighlight(card);
    
    // Highlight in title
    if (title) {
        const highlightedTitle = title.textContent.replace(
            new RegExp(searchTerm, 'gi'),
            `<mark style="background: #fff3cd; color: #856404; padding: 0.1rem 0.3rem; border-radius: 3px;">$&</mark>`
        );
        title.innerHTML = highlightedTitle;
    }
    
    // Highlight in description
    if (description) {
        const highlightedDescription = description.textContent.replace(
            new RegExp(searchTerm, 'gi'),
            `<mark style="background: #fff3cd; color: #856404; padding: 0.1rem 0.3rem; border-radius: 3px;">$&</mark>`
        );
        description.innerHTML = highlightedDescription;
    }
}

/**
 * Remove highlight from card content
 * @param {HTMLElement} card - The scheme card element
 */
function removeHighlight(card) {
    const title = card.querySelector('.scheme-title');
    const description = card.querySelector('.scheme-description');
    
    if (title) {
        title.innerHTML = title.textContent;
    }
    
    if (description) {
        description.innerHTML = description.textContent;
    }
}

/**
 * Show no results message
 * @param {string} searchTerm - The search term that returned no results
 */
function showNoResults(searchTerm) {
    noResults.style.display = 'block';
    noResults.classList.add('visible');
    
    // Update no results message
    const noResultsTitle = noResults.querySelector('h3');
    const noResultsText = noResults.querySelector('p');
    
    if (noResultsTitle) {
        noResultsTitle.textContent = `No schemes found for "${searchTerm}"`;
    }
    
    if (noResultsText) {
        noResultsText.textContent = 'Try searching with different keywords like "credit", "insurance", "irrigation", or "soil".';
    }
}

/**
 * Hide no results message
 */
function hideNoResults() {
    noResults.style.display = 'none';
    noResults.classList.remove('visible');
}

/**
 * Show search results summary
 * @param {number} count - Number of results found
 * @param {string} searchTerm - The search term
 */
function showSearchResults(count, searchTerm) {
    // Create or update search results indicator
    let resultsIndicator = document.querySelector('.search-results-indicator');
    
    if (!resultsIndicator) {
        resultsIndicator = document.createElement('div');
        resultsIndicator.className = 'search-results-indicator';
        resultsIndicator.style.cssText = `
            text-align: center;
            margin-bottom: 1rem;
            padding: 1rem;
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-radius: 10px;
            color: #2e7d32;
            font-weight: 500;
        `;
        
        const container = document.querySelector('.schemes-section .container');
        container.insertBefore(resultsIndicator, schemesGrid);
    }
    
    resultsIndicator.innerHTML = `
        <span>🔍 Found ${count} scheme${count !== 1 ? 's' : ''} matching "${searchTerm}"</span>
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (resultsIndicator && searchInput.value === searchTerm) {
            resultsIndicator.style.opacity = '0';
            setTimeout(() => {
                if (resultsIndicator && resultsIndicator.parentNode) {
                    resultsIndicator.remove();
                }
            }, 300);
        }
    }, 3000);
}

/**
 * Clear search and show all schemes
 */
function clearSearch() {
    showAllSchemes();
    searchInput.focus();
}

/**
 * Get scheme statistics
 */
function getSchemeStats() {
    return {
        total: schemeData.length,
        categories: {
            financial: ['pm-kisan', 'kcc'].length,
            insurance: ['pmfb'].length,
            infrastructure: ['e-nam', 'pmksy'].length,
            support: ['soil-health'].length
        }
    };
}

/**
 * Add smooth scroll to top functionality
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
function addScrollToTopButton() {
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '↑';
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
        color: white;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(56, 142, 60, 0.3);
        transition: all 0.3s ease;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
    `;
    
    scrollBtn.addEventListener('click', scrollToTop);
    scrollBtn.addEventListener('mouseenter', () => {
        scrollBtn.style.transform = 'scale(1.1)';
    });
    scrollBtn.addEventListener('mouseleave', () => {
        scrollBtn.style.transform = 'scale(1)';
    });
    
    document.body.appendChild(scrollBtn);
    
    // Show/hide based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.visibility = 'visible';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.visibility = 'hidden';
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializePage();
    addScrollToTopButton();
    
    // Log scheme statistics
    console.log('Scheme Statistics:', getSchemeStats());
});

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        filterSchemes,
        showAllSchemes,
        clearSearch,
        getSchemeStats
    };
}
