from typing import List, Dict, Any
import re
from src.llmsec.mitigation import preprocess, postprocess
from src.llmsec.clients.base_client import LLMClient
from src.llmsec.clients.hf_client import HFClient
from src.llmsec.database import MySQLDatabase
from src.llmsec.mitigation import make_system_prompt

class ChatSession:
    """
    Maintains a conversation with ChatGPT,
    enforcing RBAC and actually hitting the database.
    """
    def __init__(self, client: LLMClient, db: MySQLDatabase,
        user_id: int, policy: Dict[str, Any]):
        self.client  = client
        self.db      = db
        self.user_id = user_id
        self.role    = db.get_user_role(user_id) or "Unknown"
        self.policy  = policy

        # Build and log the system‐prompt
        sysmsg = make_system_prompt(self.role, policy)
        print("System prompt is:\n", sysmsg)
        self.history = [{"role":"system","content":sysmsg}]

    def send(self, user_text: str) -> str:
        # 1) Enforce deny‐rules
        filtered = preprocess(user_text, self.role, self.policy)
        print("Preprocessed input:", filtered)
        if filtered.startswith("ACCESS DENIED"):
            return filtered

        # 2) Ask ChatGPT for a SQL query
        sql_request = (
            "Translate the user’s request into a single SQL SELECT statement "
            "on the Employees table.  \n**Only** output the SQL, no explanation.\n"
            f"Request: {filtered}"
        )
        if isinstance(self.client, HFClient):
            # Flatten full prompt for Zephyr
            flattened_prompt = f"{self.history[0]['content']}\n\n{sql_request}"
            raw_sql = self.client.chat([{"role": "user", "content": flattened_prompt}]).strip()
        else:
            self.history.append({"role":"user","content":sql_request})
            raw_sql = self.client.chat(self.history).strip()
        print("🔍 Generated SQL:\n", raw_sql)

        # … after you grab raw_sql …
        clean = raw_sql.strip()

        # strip markdown fences
        clean = re.sub(r"^```(?:sql)?\s*|\s*```$", "", clean, flags=re.IGNORECASE).strip()
        # drop any leading prose before the first SELECT
        clean = re.sub(r"^.*?SELECT", "SELECT", clean, flags=re.IGNORECASE | re.DOTALL)

        # OPTION A: ensure semicolon
        if not clean.endswith(";"):
            clean += ";"

        print("Cleaned SQL:", clean)

        # now match (semicolon optional if you choose Option B instead)
        pattern = (
            r"SELECT\s+(?P<cols>[\s\S]+?)\s+FROM\s+(?P<table>\w+)"
            r"(?:\s+WHERE\s+(?P<where>[\s\S]+?))?\s*;?"
        )
        m = re.search(pattern, clean, flags=re.IGNORECASE)
        if not m:
            return f"Error: could not parse SQL from LLM:\n{raw_sql}"

        cols  = [c.strip() for c in m.group("cols").split(",")]
        table = m.group("table")
        where = (m.group("where") or "").strip()

        # 4) Run the query
        try:
            rows = self.db.query(table, cols, where)
        except Exception as e:
            return f"Database error: {e}"

        # 5) Format the results
        if not rows:
            result_str = "(no rows returned)"
        else:
            # Simple text table
            header = " | ".join(cols)
            lines = [header, "-" * len(header)]
            for row in rows:
                lines.append(" | ".join(str(v) for v in row))
            result_str = "\n".join(lines)

        # 6) Optionally postprocess & append to history
        out = postprocess(result_str, self.role)
        self.history.append({"role":"assistant","content":out})
        return out