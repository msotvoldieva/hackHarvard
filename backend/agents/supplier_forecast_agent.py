from gemini_client import GeminiClient
from database import Database
import json

class SupplierForecastAgent:
    """Agent for demand forecasting and supplier order recommendations"""
    
    def __init__(self, gemini_client: GeminiClient = None):
        self.gemini = gemini_client or GeminiClient()
        self.db = Database()
    
    def forecast_and_order(self, product: str, days_ahead: int = 7) -> dict:
        """
        Analyze demand forecast and generate supplier order recommendation.
        
        Returns:
            Dict with forecast and order recommendation
        """
        
        # Get Prophet forecast
        forecast = self.db.get_prophet_prediction(product, days_ahead=days_ahead)
        
        if "error" in forecast:
            return forecast
        
        # Get historical baseline
        historical = self.db.get_sales_trend(product, days=30)
        historical_avg_weekly = historical['statistics']['avg_daily_sold'] * 7
        
        # Get weather impact
        weather = self.db.get_weather_correlation(product)
        
        # Calculate recommended order
        forecast_total = forecast['total_predicted']
        change_pct = ((forecast_total - historical_avg_weekly) / historical_avg_weekly * 100) if historical_avg_weekly > 0 else 0
        
        # Generate order recommendation with Gemini
        order_prompt = f"""You are a supply chain analyst preparing a supplier order recommendation.

        Product: {product}
        Next week forecast: {forecast_total:.0f} units
        Historical weekly average: {historical_avg_weekly:.0f} units
        Change: {change_pct:+.1f}%
        Weather impact: {weather.get('interpretation', 'Unknown')}

        Daily breakdown:
        {json.dumps(forecast['predictions'], indent=2)}

        Generate a recommended order quantity considering safety stock (+10%).
        Explain the reasoning briefly."""
        
        schema = {
            "type": "object",
            "properties": {
                "recommended_order_quantity": {"type": "number"},
                "reasoning": {"type": "string"}
            },
            "required": ["recommended_order_quantity", "reasoning"]
        }
        
        order_rec = self.gemini.generate(
            user_prompt="Create an order recommendation based on the following data.",
            system_instruction=order_prompt,
            response_schema=schema,
            temperature=0.5
        )
        
        if "error" in order_rec:
            # Fallback
            order_rec = {
                "recommended_order_quantity": forecast_total * 1.1,
                "reasoning": f"Order adjusted to {forecast_total * 1.1:.0f} units based on forecast analysis with 10% safety stock."
            }
        
        return {
            "product": product,
            "forecast_days": days_ahead,
            "daily_forecast": forecast['predictions'],
            "total_predicted_demand": forecast_total,
            "historical_weekly_avg": historical_avg_weekly,
            "change_percentage": change_pct,
            "recommended_order_quantity": order_rec['recommended_order_quantity'],
            "reasoning": order_rec['reasoning'],
            "weather_impact": weather.get('interpretation', '')
        }
