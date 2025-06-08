import os
import re
import openai
from typing import List, Dict, Any
from openai import OpenAI

class ChatGPTClient:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)        # create a client instance
        self.model  = model

    def chat(self, messages):
        # “chat.completions.create” is the new method name:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return resp.choices[0].message.content
    
def preprocess(prompt: str, role: str, policy: Dict[str, Any]) -> str:
    perms = policy.get(role, {})
    # look for "<resource>.<field>" or SQL keywords + resource names:
    for resource, ops in perms.items():
        for op, rules in ops.items():
            for field in rules.get("deny", []):
                token = f"{resource}.{field}"
                if token.lower() in prompt.lower():
                    return f"ACCESS DENIED: {role}s may not perform {op} on `{token}`."
    return prompt

def postprocess(response: str, role: str) -> str:
    # stub for OPA or any other policy engine
    return response

def make_system_prompt(role: str, policy: Dict[str, Any]) -> str:
    """
    Turn the JSON policy for this role into a human‐readable
    instruction block so ChatGPT itself enforces it.
    """
    lines = []
    for resource, ops in policy.get(role, {}).items():
        for op, rules in ops.items():
            allow = ", ".join(rules.get("allow", [])) or "none"
            deny  = ", ".join(rules.get("deny", []))  or "none"
            lines.append(f"- {op} on {resource}: allow=[{allow}], deny=[{deny}]")
    body = "\n".join(lines)
    return (
        f"You are a secure assistant.\n"
        f"User role: {role}\n"
        f"Enforce exactly these rules:\n{body}\n"
        f"If the user asks for anything denied, reply `ACCESS DENIED: <reason>`."
    )