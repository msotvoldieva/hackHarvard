from gemini_client import GeminiClient
from database import Database
from typing import Dict, List
import json

class WasteLessChatbot:
    """
    Conversational chatbot for WasteLess supply chain management.
    Provides detailed, data-driven responses about inventory, waste, and ordering.
    """
    
    def __init__(self):
        self.gemini = GeminiClient()
        self.db = Database()
        self.conversation_history = []
        
        # System instruction for Gemini
        self.system_instruction = """You are an AI assistant for WasteLess, a grocery store supply chain management system.

Your role:
- Help store managers reduce food waste through data-driven decisions
- Explain Prophet ML predictions in clear, actionable language
- Provide detailed analysis with specific numbers and data points
- Reference historical trends, weather impacts, and seasonal patterns
- Be proactive with recommendations

Communication style:
- Professional but conversational
- Always cite specific data (dates, quantities, percentages)
- Explain "why" behind predictions
- Give clear, actionable recommendations
- Be concise but thorough (3-5 sentences for simple queries, more for complex)

Available data:
- Historical sales and waste data
- Prophet ML forecasts
- Weather correlations
- Current inventory status

When answering:
1. Acknowledge the question
2. Provide specific data/numbers
3. Explain reasoning (cite Prophet model, weather, trends)
4. Give clear recommendation
5. Offer follow-up if appropriate"""
    
    def handle_message(self, user_message: str, session_data: Dict = None) -> Dict:
        """
        Handle a user message and return response with data.
        
        Args:
            user_message: User's question
            session_data: Session context (for multi-turn conversations)
        
        Returns:
            Dict with response, data used, and session info
        """
        
        # Step 1: Understand what data is needed
        data_needed = self._identify_data_needs(user_message)
        
        # Step 2: Gather relevant data
        gathered_data = self._gather_data(data_needed)
        
        # Step 3: Generate response with Gemini
        response = self._generate_response(user_message, gathered_data, session_data)
        
        return {
            "response": response,
            "data_used": gathered_data,
            "data_needs": data_needed
        }
    
    def _identify_data_needs(self, user_message: str) -> Dict:
        """Use Gemini to identify what data is needed to answer the question"""
        
        schema = {
            "type": "object",
            "properties": {
                "needs_current_status": {
                    "type": "boolean",
                    "description": "Does the query need current inventory/sales status?"
                },
                "needs_forecast": {
                    "type": "boolean",
                    "description": "Does the query need future predictions?"
                },
                "needs_historical_trend": {
                    "type": "boolean",
                    "description": "Does the query need past sales trends?"
                },
                "needs_weather_analysis": {
                    "type": "boolean",
                    "description": "Does the query need weather impact analysis?"
                },
                "needs_discount_recommendation": {
                    "type": "boolean",
                    "description": "Does the query need discount/pricing recommendations?"
                },
                "products": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of products mentioned (or ['all'] for all products)"
                },
                "timeframe_days": {
                    "type": "integer",
                    "description": "How many days of data needed (default 7)"
                }
            },
            "required": ["needs_current_status", "needs_forecast", "needs_historical_trend", 
                        "needs_weather_analysis", "needs_discount_recommendation", "products"]
        }
        
        prompt = f"""Analyze this user question and determine what data is needed to answer it:

User question: "{user_message}"

Available products: {', '.join(self.db.get_all_products())}

Determine what data we need to fetch."""
        
        result = self.gemini.generate(
            user_prompt=prompt,
            system_instruction="You are a data analyst identifying information needs.",
            response_schema=schema,
            temperature=0.3
        )
        
        if "error" in result:
            # Fallback: assume they want current status for all products
            return {
                "needs_current_status": True,
                "needs_forecast": False,
                "needs_historical_trend": False,
                "needs_weather_analysis": False,
                "needs_discount_recommendation": False,
                "products": ["all"],
                "timeframe_days": 7
            }
        
        return result
    
    def _gather_data(self, data_needs: Dict) -> Dict:
        """Gather all requested data from database"""
        
        gathered = {}
        products = data_needs.get("products", ["all"])
        
        if "all" in products:
            products = self.db.get_all_products()
        
        for product in products:
            product_data = {"product": product}
            
            if data_needs.get("needs_current_status"):
                product_data["current_status"] = self.db.get_current_status(product)
            
            if data_needs.get("needs_forecast"):
                product_data["forecast"] = self.db.get_prophet_prediction(
                    product, 
                    days_ahead=data_needs.get("timeframe_days", 7)
                )
            
            if data_needs.get("needs_historical_trend"):
                product_data["historical_trend"] = self.db.get_sales_trend(
                    product,
                    days=data_needs.get("timeframe_days", 30)
                )
            
            if data_needs.get("needs_weather_analysis"):
                product_data["weather_impact"] = self.db.get_weather_correlation(product)
            
            if data_needs.get("needs_discount_recommendation"):
                product_data["discount_recommendation"] = self.db.get_discount_recommendation(product)
            
            gathered[product] = product_data
        
        return gathered
    
    def _generate_response(self, user_message: str, data: Dict, session_data: Dict = None) -> str:
        """Generate natural language response using Gemini"""
        
        # Build context
        context = f"""User asked: "{user_message}"

Here is the relevant data from our system:

{json.dumps(data, indent=2)}

Generate a detailed, helpful response that:
1. Directly answers their question
2. Cites specific numbers and data points
3. Explains WHY (reference Prophet model, weather correlations, historical patterns)
4. Provides clear, actionable recommendations
5. Offers relevant follow-up if appropriate

Be conversational but data-driven. Always include specifics."""
        
        # Add conversation history if available
        if session_data and "history" in session_data:
            context = f"Previous conversation:\n{session_data['history']}\n\n{context}"
        
        response = self.gemini.generate_text(
            user_prompt=context,
            system_instruction=self.system_instruction,
            temperature=0.7
        )
        
        return response
    
    def get_proactive_greeting(self) -> str:
        """Generate proactive greeting with current insights"""
        
        # Get current status for all products
        all_products = self.db.get_all_products()
        insights = []
        
        for product in all_products:
            discount_rec = self.db.get_discount_recommendation(product)
            if discount_rec.get("needs_discount"):
                insights.append({
                    "product": product,
                    "urgency": discount_rec["urgency"],
                    "discount": discount_rec["recommended_discount_pct"],
                    "reason": discount_rec["reasoning"]
                })
        
        # Generate greeting
        if insights:
            context = f"""Generate a friendly, proactive greeting for the store manager.

Current situation:
{json.dumps(insights, indent=2)}

The greeting should:
- Be warm and professional
- Highlight the most urgent issues (2-3 items max)
- Include specific recommendations
- End with "How can I help you today?" or similar

Keep it concise (3-4 sentences)."""
            
            greeting = self.gemini.generate_text(
                user_prompt=context,
                system_instruction=self.system_instruction,
                temperature=0.8
            )
        else:
            greeting = "Good morning! All products are performing well today with low waste rates. How can I help you manage your inventory?"
        
        return greeting
