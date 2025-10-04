# WasteLess - AI-Powered Product Demand Prediction

EcoPredict is an intelligent demand forecasting system for grocery stores that uses machine learning to predict product demand, reduce food waste, and optimize inventory management.

## 🚀 Features

- **AI-Powered Forecasting**: Uses Facebook Prophet for accurate demand predictions
- **Interactive Dashboard**: React-based dashboard with real-time visualizations
- **Multi-Product Support**: Forecasts for various grocery products (Milk, Eggs, Strawberries, etc.)
- **Weather Integration**: Considers weather data for more accurate predictions
- **Waste Reduction**: Helps reduce food waste through better demand planning

## 📁 Project Structure

```
hackHarvard/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   │   └── dashboard.js # Main dashboard component
|   |   |   └── StoreInventory.js # Store Inventory
│   │   ├── App.js          # Main App component
│   │   ├── App.css         # App styles
│   │   └── index.js        # Entry point
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── backend/                # Python backend
│   ├── src/               # Source code
│   │   ├── model.py       # ML model training
│   │   ├── test.py        # Testing utilities
│   │   └── adjust_sales_data.py
│   ├── data/              # Data files
│   │   ├── daily_sales_dataset.csv
│   │   ├── daily_weather_data.csv
│   │   └── store_sales_2024.csv
│   ├── models/            # Trained ML models
│   ├── visualizations/    # Generated charts
│   ├── main.py           # Flask API server
│   ├── predictions.csv   # Generated predictions
│   ├── validation_metrics.csv
│   └── requirements.txt  # Backend dependencies
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Train the models (optional - pre-trained models are included):
   ```bash
   python src/model.py
   ```

5. Start the Flask API server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`

## 🧠 Machine Learning

The system uses Facebook Prophet for time series forecasting with the following features:

- **Seasonality Detection**: Automatically detects weekly patterns
- **Weather Integration**: Considers temperature and precipitation
- **Holiday Effects**: Accounts for holiday impacts on demand
- **Confidence Intervals**: Provides uncertainty estimates

## 📈 Dashboard Features

- **Interactive Charts**: Real-time demand forecasting visualizations
- **Product Selection**: Switch between different products
- **Waste Tracking**: Monitor and reduce food waste
- **Insights**: Environmental impact calculations
- **Responsive Design**: Works on desktop and mobile

Authors: Ana Lopes, Tommy Chen, Madina Sotvoldieva