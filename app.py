# Kisan Mitra - Mandi Prices Backend API
# Flask application for serving live mandi prices

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime
import logging
from functools import wraps
import time

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GOV_API_BASE_URL = 'https://api.data.gov.in/resource/579b464db66ec23bdd000001ae4cb9913454413271869d3735fb2693'
GOV_API_KEY = '579b464db66ec23bdd000001ae4cb9913454413271869d3735fb2693'

# Cache for storing API responses (simple in-memory cache)
price_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': 300  # 5 minutes in seconds
}

def cache_response(data):
    """Cache the API response with timestamp"""
    price_cache['data'] = data
    price_cache['timestamp'] = time.time()

def is_cache_valid():
    """Check if cached data is still valid"""
    if price_cache['data'] is None or price_cache['timestamp'] is None:
        return False
    
    elapsed_time = time.time() - price_cache['timestamp']
    return elapsed_time < price_cache['cache_duration']

def fetch_from_government_api():
    """Fetch data from Indian Government API"""
    try:
        url = f"{GOV_API_BASE_URL}"
        params = {
            'api-key': GOV_API_KEY,
            'format': 'json',
            'limit': 1000  # Increase limit to get more data
        }
        
        logger.info(f"Fetching data from government API: {url}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Successfully fetched {len(data.get('records', []))} records")
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from government API: {str(e)}")
        raise Exception(f"Government API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {str(e)}")
        raise Exception("Invalid JSON response from government API")

def process_price_data(raw_data):
    """Process raw API data into our format"""
    if not raw_data or 'records' not in raw_data:
        return []
    
    processed_prices = []
    
    for record in raw_data['records']:
        try:
            # Extract crop name and price
            name = record.get('commodity', record.get('state', record.get('district', 'Unknown')))
            price = float(record.get('price', record.get('min_price', 0)))
            
            # Filter valid entries
            if name != 'Unknown' and price > 0 and len(name) > 2:
                processed_prices.append({
                    'name': name.strip(),
                    'price': price,
                    'state': record.get('state', ''),
                    'district': record.get('district', ''),
                    'market': record.get('market', ''),
                    'date': record.get('date', '')
                })
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping invalid record: {record}, Error: {str(e)}")
            continue
    
    # Sort by price and return top items
    processed_prices.sort(key=lambda x: x['price'], reverse=True)
    return processed_prices[:20]  # Return top 20 items

def get_fallback_data():
    """Return fallback data when API is unavailable"""
    return [
        # Punjab
        {'name': 'Wheat', 'price': 2150.00, 'state': 'Punjab', 'district': 'Amritsar', 'market': 'APMC Amritsar'},
        {'name': 'Rice', 'price': 1950.00, 'state': 'Punjab', 'district': 'Ludhiana', 'market': 'APMC Ludhiana'},
        {'name': 'Maize', 'price': 1750.00, 'state': 'Punjab', 'district': 'Jalandhar', 'market': 'APMC Jalandhar'},
        
        # Haryana
        {'name': 'Rice', 'price': 1850.00, 'state': 'Haryana', 'district': 'Karnal', 'market': 'APMC Karnal'},
        {'name': 'Wheat', 'price': 2100.00, 'state': 'Haryana', 'district': 'Rohtak', 'market': 'APMC Rohtak'},
        {'name': 'Mustard', 'price': 5100.00, 'state': 'Haryana', 'district': 'Hisar', 'market': 'APMC Hisar'},
        
        # Madhya Pradesh
        {'name': 'Maize', 'price': 1650.00, 'state': 'Madhya Pradesh', 'district': 'Indore', 'market': 'APMC Indore'},
        {'name': 'Soybean', 'price': 4200.00, 'state': 'Madhya Pradesh', 'district': 'Bhopal', 'market': 'APMC Bhopal'},
        {'name': 'Wheat', 'price': 2080.00, 'state': 'Madhya Pradesh', 'district': 'Gwalior', 'market': 'APMC Gwalior'},
        
        # Uttar Pradesh
        {'name': 'Sugarcane', 'price': 325.00, 'state': 'Uttar Pradesh', 'district': 'Meerut', 'market': 'APMC Meerut'},
        {'name': 'Potato', 'price': 28.00, 'state': 'Uttar Pradesh', 'district': 'Agra', 'market': 'APMC Agra'},
        {'name': 'Rice', 'price': 1900.00, 'state': 'Uttar Pradesh', 'district': 'Lucknow', 'market': 'APMC Lucknow'},
        {'name': 'Wheat', 'price': 2120.00, 'state': 'Uttar Pradesh', 'district': 'Kanpur', 'market': 'APMC Kanpur'},
        
        # Gujarat
        {'name': 'Cotton', 'price': 6500.00, 'state': 'Gujarat', 'district': 'Ahmedabad', 'market': 'APMC Ahmedabad'},
        {'name': 'Groundnut', 'price': 5800.00, 'state': 'Gujarat', 'district': 'Surat', 'market': 'APMC Surat'},
        {'name': 'Wheat', 'price': 2090.00, 'state': 'Gujarat', 'district': 'Vadodara', 'market': 'APMC Vadodara'},
        
        # Rajasthan
        {'name': 'Groundnut', 'price': 5800.00, 'state': 'Rajasthan', 'district': 'Kota', 'market': 'APMC Kota'},
        {'name': 'Mustard', 'price': 5200.00, 'state': 'Rajasthan', 'district': 'Bharatpur', 'market': 'APMC Bharatpur'},
        {'name': 'Wheat', 'price': 2070.00, 'state': 'Rajasthan', 'district': 'Jaipur', 'market': 'APMC Jaipur'},
        
        # Maharashtra
        {'name': 'Soybean', 'price': 4200.00, 'state': 'Maharashtra', 'district': 'Nagpur', 'market': 'APMC Nagpur'},
        {'name': 'Onion', 'price': 32.75, 'state': 'Maharashtra', 'district': 'Nashik', 'market': 'APMC Nashik'},
        {'name': 'Cotton', 'price': 6450.00, 'state': 'Maharashtra', 'district': 'Pune', 'market': 'APMC Pune'},
        {'name': 'Wheat', 'price': 2060.00, 'state': 'Maharashtra', 'district': 'Mumbai', 'market': 'APMC Mumbai'},
        
        # Karnataka
        {'name': 'Tomato', 'price': 45.50, 'state': 'Karnataka', 'district': 'Bangalore', 'market': 'APMC Bangalore'},
        {'name': 'Rice', 'price': 1880.00, 'state': 'Karnataka', 'district': 'Mysore', 'market': 'APMC Mysore'},
        {'name': 'Maize', 'price': 1680.00, 'state': 'Karnataka', 'district': 'Hubli', 'market': 'APMC Hubli'},
        
        # Telangana
        {'name': 'Turmeric', 'price': 125.00, 'state': 'Telangana', 'district': 'Nizamabad', 'market': 'APMC Nizamabad'},
        {'name': 'Cotton', 'price': 6480.00, 'state': 'Telangana', 'district': 'Hyderabad', 'market': 'APMC Hyderabad'},
        {'name': 'Rice', 'price': 1920.00, 'state': 'Telangana', 'district': 'Warangal', 'market': 'APMC Warangal'},
        
        # Andhra Pradesh
        {'name': 'Rice', 'price': 1940.00, 'state': 'Andhra Pradesh', 'district': 'Vijayawada', 'market': 'APMC Vijayawada'},
        {'name': 'Cotton', 'price': 6520.00, 'state': 'Andhra Pradesh', 'district': 'Guntur', 'market': 'APMC Guntur'},
        {'name': 'Chilli', 'price': 180.00, 'state': 'Andhra Pradesh', 'district': 'Kurnool', 'market': 'APMC Kurnool'}
    ]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Kisan Mitra Mandi Prices API'
    })

def apply_filters_to_data(data, state_filter, district_filter, commodity_filter):
    """Apply filters to price data"""
    if not data:
        return []
    
    filtered_data = data
    
    # Apply state filter
    if state_filter:
        filtered_data = [item for item in filtered_data if item.get('state', '').lower() == state_filter.lower()]
    
    # Apply district filter
    if district_filter:
        filtered_data = [item for item in filtered_data if item.get('district', '').lower() == district_filter.lower()]
    
    # Apply commodity filter
    if commodity_filter:
        filtered_data = [item for item in filtered_data if item.get('name', '').lower() == commodity_filter.lower()]
    
    return filtered_data

@app.route('/api/mandi-prices', methods=['GET'])
def get_mandi_prices():
    """Get live mandi prices with optional filtering"""
    try:
        # Get filter parameters from query string
        state_filter = request.args.get('state', '').strip()
        district_filter = request.args.get('district', '').strip()
        commodity_filter = request.args.get('commodity', '').strip()
        # Check if we have valid cached data
        if is_cache_valid():
            logger.info("Returning cached data")
            cached_data = price_cache['data']
            
            # Apply filters to cached data
            filtered_data = apply_filters_to_data(cached_data, state_filter, district_filter, commodity_filter)
            
            return jsonify({
                'success': True,
                'prices': filtered_data,
                'source': 'cache',
                'timestamp': datetime.fromtimestamp(price_cache['timestamp']).isoformat(),
                'message': 'Data retrieved from cache',
                'filters_applied': {
                    'state': state_filter,
                    'district': district_filter,
                    'commodity': commodity_filter
                }
            })
        
        # Try to fetch fresh data from government API
        try:
            raw_data = fetch_from_government_api()
            processed_data = process_price_data(raw_data)
            
            if processed_data:
                cache_response(processed_data)
                logger.info(f"Successfully processed {len(processed_data)} price records")
                
                # Apply filters to fresh data
                filtered_data = apply_filters_to_data(processed_data, state_filter, district_filter, commodity_filter)
                
                return jsonify({
                    'success': True,
                    'prices': filtered_data,
                    'source': 'government_api',
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Live data fetched successfully',
                    'filters_applied': {
                        'state': state_filter,
                        'district': district_filter,
                        'commodity': commodity_filter
                    }
                })
            else:
                logger.warning("No valid data processed from government API")
                
        except Exception as api_error:
            logger.error(f"Government API error: {str(api_error)}")
        
        # Fallback to sample data if API fails
        logger.info("Using fallback data")
        fallback_data = get_fallback_data()
        
        # Apply filters to fallback data
        filtered_fallback = apply_filters_to_data(fallback_data, state_filter, district_filter, commodity_filter)
        
        return jsonify({
            'success': True,
            'prices': filtered_fallback,
            'source': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'message': 'Using sample data - Government API unavailable',
            'filters_applied': {
                'state': state_filter,
                'district': district_filter,
                'commodity': commodity_filter
            }
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in get_mandi_prices: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Internal server error'
        }), 500

@app.route('/api/mandi-prices/<crop_name>', methods=['GET'])
def get_crop_price(crop_name):
    """Get specific crop price"""
    try:
        # Get all prices first
        response = get_mandi_prices()
        data = response.get_json()
        
        if not data['success']:
            return jsonify(data), 500
        
        # Filter for specific crop
        crop_prices = [price for price in data['prices'] 
                      if crop_name.lower() in price['name'].lower()]
        
        if not crop_prices:
            return jsonify({
                'success': False,
                'message': f'No prices found for crop: {crop_name}'
            }), 404
        
        return jsonify({
            'success': True,
            'crop': crop_name,
            'prices': crop_prices,
            'timestamp': data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error getting crop price for {crop_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Internal server error'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_api_stats():
    """Get API statistics"""
    try:
        cache_info = {
            'has_cached_data': price_cache['data'] is not None,
            'cache_timestamp': price_cache['timestamp'],
            'cache_valid': is_cache_valid(),
            'cache_duration': price_cache['cache_duration']
        }
        
        if cache_info['has_cached_data']:
            cache_info['data_count'] = len(price_cache['data'])
        
        return jsonify({
            'success': True,
            'cache_info': cache_info,
            'endpoints': {
                'health': '/api/health',
                'mandi_prices': '/api/mandi-prices',
                'crop_price': '/api/mandi-prices/<crop_name>',
                'stats': '/api/stats'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting API stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Kisan Mitra Mandi Prices API Server...")
    logger.info("Available endpoints:")
    logger.info("  GET /api/health - Health check")
    logger.info("  GET /api/mandi-prices - Get all mandi prices")
    logger.info("  GET /api/mandi-prices/<crop> - Get specific crop price")
    logger.info("  GET /api/stats - Get API statistics")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,  # Set to False in production
        threaded=True
    )
