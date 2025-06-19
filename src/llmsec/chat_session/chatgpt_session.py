from typing import List, Dict, Any
import re
from src.llmsec.chat_session.base import BaseChatSession
from src.llmsec.mitigation import preprocess, postprocess
from src.llmsec.mitigation import make_system_prompt

class ChatGPTChatSession(BaseChatSession):
    """
    Maintains a conversation with ChatGPT,
    enforcing RBAC and actually hitting the database.
    """
    def __init__(self, client, db, user_id, policy):
        super().__init__(client, db, user_id, policy)
        sysmsg = make_system_prompt(self.role, policy)
        self.history = [{"role": "system", "content": sysmsg}]

    def send(self, user_text: str) -> str:
        filtered = self._preprocess(user_text)
        print("Preprocessed:", filtered)
        if filtered.startswith("ACCESS DENIED"):
            return filtered

        self._build_prompt(filtered)
        raw_output = self._query_llm()
        clean_sql = self._extract_sql(raw_output)

        if clean_sql:
            return self._run_query_and_format_result(clean_sql)
        else:
            return raw_output  # already a natural response

    def _preprocess(self, text: str) -> str:
        return preprocess(text, self.role, self.policy, self.db)

    def _build_prompt(self, filtered_text: str):
        sql_instruction = (
            "You are a secure assistant who can generate SQL queries for the Employees database "
            "when the user asks for information that requires querying the data.\n"
            "If the user's request is conversational, general, or not related to data in the Employees table, "
            "respond naturally instead. Only generate a SQL SELECT statement if appropriate.\n"
            "When generating SQL, do not explain it — just return the raw query."
        )
        self.history.append({"role": "user", "content": f"{sql_instruction}\nRequest: {filtered_text}"})

    def _query_llm(self) -> str:
        return self.client.chat(self.history).strip()

    def _extract_sql(self, raw: str) -> str | None:
        clean = re.sub(r"^```(?:sql)?\s*|\s*```$", "", raw, flags=re.IGNORECASE).strip()
        sql_match = re.search(r"(SELECT\s.+?;)", clean, flags=re.IGNORECASE | re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        if "SELECT" in clean.upper():
            return re.sub(r"^.*?(SELECT)", r"\1", clean, flags=re.IGNORECASE | re.DOTALL).strip() + ";"
        return None

    def _run_query_and_format_result(self, sql: str) -> str:
        pattern = (
            r"SELECT\s+(?P<cols>[\s\S]+?)\s+FROM\s+(?P<table>\w+)"
            r"(?:\s+WHERE\s+(?P<where>[\s\S]+?))?\s*;?"
        )
        m = re.search(pattern, sql, flags=re.IGNORECASE)
        if not m:
            return f"Error: could not parse SQL structure:\n{sql}"

        cols = [c.strip() for c in m.group("cols").split(",")]
        table = m.group("table")
        where = (m.group("where") or "").strip()

        try:
            rows = self.db.query(table, cols, where)
        except Exception as e:
            return f"Database error: {e}"

        if not rows:
            result_str = "(no rows returned)"
        else:
            header = " | ".join(cols)
            lines = [header, "-" * len(header)]
            for row in rows:
                lines.append(" | ".join(str(v) for v in row))
            result_str = "\n".join(lines)

        out = postprocess(result_str, self.role)
        self.history.append({"role": "assistant", "content": out})
        return out