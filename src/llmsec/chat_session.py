from typing import List, Dict
from llmsec.mitigation import preprocess, postprocess, ChatGPTClient
from llmsec.database import MySQLDatabase

class ChatSession:
    """
    Maintains a conversation with ChatGPT, enforcing RBAC on every user turn.
    """
    def __init__(
        self,
        client: ChatGPTClient,
        db: MySQLDatabase,
        user_id: int,
        system_intro: str = "You are a secure banking assistant."
    ):
        self.client    = client
        self.db        = db
        self.user_id   = user_id
        self.role      = db.get_user_role(user_id) or "Unknown"
        # initialize history with a system message that embeds the role
        self.history: List[Dict[str,str]] = [
            {
              "role":    "system",
              "content": (
                f"{system_intro}  "
                f"Enforce role-based access control: this user is a {self.role}."
              )
            }
        ]

    def send(self, user_text: str) -> str:
        """
        User sends some text → we preprocess it for RBAC,
        call ChatGPT with the full history, then postprocess.
        """
        # 1) RBAC check
        filtered = preprocess(user_text, self.role)
        if filtered.startswith("USER REQUEST BLOCKED"):
            # blocked outright
            reply = filtered
        else:
            # 2) append user turn
            self.history.append({"role":"user", "content":filtered})
            # 3) call ChatGPT
            raw = self.client.chat(self.history)
            # 4) enforce any post‐processing policies
            reply = postprocess(raw, self.role)
            # 5) append assistant turn
            self.history.append({"role":"assistant", "content":reply})

        return reply