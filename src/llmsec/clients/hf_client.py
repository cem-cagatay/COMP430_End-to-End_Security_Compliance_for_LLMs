import requests
from typing import List, Dict
from src.llmsec.clients.base_client import LLMClient
import os

class HFClient(LLMClient):
    def __init__(self, endpoint_url: str = None, hf_token: str = None):
        self.endpoint_url = endpoint_url or os.getenv("HF_ENDPOINT_URL")
        self.headers = {
            "Authorization": f"Bearer {hf_token or os.getenv('HF_TOKEN')}",
            "Content-Type": "application/json"
        }
        print("HFClient endpoint in use:", self.endpoint_url)

    def chat(self, messages: List[Dict[str, str]]) -> int:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        print("Prompt to HF model:\n", prompt)

        payload = {
            "inputs": prompt
        }

        response = requests.post(self.endpoint_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"[HF Error {response.status_code}]: {response.text}")

        # Expected response format:
        # {
        #   "classification": 1,
        #   "confidence": 0.96,
        #   ...
        # }
        result = response.json()
        print("HF Classification Result:", result)
        return result.get("classification", 0)  # Default to 0 (safe) if missing