"""
Real-time Weather Service Integration
Fetches current and forecasted weather data for better predictions
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

class WeatherService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather service
        In production, you would use a real weather API like OpenWeatherMap
        """
        self.api_key = api_key or os.getenv('WEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, lat: float = 42.3601, lon: float = -71.0589) -> Dict:
        """
        Get current weather data
        Default coordinates are for Boston (adjust for your location)
        """
        if not self.api_key:
            # Return mock data for development
            return self._get_mock_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'precipitation': data.get('rain', {}).get('1h', 0),
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'cloud_cover': data['clouds']['all'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._get_mock_weather()
    
    def get_weather_forecast(self, days: int = 7, lat: float = 42.3601, lon: float = -71.0589) -> List[Dict]:
        """
        Get weather forecast for the next N days
        """
        if not self.api_key:
            return self._get_mock_forecast(days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecasts = []
            
            for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecasts.append({
                    'date': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d'),
                    'temperature': item['main']['temp'],
                    'precipitation': item.get('rain', {}).get('3h', 0),
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'cloud_cover': item['clouds']['all']
                })
            
            # Aggregate to daily averages
            df = pd.DataFrame(forecasts)
            daily_forecast = df.groupby('date').agg({
                'temperature': 'mean',
                'precipitation': 'sum',
                'humidity': 'mean',
                'wind_speed': 'mean',
                'cloud_cover': 'mean'
            }).reset_index()
            
            return daily_forecast.to_dict('records')
            
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return self._get_mock_forecast(days)
    
    def _get_mock_weather(self) -> Dict:
        """Generate mock weather data for development"""
        import random
        
        return {
            'temperature': round(random.uniform(5, 25), 1),
            'precipitation': round(random.uniform(0, 10), 1),
            'humidity': random.randint(30, 90),
            'wind_speed': round(random.uniform(0, 15), 1),
            'cloud_cover': random.randint(0, 100),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_mock_forecast(self, days: int) -> List[Dict]:
        """Generate mock weather forecast for development"""
        import random
        
        forecasts = []
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            forecasts.append({
                'date': date,
                'temperature': round(random.uniform(5, 25), 1),
                'precipitation': round(random.uniform(0, 5), 1),
                'humidity': random.randint(30, 90),
                'wind_speed': round(random.uniform(0, 15), 1),
                'cloud_cover': random.randint(0, 100)
            })
        
        return forecasts

class WeatherDataManager:
    """Manages weather data integration with predictions"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
    
    def get_weather_for_predictions(self, days_ahead: int = 30) -> pd.DataFrame:
        """
        Get weather data for prediction period
        Combines current weather with forecast
        """
        current_time = datetime.now()
        
        # Check cache
        cache_key = f"weather_{days_ahead}_{current_time.strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Get current weather
        current_weather = self.weather_service.get_current_weather()
        
        # Get forecast
        forecast = self.weather_service.get_weather_forecast(days_ahead)
        
        # Create DataFrame
        weather_data = []
        
        # Add current day
        weather_data.append({
            'date': current_time.strftime('%Y-%m-%d'),
            'temperature': current_weather['temperature'],
            'precipitation': current_weather['precipitation'],
            'humidity': current_weather['humidity'],
            'wind_speed': current_weather['wind_speed'],
            'cloud_cover': current_weather['cloud_cover']
        })
        
        # Add forecast days
        for day_forecast in forecast:
            weather_data.append(day_forecast)
        
        # Fill remaining days with historical averages if needed
        if len(weather_data) < days_ahead:
            avg_temp = sum(d['temperature'] for d in weather_data) / len(weather_data)
            avg_precip = sum(d['precipitation'] for d in weather_data) / len(weather_data)
            
            for i in range(len(weather_data), days_ahead):
                date = (current_time + timedelta(days=i)).strftime('%Y-%m-%d')
                weather_data.append({
                    'date': date,
                    'temperature': avg_temp,
                    'precipitation': avg_precip,
                    'humidity': 60,  # Default
                    'wind_speed': 5,  # Default
                    'cloud_cover': 50  # Default
                })
        
        df = pd.DataFrame(weather_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Cache the result
        self.cache[cache_key] = df
        
        return df

# Example usage
if __name__ == "__main__":
    weather_manager = WeatherDataManager()
    weather_data = weather_manager.get_weather_for_predictions(7)
    print("Weather data for next 7 days:")
    print(weather_data)
