from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.llmsec.database import MySQLDatabase
from src.llmsec.chat_session import ChatSession
from src.llmsec.policy import load_policy
from src.llmsec.mitigation import preprocess, postprocess, ChatGPTClient
#from src.llmsec.clients.openai_client import OpenAIClient
# from src.llmsec.clients.hf_client import HFLocalClient  # Swap later if needed

import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
db = MySQLDatabase(
    host="db-430.c52weece2t3h.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="Soydino1907.?02",
    database="db-430"
)
POLICY = load_policy("permissions.json")
client = ChatGPTClient(api_key=os.getenv("OPENAI_API_KEY")) 
sessions = {}

class LoginRequest(BaseModel):
    user_id: int

@router.post("/login")
def login(data: LoginRequest):
    role = db.get_user_role(data.user_id)
    if not role:
        raise HTTPException(status_code=404, detail="User not found")
    sessions[data.user_id] = ChatSession(client, db, data.user_id, POLICY)
    return {"user_id": data.user_id, "role": role}

class ChatRequest(BaseModel):
    user_id: int
    message: str

@router.post("/chat")
def chat(data: ChatRequest):
    session = sessions.get(data.user_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session not initialized. Call /login first.")
    reply = session.send(data.message)
    return {"reply": reply}