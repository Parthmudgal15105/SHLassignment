from fastapi import FastAPI

from app.agent import handle_chat
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="SHL Assessment Recommender")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return handle_chat(request)
