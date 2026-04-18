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
    
    # HF limited to 20-30 texts per call locally
    response = requests.post(
        HF_API_URL, 
        headers=headers, 
        json={"inputs": texts, "options":{"wait_for_model":True}}
    )
    
    if response.status_code != 200:
        raise Exception(f"HF API Error: {response.text}")
        
    return response.json()
