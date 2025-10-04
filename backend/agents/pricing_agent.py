from database import Database
from datetime import datetime
import pickle
import os

class PricingAgent:
    """Agent for pricing and discount recommendations"""
    
    def __init__(self):
        self.db = Database()
        self.models = self._load_models()
    
    def _load_models(self):
        """Load trained Prophet models"""
        models = {}
        model_dir = "models"
        
        for filename in os.listdir(model_dir):
            if filename.endswith("_model.pkl"):
                product_name = filename.replace("_model.pkl", "").replace("_", " ")
                with open(os.path.join(model_dir, filename), 'rb') as f:
                    models[product_name] = pickle.load(f)
        
        return models
    
    def analyze(self, product: str) -> dict:
        """
        Analyze if a product needs discounting.
        
        Args:
            product: Product name
        
        Returns:
            Dict with recommendation and reasoning
        """
        
        # Get current sales data
        today = datetime.now().date()
        actual_sales = self.db.get_sales(product, today)
        
        # Get prediction for today
        predicted_sales = self._predict_today(product)
        
        # Calculate performance
        performance = actual_sales / predicted_sales if predicted_sales > 0 else 1.0
        
        # Get expiry info
        hours_to_expiry = self.db.get_hours_to_expiry(product)
        
        # Decision logic
        if performance < 0.6 and hours_to_expiry < 48:
            recommendation = "discount"
            discount = self._calculate_optimal_discount(performance, hours_to_expiry)
        elif performance > 0.9:
            recommendation = "no_action"
            discount = 0
        else:
            recommendation = "monitor"
            discount = 0
        
        return {
            "product": product,
            "actual_sales": round(actual_sales, 1),
            "predicted_sales": round(predicted_sales, 1),
            "performance_ratio": round(performance, 2),
            "hours_to_expiry": round(hours_to_expiry, 1),
            "recommendation": recommendation,
            "recommended_discount": discount,
            "reasoning": self._generate_reasoning(performance, hours_to_expiry, recommendation)
        }
    
    def _predict_today(self, product: str) -> float:
        """Get Prophet prediction for today"""
        # Simplified - in reality, call Prophet with today's features
        return self.db.get_historical_avg(product)
    
    def _calculate_optimal_discount(self, performance: float, hours_to_expiry: float) -> float:
        """Calculate optimal discount percentage"""
        base_discount = (1 - performance) * 50
        urgency_factor = max(0, (48 - hours_to_expiry) / 48) * 20
        return min(round(base_discount + urgency_factor, 0), 50)
    
    def _generate_reasoning(self, performance: float, hours: float, rec: str) -> str:
        """Generate human-readable reasoning"""
        if rec == "discount":
            return f"Underperforming by {(1-performance)*100:.0f}% with {hours:.0f}h to expiry"
        elif rec == "no_action":
            return "On track - no action needed"
        else:
            return "Monitor closely"
