#!/usr/bin/env python3
"""
Simple test to verify Prophet models can take weather data for predictions
"""

import pandas as pd
import pickle
import os
from datetime import datetime, timedelta

def test_weather_predictions():
    """Test that our Prophet models can accept weather data"""
    
    print("Testing weather-based predictions...")
    
    # Load a trained model (try Strawberries first)
    model_path = 'models/Strawberries_model.pkl'
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        print("Available models:")
        if os.path.exists('models'):
            for f in os.listdir('models'):
                if f.endswith('.pkl'):
                    print(f"  - {f}")
        return
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"Loaded model: {model_path}")
    
    # Create simple 7-day future data with mock weather
    future_dates = pd.date_range(
        start='2025-04-01',  # Start from future date
        periods=7
    )
    
    # Simple weather scenarios for 7 days
    weather_data = [
        {"temp": 75, "precip": 0.0, "desc": "Sunny"},
        {"temp": 68, "precip": 0.0, "desc": "Clear"},
        {"temp": 45, "precip": 0.8, "desc": "Rainy"},
        {"temp": 32, "precip": 0.0, "desc": "Cold"},
        {"temp": 55, "precip": 0.2, "desc": "Light Rain"},
        {"temp": 80, "precip": 0.0, "desc": "Hot"},
        {"temp": 28, "precip": 1.2, "desc": "Snow"}
    ]
    
    # Create future dataframe with weather
    future = pd.DataFrame({
        'ds': future_dates,
        'temperature': [w['temp'] for w in weather_data],
        'precipitation': [w['precip'] for w in weather_data],
        'is_weekend': [1 if d.dayofweek >= 5 else 0 for d in future_dates],
        'is_holiday': [0] * 7
    })
    
    print("\nFuture weather data:")
    for i, row in future.iterrows():
        weather = weather_data[i]
        weekend = " (Weekend)" if row['is_weekend'] else ""
        print(f"  {row['ds'].strftime('%Y-%m-%d')}: {weather['desc']} - {weather['temp']}°F, {weather['precip']}\" rain{weekend}")
    
    # Try to make predictions
    try:
        print("\nMaking predictions...")
        forecast = model.predict(future)
        
        print("\nPredictions with weather impact:")
        print("=" * 70)
        for i, row in forecast.iterrows():
            weather = weather_data[i]
            future_row = future.iloc[i]
            weekend = " (Weekend)" if future_row['is_weekend'] else ""
            
            print(f"{future_row['ds'].strftime('%Y-%m-%d')}: {row['yhat']:.1f} units "
                  f"({row['yhat_lower']:.1f}-{row['yhat_upper']:.1f}) | "
                  f"{weather['desc']} - {weather['temp']}°F{weekend}")
        
        print(f"\nSUCCESS! Model predictions work with weather data.")
        print(f"Average prediction: {forecast['yhat'].mean():.1f} units")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Model might not have been trained with weather regressors.")
        return False

if __name__ == "__main__":
    test_weather_predictions()
