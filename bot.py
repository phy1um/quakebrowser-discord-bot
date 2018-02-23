import discord
import asyncio
from serverstatus import ServerStatus

token = "NDE5Nzg5NTYyOTY1OTE3Njk3.DX1UgA.yZpv9xCJNBKtzQc3LtpwCt6J5FU" 
client = discord.Client()
active_chans= {}

async def clear_chan(c):
    logs = client.logs_from(c,limit=10)
    async for msg in logs:
        await client.delete_message(msg)


@client.async_event
async def on_ready():
    print("Logged in: " + client.user.name + ":" + client.user.id)


@client.async_event
async def on_message(msg):
    if msg.author == client.user:
        return

    else:
        chan = msg.channel
        sender = msg.author
        body = msg.content

        if body[0] == "!":
            perms = chan.permissions_for(sender)
            if perms.manage_server or str(sender).index("phylum"):
                c = body[1:]
                print(c)
                if c == "browser-init":
                    print("TARGET: " + str(chan.server)+":"+str(chan))
                    x = ServerStatus('http://0.0.0.0:3000/api/list')
                    last_msg = hash("")
                    @x.async_server_handler
                    async def put_message(s):
                        h = hash(s)
                        if h != last_msg:
                            await clear_chan(chan)
                            await client.send_message(chan, x.get_browser_string())
                        else:
                            print("duplicate of last message")
                    key = str(chan.server)+":"+str(chan)
                    active_chans[key] = asyncio.Event()
                    interval = 120
                    counter = 0
                    x.update()
                    while not active_chans[key].is_set():
                        counter += 1
                        await asyncio.sleep(1)
                        if counter >= interval:
                            counter = 0
                            x.update()

                    print("Done " + key)
                    await clear_chan(chan)
                    await client.send_message(chan, "SERVER BROWSER STOPPED!")

                if c == "foo":
                    print("AHH")

                if c == "browser-stop":
                    key = str(chan.server) + ":" + str(chan)
                    if key in active_chans:
                        active_chans[key].set()
                    else:
                        print("Unknown " + key)

        
            else:
                print("COMMAND PERMISSION DENIED FOR: " + str(sender))

@client.async_event
async def on_server_join(server):
    print("Joined " + str(server))
    for ch in server.channels:
        print("Chan: " + str(ch))

client.run(token)
