from src.llmsec.chat_session.base import BaseChatSession
from src.llmsec.mitigation import preprocess, postprocess, make_system_prompt
from src.llmsec.database import MySQLDatabase
from src.llmsec.clients.hf_client import HFClient
import re

class HFChatSession(BaseChatSession):
    def __init__(self, client, db, user_id, policy):
        super().__init__(client, db, user_id, policy)
        self.system_prompt = make_system_prompt(self.role, policy)

    def send(self, user_text: str) -> str:
        filtered = self._preprocess(user_text)
        if filtered.startswith("ACCESS DENIED"):
            return filtered

        prompt = self._build_prompt(filtered)
        raw_sql = self._query_llm(prompt)
        print("🔍 Generated SQL:\n", raw_sql)

        clean_sql = self._extract_sql(raw_sql)
        if clean_sql is None:
            return f"Error: could not find valid SQL:\n{raw_sql}"

        return self._run_query_and_format_result(clean_sql)

    def _preprocess(self, text: str) -> str:
        return preprocess(text, self.role, self.policy)

    def _build_prompt(self, filtered_text: str) -> str:
        return (
            f"{self.system_prompt}\n\n"
            "You are a secure SQL assistant.\n"
            "ONLY output a single SQL SELECT statement, no explanation or commentary.\n"
            "DO NOT include markdown formatting or extra text.\n"
            "The SQL must query the Employees table based on the user request.\n"
            f"User request: {filtered_text}"
        )

    def _query_llm(self, prompt: str) -> str:
        return self.client.chat([{"role": "user", "content": prompt}]).strip()

    def _extract_sql(self, raw: str) -> str | None:
        # Remove markdown-style code fences from LLM output like ```sql ... ```
        clean = re.sub(r"^```(?:sql)?\s*|\s*```$", "", raw, flags=re.IGNORECASE).strip()

        # Attempt to extract a valid SQL SELECT statement that ends with a semicolon
        # This pattern captures everything from SELECT to the first semicolon
        sql_match = re.search(r"(SELECT\s.+?;)", clean, flags=re.IGNORECASE | re.DOTALL)

        # If we find a valid SQL block, return the matched portion with surrounding whitespace removed
        if sql_match:
            return sql_match.group(1).strip()
        if "SELECT" in clean.upper():
            # This strips off any leading commentary or instruction before the SELECT keyword
            return re.sub(r"^.*?(SELECT)", r"\1", clean, flags=re.IGNORECASE | re.DOTALL).strip() + ";"
        return None

    def _run_query_and_format_result(self, sql: str) -> str:
        # Define a regex pattern to parse the SQL query into its components:
        # - SELECT columns
        # - FROM table name
        # - Optional WHERE clause
        pattern = (
            r"SELECT\s+(?P<cols>[\s\S]+?)\s+FROM\s+(?P<table>\w+)"
            r"(?:\s+WHERE\s+(?P<where>[\s\S]+?))?\s*;?"
        )
        # Try to match the SQL string against the regex pattern
        m = re.search(pattern, sql, flags=re.IGNORECASE)

        # If the pattern does not match, the SQL is malformed or not supported
        if not m:
            return f"Error: could not parse SQL structure:\n{sql}"

        # Extract the column list from the SELECT clause and split it into individual columns
        cols = [c.strip() for c in m.group("cols").split(",")]

        # Extract the table name from the FROM clause
        table = m.group("table")
        # Extract the WHERE clause if it exists, otherwise use an empty string
        where = (m.group("where") or "").strip()

        # Attempt to run the SQL query using your database adapter
        try:
            rows = self.db.query(table, cols, where)
        except Exception as e:
            # Catch and return any database-level errors (e.g., malformed columns, invalid conditions)
            return f"Database error: {e}"

        # If no rows were returned by the query, display a default message
        if not rows:
            result_str = "(no rows returned)"
        else:
            # Build a simple text table representation of the query results
            header = " | ".join(cols) # Join column headers with vertical bars
            lines = [header, "-" * len(header)] # Add a line of dashes under the header
            for row in rows:
                lines.append(" | ".join(str(v) for v in row))
            # Combine all lines into a single string separated by newlines
            result_str = "\n".join(lines)

        return postprocess(result_str, self.role)