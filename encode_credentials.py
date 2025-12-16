"""
Helper script to encode credentials for Render.com deployment.
Run this locally to generate base64 strings for your environment variables.
"""

import base64
import os

def encode_file(filepath):
    """Encode a file to base64 string."""
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return None
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    encoded = base64.b64encode(content).decode('utf-8')
    return encoded

def main():
    print("=" * 60)
    print("Render.com Credential Encoder")
    print("=" * 60)
    print()
    
    # Encode client_secret.json
    print("1. Encoding client_secret.json...")
    client_secret_b64 = encode_file('client_secret.json')
    if client_secret_b64:
        print("✓ Successfully encoded client_secret.json")
        print()
        print("Add this to Render.com environment variables:")
        print("Variable Name: CLIENT_SECRET_BASE64")
        print("Value:")
        print("-" * 60)
        print(client_secret_b64)
        print("-" * 60)
        print()
    
    # Encode token.pickle
    print("2. Encoding token.pickle...")
    token_pickle_b64 = encode_file('token.pickle')
    if token_pickle_b64:
        print("✓ Successfully encoded token.pickle")
        print()
        print("Add this to Render.com environment variables:")
        print("Variable Name: TOKEN_PICKLE_BASE64")
        print("Value:")
        print("-" * 60)
        print(token_pickle_b64)
        print("-" * 60)
        print()
    
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Copy the base64 strings above")
    print("2. Go to Render.com dashboard")
    print("3. Open your cron job settings")
    print("4. Go to 'Environment' tab")
    print("5. Add both variables with their values")
    print("6. Also add your API keys:")
    print("   - PEXELS_API_KEY")
    print("   - PIXABAY_API_KEY")
    print("   - GEMINI_API_KEY")
    print("   - YOUTUBE_API_KEY")
    print()
    print("Then trigger a manual run to test!")
    print("=" * 60)

if __name__ == "__main__":
    main()
