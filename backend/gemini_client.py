import json
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """Reusable client for Gemini REST API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
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
        """
        Make a Gemini API request with structured output.
        
        Args:
            user_prompt: The user's question/request
            system_instruction: System-level instructions for behavior
            response_schema: JSON schema for structured output (optional)
            temperature: Creativity level (0.0 - 1.0)
            timeout: Request timeout in seconds
        
        Returns:
            Dict containing the response or error
        """
        
        # Build API URL
        api_url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        # Build payload
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
            response.raise_for_status()  # Raise error for bad status codes
            
            result = response.json()
            
            response_text = result["candidates"][0]["content"]["parts"][0]["text"]
            if response_schema:
                return json.loads(response_text)
            else:
                return {"response": response_text}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return {"error": f"Malformed response: {str(e)}", "raw": result}
    
    def generate_text(
        self,
        user_prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        temperature: float = 0.7
    ) -> str:
        """
        Convenience method for simple text generation (no JSON schema).
        
        Returns:
            String response from Gemini
        """
        result = self.generate(
            user_prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=temperature
        )
        
        if "error" in result:
            raise Exception(result["error"])
        
        return result.get("response", "")


if __name__ == "__main__":
    client = GeminiClient()
    
    # Test 1: Simple text generation
    response = client.generate_text("What is 2+2?")
    print("Text response:", response)
    
    # Test 2: Structured JSON output
    schema = {
        "type": "object",
        "properties": {
            "answer": {"type": "number"},
            "explanation": {"type": "string"}
        },
        "required": ["answer", "explanation"]
    }
    
    response = client.generate(
        user_prompt="What is 2+2? Explain your reasoning.",
        response_schema=schema
    )
    print("Structured response:", response)
