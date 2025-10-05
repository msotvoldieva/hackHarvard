from gemini_client import GeminiClient
from database import Database
from datetime import datetime, timedelta
import json

class PricingInventoryAgent:
    """Agent for pricing recommendations and inventory status (expiration tracking)"""
    
    def __init__(self, gemini_client: GeminiClient = None):
        self.gemini = gemini_client or GeminiClient()
        self.db = Database()
    
    def analyze(self, product: str) -> dict:
        """
        Analyze inventory status and pricing for a product.
        
        Returns:
            Dict with expiration status, discount recommendations, reasoning
        """
        
        # Get inventory data
        inventory = self.db.get_inventory_status(product)
        
        if "error" in inventory:
            return inventory
        
        # Get recent waste data
        waste_stats = self.db.get_discount_recommendation(product)
        
        # Calculate urgency
        days_until_expiry = inventory['days_until_nearest_expiry']
        quantity_on_hand = inventory['total_quantity']

        # Decision logic with Gemini
        analysis_prompt = f"""You are analyzing inventory for a grocery store product.

        Product: {product}
        Quantity on hand: {quantity_on_hand} units
        Days until expiration: {days_until_expiry} days
        Recent waste rate: {waste_stats.get('waste_rate_pct', 0):.1f}%
        Unit price: ${inventory.get('unit_price', 0):.2f}

        Determine:
        1. Does this product need a discount? (urgency: high/medium/low/none)
        2. What discount percentage? (0-50%)
        3. Brief reasoning (2 sentences max)

        Consider:
        - Items expiring in <3 days = high urgency
        - Items expiring in 3-5 days = medium urgency
        - High stock + approaching expiry = higher discount
        - Recent waste rate >15% = needs action"""

        schema = {
            "type": "object",
            "properties": {
                "needs_discount": {"type": "boolean"},
                "urgency": {
                    "type": "string",
                    "enum": ["none", "low", "medium", "high"]
                },
                "recommended_discount_pct": {"type": "number"},
                "reasoning": {"type": "string"}
            },
            "required": ["needs_discount", "urgency", "recommended_discount_pct", "reasoning"]
        }
        
        decision = self.gemini.generate(
            user_prompt=analysis_prompt,
            system_instruction="You are a pricing optimization expert for grocery stores.",
            response_schema=schema,
            temperature=0.3
        )
        
        if "error" in decision:
            # Fallback to rule-based
            decision = self._fallback_pricing_logic(days_until_expiry, quantity_on_hand, waste_stats)
        
        # Combine inventory data with pricing decision
        return {
            "product": product,
            "quantity_on_hand": quantity_on_hand,
            "days_until_expiry": days_until_expiry,
            "expiration_date": inventory['nearest_expiration_date'],
            "needs_discount": decision['needs_discount'],
            "urgency": decision['urgency'],
            "recommended_discount_pct": decision['recommended_discount_pct'],
            "reasoning": decision['reasoning'],
            "waste_rate_pct": waste_stats.get('waste_rate_pct', 0)
        }
    
    def _fallback_pricing_logic(self, days_until_expiry, quantity, waste_stats):
        """Simple rule-based fallback if Gemini fails"""
        if days_until_expiry <= 2:
            return {
                "needs_discount": True,
                "urgency": "high",
                "recommended_discount_pct": 30,
                "reasoning": "Expires in 2 days - urgent discount needed"
            }
        elif days_until_expiry <= 4:
            return {
                "needs_discount": True,
                "urgency": "medium",
                "recommended_discount_pct": 20,
                "reasoning": "Approaching expiration - moderate discount recommended"
            }
        else:
            return {
                "needs_discount": False,
                "urgency": "none",
                "recommended_discount_pct": 0,
                "reasoning": "Sufficient time before expiration"
            }
