// Kisan Mitra - Mandi Prices Dashboard JavaScript

// Configuration - Backend API endpoint
const BACKEND_API_URL = 'http://localhost:5000/api';

// DOM Elements
const refreshBtn = document.getElementById('refreshBtn');
const refreshText = document.getElementById('refreshText');
const refreshSpinner = document.getElementById('refreshSpinner');
const statusMessage = document.getElementById('statusMessage');
const priceTableBody = document.getElementById('priceTableBody');
const lastUpdated = document.getElementById('lastUpdated');

// Filter Elements
const stateFilter = document.getElementById('stateFilter');
const districtFilter = document.getElementById('districtFilter');
const commodityFilter = document.getElementById('commodityFilter');

// Global variables
let allPriceData = [];
let filteredData = [];
let isRefreshing = false; // guard to avoid overwriting fresh data
let latestRequestId = 0; // incrementing token to ignore stale responses

// Static list of Indian States and Union Territories
const INDIAN_STATES_AND_UTS = [
    // States
    'Andhra Pradesh',
    'Arunachal Pradesh',
    'Assam',
    'Bihar',
    'Chhattisgarh',
    'Goa',
    'Gujarat',
    'Haryana',
    'Himachal Pradesh',
    'Jharkhand',
    'Karnataka',
    'Kerala',
    'Madhya Pradesh',
    'Maharashtra',
    'Manipur',
    'Meghalaya',
    'Mizoram',
    'Nagaland',
    'Odisha',
    'Punjab',
    'Rajasthan',
    'Sikkim',
    'Tamil Nadu',
    'Telangana',
    'Tripura',
    'Uttar Pradesh',
    'Uttarakhand',
    'West Bengal',
    // Union Territories
    'Andaman and Nicobar Islands',
    'Chandigarh',
    'Dadra and Nagar Haveli and Daman and Diu',
    'Delhi',
    'Jammu and Kashmir',
    'Ladakh',
    'Lakshadweep',
    'Puducherry'
].sort();

function populateStateFilterWithAllStates() {
    if (!stateFilter) return;
    populateSelect(stateFilter, INDIAN_STATES_AND_UTS);
}

/**
 * Show status message
 * @param {string} message - The message to display
 * @param {string} type - The type of message (loading, error, success)
 */
function showStatusMessage(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    
    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 3000);
    }
}

/**
 * Hide status message
 */
function hideStatusMessage() {
    statusMessage.style.display = 'none';
}

/**
 * Set loading state for refresh button
 * @param {boolean} isLoading - Whether to show loading state
 */
function setLoadingState(isLoading) {
    refreshBtn.disabled = isLoading;
    refreshSpinner.style.display = isLoading ? 'inline-block' : 'none';
    refreshText.textContent = isLoading ? 'Loading...' : 'Update Mandi Prices';
}

/**
 * Update last updated timestamp
 */
function updateLastUpdatedTime() {
    const now = new Date();
    const timeString = now.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Kolkata'
    });
    lastUpdated.textContent = `Last updated: ${timeString}`;
}

/**
 * Render price table with data
 * @param {Array} prices - Array of crop price objects
 */
function renderPriceTable(prices) {
    priceTableBody.innerHTML = '';
    
    if (prices.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="4" style="text-align: center; color: #666; padding: 40px; font-style: italic;">
                No data found for the selected filters. Try adjusting your search criteria.
            </td>
        `;
        priceTableBody.appendChild(row);
        return;
    }
    
    prices.forEach((crop, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="crop-name">${crop.name}</td>
            <td class="state">${crop.state || 'N/A'}</td>
            <td class="district">${crop.district || 'N/A'}</td>
            <td class="price">${crop.price.toFixed(2)}</td>
        `;
        
        // Add animation delay
        row.style.animationDelay = `${index * 0.1}s`;
        
        priceTableBody.appendChild(row);
    });
}

/**
 * Fetch market prices from backend API
 */
async function fetchMarketPrices(force = false) {
    try {
        isRefreshing = true;
        const requestId = ++latestRequestId;
        setLoadingState(true);
        showStatusMessage('Fetching live mandi prices...', 'loading');
        
        // Build query parameters for filters
        const params = new URLSearchParams();
        if (stateFilter.value) params.append('state', stateFilter.value);
        if (districtFilter.value) params.append('district', districtFilter.value);
        if (commodityFilter.value) params.append('commodity', commodityFilter.value);
        if (force) params.append('force', 'true');
        params.append('_', Date.now().toString());
        
        // Make API call to backend
        const response = await fetch(`${BACKEND_API_URL}/mandi-prices?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Failed to fetch prices');
        }
        
        if (!data.prices || data.prices.length === 0) {
            throw new Error('No price data available');
        }
        
        // Ignore stale responses
        if (requestId !== latestRequestId) {
            return;
        }
        
        // Store all data globally
        allPriceData = data.prices;
        filteredData = [...allPriceData];
        
        // Populate filter options
        populateFilters();
        
        // Apply current filters and render
        applyFilters();
        updateLastUpdatedTime();
        showStatusMessage('Live mandi prices updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error fetching market prices:', error);
        
        // Show detailed error information
        let errorMessage = 'Unable to fetch real-time prices. ';
        
        if (error.message.includes('Failed to fetch') || error.message.includes('network')) {
            errorMessage += 'Backend server connection issue. ';
        } else if (error.message.includes('500')) {
            errorMessage += 'Server error occurred. ';
        } else if (error.message.includes('404')) {
            errorMessage += 'API endpoint not found. ';
        }
        
        errorMessage += 'Please try again or check if the backend server is running.';
        
        showStatusMessage(`⚠️ ${errorMessage}`, 'error');
        
        // Fallback: Show sample mandi data with note (expanded dataset)
        const fallbackData = [
            // Punjab
            { name: 'Wheat', price: 22150.00, state: 'Punjabi', district: 'Amritsar', market: 'APMC Amritsar' },
            { name: 'Rice', price: 1950.00, state: 'Punjab', district: 'Ludhiana', market: 'APMC Ludhiana' },
            { name: 'Maize', price: 2750.00, state: 'Punjab', district: 'Jalandhar', market: 'APMC Jalandhar' },
            
            // Haryana
            { name: 'Rice', price: 1850.00, state: 'Haryana', district: 'Karnal', market: 'APMC Karnal' },
            { name: 'Wheat', price: 2100.00, state: 'Haryana', district: 'Rohtak', market: 'APMC Rohtak' },
            { name: 'Mustard', price: 5100.00, state: 'Haryana', district: 'Hisar', market: 'APMC Hisar' },
            
            // Madhya Pradesh
            { name: 'Maize', price: 1650.00, state: 'Madhya Pradesh', district: 'Indore', market: 'APMC Indore' },
            { name: 'Soybean', price: 4200.00, state: 'Madhya Pradesh', district: 'Bhopal', market: 'APMC Bhopal' },
            { name: 'Wheat', price: 2080.00, state: 'Madhya Pradesh', district: 'Gwalior', market: 'APMC Gwalior' },
            
            // Uttar Pradesh
            { name: 'Sugarcane', price: 325.00, state: 'Uttar Pradesh', district: 'Meerut', market: 'APMC Meerut' },
            { name: 'Potato', price: 28.00, state: 'Uttar Pradesh', district: 'Agra', market: 'APMC Agra' },
            { name: 'Rice', price: 1900.00, state: 'Uttar Pradesh', district: 'Lucknow', market: 'APMC Lucknow' },
            { name: 'Wheat', price: 2120.00, state: 'Uttar Pradesh', district: 'Kanpur', market: 'APMC Kanpur' },
            
            // Gujarat
            { name: 'Cotton', price: 6500.00, state: 'Gujarat', district: 'Ahmedabad', market: 'APMC Ahmedabad' },
            { name: 'Groundnut', price: 5800.00, state: 'Gujarat', district: 'Surat', market: 'APMC Surat' },
            { name: 'Wheat', price: 2090.00, state: 'Gujarat', district: 'Vadodara', market: 'APMC Vadodara' },
            
            // Rajasthan
            { name: 'Groundnut', price: 5800.00, state: 'Rajasthan', district: 'Kota', market: 'APMC Kota' },
            { name: 'Mustard', price: 5200.00, state: 'Rajasthan', district: 'Bharatpur', market: 'APMC Bharatpur' },
            { name: 'Wheat', price: 2070.00, state: 'Rajasthan', district: 'Jaipur', market: 'APMC Jaipur' },
            
            // Maharashtra
            { name: 'Soybean', price: 4200.00, state: 'Maharashtra', district: 'Nagpur', market: 'APMC Nagpur' },
            { name: 'Onion', price: 32.75, state: 'Maharashtra', district: 'Nashik', market: 'APMC Nashik' },
            { name: 'Cotton', price: 6450.00, state: 'Maharashtra', district: 'Pune', market: 'APMC Pune' },
            { name: 'Wheat', price: 2060.00, state: 'Maharashtra', district: 'Mumbai', market: 'APMC Mumbai' },
            
            // Karnataka
            { name: 'Tomato', price: 45.50, state: 'Karnataka', district: 'Bangalore', market: 'APMC Bangalore' },
            { name: 'Rice', price: 1880.00, state: 'Karnataka', district: 'Mysore', market: 'APMC Mysore' },
            { name: 'Maize', price: 1680.00, state: 'Karnataka', district: 'Hubli', market: 'APMC Hubli' },
            
            // Telangana
            { name: 'Turmeric', price: 125.00, state: 'Telangana', district: 'Nizamabad', market: 'APMC Nizamabad' },
            { name: 'Cotton', price: 6480.00, state: 'Telangana', district: 'Hyderabad', market: 'APMC Hyderabad' },
            { name: 'Rice', price: 1920.00, state: 'Telangana', district: 'Warangal', market: 'APMC Warangal' },
            
            // Andhra Pradesh
            { name: 'Rice', price: 1940.00, state: 'Andhra Pradesh', district: 'Vijayawada', market: 'APMC Vijayawada' },
            { name: 'Cotton', price: 6520.00, state: 'Andhra Pradesh', district: 'Guntur', market: 'APMC Guntur' },
            { name: 'Chilli', price: 180.00, state: 'Andhra Pradesh', district: 'Kurnool', market: 'APMC Kurnool' }
        ];
        
        // Store fallback data globally (only if not superseded)
        const requestId = ++latestRequestId;
        allPriceData = fallbackData;
        filteredData = [...allPriceData];
        
        // Populate filter options
        populateFilters();
        
        // Apply current filters and render
        applyFilters();
        
        // Add a note about fallback data
        const noteRow = document.createElement('tr');
        noteRow.innerHTML = `
            <td colspan="4" style="text-align: center; color: #ff9800; padding: 15px; font-style: italic; background: #fff3e0;">
                ⚠️ Showing sample mandi prices - Backend API unavailable
            </td>
        `;
        priceTableBody.appendChild(noteRow);
        
        updateLastUpdatedTime();
        
    } finally {
        setLoadingState(false);
        isRefreshing = false;
    }
}

/**
 * Check backend server health
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${BACKEND_API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('Backend server is healthy');
            return true;
        }
    } catch (error) {
        console.warn('Backend server is not responding:', error.message);
        return false;
    }
    return false;
}

/**
 * Initialize the page
 */
async function initializePage() {
    // Populate State dropdown with all Indian states/UTs upfront
    populateStateFilterWithAllStates();
    // Check if backend is available
    const isBackendHealthy = await checkBackendHealth();
    
    if (!isBackendHealthy) {
        showStatusMessage('⚠️ Backend server not available. Using sample data.', 'error');
        // Load fallback data immediately
        setTimeout(() => {
            fetchMarketPrices();
        }, 1000);
    } else {
        // Load initial data from backend
        fetchMarketPrices();
    }
    
    // Set up auto-refresh every 5 minutes
    setInterval(() => {
        fetchMarketPrices();
    }, 5 * 60 * 1000);
}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePage);

// Add keyboard shortcut for refresh (Ctrl/Cmd + R)
document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        fetchMarketPrices();
    }
});

/**
 * Populate filter dropdowns with unique values from data
 */
function populateFilters() {
    if (!allPriceData || allPriceData.length === 0) return;
    
    // Keep state filter as the predefined full list; don't overwrite here
    // Get unique districts
    const districts = [...new Set(allPriceData.map(item => item.district).filter(district => district && district.trim()))].sort();
    populateSelect(districtFilter, districts);
    
    // Get unique commodities
    const commodities = [...new Set(allPriceData.map(item => item.name).filter(name => name && name.trim()))].sort();
    populateSelect(commodityFilter, commodities);
}

/**
 * Populate a select element with options
 * @param {HTMLSelectElement} selectElement - The select element to populate
 * @param {Array} options - Array of option values
 */
function populateSelect(selectElement, options) {
    // Keep the first option (All States/Districts/Commodities)
    const firstOption = selectElement.firstElementChild;
    selectElement.innerHTML = '';
    selectElement.appendChild(firstOption);
    
    // Add new options
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
}

/**
 * Apply current filters to data and render table
 */
async function applyFilters() {
    const requestId = ++latestRequestId;
    const selectedState = stateFilter.value;
    const selectedDistrict = districtFilter.value;
    const selectedCommodity = commodityFilter.value;
    
    // Show loading state when applying filters
    showStatusMessage('Applying filters and fetching data...', 'loading');
    
    try {
        // Try to fetch fresh data from backend with current filters
        const params = new URLSearchParams();
        if (selectedState) params.append('state', selectedState);
        if (selectedDistrict) params.append('district', selectedDistrict);
        if (selectedCommodity) params.append('commodity', selectedCommodity);
        
        const response = await fetch(`${BACKEND_API_URL}/mandi-prices?${params.toString()}`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.prices && data.prices.length > 0) {
                // Update with fresh filtered data from backend
                filteredData = data.prices;
                // Do NOT overwrite global dataset with filtered subset
                
                // Populate filter options with new data
                populateFilters();
                
                // Set the current filter values
                stateFilter.value = selectedState;
                districtFilter.value = selectedDistrict;
                commodityFilter.value = selectedCommodity;
                
                // Ignore stale responses
                if (requestId === latestRequestId) {
                    renderPriceTable(filteredData);
                    showStatusMessage(`Found ${filteredData.length} records matching your filters`, 'success');
                }
                return;
            }
        }
    } catch (error) {
        console.log('Backend filter request failed, using client-side filtering');
    }
    
    // Fallback to client-side filtering if backend is unavailable
    if (!allPriceData || allPriceData.length === 0) {
        showStatusMessage('No data available. Please refresh to load data first.', 'error');
        return;
    }
    
    // Update district filter based on selected state
    if (selectedState) {
        const filteredDistricts = allPriceData
            .filter(item => item.state === selectedState)
            .map(item => item.district)
            .filter(district => district && district.trim());
        
        const uniqueDistricts = [...new Set(filteredDistricts)].sort();
        populateSelect(districtFilter, uniqueDistricts);
    } else {
        // If no state selected, show all districts
        const allDistricts = [...new Set(allPriceData.map(item => item.district).filter(district => district && district.trim()))].sort();
        populateSelect(districtFilter, allDistricts);
    }
    
    // Filter data based on selections (client-side filtering)
    filteredData = allPriceData.filter(item => {
        const stateMatch = !selectedState || item.state === selectedState;
        const districtMatch = !selectedDistrict || item.district === selectedDistrict;
        const commodityMatch = !selectedCommodity || item.name === selectedCommodity;
        
        return stateMatch && districtMatch && commodityMatch;
    });
    
    // Render filtered data
    renderPriceTable(filteredData);
    
    // Update status message
    if (filteredData.length === 0) {
        showStatusMessage('No records found matching your filters. Try different criteria.', 'error');
    } else {
        const count = filteredData.length;
        const total = allPriceData.length;
        showStatusMessage(`Showing ${count} of ${total} records (client-side filtering)`, 'success');
    }
}

/**
 * Clear all filters and show all data
 */
function clearFilters() {
    stateFilter.value = '';
    districtFilter.value = '';
    commodityFilter.value = '';
    
    // Repopulate all filters
    populateFilters();
    
    // Show all data
    filteredData = [...allPriceData];
    renderPriceTable(filteredData);
    
    showStatusMessage('All filters cleared', 'success');
}

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fetchMarketPrices,
        renderPriceTable,
        showStatusMessage,
        setLoadingState,
        updateLastUpdatedTime,
        applyFilters,
        clearFilters,
        populateFilters
    };
}
