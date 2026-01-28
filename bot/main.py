import discord
import os
import requests
import httpx



FASTAPI_URL = "http://localhost:8000/intake/discord/message"
API_KEY = os.environ.get("FASTAPI_KEY_BOT")

intents = discord.Intents.default()
intents.members = True

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    mess = message.content.lower()

    if message.author == client.user:
        return

    if "gay" in mess:
        await message.add_reaction("🏳️‍🌈")

    if "!ask" in mess:
        processed = mess.split("!ask", 1)

        if len(processed) > 1:
            prompt = processed[1].strip()
            payload = {
                "platform": "discord",
                "tenant_id": "123",
                "message_id": str(message.id),
                "channel_id": str(message.channel.id),
                "author_id": str(message.author.id),
                "author_name": str(message.author),
                "prompt": prompt,
                "created_at": str(message.created_at),
            }

            resp = requests.post(
                FASTAPI_URL,
                json=payload,
                headers={"x_api_key": API_KEY},
                timeout=5
            )
            resp.raise_for_status()
            reply = resp.json().get("reply", "")

            if reply:
                await message.channel.send(reply)

            print("response:", resp.text)

clientToken = os.environ.get('goofbot_token')
#print(API_KEY)
client.run(clientToken)
