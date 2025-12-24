import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Try GEMINI_API_KEYS
    api_keys = os.getenv("GEMINI_API_KEYS")
    if api_keys:
        api_key = api_keys.split(",")[0].strip()
    else:
        print("Error: No GEMINI_API_KEY or GEMINI_API_KEYS found in environment variables")
        exit(1)

# Configure the API
genai.configure(api_key=api_key)

# List all available models
print("\n" + "="*70)
print("AVAILABLE MODELS FOR GENERATECONTENT")
print("="*70 + "\n")

try:
    models = genai.list_models()
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"Model Name: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Description: {model.description if hasattr(model, 'description') else 'N/A'}")
            print(f"Supported Methods: {', '.join(model.supported_generation_methods)}")
            print("-" * 70)
            print()
except Exception as e:
    print(f"Error listing models: {e}")
