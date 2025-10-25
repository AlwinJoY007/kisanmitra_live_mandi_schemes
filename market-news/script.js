// Kisan Mitra - Market News JavaScript

// Configuration - Backend API endpoint
const BACKEND_API_URL = 'http://localhost:5000/api';

// Sample news data (fallback)
const fallbackNewsData = [
    {
        id: 1,
        title: "Government Announces New MSP for Kharif Crops 2024-25",
        excerpt: "The Cabinet Committee on Economic Affairs has approved new Minimum Support Prices for 14 Kharif crops, with paddy MSP increased by ₹117 per quintal.",
        category: "policy",
        date: "2024-01-15",
        source: "Ministry of Agriculture",
        image: "🏛️",
        content: "The government has announced significant increases in MSP for major Kharif crops for the 2024-25 season. Paddy MSP has been increased by ₹117 per quintal to ₹2,300 per quintal. Other major increases include maize (₹105), cotton (₹150), and groundnut (₹200). This move is expected to benefit over 10 million farmers across the country."
    },
    {
        id: 2,
        title: "Wheat Prices Surge 15% Due to Supply Shortage",
        excerpt: "Wheat prices have increased significantly across major mandis due to reduced production and increased demand from flour mills.",
        category: "market",
        date: "2024-01-14",
        source: "Agricultural Market Intelligence",
        image: "🌾",
        content: "Wheat prices have seen a sharp increase of 15% in the last month across major agricultural mandis. The surge is attributed to lower production due to adverse weather conditions and increased demand from flour mills. Experts suggest prices may stabilize once the new crop arrives in March."
    },
    {
        id: 3,
        title: "IMD Predicts Normal Monsoon for 2024",
        excerpt: "India Meteorological Department forecasts normal rainfall for the upcoming monsoon season, which is expected to boost agricultural production.",
        category: "weather",
        date: "2024-01-13",
        source: "India Meteorological Department",
        image: "🌧️",
        content: "The India Meteorological Department has predicted normal monsoon rainfall for 2024, with 96% of the long-period average. This is good news for farmers as normal monsoon is crucial for Kharif crop production. The forecast suggests well-distributed rainfall across most agricultural regions."
    },
    {
        id: 4,
        title: "New Drone Technology for Precision Agriculture",
        excerpt: "Government launches subsidy scheme for agricultural drones to help farmers with crop monitoring and pesticide application.",
        category: "technology",
        date: "2024-01-12",
        source: "Ministry of Agriculture",
        image: "🚁",
        content: "The government has launched a new scheme providing 50% subsidy on agricultural drones for farmers. These drones can be used for crop monitoring, pesticide spraying, and yield estimation. The scheme aims to modernize Indian agriculture and improve efficiency."
    },
    {
        id: 5,
        title: "Tomato Prices Crash Due to Oversupply",
        excerpt: "Tomato farmers in Maharashtra and Karnataka face significant losses as prices drop to ₹5-10 per kg due to bumper harvest.",
        category: "market",
        date: "2024-01-11",
        source: "Agricultural Market Intelligence",
        image: "🍅",
        content: "Tomato prices have crashed to ₹5-10 per kg in major markets due to oversupply from Maharashtra and Karnataka. Farmers are struggling to recover even the transportation costs. The government is considering intervention through procurement agencies."
    },
    {
        id: 6,
        title: "PM-KISAN 15th Installment Released",
        excerpt: "The 15th installment of PM-KISAN scheme has been released, benefiting over 11 crore farmer families with ₹6,000 each.",
        category: "policy",
        date: "2024-01-10",
        source: "PMO India",
        image: "💰",
        content: "Prime Minister Narendra Modi has released the 15th installment of PM-KISAN scheme, transferring ₹6,000 to each eligible farmer family. The scheme has now disbursed over ₹2.8 lakh crore to farmers since its inception in 2019."
    },
    {
        id: 7,
        title: "Cyclone Warning for Coastal Areas",
        excerpt: "IMD issues cyclone warning for coastal areas of Andhra Pradesh and Odisha, farmers advised to take precautions.",
        category: "weather",
        date: "2024-01-09",
        source: "India Meteorological Department",
        image: "🌀",
        content: "The India Meteorological Department has issued a cyclone warning for coastal areas of Andhra Pradesh and Odisha. Farmers in these regions are advised to harvest mature crops and take necessary precautions to protect standing crops and livestock."
    },
    {
        id: 8,
        title: "AI-Powered Soil Testing Kits Launched",
        excerpt: "New AI-powered soil testing kits can provide instant soil health reports and fertilizer recommendations to farmers.",
        category: "technology",
        date: "2024-01-08",
        source: "Agricultural Technology News",
        image: "🤖",
        content: "A startup has launched AI-powered soil testing kits that can analyze soil samples and provide instant reports on soil health, nutrient levels, and fertilizer recommendations. The portable device costs ₹15,000 and can help farmers optimize fertilizer use."
    },
    {
        id: 9,
        title: "Sugarcane Farmers Protest Over Pending Dues",
        excerpt: "Sugarcane farmers in Uttar Pradesh protest over pending dues worth ₹15,000 crore from sugar mills.",
        category: "policy",
        date: "2024-01-07",
        source: "Farmer Union News",
        image: "🚜",
        content: "Sugarcane farmers in Uttar Pradesh are protesting over pending dues of ₹15,000 crore from sugar mills. The farmers demand immediate payment and implementation of the Sugarcane Control Order. The state government has assured resolution within 15 days."
    },
    {
        id: 10,
        title: "Organic Farming Gets Boost with New Certification",
        excerpt: "Government simplifies organic farming certification process and reduces fees to encourage more farmers to adopt organic practices.",
        category: "policy",
        date: "2024-01-06",
        source: "Ministry of Agriculture",
        image: "🌱",
        content: "The government has simplified the organic farming certification process and reduced certification fees by 50%. This move aims to encourage more farmers to adopt organic farming practices and increase India's organic food exports."
    }
];

// Global variables
let allNewsData = [];
let filteredNews = [];
let currentCategory = 'all';
let currentSearchTerm = '';
let isLoading = false;

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const searchInput = document.getElementById('searchInput');
const noResults = document.getElementById('noResults');

/**
 * Initialize the page
 */
async function initializePage() {
    setupEventListeners();
    await fetchNewsData();
}

/**
 * Fetch news data from API
 */
async function fetchNewsData(category = 'all', force = false) {
    try {
        isLoading = true;
        showLoadingState();
        
        // Build query parameters
        const params = new URLSearchParams();
        if (category !== 'all') params.append('category', category);
        params.append('limit', '20');
        if (force) params.append('force', 'true');
        
        // Make API call to backend
        const response = await fetch(`${BACKEND_API_URL}/news?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Failed to fetch news');
        }
        
        if (!data.news || data.news.length === 0) {
            throw new Error('No news data available');
        }
        
        // Store all data globally
        allNewsData = data.news;
        filteredNews = [...allNewsData];
        
        // Apply current filters and render
        applyFilters();
        
        console.log(`News loaded from ${data.source}: ${data.news.length} articles`);
        
    } catch (error) {
        console.error('Error fetching news data:', error);
        
        // Fallback to sample data
        allNewsData = [...fallbackNewsData];
        filteredNews = [...allNewsData];
        applyFilters();
        
        console.log('Using fallback news data');
        
    } finally {
        isLoading = false;
        hideLoadingState();
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    newsGrid.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading news articles...</p>
        </div>
    `;
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    // Loading state will be replaced by renderNewsGrid
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search input event listener
    searchInput.addEventListener('input', (e) => {
        currentSearchTerm = e.target.value.toLowerCase();
        applyFilters();
    });
    
    // Enter key search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchNews();
        }
    });
}

/**
 * Render news grid
 * @param {Array} news - Array of news articles
 */
function renderNewsGrid(news) {
    if (!news || news.length === 0) {
        newsGrid.innerHTML = '';
        noResults.style.display = 'block';
        return;
    }
    
    noResults.style.display = 'none';
    
    newsGrid.innerHTML = news.map(article => `
        <div class="news-card" onclick="openNewsModal(${article.id})">
            <div class="news-image">
                ${article.image}
            </div>
            <div class="news-content">
                <span class="news-category">${article.category}</span>
                <h3 class="news-title">${article.title}</h3>
                <p class="news-excerpt">${article.excerpt}</p>
                <div class="news-meta">
                    <div class="news-date">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8 2V5M16 2V5M3.5 9.09H20.5M21 8.5V17C21 20 19.5 22 16 22H8C4.5 22 3 20 3 17V8.5C3 5.5 4.5 3.5 8 3.5H16C19.5 3.5 21 5.5 21 8.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        ${formatDate(article.date)}
                    </div>
                    <div class="news-source">${article.source}</div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Filter news by category
 * @param {string} category - Category to filter by
 */
async function filterNews(category) {
    currentCategory = category;
    
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-category="${category}"]`).classList.add('active');
    
    // Fetch fresh data for the category
    await fetchNewsData(category);
}

/**
 * Search news
 */
function searchNews() {
    currentSearchTerm = searchInput.value.toLowerCase();
    applyFilters();
}

/**
 * Apply all filters
 */
function applyFilters() {
    if (!allNewsData || allNewsData.length === 0) {
        renderNewsGrid([]);
        return;
    }
    
    filteredNews = allNewsData.filter(article => {
        const matchesCategory = currentCategory === 'all' || article.category === currentCategory;
        const matchesSearch = currentSearchTerm === '' || 
            article.title.toLowerCase().includes(currentSearchTerm) ||
            article.excerpt.toLowerCase().includes(currentSearchTerm) ||
            article.content.toLowerCase().includes(currentSearchTerm);
        
        return matchesCategory && matchesSearch;
    });
    
    renderNewsGrid(filteredNews);
}

/**
 * Clear search
 */
async function clearSearch() {
    searchInput.value = '';
    currentSearchTerm = '';
    currentCategory = 'all';
    
    // Reset active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector('[data-category="all"]').classList.add('active');
    
    // Fetch fresh data
    await fetchNewsData('all', true);
}

/**
 * Format date
 * @param {string} dateString - Date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Open news modal (placeholder for future implementation)
 * @param {number} newsId - News article ID
 */
function openNewsModal(newsId) {
    const article = allNewsData.find(item => item.id === newsId);
    if (article) {
        // For now, show alert. In future, implement a proper modal
        if (article.url && article.url !== '#') {
            window.open(article.url, '_blank');
        } else {
            alert(`${article.title}\n\n${article.content}\n\nSource: ${article.source}\nDate: ${formatDate(article.date)}`);
        }
    }
}

/**
 * Get news by category
 * @param {string} category - Category name
 * @returns {Array} Filtered news array
 */
function getNewsByCategory(category) {
    return allNewsData.filter(article => article.category === category);
}

/**
 * Get latest news
 * @param {number} limit - Number of articles to return
 * @returns {Array} Latest news array
 */
function getLatestNews(limit = 5) {
    return allNewsData
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, limit);
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePage);

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializePage,
        filterNews,
        searchNews,
        clearSearch,
        getNewsByCategory,
        getLatestNews,
        formatDate
    };
}
