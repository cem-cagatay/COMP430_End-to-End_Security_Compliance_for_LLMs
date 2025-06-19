from pydantic import BaseModel

class LoginRequest(BaseModel):
    user_id: int

class ChatRequest(BaseModel):
    user_id: int
    message: str