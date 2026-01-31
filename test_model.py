import google.generativeai as genai
import os

# Configure API
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

print("Testing model names...\n")

# Test different model names
models_to_test = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro-latest',
    'gemini-1.5-pro',
    'gemini-pro'
]

for model_name in models_to_test:
    try:
        print(f"Trying: {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        result = model.generate_content("Say 'Hello'")
        print(f"✅ WORKS! Response: {result.text[:50]}")
        break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:80]}")

print("\nListing all available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
