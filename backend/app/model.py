"""
Local LLM Model Handler (Ollama)

This module connects to Ollama to run LLMs locally.
All inference happens on your machine - no data is sent to external servers.

Key principles:
- Offline execution: Complete privacy and no internet required after model download
- Deterministic: Low temperature for consistent code output
- Safe: LLM generates code, Python validates and executes it

To change models:
1. Open config.py
2. Update MODEL_NAME to your preferred model (e.g., "llama3.2", "codellama", "mistral")
3. Make sure the model is installed: ollama pull <model_name>
"""

import requests
import json
from app.config import MODEL_NAME, GENERATION_CONFIG, OLLAMA_BASE_URL

print(f"\n📦 Using Ollama with model: {MODEL_NAME}")
print(f"   Ollama endpoint: {OLLAMA_BASE_URL}")
print("   This runs entirely on your machine - no data leaves your computer.")
print("\n   To change the model, edit MODEL_NAME in config.py")
print(f"   Current model: {MODEL_NAME}\n")


def check_ollama_connection():
    """Check if Ollama is running and the model is available."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            if MODEL_NAME.split(":")[0] in model_names or any(MODEL_NAME in m.get("name", "") for m in models):
                print(f"✅ Ollama connected! Model '{MODEL_NAME}' is available.")
                return True
            else:
                print(f"⚠️  Model '{MODEL_NAME}' not found. Run: ollama pull {MODEL_NAME}")
                print(f"   Available models: {', '.join(model_names) if model_names else 'None'}")
                return False
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


# Check connection at startup
check_ollama_connection()


def run_llm(prompt: str) -> str:
    """
    Run the local LLM via Ollama to generate Python code from natural language.
    
    This function:
    1. Takes a user's natural language request (embedded in a structured prompt)
    2. Sends it to Ollama running locally
    3. Returns generated Python code for human review
    
    The generated code is NOT executed here - it's returned for validation
    and user approval first (human-in-the-loop).
    
    Args:
        prompt: Structured prompt containing system instructions, schema, and user request
        
    Returns:
        Generated Python code as a string (for human review before execution)
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": GENERATION_CONFIG.get("temperature", 0.1),
                    "num_predict": GENERATION_CONFIG.get("num_predict", 512),
                    "top_p": GENERATION_CONFIG.get("top_p", 0.9),
                    "stop": GENERATION_CONFIG.get("stop", [])
                }
            },
            timeout=120  # 2 minute timeout for generation
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"❌ Ollama error: {response.status_code} - {response.text}")
            return ""

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running: ollama serve")
        return ""
    except requests.exceptions.Timeout:
        print("❌ Ollama request timed out. The model might be too slow.")
        return ""
    except Exception as e:
        print(f"❌ Error calling Ollama: {e}")
        return ""


# Alias for backward compatibility
run_gemma = run_llm