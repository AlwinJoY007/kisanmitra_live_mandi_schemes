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
import os
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env (project root)
load_dotenv()

# Configuration
# Resource: Variety-wise Daily Market Prices Data of Commodity
GOV_API_BASE_URL = 'https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24'
# IMPORTANT: Set your personal API key in the environment variable DATA_GOV_API_KEY
GOV_API_KEY = os.getenv('DATA_GOV_API_KEY', '').strip()

# News API Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '').strip()
NEWS_API_URL = 'https://newsapi.org/v2/everything'

# Cache for storing API responses (simple in-memory cache)
price_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': 300  # 5 minutes in seconds
}

news_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': 1800  # 30 minutes in seconds
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

def fetch_diverse_data(limit=50):
    """Fetch diverse data from multiple states when no filters are applied"""
    try:
        logger.info("Fetching diverse data from multiple states (no filters applied)")
        
        # List of major Indian states to get diverse data
        major_states = ['Karnataka', 'Punjab', 'Maharashtra', 'Tamil Nadu', 'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Madhya Pradesh']
        
        all_records = []
        records_per_state = max(5, limit // len(major_states))
        
        for state in major_states:
            try:
                params = {
                    'api-key': GOV_API_KEY,
                    'format': 'json',
                    'limit': records_per_state,
                    'offset': 0,
                    'filters[State]': state
                }
                
                logger.info(f"Fetching data for state: {state}")
                response = requests.get(GOV_API_BASE_URL, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'records' in data and data['records']:
                        all_records.extend(data['records'])
                        logger.info(f"Fetched {len(data['records'])} records from {state}")
                    else:
                        logger.warning(f"No records found for {state}")
                else:
                    logger.warning(f"Failed to fetch data for {state}: HTTP {response.status_code}")
                
            except Exception as e:
                logger.warning(f"Failed to fetch data for {state}: {e}")
                continue
        
        # Return combined data
        if all_records:
            logger.info(f"Total diverse records collected: {len(all_records)}")
            return {'records': all_records[:limit]}
        else:
            logger.warning("No diverse data collected, falling back to single API call")
            # Fallback to single API call if diverse fetching fails
            params = {
                'api-key': GOV_API_KEY,
                'format': 'json',
                'limit': limit,
                'offset': 0
            }
            response = requests.get(GOV_API_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        logger.error(f"Error fetching diverse data: {e}")
        raise Exception(f"Failed to fetch diverse data: {str(e)}")

def fetch_from_government_api(state: str = '', district: str = '', commodity: str = '', limit: int = 35):
    """Fetch data from Indian Government API"""
    try:
        if not GOV_API_KEY:
            raise Exception("DATA_GOV_API_KEY not set. Please set your data.gov.in API key in environment.")
        url = f"{GOV_API_BASE_URL}"
        # If no filters are applied, try to get diverse data from multiple states
        if not (state or district or commodity):
            return fetch_diverse_data(limit)
        
        # For filtered requests, use the requested limit
        api_limit = max(1, min(limit, 1000))
        
        params = {
            'api-key': GOV_API_KEY,
            'format': 'json',
            'limit': api_limit,
            'offset': 0
        }
        # Forward filters using data.gov.in expected format
        # Field names based on actual API schema: State, District, Commodity
        if commodity:
            params['filters[Commodity]'] = commodity
            logger.info(f"Applied commodity filter: {commodity}")
        if state:
            params['filters[State]'] = state
            logger.info(f"Applied state filter: {state}")
        if district:
            params['filters[District]'] = district
            logger.info(f"Applied district filter: {district}")
        
        logger.info(f"Fetching data from government API: {url}")
        logger.info(f"API parameters: {params}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        # data.gov.in signals errors via keys
        if isinstance(data, dict) and data.get('status') == 'error':
            msg = data.get('message', 'Unknown API error')
            raise Exception(f"Government API error: {msg}")
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
            # Extract crop name and price using actual API field names
            name = record.get('Commodity', 'Unknown')
            # Use Modal_Price as primary, fallback to Min_Price
            price_str = record.get('Modal_Price') or record.get('Min_Price') or '0'
            price = float(str(price_str).strip() or 0)
            
            # Filter valid entries
            if name != 'Unknown' and price > 0 and len(name) > 2:
                processed_prices.append({
                    'name': name.strip(),
                    'price': price,
                    'state': record.get('State', ''),
                    'district': record.get('District', ''),
                    'market': record.get('Market', ''),
                    'date': record.get('Arrival_Date', '')
                })
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping invalid record: {record}, Error: {str(e)}")
            continue
    
    # Sort by price for consistent ordering; do not slice here
    processed_prices.sort(key=lambda x: x['price'], reverse=True)
    return processed_prices

def cache_news_response(data):
    """Cache the news API response with timestamp"""
    news_cache['data'] = data
    news_cache['timestamp'] = time.time()

def is_news_cache_valid():
    """Check if cached news data is still valid"""
    if news_cache['data'] is None or news_cache['timestamp'] is None:
        return False
    
    elapsed_time = time.time() - news_cache['timestamp']
    return elapsed_time < news_cache['cache_duration']

def fetch_agricultural_news(category='all', limit=20):
    """Fetch agricultural news from NewsAPI"""
    try:
        if not NEWS_API_KEY:
            raise Exception("NEWS_API_KEY not set. Please set your NewsAPI key in environment.")
        
        # Define search queries based on category
        queries = {
            'all': 'agriculture OR farming OR crop OR mandi OR farmer OR MSP OR PM-KISAN',
            'policy': 'agriculture policy OR farming policy OR MSP OR PM-KISAN OR government scheme',
            'market': 'crop prices OR mandi prices OR agricultural market OR commodity prices',
            'weather': 'agriculture weather OR monsoon OR rainfall OR drought OR flood',
            'technology': 'agriculture technology OR farming technology OR precision agriculture OR drone'
        }
        
        query = queries.get(category, queries['all'])
        
        params = {
            'apiKey': NEWS_API_KEY,
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': min(limit, 100),
            'domains': 'timesofindia.indiatimes.com,indianexpress.com,thehindu.com,hindustantimes.com,economic times.com'
        }
        
        logger.info(f"Fetching agricultural news from NewsAPI: {category}")
        response = requests.get(NEWS_API_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get('status') == 'error':
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        
        logger.info(f"Successfully fetched {len(data.get('articles', []))} news articles")
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from NewsAPI: {str(e)}")
        raise Exception(f"NewsAPI request failed: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing NewsAPI JSON response: {str(e)}")
        raise Exception("Invalid JSON response from NewsAPI")

def process_news_data(raw_data):
    """Process raw news API data into our format"""
    if not raw_data or 'articles' not in raw_data:
        return []
    
    processed_news = []
    
    for article in raw_data['articles']:
        try:
            # Extract and clean data
            title = article.get('title', '').strip()
            description = article.get('description', '').strip()
            url = article.get('url', '')
            published_at = article.get('publishedAt', '')
            source = article.get('source', {}).get('name', 'Unknown')
            
            # Determine category based on content
            content_lower = (title + ' ' + description).lower()
            if any(word in content_lower for word in ['policy', 'scheme', 'government', 'msp', 'pm-kisan']):
                category = 'policy'
            elif any(word in content_lower for word in ['price', 'market', 'mandi', 'commodity']):
                category = 'market'
            elif any(word in content_lower for word in ['weather', 'monsoon', 'rainfall', 'drought', 'flood']):
                category = 'weather'
            elif any(word in content_lower for word in ['technology', 'drone', 'ai', 'digital', 'smart']):
                category = 'technology'
            else:
                category = 'market'  # default
            
            # Filter valid articles
            if title and len(title) > 10 and description and len(description) > 20:
                processed_news.append({
                    'id': len(processed_news) + 1,
                    'title': title,
                    'excerpt': description[:200] + '...' if len(description) > 200 else description,
                    'content': description,
                    'category': category,
                    'date': published_at[:10] if published_at else datetime.now().strftime('%Y-%m-%d'),
                    'source': source,
                    'url': url,
                    'image': '📰'  # Default emoji
                })
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping invalid news article: {article}, Error: {str(e)}")
            continue
    
    # Sort by date (newest first)
    processed_news.sort(key=lambda x: x['date'], reverse=True)
    return processed_news

def get_fallback_news():
    """Return fallback news data when API is unavailable"""
    return [
        {
            'id': 1,
            'title': 'Government Announces New MSP for Kharif Crops 2024-25',
            'excerpt': 'The Cabinet Committee on Economic Affairs has approved new Minimum Support Prices for 14 Kharif crops, with paddy MSP increased by ₹117 per quintal.',
            'content': 'The government has announced significant increases in MSP for major Kharif crops for the 2024-25 season. Paddy MSP has been increased by ₹117 per quintal to ₹2,300 per quintal. Other major increases include maize (₹105), cotton (₹150), and groundnut (₹200). This move is expected to benefit over 10 million farmers across the country.',
            'category': 'policy',
            'date': '2024-01-15',
            'source': 'Ministry of Agriculture',
            'url': '#',
            'image': '🏛️'
        },
        {
            'id': 2,
            'title': 'Wheat Prices Surge 15% Due to Supply Shortage',
            'excerpt': 'Wheat prices have increased significantly across major mandis due to reduced production and increased demand from flour mills.',
            'content': 'Wheat prices have seen a sharp increase of 15% in the last month across major agricultural mandis. The surge is attributed to lower production due to adverse weather conditions and increased demand from flour mills. Experts suggest prices may stabilize once the new crop arrives in March.',
            'category': 'market',
            'date': '2024-01-14',
            'source': 'Agricultural Market Intelligence',
            'url': '#',
            'image': '🌾'
        },
        {
            'id': 3,
            'title': 'IMD Predicts Normal Monsoon for 2024',
            'excerpt': 'India Meteorological Department forecasts normal rainfall for the upcoming monsoon season, which is expected to boost agricultural production.',
            'content': 'The India Meteorological Department has predicted normal monsoon rainfall for 2024, with 96% of the long-period average. This is good news for farmers as normal monsoon is crucial for Kharif crop production. The forecast suggests well-distributed rainfall across most agricultural regions.',
            'category': 'weather',
            'date': '2024-01-13',
            'source': 'India Meteorological Department',
            'url': '#',
            'image': '🌧️'
        }
    ]

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
        force_refresh = request.args.get('force', '').lower() == 'true'
        # Check if we have valid cached data
        if is_cache_valid() and not force_refresh and not (state_filter or district_filter or commodity_filter):
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
        
        # Try to fetch fresh data from government API using query filters first
        try:
            raw_data = fetch_from_government_api(
                state=state_filter,
                district=district_filter,
                commodity=commodity_filter,
                limit=35
            )
            processed_data = process_price_data(raw_data)
            
            if processed_data:
                cache_response(processed_data)
                logger.info(f"Successfully processed {len(processed_data)} price records")
                
                # Already fetched with filters; keep only first 35 (safety)
                filtered_data = processed_data[:35]
                
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
        filtered_fallback = apply_filters_to_data(fallback_data, state_filter, district_filter, commodity_filter)[:35]
        
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

@app.route('/api/news', methods=['GET'])
def get_agricultural_news():
    """Get agricultural news with optional filtering"""
    try:
        # Get filter parameters from query string
        category_filter = request.args.get('category', 'all').strip()
        limit = int(request.args.get('limit', 20))
        force_refresh = request.args.get('force', '').lower() == 'true'
        
        # Check if we have valid cached data
        if is_news_cache_valid() and not force_refresh and category_filter == 'all':
            logger.info("Returning cached news data")
            cached_data = news_cache['data']
            
            # Apply category filter to cached data
            if category_filter != 'all':
                filtered_data = [article for article in cached_data if article.get('category') == category_filter]
            else:
                filtered_data = cached_data
            
            return jsonify({
                'success': True,
                'news': filtered_data[:limit],
                'source': 'cache',
                'timestamp': datetime.fromtimestamp(news_cache['timestamp']).isoformat(),
                'message': 'News data retrieved from cache',
                'filters_applied': {
                    'category': category_filter,
                    'limit': limit
                }
            })
        
        # Try to fetch fresh data from NewsAPI
        try:
            raw_data = fetch_agricultural_news(category=category_filter, limit=limit)
            processed_data = process_news_data(raw_data)
            
            if processed_data:
                cache_news_response(processed_data)
                logger.info(f"Successfully processed {len(processed_data)} news articles")
                
                return jsonify({
                    'success': True,
                    'news': processed_data[:limit],
                    'source': 'newsapi',
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Live news data fetched successfully',
                    'filters_applied': {
                        'category': category_filter,
                        'limit': limit
                    }
                })
            else:
                logger.warning("No valid news articles processed from NewsAPI")
                
        except Exception as api_error:
            logger.error(f"NewsAPI error: {str(api_error)}")
        
        # Fallback to sample data if API fails
        logger.info("Using fallback news data")
        fallback_data = get_fallback_news()
        
        # Apply category filter to fallback data
        if category_filter != 'all':
            filtered_fallback = [article for article in fallback_data if article.get('category') == category_filter]
        else:
            filtered_fallback = fallback_data
        
        return jsonify({
            'success': True,
            'news': filtered_fallback[:limit],
            'source': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'message': 'Using sample news data - NewsAPI unavailable',
            'filters_applied': {
                'category': category_filter,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in get_agricultural_news: {str(e)}")
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
    logger.info("  GET /api/news - Get agricultural news")
    logger.info("  GET /api/stats - Get API statistics")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,  # Set to False in production
        threaded=True
    )
