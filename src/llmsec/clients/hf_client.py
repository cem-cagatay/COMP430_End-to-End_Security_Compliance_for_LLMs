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

    def chat(self, messages: List[Dict[str, str]]) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        print("Prompt to HF model:\n", prompt)

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 30,
                "do_sample": False,
                "temperature": 0.2,            # No creativity
                "top_k": 1,                    # Limit sampling space
                "top_p": 0.9,
                "stop": ["User:", "Assistant:"]
            }
        }

        response = requests.post(self.endpoint_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            return f"[HF Error {response.status_code}]: {response.text}"

        # 🛑 Do NOT strip prompt
        return response.json()[0]["generated_text"].strip()