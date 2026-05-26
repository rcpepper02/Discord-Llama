import discord
import os
import httpx
from PIL import Image, ImageOps
from PIL import ImageFilter
from PIL import ImageShow
import random

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

    if "!bingo" in mess:
        processed = mess.split("!bingo", 1)
        prompt = processed[1].strip()

        global bingo_msg, boxes, box_width, box_height, slices, grid, freespace

        if "new" in prompt:
            with Image.open("bingo.png") as im:
                width, height = im.size
                box_width = width // 5
                box_height = height // 7
                boxes = []
                slices = []

                for row in range(7):
                    for col in range(5):
                        box = (
                            col * box_width,
                            row * box_height,
                            (col + 1) * box_width,
                            (row + 1) * box_height
                        )
                        boxes.append(box)
                        if row == 6 and col == 2:
                            freespace = im.crop(box)
                        else:
                            slices.append(im.crop(box))

                random.shuffle(slices)
                grid = [boxes[i:i+5] for i in range(0, len(boxes), 5)]

                for i in range(len(boxes)-10):
                    if i == 12:
                        im.paste(freespace, boxes[i])
                    else:
                        im.paste(slices[i], boxes[i])

                im = im.crop([0,0,width, box_height*5])
                im.save("bingo_shuffle.png")
    
            with open('bingo_shuffle.png', 'rb') as f:
                picture = discord.File(f)
                bingo_msg = await message.channel.send(file=picture)

        elif "x" in prompt:
            if bingo_msg is None:
                await message.channel.send("no bingo board")
                return

            col = int(prompt[-2])-1
            row = int(prompt[-1])-1

            #grid = [boxes[i:i+5] for i in range(0, len(boxes), 5)]

            bingo = Image.open("bingo_shuffle.png")
            x = Image.open("cross-x.png")
            x = ImageOps.contain(x, (box_width, box_height))
            box = grid[row][col]
            bingo.paste(x, box[:2], mask=x)
            bingo.save("bingo_shuffle.png")
            with open('bingo_shuffle.png', 'rb') as f:
                picture = discord.File(f)
                await bingo_msg.edit(attachments=[picture])
        
        elif "rm" in prompt:
            if bingo_msg is None:
                await message.channel.send("no bingo board")
                return
            
            col = int(prompt[-2])-1
            row = int(prompt[-1])-1

            bingo = Image.open("bingo_shuffle.png")
            slices_grid = [slices[i:i+5] for i in range(0, len(slices), 5)]
            square = slices_grid[row][col]
            box = grid[row][col]
            bingo.paste(square, box[:2])
            bingo.save("bingo_shuffle.png")
            with open('bingo_shuffle.png', 'rb') as f:
                picture = discord.File(f)
                await bingo_msg.edit(attachments=[picture])

        elif "repost" in prompt:
            with open('bingo_shuffle.png', 'rb') as f:
                picture = discord.File(f)
                bingo_msg = await message.channel.send(file=picture)

        else:
            help_message = """!bingo new - new board
            !bingo x <col><row> - add x
            !bingo rm <col><row> - remove an x
            !bingo repost - repost board"""
            await message.channel.send(help_message)

clientToken = os.environ.get('goofbot_token')
#print(API_KEY)
client.run(clientToken)
