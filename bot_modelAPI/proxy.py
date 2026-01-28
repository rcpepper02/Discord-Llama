#from dns import message
import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()
INTERNAL_API_KEY = os.environ.get("FASTAPI_KEY_BOT")
seen = set()

class DiscordMsgIn(BaseModel):
    platform: str
    tenant_id: str
    message_id: str
    channel_id: str
    author_id: str
    author_name: str
    prompt: str
    created_at: str


@app.post("/intake/discord/message")
async def intake_discord(msg: DiscordMsgIn, x_api_key: str = Header(default = INTERNAL_API_KEY)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Internal API key required")

    prompt = f"{msg.author_name}: {msg.prompt}\nYou possess an iq of ~80. Respond concisely:"

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "http://ollama:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        data = response.json()

    return {"reply": (data.get("response") or "").strip()}