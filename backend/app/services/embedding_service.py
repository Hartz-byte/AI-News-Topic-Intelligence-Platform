import requests
from app.core.config import get_settings

settings = get_settings()
HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HF_TOKEN = settings.huggingface_token

def embed_texts(texts: list[str]) -> list[list[float]]:
    # Using Hugging Face Inference API
    if not HF_TOKEN:
        raise Exception("HUGGINGFACE_TOKEN not provided in environment variables")
        
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # HF limited to 20-30 texts per call
    try:
        response = requests.post(
            HF_API_URL, 
            headers=headers, 
            json={"inputs": texts, "options":{"wait_for_model":True}},
            timeout=25
        )
        
        if response.status_code == 503:
            return [] 
            
        if response.status_code == 401:
            print("HF Error: Unauthorized. Check your HUGGINGFACE_TOKEN.")
            return []

        if response.status_code != 200:
            print(f"HF Error {response.status_code}: {response.text}")
            return []
            
        result = response.json()
        
        # Consistent format: Always return a list of lists
        # If result is [0.1, 0.2...], wrap it in [[...]]
        if isinstance(result, list) and len(result) > 0 and not isinstance(result[0], list):
            return [result]
            
        return result

    except Exception as e:
        print(f"Embedding failed: {e}")
        return []
