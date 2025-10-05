import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from flask import jsonify

class Database:
    """Data access layer for sales, weather, and predictions"""
    
    def __init__(self):
        self.sales_df = pd.read_csv('data/daily_sales_dataset.csv')
        self.sales_df['date'] = pd.to_datetime(self.sales_df['date'])
        
        self.weather_df = pd.read_csv('data/daily_weather_data.csv')
        self.weather_df['date'] = pd.to_datetime(self.weather_df['date'])
        
        self.models = self._load_models()
    
    def _load_models(self) -> Dict:
        """Load trained Prophet models"""
        models = {}
        model_dir = 'models'
        
        if not os.path.exists(model_dir):
            return models
        
        for filename in os.listdir(model_dir):
            if filename.endswith('_model.pkl'):
                product = filename.replace('_model.pkl', '').replace('_', ' ')
                try:
                    with open(os.path.join(model_dir, filename), 'rb') as f:
                        models[product] = pickle.load(f)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return models
    
    def get_all_products(self) -> List[str]:
        """Get list of all products"""
        return self.sales_df['product'].unique().tolist()
    
    def get_current_status(self, product: str, date: Optional[datetime] = None) -> Dict:
        """Get current sales status for a product on a specific date"""
        if date is None:
            date = datetime.now().date()
        
        # Get sales for this date
        sales_today = self.sales_df[
            (self.sales_df['product'] == product) & 
            (self.sales_df['date'].dt.date == date)
        ]
        
        if sales_today.empty:
            # Get most recent data
            sales_today = self.sales_df[
                self.sales_df['product'] == product
            ].tail(1)
        
        if sales_today.empty:
            return {"error": f"No data found for {product}"}
        
        row = sales_today.iloc[0]
        result = {
            "product": product,
            "date": str(row['date'].date()),
            "items_sold": int(row['items_sold']),
            "items_wasted": int(row['items_wasted']),
            "is_weekend": bool(row['is_weekend']),
            "is_holiday": bool(row['is_holiday'])
        }
        return convert_types(result)

    def get_sales_trend(self, product: str, days: int = 30) -> Dict:
        """Get sales trend for past N days"""
        product_data = self.sales_df[self.sales_df['product'] == product].copy()
        product_data = product_data.sort_values('date').tail(days)
        
        trend_data = []
        for _, row in product_data.iterrows():
            trend_data.append({
                "date": str(row['date'].date()),
                "items_sold": int(row['items_sold']),
                "items_wasted": int(row['items_wasted']),
                "day_of_week": row['date'].strftime("%A")
            })
        
        # Calculate statistics
        avg_sold = product_data['items_sold'].mean()
        avg_wasted = product_data['items_wasted'].mean()
        waste_rate = (product_data['items_wasted'].sum() / 
                     (product_data['items_sold'].sum() + product_data['items_wasted'].sum()) * 100)
        
        result = {
            "product": product,
            "period_days": days,
            "trend_data": trend_data,
            "statistics": {
                "avg_daily_sold": round(avg_sold, 1),
                "avg_daily_wasted": round(avg_wasted, 1),
                "waste_rate_pct": round(waste_rate, 1),
                "total_sold": int(product_data['items_sold'].sum()),
                "total_wasted": int(product_data['items_wasted'].sum())
            }
        }
        return convert_types(result)

    def get_prophet_prediction(self, product: str, days_ahead: int = 7) -> Dict:
        """Get Prophet forecast for next N days using real weather data"""
        if product not in self.models:
            return {"error": f"No trained model for {product}"}
        
        model = self.models[product]
        
        # Try to get real weather data, fallback to mock if needed
        try:
            weather_data = weather_service.get_forecast(days_ahead)
            weather_source = "OpenWeather API"
        except Exception as e:
            print(f"Weather API failed, using mock data: {str(e)}")
            weather_data = generate_mock_weather_data(days_ahead)
            weather_source = "Mock Data (API unavailable)"
        
        # Create future dataframe with weather data
        last_date = self.sales_df[self.sales_df['product'] == product]['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead)
        
        future = pd.DataFrame({
            'ds': future_dates,
            'temperature': [day['temperature'] for day in weather_data],
            'precipitation': [day['precipitation'] for day in weather_data],
            'is_weekend': [1 if d.dayofweek >= 5 else 0 for d in future_dates],
            'is_holiday': [0] * days_ahead
        })
        
        # Use model.predict() with weather data
        try:
            forecast = model.predict(future)
            
            predictions = []
            for i, row in forecast.iterrows():
                weather_day = weather_data[i]
                predictions.append({
                    "date": str(row['ds'].date()),
                    "day_of_week": row['ds'].strftime("%A"),
                    "predicted_demand": round(row['yhat'], 1),
                    "lower_bound": round(row['yhat_lower'], 1),
                    "upper_bound": round(row['yhat_upper'], 1),
                    "weather_description": weather_day['description'],
                    "temperature": weather_day['temperature'],
                    "precipitation": weather_day['precipitation'],
                    "is_weekend": bool(row['ds'].dayofweek >= 5)
                })
            
            result = {
                "product": product,
                "forecast_days": days_ahead,
                "predictions": predictions,
                "weather_source": weather_source,
                "total_predicted": round(forecast['yhat'].sum(), 1)
            }
            return convert_types(result)
            
        except Exception as e:
            return {"error": f"Prophet prediction failed: {str(e)}"}

    def get_weather_correlation(self, product: str) -> Dict:
        """Analyze weather's impact on sales"""
        product_data = self.sales_df[self.sales_df['product'] == product].copy()
        
        # Merge with weather
        merged = product_data.merge(self.weather_df, on='date', how='left')
        
        if merged.empty or 'temperature_2m_mean' not in merged.columns:
            return {"error": "Weather data not available"}
        
        # Calculate correlation
        temp_corr = merged['items_sold'].corr(merged['temperature_2m_mean'])
        rain_days = merged[merged['precipitation_sum'] > 0.1]
        
        avg_sales_rain = rain_days['items_sold'].mean() if not rain_days.empty else 0
        avg_sales_no_rain = merged[merged['precipitation_sum'] <= 0.1]['items_sold'].mean()
        
        rain_impact_pct = ((avg_sales_rain - avg_sales_no_rain) / avg_sales_no_rain * 100) if avg_sales_no_rain > 0 else 0
        
        result = {
            "product": product,
            "temperature_correlation": round(temp_corr, 3),
            "rain_impact_pct": round(rain_impact_pct, 1),
            "avg_sales_rainy_days": round(avg_sales_rain, 1),
            "avg_sales_clear_days": round(avg_sales_no_rain, 1),
            "interpretation": self._interpret_weather_impact(temp_corr, rain_impact_pct)
        }
        return convert_types(result)

    def _interpret_weather_impact(self, temp_corr: float, rain_impact: float) -> str:
        """Generate human-readable interpretation"""
        parts = []
        
        if abs(temp_corr) > 0.3:
            if temp_corr > 0:
                parts.append(f"Sales increase {abs(temp_corr)*100:.0f}% with warmer weather")
            else:
                parts.append(f"Sales decrease {abs(temp_corr)*100:.0f}% with warmer weather")
        else:
            parts.append("Temperature has minimal impact on sales")
        
        if rain_impact < -10:
            parts.append(f"Rain reduces sales by ~{abs(rain_impact):.0f}%")
        elif rain_impact > 10:
            parts.append(f"Rain increases sales by ~{rain_impact:.0f}%")
        else:
            parts.append("Rain has minimal impact")
        
        return ". ".join(parts)
    
    def get_discount_recommendation(self, product: str) -> Dict:
        """Calculate if product needs discounting"""
        # Get latest data
        latest = self.sales_df[self.sales_df['product'] == product].tail(7)
        
        if latest.empty:
            return {"error": f"No recent data for {product}"}
        
        # Calculate waste rate
        total_sold = latest['items_sold'].sum()
        total_wasted = latest['items_wasted'].sum()
        waste_rate = (total_wasted / (total_sold + total_wasted) * 100) if (total_sold + total_wasted) > 0 else 0
        
        # Get prediction for today
        prediction = self.get_prophet_prediction(product, days_ahead=1)
        
        if "error" not in prediction and prediction['predictions']:
            predicted_today = prediction['predictions'][0]['predicted_demand']
            actual_today = latest.iloc[-1]['items_sold']
            performance = (actual_today / predicted_today * 100) if predicted_today > 0 else 100
        else:
            performance = 100
        
        # Decision logic
        needs_discount = waste_rate > 15 or performance < 70
        
        if needs_discount:
            if waste_rate > 25:
                discount = 30
                urgency = "high"
            elif waste_rate > 15:
                discount = 20
                urgency = "medium"
            else:
                discount = 15
                urgency = "low"
        else:
            discount = 0
            urgency = "none"
        
        result = {
            "product": product,
            "needs_discount": needs_discount,
            "recommended_discount_pct": discount,
            "urgency": urgency,
            "waste_rate_pct": round(waste_rate, 1),
            "performance_vs_prediction_pct": round(performance, 1),
            "reasoning": self._generate_discount_reasoning(waste_rate, performance, urgency)
        }
        return convert_types(result)
    
    def _generate_discount_reasoning(self, waste_rate: float, performance: float, urgency: str) -> str:
        """Generate reasoning for discount recommendation"""
        if urgency == "none":
            return "Product is performing well with low waste"
        
        reasons = []
        if waste_rate > 15:
            reasons.append(f"High waste rate ({waste_rate:.0f}%)")
        if performance < 70:
            reasons.append(f"Underperforming vs forecast ({performance:.0f}%)")
        
        return " and ".join(reasons)

import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from flask import jsonify
from weather_service import weather_service

def generate_mock_weather_data(days_ahead=7):
    """Generate realistic mock weather data for predictions"""
    
    # Define weather scenarios with good variety
    weather_scenarios = [
        {"description": "Sunny and Hot", "temp": 78, "precip": 0.0},
        {"description": "Warm and Clear", "temp": 68, "precip": 0.0},
        {"description": "Cool and Rainy", "temp": 45, "precip": 0.8},
        {"description": "Cold and Dry", "temp": 32, "precip": 0.0},
        {"description": "Mild with Light Rain", "temp": 55, "precip": 0.2},
        {"description": "Hot and Humid", "temp": 82, "precip": 0.1},
        {"description": "Cold and Snowy", "temp": 28, "precip": 1.2}
    ]
    
    # Use first 'days_ahead' scenarios, cycling if needed
    weather_data = []
    for i in range(days_ahead):
        scenario = weather_scenarios[i % len(weather_scenarios)]
        weather_data.append({
            "day": i + 1,
            "temperature": scenario["temp"],
            "precipitation": scenario["precip"],
            "description": scenario["description"]
        })
    
    return weather_data

def convert_types(obj):
    if isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(i) for i in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    return obj

