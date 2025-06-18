import openai
from openai import OpenAI
from typing import List, Dict
from src.llmsec.clients.base_client import LLMClient

class ChatGPTClient(LLMClient):
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return resp.choices[0].message.content