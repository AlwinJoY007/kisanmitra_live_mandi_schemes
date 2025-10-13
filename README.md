# 🌾 Kisan Mitra - Mandi Prices Dashboard

A responsive web application that displays live mandi prices for farmers to make informed selling decisions.

## 📁 Project Structure

```
Kisan-Mitra/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── script.js           # Frontend JavaScript
├── app.py              # Python Flask backend API
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── market.html         # Original combined file (backup)
```

## 🚀 Quick Start

### Option 1: Frontend Only (No Backend)
1. Open `index.html` directly in your web browser
2. The page will show sample data with a note about backend being unavailable
3. Perfect for demonstration purposes

### Option 2: Full Stack (Frontend + Backend)

#### Backend Setup:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5000` or open index.html (most probably working)

#### Frontend Setup:
1. Open `index.html` in your web browser
2. The page will automatically connect to the backend API
3. Real-time mandi prices will be fetched and displayed

## 🎯 Features

### ✅ Frontend Features:
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Live Price Updates** - Real-time mandi prices from Indian Government API
- **Auto-refresh** - Updates every 5 minutes automatically
- **Loading States** - Visual feedback during data fetching
- **Error Handling** - Graceful fallback to sample data
- **Modern UI** - Clean, agriculture-themed design with green colors

### ✅ Backend Features:
- **Flask API** - RESTful endpoints for data serving
- **Government API Integration** - Fetches real data from data.gov.in
- **Caching** - 5-minute cache to reduce API calls
- **Fallback Data** - Sample data when API is unavailable
- **CORS Enabled** - Allows frontend communication
- **Health Check** - API status monitoring

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/mandi-prices` | GET | Get all mandi prices |
| `/api/mandi-prices/<crop>` | GET | Get specific crop price |
| `/api/stats` | GET | API statistics |

## 🎨 Customization

### Frontend Customization:
- **Colors**: Edit `styles.css` to change the green theme
- **API URL**: Modify `BACKEND_API_URL` in `script.js`
- **Content**: Update text in `index.html`

### Backend Customization:
- **API Key**: Update `GOV_API_KEY` in `app.py`
- **Cache Duration**: Modify `cache_duration` in `app.py`
- **Data Processing**: Customize `process_price_data()` function

## 📱 Integration with Main Project

To integrate this into your main project:

1. **Copy Files**:
   ```bash
   # Copy these files to your main project
   cp index.html your-project/
   cp styles.css your-project/assets/css/
   cp script.js your-project/assets/js/
   ```

2. **Update HTML**:
   - Include the CSS: `<link rel="stylesheet" href="styles.css">`
   - Include the JS: `<script src="script.js"></script>`
   - Copy the HTML structure into your main page

3. **Update API URL**:
   - Change `BACKEND_API_URL` in `script.js` to your backend URL

## 🛠️ Technical Details

### Frontend:
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox and animations
- **Vanilla JavaScript** - No frameworks, pure JS
- **Responsive Design** - Mobile-first approach

### Backend:
- **Flask** - Lightweight Python web framework
- **CORS** - Cross-origin resource sharing enabled
- **Caching** - In-memory cache for performance
- **Error Handling** - Comprehensive error management

## 🔧 Troubleshooting

### Common Issues:

1. **Backend not connecting**:
   - Check if Flask server is running on port 5000
   - Verify `BACKEND_API_URL` in `script.js`

2. **No data showing**:
   - Check browser console for errors
   - Verify internet connection
   - Backend will show sample data as fallback

3. **CORS errors**:
   - Backend has CORS enabled
   - If issues persist, run frontend on a local server

### Development Tips:
- Use browser developer tools to debug
- Check console logs for API responses
- Test with sample data first

## 📞 Support

For issues or questions:
1. Check the browser console for error messages
2. Verify all files are in the correct locations
3. Ensure Python dependencies are installed correctly

## 🎯 Demo

The application is designed for hackathon demonstrations and can be easily customized for different agricultural data sources or regions.

---

**Ready to help farmers make informed decisions! 🌾📊**
