from pydantic import BaseModel

class LoginRequest(BaseModel):
    user_id: int

class ModelSelectRequest(BaseModel):
    user_id: int
    model: str  # "openai" or "hf"

class ChatRequest(BaseModel):
    user_id: int
    message: str