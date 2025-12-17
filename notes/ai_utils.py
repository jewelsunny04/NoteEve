import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json",
}

def generate_summary(text):
    """
    Generate a summary using Hugging Face Inference API (cloud-based).
    No local ML. Railway-safe.
    """
    if not HF_API_TOKEN:
        return "ERROR: Hugging Face API token not configured."

    payload = {
        "inputs": f"Summarize the following text:\n{text}",
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.3,
        },
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()

        # Hugging Face returns a list
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        return "ERROR: Unexpected response from Hugging Face API."

    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"
