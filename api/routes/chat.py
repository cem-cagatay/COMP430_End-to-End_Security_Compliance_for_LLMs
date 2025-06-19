from fastapi import APIRouter, HTTPException
from api.schemas.chat_schema import LoginRequest, ChatRequest
from src.llmsec.chat_session.chatgpt_session import ChatGPTChatSession
from src.llmsec.database import MySQLDatabase
from src.llmsec.policy import load_policy
from src.llmsec.clients.chatgpt_client import ChatGPTClient
from src.llmsec.clients.hf_client import HFClient
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
gpt_client = ChatGPTClient(api_key=os.getenv("OPENAI_API_KEY"))
hf_client = HFClient()
sessions = {}

# ——— Routes ———
@router.post("/login")
def login(data: LoginRequest):
    role = db.get_user_role(data.user_id)
    if not role:
        raise HTTPException(status_code=404, detail="User not found")

    sessions[data.user_id] = ChatGPTChatSession(gpt_client, db, data.user_id, POLICY)
    return {"user_id": data.user_id, "role": role}


@router.post("/chat")
def chat(data: ChatRequest):
    session = sessions.get(data.user_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session not initialized. Please log in first.")

    # Call HF model to detect malicious prompt
    hf_label = hf_client.chat([{"role": "user", "content": data.message}])
    print("HF Detected Classification Label:", hf_label)

    if hf_label == 1:
        return {"reply": "This prompt was flagged as suspicious or potentially unsafe. Please rephrase your request."}
    
    reply = session.send(data.message)
    return {"reply": reply}