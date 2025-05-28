import os
import re
import openai
from typing import List, Dict

class ChatGPTClient:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.model = model
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Set OPENAI_API_KEY env var or pass api_key")

    def chat(self, messages: List[Dict[str,str]]) -> str:
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        return resp.choices[0].message.content

# disallowed keywords by role
ROLE_KEYWORDS = {
    "Teller": [r"\bsalary\b", r"\bssn\b", r"\bcredit_score\b"],
    "Manager": []
}

def preprocess(prompt: str, role: str) -> str:
    for patt in ROLE_KEYWORDS.get(role, []):
        if re.search(patt, prompt, re.IGNORECASE):
            return f"USER REQUEST BLOCKED: as a {role} you may not access that field."
    return prompt

def postprocess(response: str, role: str) -> str:
    # stub for OPA or any other policy engine
    return response