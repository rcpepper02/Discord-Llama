import discord
import os
import httpx

FASTAPI_URL = "http://fastapi:8000/intake/discord/message"
FASTAPI_KEY_BOT = os.environ.get("FASTAPI_KEY_BOT")

intents = discord.Intents.default()
intents.members = True

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}', flush=True)

@client.event
async def on_message(message):
    mess = message.content.lower()

    if message.author == client.user:
        return

    if "gay" in mess:
        await message.add_reaction("🏳️‍🌈")

    if "!goofbot" in mess:
        processed = mess.split("!goofbot", 1)

        if len(processed) > 1:
            prompt = processed[1].strip()
            payload = {
                "message_id": str(message.id),
                "channel_id": str(message.channel.id),
                "author_name": str(message.author),
                "prompt": prompt,
            }

            try:
                async with httpx.AsyncClient(
                        timeout=httpx.Timeout(120.0, connect=5.0)
                ) as http:
                    resp = await http.post(
                        FASTAPI_URL,
                        json=payload,
                        headers={"x-api-key": FASTAPI_KEY_BOT},
                    )
            except httpx.ReadTimeout:
                await message.channel.send("model had too much whiskey")
                return
            except httpx.RequestError:
                await message.channel.send("error")
                return

            if resp.status_code != 200:
                print("Fastapi error:", resp.status_code, resp.text, flush=True)
                await message.channel.send("booty error")
                return

            reply = resp.json().get("reply","")
            if reply:
                await message.channel.send(reply)

clientToken = os.environ.get('goofbot_token')
#print(API_KEY)
client.run(clientToken)
