import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json",
}

def generate_summary(text):
    if not HF_API_TOKEN:
        return "ERROR: Hugging Face API token not configured."

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 150,
            "min_length": 40,
            "do_sample": False
        }
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=40,
        )
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]

        return "ERROR: Unexpected response from Hugging Face API."

    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"
