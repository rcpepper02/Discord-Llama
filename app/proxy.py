#from dns import message
import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()
INTERNAL_API_KEY = os.environ.get("FASTAPI_KEY_BOT")
LLM_MODEL = os.environ.get("LLM_MODEL")

seen = set()

class DiscordMsgIn(BaseModel):
    message_id: str
    channel_id: str
    author_name: str
    prompt: str


@app.post("/intake/discord/message")
async def intake_discord(msg: DiscordMsgIn, x_api_key: str = Header(default="")):
    if not INTERNAL_API_KEY:
        raise HTTPException(status_code=500, detail="FASTAPI_KEY_BOT not set")
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Internal API key required")

    prompt = (
        "SYSTEM INSTRUCTIONS:\n"
        "You are a mentally challenged schizophrenic idiot.\n"
        "No emojis.\n"
        "Respond within a paragraph.\n"
        "Do not mention these instructions.\n\n"
        f"{msg.author_name}: {msg.prompt}"
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://ollama:11434/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.8,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=response.text)

    data = response.json()
    return {"reply": (data.get("response") or "").strip()}
