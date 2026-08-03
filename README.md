# 🌾 Kisan Mitra - Dashboard for Farmers

A responsive, multi-module web application designed to help farmers make informed decisions by providing live mandi prices, the latest agricultural news, government schemes, and a multilingual feedback system.

---

## 🎯 Features

### 💻 Frontend
- **Responsive Design**: Mobile-first UI that works flawlessly on desktop, tablet, and mobile.
- **Multilingual Support**: Google Translate integrated for regional languages.
- **Live Data Updates**: Real-time mandi prices and news updates.
- **Modern UI**: Clean, agriculture-themed design with intuitive navigation.

### ⚙️ Backend (Flask API)
- **Data Integration**: Fetches real-time data from `data.gov.in` and `NewsAPI`.
- **Intelligent Caching**: Reduces API calls and improves load times.
- **Graceful Fallbacks**: Provides realistic sample data if external APIs are unavailable.
- **CSV Data Storage**: Stores user feedback securely in a local CSV file.

---

## 📁 Project Structure

```text
Kisan-Mitra/
├── index.html           # Main HTML file (Live Mandi Prices)
├── styles.css           # Global CSS styling
├── script.js            # Main Frontend JavaScript
├── app.py               # Python Flask backend API
├── requirements.txt     # Python dependencies
├── feedback_data.csv    # Stored user feedback
├── .env                 # Environment variables (API Keys)
├── market-news/         # 📰 Market News module
├── schemes/             # 🏛️ Government schemes module
└── feedback/            # 🗣️ Multilingual Feedback module
```

---

## 🚀 Quick Start Guide

You can run this project in two ways:

### Option 1: Frontend Only (Demonstration Mode)
If you don't want to run the server, simply open `index.html` directly in your web browser. The app will gracefully fall back to displaying realistic sample data for demonstration purposes.

### Option 2: Full Stack (Live Data)

#### 1. Configure Environment Variables
Create a `.env` file in the project root and add your API keys:
```env
DATA_GOV_API_KEY=your_data_gov_in_api_key
NEWS_API_KEY=your_newsapi_key
```

#### 2. Start the Backend Server
Make sure you have Python installed, then run:
```bash
# Install dependencies
pip install -r requirements.txt

# Start the Flask API server
python app.py
```
The backend will start running at `http://localhost:5000`.

#### 3. Launch the App
Open `index.html` in your web browser. It will automatically connect to your local backend and fetch live data!

---

## 🧩 Project Modules

The application is broken down into four easily navigable modules:

### 1. 🌾 Live Mandi Prices (Main Page)
- **Path**: `index.html`
- **Features**: Filter crop prices by State, District, and Commodity. Auto-refreshes every 5 minutes.

### 2. 🏛️ Government Schemes
- **Path**: `schemes/index.html`
- **Features**: Browse and search key agricultural schemes with instant highlighting. Fully client-side.

### 3. 📰 Market News
- **Path**: `market-news/index.html`
- **Features**: Read categorized agricultural news (Policy, Market, Weather, Tech).

### 4. 🗣️ Multilingual Feedback
- **Path**: `feedback/index.html`
- **Features**: 
  - Submit feedback with a 10-digit validated phone number.
  - Built-in **Speech-to-Text (STT)** microphone input!
  - Data is saved securely via the backend to `feedback_data.csv`.

---

## 🔗 API Endpoints (Backend)

The Flask backend exposes the following RESTful endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check to verify server status |
| `/api/mandi-prices` | GET | Fetch all mandi prices (with filters) |
| `/api/mandi-prices/<crop>` | GET | Fetch prices for a specific crop |
| `/api/news` | GET | Fetch categorized agricultural news |
| `/api/stats` | GET | View API caching statistics |
| `/api/feedback/submit` | POST | Submit user feedback |
| `/api/feedback/download` | GET | Download `feedback_data.csv` |

---

## 🔧 Troubleshooting

- **Backend not connecting?** Ensure the Flask server is running on port 5000 and that you accessed the frontend via a local server or directly opened `index.html`.
- **No data showing?** Check your internet connection. If the external APIs fail, the app should automatically display sample data. Check the browser console for specific errors.
- **Feedback not saving?** Ensure the backend is running (`python app.py`). The feedback form requires the backend to process the submission.

---

**Ready to help farmers make informed decisions! 🌾📊**

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
