import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"


def generate_interactive_script(user_prompt: str) -> dict:

    script_response_schema = {
        "type": "object",
        "properties": {
            "script": {
                "type": "string",
                "description": "ANSWER THE QUESTION."
            },
            "chainOfThought": {
                "type": "string",
                "description": "A detailed explanation of the reasoning process used to arrive at the final interactive script."
            }
        },
        "required": ["script", "chainOfThought"]
    }


    payload = {
        "system_instruction": {
            "parts": [{"text": "respond to the user prompt with a JSON object matching the provided schema"}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": script_response_schema
        }
    }

    response = requests.post(api_url, json=payload, timeout=30)
    result = response.json()
    try:
        script_response_json_str = (
            result["candidates"][0]["content"]["parts"][0]["text"]
        )
        script_output = json.loads(script_response_json_str)
        return script_output
    except Exception as e:
        return {"error": f"Malformed response or error: {str(e)}", "raw": result}

print(generate_interactive_script("HELLO WORLD WHAT IS UP"))
