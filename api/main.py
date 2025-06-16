from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat

app = FastAPI()

# Enable frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)