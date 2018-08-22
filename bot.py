import discord
import asyncio
import server_api

client = discord.Client()


async def clear_chan(c):
    logs = client.logs_from(c, limit=10)
    async for msg in logs:
        await client.delete_message(msg)


@client.async_event
async def on_ready():
    print("Logged in: " + client.user.name + ":" + client.user.id)


@client.async_event
async def on_server_join(server):
    print("Joined " + str(server))
    for ch in server.channels:
        print("Chan: " + str(ch))
