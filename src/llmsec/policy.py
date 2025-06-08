import json
from typing import Dict, Any

def load_policy(path: str) -> Dict[str, Any]:
    """
    Loads your JSON policy file into a nested dict:
      { role: { resource: { operation: { allow: [...], deny: [...] }}}}
    """
    with open(path, "r", encoding="utf-8") as f:
        policy = json.load(f)
    return policy