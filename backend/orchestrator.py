from gemini_client import GeminiClient
from database import Database
import json
import random

class Orchestrator:
    def __init__(self):
        self.gemini = GeminiClient()
        self.db = Database()
        self.webhook_url = "https://hook.us2.make.com/8oj18ng2vakhmea2lk9kgl0rgq2yyffo"
    
    def handle_query(self, user_message: str, session_data: dict = None) -> dict:
        # Get conversation history
        history = session_data.get("history", [])[-3:] if session_data else []
        
        # Extract products mentioned
        products = self._extract_products(user_message)
        
        # Gather ALL data for these products
        all_data = self._gather_complete_data(products)
        
        # Generate response with full context
        response = self._generate_unified_response(user_message, all_data, history)
        
        return {
            "routing_message": "Analyzing...",
            "response": response,
            "data_used": all_data
        }
    
    def _gather_complete_data(self, products: list) -> dict:
        """Get all data types for all products upfront"""
        # Handle 'all' keyword
        if 'all' in products:
            products = self.db.get_all_products()
        
        data = {}
        for product in products:
            try:
                data[product] = {
                    "inventory": self.db.get_inventory_status(product),
                    "forecast": self.db.get_prophet_prediction(product, 7),
                    "historical": self.db.get_sales_trend(product, 30),
                    "weather": self.db.get_weather_correlation(product)
                }
            except Exception as e:
                data[product] = {"error": f"Error gathering data for {product}: {str(e)}"}
        return data
    
    def _generate_unified_response(self, query: str, data: dict, history: list) -> str:
        system = """You are WasteLess assistant handling ALL aspects of grocery inventory management.

        You have access to:
        - Current inventory and expiration data
        - Pricing and discount recommendations  
        - Demand forecasts from Prophet ML model
        - Historical sales trends
        - Weather impact analysis

        Respond naturally to questions about ANY of these topics. If conversation shifts topics, acknowledge it smoothly ("Regarding ordering..." or "As for pricing...").

        Be specific, cite data, give clear recommendations."""

        context = f"""Conversation history:
        {json.dumps(history, indent=2) if history else "First message"}

        User: "{query}"

        Complete data:
        {json.dumps(data, indent=2)}

        Provide a helpful, data-driven response. Handle pricing questions, forecast questions, or both naturally."""

        return self.gemini.generate_text(context, system, temperature=0.7)
    
    def _extract_products(self, user_message: str) -> list:
        """Extract product names from user message using Gemini"""
        available_products = self.db.get_all_products()
        
        prompt = f"""Extract product names from this message: "{user_message}"
        
        Available products: {', '.join(available_products)}
        
        Rules:
        - Return exact product names that match the available products
        - If no specific products mentioned, return ['all']
        - If message mentions "everything" or "all products", return ['all']
        - Return as a simple list, e.g., ["Milk", "Eggs"] or ["all"]
        """
        
        try:
            result = self.gemini.generate_text(
                user_prompt=prompt,
                system_instruction="Extract product names and return as a Python list.",
                temperature=0.1
            )
            
            # Try to parse the result as a Python list
            import ast
            try:
                products = ast.literal_eval(result.strip())
                if isinstance(products, list):
                    return products
            except:
                pass
                
            # Fallback: check if any available products are mentioned
            mentioned_products = []
            message_lower = user_message.lower()
            for product in available_products:
                if product.lower() in message_lower:
                    mentioned_products.append(product)
            
            return mentioned_products if mentioned_products else ['all']
            
        except Exception as e:
            print(f"Error extracting products: {e}")
            return ['all']
    
    def get_proactive_greeting(self) -> str:
        """Return a warm, capability-focused greeting for the chat system."""
        import random
        greetings = [
            "Welcome to WasteLess! I can help you track inventory, forecast demand, and suggest discounts to reduce waste.",
            "Hello! Ask me about sales trends, inventory status, or get recommendations for ordering and pricing.",
            "Howdy-hoo! I'm here to assist with inventory management, demand forecasting, and supplier planning.",
            "Greetings boss! I can analyze your sales, predict future demand, and help you make smarter ordering decisions.",
            "Hello! Need insights on your store's inventory or want to optimize your ordering? Just ask!",
            "Hi! I can provide waste reduction tips, sales analytics, and supplier recommendations for your store.",
            "Welcome to your store assistant! I can answer questions about inventory, sales, and future demand.",
            "Salutations! I'm here to help you manage stock, forecast needs, and minimize waste in your store.",
            "Hi there! Ask me about current inventory, sales predictions, or how to reduce overstock and waste.",
            "Welcome! I can help you with inventory checks, demand forecasts, and actionable recommendations."
        ]
        return random.choice(greetings)
