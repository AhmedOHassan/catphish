#!/usr/bin/env bash
# Quick test to verify Gemini API is working with new API

set -e

echo "=========================================="
echo "Testing Gemini API Connection"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

python3 << 'EOF'
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("   Please add your API key to .env")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Test new API
try:
    from google import genai
    
    print("\n✅ Successfully imported: from google import genai")
    
    print("\nInitializing Gemini client...")
    client = genai.Client(api_key=api_key)
    
    print("Sending test request to gemini-3-flash-preview...")
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents='Respond with exactly: "Gemini API is working correctly!"'
    )
    
    response_text = response.text if hasattr(response, 'text') else str(response)
    
    print(f"\n✅ Gemini API Response:")
    print(f"   {response_text}")
    print("\n✅ SUCCESS: Gemini API is working with gemini-3-flash-preview!")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nPlease install the Google Generative AI package:")
    print("   pip install google-generativeai")
    exit(1)
    
except Exception as e:
    print(f"\n❌ API Test Failed: {e}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. Network connectivity")
    print("  3. API quota exceeded")
    print("  4. Model name incorrect")
    exit(1)

EOF

echo ""
echo "=========================================="
echo "✅ Gemini API test complete!"
echo "=========================================="
