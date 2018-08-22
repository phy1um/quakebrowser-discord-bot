import bot
from channel_connection import ChannelCon, MessageSenderCon
from chat_command import ChatCommand, CommandsHelp
import server_api
import asyncio
import threading
from settings import DISCORD_API_TOKEN

# server API url
url = "http://phylum.sureis.sexy/browser"
# temporary API parameters
api_params = "game=CPMA&country=AU|NZ|SG"


class ChatInit(ChatCommand):
    """chat command handler for initializing server browser"""
    def _body(self):
        count = 2
        if len(self.args) > 1:
            try:
                count = int(self.args[1])
            except:
                pass
        MessageSenderCon(self.chan, api_params, message_count=count)


class ChatTest(ChatCommand):
    """trivial test that chat commands are working"""
    def _body(self):
        print("Ayy messageo")


@bot.client.async_event
async def on_message(msg):
    if(msg.author == bot.client.user):
        return
    chan = msg.channel
    sender = msg.author
    body = msg.content
    perms = chan.permissions_for(sender)
    if perms.manage_server:
        cmd = ChatCommand.process_text(body)
        print("Command processed = {}".format(cmd))
        cmd.bind_context(chan, sender)
        cmd.execute()
        await bot.client.delete_message(msg)

async def run_connections():
    api = server_api.ServerAPI(url)
    while True:
        async for servers in api.get_updating_servers(api_params, interval=5):
            async for con in ChannelCon.connection_iter():
                await con.update(servers)
        asyncio.sleep(0.1)


if __name__ == "__main__":
    ChatInit.register("browser-init")
    ChatTest.register("foo")

    class RunDiscord(threading.Thread):
        def run(self):
            bot.client.run(DISCORD_API_TOKEN)
    RunDiscord().start()
    # start async loop OR just add this task (discord.py might get in first?)
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        loop.run_until_complete(run_connections())
    else:
        loop.create_task(run_connections())
