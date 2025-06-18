from abc import ABC, abstractmethod
from src.llmsec.database import MySQLDatabase
from src.llmsec.clients.base_client import LLMClient
from typing import Dict, Any

class BaseChatSession(ABC):
    def __init__(self, client: LLMClient, db: MySQLDatabase, user_id: int, policy: Dict[str, Any]):
        self.client = client
        self.db = db
        self.user_id = user_id
        self.role = db.get_user_role(user_id) or "Unknown"
        self.policy = policy

    @abstractmethod
    def send(self, user_text: str) -> str:
        pass