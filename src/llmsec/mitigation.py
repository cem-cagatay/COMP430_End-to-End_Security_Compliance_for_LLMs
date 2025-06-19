import os
import re
import openai
from typing import List, Dict, Any
from openai import OpenAI

from src.llmsec.database import MySQLDatabase
    
def preprocess(prompt: str, role: str, policy: Dict[str, Any], db: MySQLDatabase) -> str:
    operation = detect_operation(prompt)
    print(f"[DEBUG] OPERATION: {operation}")

    friendly_ops = {
        "SELECT": "access",
        "UPDATE": "update",
        "INSERT": "add",
        "DELETE": "delete",
        "GRANT": "grant"
    }
    action = friendly_ops.get(operation, operation.lower())

    if operation == "UNKNOWN":
        return prompt

    perms = policy.get(role, {})

    for resource, ops in perms.items():
        rules = ops.get(operation)
        table_fields = db.get_fields_for_table(resource)
        accessed_fields = extract_fields_from_prompt(prompt, table_fields)

        if not rules:
            if accessed_fields:
                field_name = accessed_fields[0].split(".")[-1]
                return f"ACCESS DENIED: {role}s may not {action} the `{field_name}` field."
            return f"ACCESS DENIED: {role}s are not allowed to {action} information in this company."

        allowed = rules.get("allow", [])
        denied = rules.get("deny", [])

        if not allowed:
            if accessed_fields:
                field_name = accessed_fields[0].split(".")[-1]
                return f"ACCESS DENIED: {role}s may not {action} the `{field_name}` field."
            return f"ACCESS DENIED: {role}s are not allowed to {action} information in this company."

        if "*" in allowed:
            for field in accessed_fields:
                if field in denied:
                    return f"ACCESS DENIED: {role}s may not {action} the `{field}` field."

        else:
            print(f"[DEBUG] ROLE: {role}")
            print(f"[DEBUG] Allowed fields: {allowed}")
            print(f"[DEBUG] Denied fields: {denied}")
            print(f"[DEBUG] Prompt: {prompt}")
            print(f"[DEBUG] Accessed fields: {accessed_fields}")
            for field in accessed_fields:
                if field not in allowed:
                    return f"ACCESS DENIED: {role}s may not {action} the `{field}` field."

    return prompt

def extract_fields_from_prompt(prompt: str, table_fields: List[str]) -> List[str]:
    prompt = prompt.lower()
    print("[DEBUG] extract_fields_from_prompt() scanning for:", table_fields)
    return [field for field in table_fields if field.lower() in prompt]

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
        f"Generate the appropriate SQL query or answer."
    )
