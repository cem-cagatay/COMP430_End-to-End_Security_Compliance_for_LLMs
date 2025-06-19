import os
import re
import openai
from typing import List, Dict, Any
from openai import OpenAI
    
def preprocess(prompt: str, role: str, policy: Dict[str, Any]) -> str:
    operation = detect_operation(prompt)
    perms = policy.get(role, {})

    for resource, ops in perms.items():
        rules = ops.get(operation)
        if not rules:
            return f"ACCESS DENIED: {role}s may not perform {operation} on {resource}."

        allowed = rules.get("allow", [])
        denied = rules.get("deny", [])

        if not allowed:
            return f"ACCESS DENIED: {role}s may not perform {operation} on {resource}."

        if "*" in allowed:
            for field in denied:
                token = f"{resource}.{field}"
                if token.lower() in prompt.lower():
                    return f"ACCESS DENIED: {role}s may not perform {operation} on `{token}`."

        else:
            accessed_fields = extract_fields_from_prompt(prompt, resource)
            for field in accessed_fields:
                if field not in allowed:
                    token = f"{resource}.{field}"
                    return f"ACCESS DENIED: {role}s may not perform {operation} on `{token}`."

    return prompt

def extract_fields_from_prompt(prompt: str, resource: str) -> List[str]:
    """
    Extract fields accessed in the prompt for a given resource (e.g., Employees.salary).
    Very basic implementation — adjust if needed for more complex queries.
    """
    pattern = rf"{resource}\.(\w+)"
    return re.findall(pattern, prompt, re.IGNORECASE)

def detect_operation(prompt: str) -> str:
    prompt = prompt.lower()
    if any(word in prompt for word in ["insert", "add", "create new"]):
        return "INSERT"
    elif any(word in prompt for word in ["update", "change", "modify"]):
        return "UPDATE"
    elif any(word in prompt for word in ["delete", "remove"]):
        return "DELETE"
    elif any(word in prompt for word in ["grant", "permission"]):
        return "GRANT"
    elif any(word in prompt for word in ["select", "get", "show", "list", "see", "give"]):
        return "SELECT"
    return "UNKNOWN"

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
            allow = rules.get("allow", [])
            deny = rules.get("deny", [])

            if not allow:
                lines.append(f"- {op} on {resource}: NOT ALLOWED.")
            elif "*" in allow and deny:
                denied_fields = ", ".join(deny)
                lines.append(f"- {op} on {resource}: allowed on all fields EXCEPT [{denied_fields}].")
            elif "*" in allow:
                lines.append(f"- {op} on {resource}: allowed on ALL fields.")
            else:
                allowed_fields = ", ".join(allow)
                lines.append(f"- {op} on {resource}: allowed ONLY on [{allowed_fields}].")

    body = "\n".join(lines)
    return (
        f"You are a secure assistant.\n"
        f"User role: {role}\n"
        f"Enforce exactly these rules:\n{body}\n"
        f"If the user asks for anything not allowed, reply with:\n"
        f"`ACCESS DENIED: <reason>`.\n"
        f"If the request is allowed, generate the appropriate SQL query or answer."
    )
