"""
Weather Service for OpenWeather API Integration
Fetches real weather forecasts for Cambridge, Boston
"""

import requests
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherService:
    """Service for fetching real weather data from OpenWeather API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast/daily"
        
        # Cambridge, Boston coordinates
        self.lat = 42.3736
        self.lon = -71.1097
        
        if not self.api_key:
            print("Warning: OPENWEATHER_API_KEY not found in environment variables")
    
    def get_forecast(self, days=7):
        """
        Get weather forecast for the specified number of days.
        Falls back to mock data when API key is not available.
        """
        try:
            # API call temporarily commented out - uncomment when API key is ready            
            return self._fetch_from_api(days)
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return self._generate_mock_forecast(days)
    
    def _fetch_from_api(self, days: int) -> List[Dict]:
        """Fetch weather data from OpenWeather API"""
        
        if not self.api_key:
            raise Exception("OpenWeather API key not configured")
        
        # API parameters
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'cnt': min(days, 16),  # API supports max 16 days
            'appid': self.api_key,
            'units': 'imperial'  # Fahrenheit and mph
        }
        
        # Make API request
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Transform to our format
        return self._transform_api_response(data, days)
    
    def _transform_api_response(self, api_data: Dict, requested_days: int) -> List[Dict]:
        """Transform OpenWeather API response to our mock weather format"""
        
        forecast_list = []
        
        # Process daily forecasts
        for i, day_data in enumerate(api_data.get('list', [])[:requested_days]):
            
            # Extract temperature (day temp) and convert Kelvin to Fahrenheit
            temp_data = day_data.get('temp', {})
            temp_kelvin = temp_data.get('day', temp_data.get('max', 288))  # Default ~60°F in Kelvin
            temperature = (temp_kelvin - 273.15) * 9/5 + 32  # K to F conversion
            
            # Extract precipitation (rain + snow in mm, convert to inches)
            precipitation_mm = 0.0
            
            # Rain field (may not exist)
            if 'rain' in day_data:
                precipitation_mm += day_data['rain']
            
            # Snow field (may not exist) 
            if 'snow' in day_data:
                precipitation_mm += day_data['snow']
            
            # Convert mm to inches
            precipitation_inches = precipitation_mm / 25.4
            
            # Extract weather description
            weather_list = day_data.get('weather', [{}])
            weather_main = weather_list[0].get('main', 'Clear') if weather_list else 'Clear'
            weather_desc = weather_list[0].get('description', 'clear sky') if weather_list else 'clear sky'
            
            # Generate our description
            description = self._get_weather_description(weather_main, temperature, precipitation_inches)
            
            # Convert timestamp to date
            timestamp = day_data.get('dt', 0)
            forecast_date = datetime.fromtimestamp(timestamp) if timestamp else datetime.now() + timedelta(days=i+1)
            
            forecast_list.append({
                "day": i + 1,
                "temperature": round(temperature, 1),
                "precipitation": round(precipitation_inches, 2),
                "description": description,
                "date": forecast_date,
                "weather_main": weather_main,
                "weather_description": weather_desc,
                "humidity": day_data.get('humidity', 50),
                "pressure": day_data.get('pressure', 1013)
            })
        
        return forecast_list
    
    def _get_weather_description(self, weather_main: str, temp: float, precip: float) -> str:
        """Generate human-readable weather description"""
        
        # Temperature categories
        if temp >= 80:
            temp_desc = "Hot"
        elif temp >= 70:
            temp_desc = "Warm"
        elif temp >= 60:
            temp_desc = "Mild"
        elif temp >= 45:
            temp_desc = "Cool"
        else:
            temp_desc = "Cold"
        
        # Precipitation categories
        if precip >= 1.0:
            weather_desc = "Heavy Rain" if weather_main == "Rain" else "Heavy Snow"
        elif precip >= 0.3:
            weather_desc = "Rainy" if weather_main == "Rain" else "Snowy"
        elif precip >= 0.1:
            weather_desc = "Light Rain" if weather_main == "Rain" else "Light Snow"
        elif weather_main in ["Clouds", "Overcast"]:
            weather_desc = "Cloudy"
        else:
            weather_desc = "Clear"
        
        return f"{temp_desc} and {weather_desc}"
    
    def _generate_mock_forecast(self, days: int) -> List[Dict]:
        """Generate mock weather forecast data"""
        import random
        
        forecast_list = []
        base_date = datetime.now()
        
        for i in range(days):
            # Generate realistic seasonal temperatures for Boston in October
            base_temp = 65  # Average October temp in Boston
            temp_variation = random.uniform(-15, 15)
            temperature = base_temp + temp_variation
            
            # Generate precipitation (0-2 inches, with bias toward lower amounts)
            if random.random() < 0.3:  # 30% chance of precipitation
                precipitation = random.uniform(0.1, 1.5)
            else:
                precipitation = 0.0
            
            # Generate weather description
            if precipitation > 0.5:
                weather_main = "Rain"
                weather_desc = "rainy"
            elif precipitation > 0:
                weather_main = "Drizzle" 
                weather_desc = "light rain"
            elif random.random() < 0.4:
                weather_main = "Clouds"
                weather_desc = "cloudy"
            else:
                weather_main = "Clear"
                weather_desc = "clear sky"
            
            description = self._get_weather_description(weather_main, temperature, precipitation)
            forecast_date = base_date + timedelta(days=i+1)
            
            forecast_list.append({
                "day": i + 1,
                "temperature": round(temperature, 1),
                "precipitation": round(precipitation, 2),
                "description": description,
                "date": forecast_date,
                "weather_main": weather_main,
                "weather_description": weather_desc,
                "humidity": random.randint(40, 80),
                "pressure": random.randint(1000, 1025)
            })
        
        return forecast_list
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cached_time = self._cache[cache_key]['timestamp']
        return (datetime.now() - cached_time).seconds < self._cache_timeout
    
    def clear_cache(self):
        """Clear the weather cache"""
        self._cache = {}
        print("Weather cache cleared")

# Global instance
weather_service = WeatherService()
