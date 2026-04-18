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
            timeout=20
        )
        
        if response.status_code == 503:
            # Model is still loading on HF servers
            return [] 
            
        if response.status_code != 200:
            print(f"HF Error: {response.text}")
            return []
            
        return response.json()
    except Exception as e:
        print(f"Embedding failed: {e}")
        return []
