import json
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """Reusable client for Gemini REST API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.5-flash"
    
    def generate(
        self, 
        user_prompt: str, 
        system_instruction: str = "You are a helpful assistant.",
        response_schema: Optional[Dict] = None,
        temperature: float = 0.7,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Generate response from Gemini"""
        
        api_url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "temperature": temperature,
            }
        }
        
        if response_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"
            payload["generationConfig"]["responseSchema"] = response_schema
        
        try:
            response = requests.post(api_url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            response_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            if response_schema:
                return json.loads(response_text)
            else:
                return {"response": response_text}
            
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def generate_text(self, user_prompt: str, system_instruction: str = "", temperature: float = 0.7) -> str:
        """Simple text generation"""
        result = self.generate(user_prompt, system_instruction, temperature=temperature)
        
        if "error" in result:
            raise Exception(result["error"])
        
        return result.get("response", "")
