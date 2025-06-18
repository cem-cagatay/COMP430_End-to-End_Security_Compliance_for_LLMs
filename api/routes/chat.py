from fastapi import APIRouter, HTTPException
from api.schemas.chat_schema import LoginRequest, ModelSelectRequest, ChatRequest
from src.llmsec.chat_session.hf_session import HFChatSession
from src.llmsec.database import MySQLDatabase
from src.llmsec.chat_session.chatgpt_session import ChatGPTChatSession
from src.llmsec.policy import load_policy
from src.llmsec.clients.hf_client import HFClient
from src.llmsec.clients.chatgpt_client import ChatGPTClient

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

# ——— Routes ———
@router.post("/login")
def login(data: LoginRequest):
    role = db.get_user_role(data.user_id)
    if not role:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Session will be created after model is selected
    return {"user_id": data.user_id, "role": role}


@router.post("/select-model")
def select_model(data: ModelSelectRequest):
    role = db.get_user_role(data.user_id)
    if not role:
        raise HTTPException(status_code=404, detail="User not found")

    # Choose model
    if data.model == "hf":
        llm_client = HFClient()
        sessions[data.user_id] = HFChatSession(llm_client, db, data.user_id, POLICY)
    elif data.model == "openai":
        llm_client = ChatGPTClient(api_key=os.getenv("OPENAI_API_KEY"))
        sessions[data.user_id] = ChatGPTChatSession(llm_client, db, data.user_id, POLICY)
    else:
        raise HTTPException(status_code=400, detail="Invalid model selection")

    return {"status": "Model set successfully"}


@router.post("/chat")
def chat(data: ChatRequest):
    session = sessions.get(data.user_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session not initialized. Select a model first.")
    
    reply = session.send(data.message)
    return {"reply": reply}